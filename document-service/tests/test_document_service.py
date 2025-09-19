import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, AsyncMock

from app.main import app, get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def sample_pdf_content():
    """Create a simple PDF content for testing"""
    # This is a mock PDF content - in real tests you'd use a proper PDF library
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \n0000000179 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n238\n%%EOF"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_documents_empty():
    response = client.get("/documents")
    assert response.status_code == 200
    assert response.json() == []

@patch('app.main.send_to_vector_service')
@patch('app.main.extract_text_from_pdf')
def test_ingest_document(mock_extract_text, mock_vector_service, sample_pdf_content):
    # Mock the PDF text extraction
    mock_extract_text.return_value = ("This is a test document content.", 1)
    mock_vector_service.return_value = AsyncMock(return_value={"upserted": 1})
    
    files = {"file": ("test.pdf", io.BytesIO(sample_pdf_content), "application/pdf")}
    
    response = client.post("/ingest", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["pages_count"] == 1

@patch('app.main.send_to_vector_service')
@patch('app.main.extract_text_from_pdf')
def test_ingest_document_with_title(mock_extract_text, mock_vector_service, sample_pdf_content):
    mock_extract_text.return_value = ("Test content", 1)
    mock_vector_service.return_value = AsyncMock(return_value={"upserted": 1})
    
    files = {"file": ("test.pdf", io.BytesIO(sample_pdf_content), "application/pdf")}
    data = {"title": "Custom Title"}
    
    response = client.post("/ingest", files=files, data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["title"] == "Custom Title"

def test_ingest_non_pdf():
    files = {"file": ("test.txt", io.BytesIO(b"text content"), "text/plain")}
    
    response = client.post("/ingest", files=files)
    
    assert response.status_code == 400
    assert "Only PDF files are supported" in response.json()["detail"]

@patch('app.main.send_to_vector_service')
@patch('app.main.extract_text_from_pdf')
def test_get_document_after_ingest(mock_extract_text, mock_vector_service, sample_pdf_content):
    mock_extract_text.return_value = ("Document content for retrieval", 1)
    mock_vector_service.return_value = AsyncMock(return_value={"upserted": 1})
    
    # First ingest a document
    files = {"file": ("retrieve_test.pdf", io.BytesIO(sample_pdf_content), "application/pdf")}
    ingest_response = client.post("/ingest", files=files)
    doc_id = ingest_response.json()["id"]
    
    # Then retrieve it
    response = client.get(f"/document/{doc_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == doc_id
    assert data["filename"] == "retrieve_test.pdf"
    assert data["content"] == "Document content for retrieval"

def test_get_nonexistent_document():
    response = client.get("/document/999")
    assert response.status_code == 404
    assert "Document not found" in response.json()["detail"]

@patch('app.main.send_to_vector_service')
@patch('app.main.extract_text_from_pdf')
def test_delete_document(mock_extract_text, mock_vector_service, sample_pdf_content):
    mock_extract_text.return_value = ("Document to be deleted", 1)
    mock_vector_service.return_value = AsyncMock(return_value={"upserted": 1})
    
    # First ingest a document
    files = {"file": ("delete_test.pdf", io.BytesIO(sample_pdf_content), "application/pdf")}
    ingest_response = client.post("/ingest", files=files)
    doc_id = ingest_response.json()["id"]
    
    # Then delete it
    response = client.delete(f"/document/{doc_id}")
    
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    
    # Verify it's gone
    get_response = client.get(f"/document/{doc_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_document():
    response = client.delete("/document/999")
    assert response.status_code == 404
    assert "Document not found" in response.json()["detail"]

def test_get_stats_empty():
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] == 0
    assert data["total_pages"] == 0
    assert data["average_pages_per_doc"] == 0

@patch('app.main.send_to_vector_service')
@patch('app.main.extract_text_from_pdf')
def test_get_stats_with_documents(mock_extract_text, mock_vector_service, sample_pdf_content):
    mock_extract_text.return_value = ("Stats test content", 2)
    mock_vector_service.return_value = AsyncMock(return_value={"upserted": 1})
    
    # Ingest a document
    files = {"file": ("stats_test.pdf", io.BytesIO(sample_pdf_content), "application/pdf")}
    client.post("/ingest", files=files)
    
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] >= 1
    assert data["total_pages"] >= 2

def test_chunk_text():
    from app.main import chunk_text
    
    text = "This is a test. " * 100  # Create a long text
    chunks = chunk_text(text, chunk_size=50, overlap=10)
    
    assert len(chunks) > 1
    assert all(len(chunk) <= 60 for chunk in chunks)  # Allow for sentence boundaries
    
def test_chunk_text_short():
    from app.main import chunk_text
    
    text = "Short text."
    chunks = chunk_text(text, chunk_size=50)
    
    assert len(chunks) == 1
    assert chunks[0] == text

@patch('os.path.exists')
@patch('os.listdir')
@patch('builtins.open')
@patch('app.main.send_to_vector_service')
@patch('app.main.extract_text_from_pdf')
def test_ingest_folder(mock_extract_text, mock_vector_service, mock_open, mock_listdir, mock_exists, sample_pdf_content):
    mock_exists.return_value = True
    mock_listdir.return_value = ['test1.pdf', 'test2.pdf', 'ignored.txt']
    mock_open.return_value.__enter__.return_value.read.return_value = sample_pdf_content
    mock_extract_text.return_value = ("Folder test content", 1)
    mock_vector_service.return_value = AsyncMock(return_value={"upserted": 1})
    
    response = client.post("/ingest_folder", json={"folder_path": "/test/path"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["processed"] == 2  # Only PDF files
    assert data["errors"] == 0

def test_ingest_folder_not_found():
    response = client.post("/ingest_folder", json={"folder_path": "/nonexistent/path"})
    
    assert response.status_code == 404
    assert "Folder not found" in response.json()["detail"]
