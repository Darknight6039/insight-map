import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

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

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "report-service"

def test_generate_report():
    payload = {
        "title": "Test Report",
        "content": "**SECTION 1**\nThis is test content.\n\n**SECTION 2**\nMore test content.",
        "analysis_type": "synthese_executive",
        "metadata": {"test_key": "test_value"}
    }
    
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "Test Report"
    assert data["analysis_type"] == "synthese_executive"
    assert "id" in data

def test_list_reports():
    # First create a report
    payload = {
        "title": "List Test Report",
        "content": "Test content for listing",
        "analysis_type": "veille_technologique"
    }
    create_response = client.post("/generate", json=payload)
    assert create_response.status_code == 200
    
    # Then list reports
    response = client.get("/reports")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(report["title"] == "List Test Report" for report in data)

def test_get_report():
    # Create a report first
    payload = {
        "title": "Get Test Report",
        "content": "Detailed test content",
        "analysis_type": "analyse_risques",
        "metadata": {"created_for": "testing"}
    }
    create_response = client.post("/generate", json=payload)
    report_id = create_response.json()["id"]
    
    # Get the report
    response = client.get(f"/reports/{report_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == report_id
    assert data["title"] == "Get Test Report"
    assert data["content"] == "Detailed test content"
    assert data["analysis_type"] == "analyse_risques"
    assert data["metadata"]["created_for"] == "testing"

def test_get_nonexistent_report():
    response = client.get("/reports/999999")
    assert response.status_code == 404
    assert "Report not found" in response.json()["detail"]

def test_delete_report():
    # Create a report first
    payload = {
        "title": "Delete Test Report",
        "content": "Content to be deleted",
        "analysis_type": "etude_marche"
    }
    create_response = client.post("/generate", json=payload)
    report_id = create_response.json()["id"]
    
    # Delete the report
    response = client.delete(f"/reports/{report_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    
    # Verify it's gone
    get_response = client.get(f"/reports/{report_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_report():
    response = client.delete("/reports/999999")
    assert response.status_code == 404
    assert "Report not found" in response.json()["detail"]

def test_export_report_pdf():
    # Create a report first
    payload = {
        "title": "Export Test Report",
        "content": "**EXECUTIVE SUMMARY**\nThis is a test report for PDF export.\n\n**RECOMMENDATIONS**\n- Action 1\n- Action 2",
        "analysis_type": "synthese_executive",
        "metadata": {"export_test": True}
    }
    create_response = client.post("/generate", json=payload)
    report_id = create_response.json()["id"]
    
    # Export as PDF
    response = client.get(f"/export/{report_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]

def test_export_nonexistent_report():
    response = client.get("/export/999999")
    assert response.status_code == 404
    assert "Report not found" in response.json()["detail"]

def test_legacy_export_pdf():
    payload = {
        "title": "Legacy Export Test",
        "executive_summary": "This is a legacy export test.",
        "citations": [
            {"doc_id": 1, "score": 0.95, "text": "Source 1"},
            {"doc_id": 2, "score": 0.87, "text": "Source 2"}
        ],
        "brand": {"company": "Test Company"}
    }
    
    response = client.post("/export_pdf", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

def test_get_stats():
    # Create reports with different analysis types
    for i, analysis_type in enumerate(["synthese_executive", "analyse_concurrentielle", "veille_technologique"]):
        payload = {
            "title": f"Stats Test Report {i+1}",
            "content": f"Content for stats test {i+1}",
            "analysis_type": analysis_type
        }
        client.post("/generate", json=payload)
    
    response = client.get("/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_reports" in data
    assert "by_analysis_type" in data
    assert "available_analysis_types" in data
    assert data["total_reports"] >= 3

def test_report_formatter():
    from app.main import ReportFormatter
    
    formatter = ReportFormatter()
    
    # Test PDF generation
    pdf_bytes = formatter.create_professional_pdf(
        title="Test PDF",
        content="**SECTION 1**\nTest content\n\n**SECTION 2**\nMore content",
        analysis_type="synthese_executive",
        sources=[{"doc_id": 1, "score": 0.9}],
        metadata={"test": "data"}
    )
    
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000  # Should be a substantial PDF
    assert pdf_bytes.startswith(b'%PDF')  # PDF header

def test_content_sections_parsing():
    from app.main import ReportFormatter
    
    formatter = ReportFormatter()
    
    # Test the internal method for parsing content sections
    test_content = """
    **EXECUTIVE SUMMARY**
    This is the executive summary.
    
    **RECOMMENDATIONS** 
    - First recommendation
    - Second recommendation
    
    **CONCLUSION**
    Final thoughts.
    """
    
    # This would be tested by creating a full PDF and checking it contains the sections
    pdf_bytes = formatter.create_professional_pdf(
        title="Section Test",
        content=test_content
    )
    
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500

def test_pagination():
    # Test with pagination parameters
    response = client.get("/reports?skip=0&limit=5")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5

def test_report_with_no_metadata():
    payload = {
        "title": "No Metadata Report",
        "content": "Simple content without metadata"
    }
    
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    
    report_id = response.json()["id"]
    
    # Get the report
    get_response = client.get(f"/reports/{report_id}")
    assert get_response.status_code == 200
    
    data = get_response.json()
    assert data["metadata"] is None

def test_error_handling():
    # Test with invalid JSON in generate
    response = client.post("/generate", json={})
    assert response.status_code == 422  # Validation error

def test_sources_table_generation():
    from app.main import ReportFormatter
    
    formatter = ReportFormatter()
    
    sources = [
        {"doc_id": 1, "score": 0.95},
        {"doc_id": 2, "score": 0.87},
        {"doc_id": 3, "score": 0.76}
    ]
    
    pdf_bytes = formatter.create_professional_pdf(
        title="Sources Test",
        content="Test content with sources",
        sources=sources
    )
    
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
