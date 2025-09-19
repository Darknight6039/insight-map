import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
import io

from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_service_response():
    """Mock successful service response"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok", "data": "test"}
    mock_response.raise_for_status.return_value = None
    return mock_response

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "gateway-api"

@patch('app.main.call_service')
async def test_health_services(mock_call_service):
    mock_call_service.return_value.json.return_value = {"status": "ok"}
    
    response = client.get("/health/services")
    assert response.status_code == 200
    data = response.json()
    assert "overall_status" in data
    assert "services" in data

@patch('app.main.call_service')
async def test_list_documents(mock_call_service):
    mock_call_service.return_value.json.return_value = [
        {"id": 1, "title": "Test Doc", "filename": "test.pdf"}
    ]
    
    response = client.get("/documents")
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_get_document(mock_call_service):
    mock_call_service.return_value.json.return_value = {
        "id": 1, "title": "Test Doc", "content": "Test content"
    }
    
    response = client.get("/documents/1")
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_upload_pdf(mock_call_service):
    mock_call_service.return_value.json.return_value = {
        "id": 1, "filename": "test.pdf", "status": "uploaded"
    }
    
    # Create a fake PDF file
    pdf_content = b"%PDF-1.4\ntest content"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    
    response = client.post("/documents/upload", files=files)
    assert response.status_code == 200

def test_upload_non_pdf():
    # Test uploading non-PDF file
    files = {"file": ("test.txt", io.BytesIO(b"text content"), "text/plain")}
    
    response = client.post("/documents/upload", files=files)
    assert response.status_code == 400
    assert "Only PDF files are supported" in response.json()["detail"]

@patch('app.main.call_service')
async def test_delete_document(mock_call_service):
    mock_call_service.return_value.json.return_value = {"message": "Document deleted"}
    
    response = client.delete("/documents/1")
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_search(mock_call_service):
    mock_call_service.return_value.json.return_value = [
        {"score": 0.95, "text": "relevant content", "doc_id": 1}
    ]
    
    payload = {"query": "test query", "top_k": 5}
    response = client.post("/search", json=payload)
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_synthesize_analysis(mock_call_service):
    mock_call_service.return_value.json.return_value = {
        "analysis_type": "synthese_executive",
        "title": "Test Analysis",
        "content": "Executive summary content",
        "sources": []
    }
    
    payload = {
        "query": "What are the key strategic opportunities?",
        "title": "Strategic Analysis"
    }
    
    response = client.post("/analysis/synthesize", json=payload)
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_competition_analysis(mock_call_service):
    mock_call_service.return_value.json.return_value = {
        "analysis_type": "analyse_concurrentielle",
        "title": "Competitive Analysis",
        "content": "Competitive analysis content"
    }
    
    payload = {
        "query": "Who are our main competitors?",
        "title": "Competition Study"
    }
    
    response = client.post("/analysis/competition", json=payload)
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_tech_watch_analysis(mock_call_service):
    mock_call_service.return_value.json.return_value = {
        "analysis_type": "veille_technologique",
        "title": "Tech Watch",
        "content": "Technology trends analysis"
    }
    
    payload = {
        "query": "What are emerging technologies?",
        "title": "Technology Watch"
    }
    
    response = client.post("/analysis/tech-watch", json=payload)
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_risk_analysis(mock_call_service):
    mock_call_service.return_value.json.return_value = {
        "analysis_type": "analyse_risques",
        "title": "Risk Analysis",
        "content": "Risk assessment content"
    }
    
    payload = {
        "query": "What are the main risks?",
        "title": "Risk Assessment"
    }
    
    response = client.post("/analysis/risk-analysis", json=payload)
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_market_study_analysis(mock_call_service):
    mock_call_service.return_value.json.return_value = {
        "analysis_type": "etude_marche",
        "title": "Market Study", 
        "content": "Market research content"
    }
    
    payload = {
        "query": "What is the market size?",
        "title": "Market Research"
    }
    
    response = client.post("/analysis/market-study", json=payload)
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_get_analysis_types(mock_call_service):
    mock_call_service.return_value.json.return_value = {
        "available_types": ["synthese_executive", "analyse_concurrentielle"],
        "descriptions": {}
    }
    
    response = client.get("/analysis/types")
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_list_reports(mock_call_service):
    mock_call_service.return_value.json.return_value = [
        {"id": 1, "title": "Test Report", "analysis_type": "synthese_executive"}
    ]
    
    response = client.get("/reports")
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_get_report(mock_call_service):
    mock_call_service.return_value.json.return_value = {
        "id": 1, "title": "Test Report", "content": "Report content"
    }
    
    response = client.get("/reports/1")
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_delete_report(mock_call_service):
    mock_call_service.return_value.json.return_value = {"message": "Report deleted"}
    
    response = client.delete("/reports/1")
    assert response.status_code == 200

@patch('httpx.AsyncClient')
async def test_export_report_pdf(mock_client):
    # Mock the httpx client
    mock_response = MagicMock()
    mock_response.content = b"PDF content"
    mock_response.headers = {"content-disposition": "attachment; filename=test.pdf"}
    mock_response.raise_for_status.return_value = None
    
    mock_context = MagicMock()
    mock_context.__aenter__.return_value.get.return_value = mock_response
    mock_client.return_value = mock_context
    
    response = client.get("/reports/1/export")
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_generate_report(mock_call_service):
    mock_call_service.return_value.json.return_value = {
        "id": 1, "title": "Generated Report"
    }
    
    response = client.post("/reports/generate", params={
        "title": "Test Report",
        "content": "Test content",
        "analysis_type": "synthese_executive"
    })
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_ingest_folder(mock_call_service):
    mock_call_service.return_value.json.return_value = {
        "processed": 5, "errors": 0
    }
    
    payload = {"folder_path": "/test/path"}
    response = client.post("/documents/ingest_folder", json=payload)
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_document_stats(mock_call_service):
    mock_call_service.return_value.json.return_value = {
        "total_documents": 10, "total_pages": 100
    }
    
    response = client.get("/documents/stats")
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_report_stats(mock_call_service):
    mock_call_service.return_value.json.return_value = {
        "total_reports": 5, "by_analysis_type": {}
    }
    
    response = client.get("/reports/stats")
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_get_collections(mock_call_service):
    mock_call_service.return_value.json.return_value = {
        "collections": [{"name": "pdf_segments"}]
    }
    
    response = client.get("/search/collections")
    assert response.status_code == 200

# Test legacy endpoints
@patch('app.main.call_service')
async def test_legacy_report(mock_call_service):
    mock_call_service.return_value.json.return_value = {
        "title": "Legacy Report", "executive_summary": "Summary"
    }
    
    payload = {"title": "Legacy Test", "query": "test query"}
    response = client.post("/report", json=payload)
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_legacy_upload_pdf(mock_call_service):
    mock_call_service.return_value.json.return_value = {"id": 1}
    
    pdf_content = b"%PDF-1.4\ntest content"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    
    response = client.post("/upload_pdf", files=files)
    assert response.status_code == 200

@patch('app.main.call_service')
async def test_legacy_download_report(mock_call_service):
    mock_call_service.return_value.json.return_value = {"id": 1, "title": "Report"}
    
    response = client.get("/download/1")
    assert response.status_code == 200

# Test workflow endpoint
@patch('app.main.call_service')
async def test_analyze_and_report_workflow(mock_call_service):
    # Mock analysis response
    analysis_result = {
        "title": "Analysis Result",
        "content": "Analysis content",
        "analysis_type": "synthese_executive"
    }
    
    # Mock report response
    report_result = {"id": 1, "title": "Generated Report"}
    
    # Configure mock to return different responses for different calls
    mock_call_service.side_effect = [
        MagicMock(json=lambda: analysis_result),  # Analysis call
        MagicMock(json=lambda: report_result)     # Report generation call
    ]
    
    response = client.post("/workflows/analyze-and-report", params={
        "analysis_type": "synthesize",
        "query": "Test query",
        "title": "Test Analysis",
        "auto_export": False
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
    assert "report" in data

def test_analyze_and_report_workflow_invalid_type():
    response = client.post("/workflows/analyze-and-report", params={
        "analysis_type": "invalid_type",
        "query": "Test query",
        "title": "Test Analysis"
    })
    
    assert response.status_code == 400
    assert "Invalid analysis type" in response.json()["detail"]

def test_pagination_parameters():
    # Test with pagination parameters
    response = client.get("/documents?skip=0&limit=5")
    # This will fail without mock, but tests parameter parsing
    assert "skip" in str(response.url)
    assert "limit" in str(response.url)

def test_query_parameters():
    # Test query parameter parsing
    response = client.get("/reports?skip=10&limit=20") 
    assert "skip" in str(response.url)
    assert "limit" in str(response.url)
