"""
Vector Service for Insight MVP - Fixed version without OpenAI compatibility issues
Handles vector embeddings and similarity search using fallback embeddings
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct
import os
import logging
from loguru import logger

# Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_URL = os.getenv("QDRANT_URL", f"http://{QDRANT_HOST}:{QDRANT_PORT}")
COLLECTION = "documents"
EMBEDDING_DIM = 1536  # Standard OpenAI embedding dimension

app = FastAPI(title="Vector Service", description="Vector embeddings and similarity search")

# Initialize Qdrant client (with URL and retry)
def create_qdrant_client_with_retry(max_retries: int = 10, delay_seconds: float = 1.0):
    import time
    last_error: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            client = QdrantClient(url=QDRANT_URL, prefer_grpc=False, timeout=5.0)
            # Trigger a lightweight call to ensure connectivity
            client.get_collections()
            logger.info(f"Connected to Qdrant at {QDRANT_URL} (attempt {attempt})")
            return client
        except Exception as e:
            last_error = e
            logger.warning(f"Qdrant not ready (attempt {attempt}/{max_retries}): {e}")
            time.sleep(delay_seconds)
    logger.error(f"Failed to connect to Qdrant after {max_retries} attempts: {last_error}")
    return None

qdrant_client = create_qdrant_client_with_retry()

def ensure_qdrant_client() -> Optional[QdrantClient]:
    """Lazy re-connect if client is not yet available."""
    global qdrant_client
    if qdrant_client is not None:
        return qdrant_client
    qdrant_client = create_qdrant_client_with_retry(max_retries=20, delay_seconds=0.5)
    return qdrant_client

class UpsertPayload(BaseModel):
    doc_id: int
    segments: List[str]

class SearchPayload(BaseModel):
    query: str
    top_k: Optional[int] = 5

def generate_mock_embedding(text: str, dim: int = EMBEDDING_DIM) -> List[float]:
    """Generate consistent mock embeddings based on text content"""
    # Simple hash-based embedding generation for consistency
    import hashlib
    
    # Create a hash of the text
    text_hash = hashlib.md5(text.encode()).hexdigest()
    
    # Convert hash to numbers
    seed = int(text_hash[:8], 16)
    np.random.seed(seed)
    
    # Generate normalized vector
    vector = np.random.normal(0, 1, dim)
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    
    return vector.tolist()

def ensure_collection(dim: int = EMBEDDING_DIM):
    """Ensure collection exists in Qdrant"""
    client = ensure_qdrant_client()
    if not client:
        return
    
    try:
        existing = client.get_collections()
        names = [c.name for c in existing.collections]
        
        if COLLECTION not in names:
            client.create_collection(
                collection_name=COLLECTION,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )
            logger.info(f"Created collection {COLLECTION} with dimension {dim}")
    except Exception as e:
        logger.error(f"Error ensuring collection: {e}")

@app.on_event("startup")
def startup_event():
    """Initialize on startup"""
    ensure_collection()
    logger.info("Vector service started successfully")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "vector-service"}

@app.post("/index")
def upsert_embedding(payload: UpsertPayload):
    """Index document segments with mock embeddings"""
    try:
        client = ensure_qdrant_client()
        if not client:
            raise HTTPException(status_code=500, detail="Qdrant client not available")
        
        ensure_collection(EMBEDDING_DIM)
        
        # Generate embeddings for all segments
        embeddings = []
        for segment in payload.segments:
            embedding = generate_mock_embedding(segment, EMBEDDING_DIM)
            embeddings.append(embedding)
        
        # Create points for Qdrant
        points = []
        base_id = payload.doc_id * 1000000
        
        for idx, (segment_text, vector) in enumerate(zip(payload.segments, embeddings)):
            point_id = base_id + idx
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "doc_id": payload.doc_id,
                        "text": segment_text,
                        "segment_index": idx
                    },
                )
            )
        
        # Upsert to Qdrant
        client.upsert(collection_name=COLLECTION, wait=True, points=points)
        logger.info(f"Successfully indexed {len(points)} segments for document {payload.doc_id}")
        
        return {
            "upserted": len(points),
            "embedding_dim": EMBEDDING_DIM,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error upserting embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
def search_vectors(payload: SearchPayload):
    """Search for similar vectors"""
    try:
        client = ensure_qdrant_client()
        if not client:
            raise HTTPException(status_code=500, detail="Qdrant client not available")
        
        # Generate embedding for query
        query_vector = generate_mock_embedding(payload.query, EMBEDDING_DIM)
        
        # Search in Qdrant
        search_results = client.search(
            collection_name=COLLECTION,
            query_vector=query_vector,
            limit=payload.top_k,
            with_payload=True
        )
        
        # Format results
        results = []
        for result in search_results:
            results.append({
                "id": result.id,
                "score": float(result.score),
                "doc_id": result.payload.get("doc_id"),
                "text": result.payload.get("text", ""),
                "segment_index": result.payload.get("segment_index", 0)
            })
        
        logger.info(f"Found {len(results)} results for query: {payload.query[:50]}...")
        
        return {
            "query": payload.query,
            "results": results,
            "total": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching vectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections")
def list_collections():
    """List available collections"""
    try:
        if not qdrant_client:
            return {"collections": []}
        
        collections = qdrant_client.get_collections()
        return {
            "collections": [c.name for c in collections.collections]
        }
    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        return {"collections": [], "error": str(e)}

@app.delete("/collections/{collection_name}")
def delete_collection(collection_name: str):
    """Delete a collection"""
    try:
        if not qdrant_client:
            raise HTTPException(status_code=500, detail="Qdrant client not available")
        
        qdrant_client.delete_collection(collection_name)
        logger.info(f"Deleted collection: {collection_name}")
        
        return {"status": "deleted", "collection": collection_name}
        
    except Exception as e:
        logger.error(f"Error deleting collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
