import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct
from openai import OpenAI
from loguru import logger


QDRANT_HOST = os.environ.get("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", 6333))
COLLECTION = "pdf_segments"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI embedding model

app = FastAPI(title="Vector Service", version="0.1.0")

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Get embeddings using OpenAI API or fallback to local model"""
    if not openai_client:
        logger.warning("OpenAI API key not available, using mock embeddings")
        # Return mock embeddings for testing
        return [[0.1] * 1536 for _ in texts]
    
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts
        )
        return [embedding.embedding for embedding in response.data]
    except Exception as e:
        logger.error(f"Error getting embeddings from OpenAI: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")

def ensure_collection(dim: int):
    existing = qdrant_client.get_collections()
    names = [c.name for c in existing.collections]
    if COLLECTION not in names:
        qdrant_client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        logger.info(f"Created collection {COLLECTION} with dimension {dim}")


class UpsertPayload(BaseModel):
    doc_id: int
    segments: List[str]


class SearchPayload(BaseModel):
    query: str
    top_k: int | None = 5


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/collections")
def collections():
    """Get information about all collections"""
    try:
        return qdrant_client.get_collections().dict()
    except Exception as e:
        logger.error(f"Error getting collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index")
def upsert_embedding(payload: UpsertPayload):
    """Index document segments with embeddings"""
    try:
        # Get embeddings from OpenAI
        embeddings = get_embeddings(payload.segments)
        embedding_dim = len(embeddings[0]) if embeddings else 1536
        
        ensure_collection(embedding_dim)
        
        points = []
        base_id = payload.doc_id * 1000000
        
        for idx, (segment_text, vec) in enumerate(zip(payload.segments, embeddings)):
            point_id = base_id + idx
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vec,
                    payload={
                        "doc_id": payload.doc_id, 
                        "text": segment_text,
                        "segment_index": idx
                    },
                )
            )
        
        qdrant_client.upsert(collection_name=COLLECTION, wait=True, points=points)
        logger.info(f"Successfully indexed {len(points)} segments for document {payload.doc_id}")
        
        return {"upserted": len(points), "embedding_dim": embedding_dim}
        
    except Exception as e:
        logger.error(f"Error upserting embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
def search(payload: SearchPayload):
    """Search for similar document segments"""
    try:
        # Get query embedding
        query_embeddings = get_embeddings([payload.query])
        query_vec = query_embeddings[0]
        
        ensure_collection(len(query_vec))
        
        results = qdrant_client.search(
            collection_name=COLLECTION, 
            query_vector=query_vec, 
            limit=payload.top_k or 5
        )
        
        return [
            {
                "score": float(r.score),
                "text": r.payload.get("text", ""),
                "doc_id": r.payload.get("doc_id"),
                "segment_index": r.payload.get("segment_index", 0)
            }
            for r in results
        ]
        
    except Exception as e:
        logger.error(f"Error searching: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upsert_embedding")
def upsert_embedding_legacy(payload: UpsertPayload):
    """Legacy endpoint for backward compatibility"""
    return upsert_embedding(payload)


