import os
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import httpx
from loguru import logger
import pypdf
import io

# Configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@postgres:5432/insight_db")
VECTOR_SERVICE_URL = os.environ.get("VECTOR_SERVICE_URL", "http://vector-service:8002")

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(title="Document Service", version="0.1.0")

# Models
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    file_path = Column(String, nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_size = Column(Integer, nullable=True)
    pages_count = Column(Integer, nullable=True)

# Pydantic models
class DocumentResponse(BaseModel):
    id: int
    filename: str
    title: Optional[str]
    upload_date: datetime
    file_size: Optional[int]
    pages_count: Optional[int]
    
    class Config:
        from_attributes = True

class DocumentDetail(BaseModel):
    id: int
    filename: str
    title: Optional[str]
    content: str
    file_path: Optional[str]
    upload_date: datetime
    file_size: Optional[int]
    pages_count: Optional[int]
    
    class Config:
        from_attributes = True

class IngestFolderRequest(BaseModel):
    folder_path: str

# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)

# Utility functions
def extract_text_from_pdf(file_content: bytes) -> tuple[str, int]:
    """Extract text from PDF content and return text and page count"""
    try:
        pdf_file = io.BytesIO(file_content)
        reader = pypdf.PdfReader(pdf_file)
        pages_count = len(reader.pages)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip(), pages_count
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Find the last complete sentence or word
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            last_space = chunk.rfind(' ')
            
            # Choose the best breaking point
            break_point = max(last_period, last_newline, last_space)
            if break_point > start + chunk_size // 2:  # Don't break too early
                chunk = text[start:start + break_point + 1]
        
        chunks.append(chunk.strip())
        
        # Move start position with overlap
        start = start + len(chunk) - overlap
        if start >= len(text):
            break
    
    return chunks

async def send_to_vector_service(doc_id: int, text_chunks: List[str]):
    """Send text chunks to vector service for embedding"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{VECTOR_SERVICE_URL}/index",  # Updated endpoint name
                json={"doc_id": doc_id, "segments": text_chunks}
            )
            response.raise_for_status()
            logger.info(f"Successfully sent {len(text_chunks)} chunks to vector service for doc {doc_id}")
            return response.json()
    except Exception as e:
        logger.error(f"Error sending to vector service: {e}")
        # Don't fail the document ingestion if vector service is down
        return {"error": str(e)}

# Endpoints
@app.get("/health")
def health():
    return {"status": "ok", "service": "document-service"}

@app.post("/ingest", response_model=DocumentResponse)
async def ingest_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Ingest a single PDF document"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Extract text from PDF
        text_content, pages_count = extract_text_from_pdf(file_content)
        
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="No text content found in PDF")
        
        # Save to database
        document = Document(
            filename=file.filename,
            title=title or file.filename,
            content=text_content,
            file_size=file_size,
            pages_count=pages_count
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Create text chunks and send to vector service
        text_chunks = chunk_text(text_content)
        await send_to_vector_service(document.id, text_chunks)
        
        logger.info(f"Successfully ingested document {document.id}: {file.filename}")
        
        return DocumentResponse.from_orm(document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.get("/documents", response_model=List[DocumentResponse])
def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of all documents"""
    documents = db.query(Document).offset(skip).limit(limit).all()
    return [DocumentResponse.from_orm(doc) for doc in documents]

@app.get("/document/{document_id}", response_model=DocumentDetail)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get detailed document information including content"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentDetail.from_orm(document)

@app.delete("/document/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(document)
    db.commit()
    
    logger.info(f"Deleted document {document_id}: {document.filename}")
    
    # TODO: Also delete from vector service
    return {"message": f"Document {document_id} deleted successfully"}

@app.post("/ingest_folder")
async def ingest_folder(request: IngestFolderRequest, db: Session = Depends(get_db)):
    """Ingest all PDF files from a folder"""
    folder_path = request.folder_path
    
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail="Folder not found")
    
    results = []
    errors = []
    
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            
            try:
                # Read file
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                file_size = len(file_content)
                
                # Extract text
                text_content, pages_count = extract_text_from_pdf(file_content)
                
                if not text_content.strip():
                    errors.append(f"{filename}: No text content found")
                    continue
                
                # Save to database
                document = Document(
                    filename=filename,
                    title=filename,
                    content=text_content,
                    file_path=file_path,
                    file_size=file_size,
                    pages_count=pages_count
                )
                
                db.add(document)
                db.commit()
                db.refresh(document)
                
                # Create chunks and send to vector service
                text_chunks = chunk_text(text_content)
                await send_to_vector_service(document.id, text_chunks)
                
                results.append({
                    "id": document.id,
                    "filename": filename,
                    "pages": pages_count,
                    "size": file_size
                })
                
                logger.info(f"Successfully ingested {filename}")
                
            except Exception as e:
                error_msg = f"{filename}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Error ingesting {filename}: {e}")
    
    return {
        "processed": len(results),
        "errors": len(errors),
        "results": results,
        "error_details": errors
    }

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get document statistics"""
    total_docs = db.query(Document).count()
    total_pages = db.query(Document).filter(Document.pages_count.isnot(None)).all()
    total_page_count = sum(doc.pages_count or 0 for doc in total_pages)
    
    return {
        "total_documents": total_docs,
        "total_pages": total_page_count,
        "average_pages_per_doc": total_page_count / total_docs if total_docs > 0 else 0
    }
