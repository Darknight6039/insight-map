import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@patch('app.main.qdrant_client')
def test_collections(mock_qdrant):
    mock_qdrant.get_collections.return_value.dict.return_value = {"collections": []}
    
    response = client.get("/collections")
    assert response.status_code == 200

@patch('app.main.openai_client', None)  # Test without OpenAI
@patch('app.main.qdrant_client')
def test_index_without_openai(mock_qdrant):
    mock_qdrant.get_collections.return_value.collections = []
    mock_qdrant.upsert.return_value = None
    
    payload = {
        "doc_id": 1,
        "segments": ["This is a test segment", "Another test segment"]
    }
    
    response = client.post("/index", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["upserted"] == 2
    assert data["embedding_dim"] == 1536  # Mock embedding dimension

@patch('app.main.openai_client')
@patch('app.main.qdrant_client')
def test_index_with_openai(mock_qdrant, mock_openai):
    # Mock OpenAI response
    mock_embedding_response = MagicMock()
    mock_embedding_response.data = [
        MagicMock(embedding=[0.1] * 1536),
        MagicMock(embedding=[0.2] * 1536)
    ]
    mock_openai.embeddings.create.return_value = mock_embedding_response
    
    # Mock Qdrant
    mock_qdrant.get_collections.return_value.collections = []
    mock_qdrant.upsert.return_value = None
    
    payload = {
        "doc_id": 1,
        "segments": ["This is a test segment", "Another test segment"]
    }
    
    response = client.post("/index", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["upserted"] == 2
    assert data["embedding_dim"] == 1536

@patch('app.main.openai_client', None)  # Test without OpenAI
@patch('app.main.qdrant_client')
def test_search_without_openai(mock_qdrant):
    # Mock search results
    mock_result = MagicMock()
    mock_result.score = 0.95
    mock_result.payload = {"text": "Test result", "doc_id": 1, "segment_index": 0}
    mock_qdrant.search.return_value = [mock_result]
    
    payload = {
        "query": "test query",
        "top_k": 5
    }
    
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["text"] == "Test result"
    assert data[0]["score"] == 0.95

@patch('app.main.openai_client')
@patch('app.main.qdrant_client')
def test_search_with_openai(mock_qdrant, mock_openai):
    # Mock OpenAI response
    mock_embedding_response = MagicMock()
    mock_embedding_response.data = [MagicMock(embedding=[0.1] * 1536)]
    mock_openai.embeddings.create.return_value = mock_embedding_response
    
    # Mock search results
    mock_result = MagicMock()
    mock_result.score = 0.95
    mock_result.payload = {"text": "Test result", "doc_id": 1, "segment_index": 0}
    mock_qdrant.search.return_value = [mock_result]
    
    payload = {
        "query": "test query",
        "top_k": 5
    }
    
    response = client.post("/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["text"] == "Test result"

def test_get_embeddings_function():
    from app.main import get_embeddings
    
    # Test with no OpenAI client (should return mock embeddings)
    with patch('app.main.openai_client', None):
        embeddings = get_embeddings(["test"])
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 1536
        assert all(x == 0.1 for x in embeddings[0])

@patch('app.main.openai_client')
def test_get_embeddings_with_openai(mock_openai):
    from app.main import get_embeddings
    
    # Mock OpenAI response
    mock_embedding_response = MagicMock()
    mock_embedding_response.data = [MagicMock(embedding=[0.5] * 1536)]
    mock_openai.embeddings.create.return_value = mock_embedding_response
    
    embeddings = get_embeddings(["test"])
    assert len(embeddings) == 1
    assert len(embeddings[0]) == 1536
    assert all(x == 0.5 for x in embeddings[0])

@patch('app.main.qdrant_client')
def test_ensure_collection(mock_qdrant):
    from app.main import ensure_collection
    
    # Test collection doesn't exist
    mock_qdrant.get_collections.return_value.collections = []
    ensure_collection(1536)
    mock_qdrant.create_collection.assert_called_once()
    
    # Test collection exists
    mock_qdrant.reset_mock()
    mock_collection = MagicMock()
    mock_collection.name = "pdf_segments"
    mock_qdrant.get_collections.return_value.collections = [mock_collection]
    ensure_collection(1536)
    mock_qdrant.create_collection.assert_not_called()

def test_legacy_endpoint():
    """Test backward compatibility endpoint"""
    with patch('app.main.openai_client', None), \
         patch('app.main.qdrant_client') as mock_qdrant:
        
        mock_qdrant.get_collections.return_value.collections = []
        mock_qdrant.upsert.return_value = None
        
        payload = {
            "doc_id": 1,
            "segments": ["Legacy test"]
        }
        
        response = client.post("/upsert_embedding", json=payload)
        assert response.status_code == 200
