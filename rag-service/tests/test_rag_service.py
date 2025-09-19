import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import datetime

from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "available_analyses" in data

def test_analysis_types():
    response = client.get("/analysis_types")
    assert response.status_code == 200
    data = response.json()
    assert "available_types" in data
    assert "descriptions" in data
    assert len(data["available_types"]) == 5
    expected_types = ["synthese_executive", "analyse_concurrentielle", "veille_technologique", "analyse_risques", "etude_marche"]
    for analysis_type in expected_types:
        assert analysis_type in data["available_types"]

@patch('app.main.get_passages')
@patch('app.main.call_openai')
async def test_synthesize_analysis(mock_openai, mock_passages):
    # Mock vector search results
    mock_passages.return_value = [
        {"text": "Test passage 1", "doc_id": 1, "score": 0.9},
        {"text": "Test passage 2", "doc_id": 2, "score": 0.8}
    ]
    
    # Mock OpenAI response
    mock_openai.return_value = "Test executive synthesis response"
    
    payload = {
        "query": "What are the main strategic opportunities?",
        "title": "Test Synthesis",
        "top_k": 5
    }
    
    response = client.post("/synthesize", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["analysis_type"] == "synthese_executive"
    assert data["title"] == "Test Synthesis"
    assert data["content"] == "Test executive synthesis response"
    assert len(data["sources"]) == 2

@patch('app.main.get_passages')
@patch('app.main.call_openai')
async def test_analyze_competition(mock_openai, mock_passages):
    mock_passages.return_value = [{"text": "Competitor analysis data", "doc_id": 1, "score": 0.9}]
    mock_openai.return_value = "Test competitive analysis response"
    
    payload = {
        "query": "Who are our main competitors?",
        "title": "Competitive Analysis"
    }
    
    response = client.post("/analyze_competition", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["analysis_type"] == "analyse_concurrentielle"
    assert data["content"] == "Test competitive analysis response"

@patch('app.main.get_passages')
@patch('app.main.call_openai')
async def test_tech_watch(mock_openai, mock_passages):
    mock_passages.return_value = [{"text": "Technology trends data", "doc_id": 1, "score": 0.9}]
    mock_openai.return_value = "Test technology watch response"
    
    payload = {
        "query": "What are emerging technologies in our sector?",
        "title": "Technology Watch"
    }
    
    response = client.post("/tech_watch", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["analysis_type"] == "veille_technologique"
    assert data["content"] == "Test technology watch response"

@patch('app.main.get_passages')
@patch('app.main.call_openai')
async def test_risk_analysis(mock_openai, mock_passages):
    mock_passages.return_value = [{"text": "Risk assessment data", "doc_id": 1, "score": 0.9}]
    mock_openai.return_value = "Test risk analysis response"
    
    payload = {
        "query": "What are the main risks we face?",
        "title": "Risk Assessment"
    }
    
    response = client.post("/risk_analysis", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["analysis_type"] == "analyse_risques"
    assert data["content"] == "Test risk analysis response"

@patch('app.main.get_passages')
@patch('app.main.call_openai')
async def test_market_study(mock_openai, mock_passages):
    mock_passages.return_value = [{"text": "Market research data", "doc_id": 1, "score": 0.9}]
    mock_openai.return_value = "Test market study response"
    
    payload = {
        "query": "What is the market size and growth potential?",
        "title": "Market Study"
    }
    
    response = client.post("/market_study", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["analysis_type"] == "etude_marche"
    assert data["content"] == "Test market study response"

@patch('app.main.call_openai')
async def test_context_override(mock_openai):
    """Test using context_override instead of vector search"""
    mock_openai.return_value = "Response based on override context"
    
    payload = {
        "query": "What should we do?",
        "title": "Test Override",
        "context_override": "This is custom context provided directly"
    }
    
    response = client.post("/synthesize", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["metadata"]["used_context_override"] == True
    assert len(data["sources"]) == 0  # No vector search performed

def test_build_analysis_prompt():
    from app.main import build_analysis_prompt
    
    passages = [
        {"text": "Test passage", "doc_id": 1, "score": 0.9}
    ]
    
    prompt = build_analysis_prompt("synthese_executive", "test query", passages)
    assert "test query" in prompt
    assert "Test passage" in prompt
    assert "RÉSUMÉ EXÉCUTIF" in prompt

def test_format_functions():
    from prompts.templates import format_context, format_sources
    
    passages = [
        {"text": "Test passage 1", "doc_id": 1, "score": 0.9},
        {"text": "Test passage 2", "doc_id": 2, "score": 0.8}
    ]
    
    context = format_context(passages)
    assert "Test passage 1" in context
    assert "Doc 1" in context
    assert "Score: 0.90" in context
    
    sources = format_sources(passages)
    assert "Document 1" in sources
    assert "Document 2" in sources

def test_call_openai_without_key():
    from app.main import call_openai
    
    with patch('app.main.OPENAI_API_KEY', None):
        result = call_openai("test prompt", "synthese_executive")
        assert "OpenAI API key not configured" in result
        assert "synthese_executive" in result

@patch('app.main.get_passages')
@patch('app.main.call_openai')
async def test_legacy_endpoints(mock_openai, mock_passages):
    """Test backward compatibility endpoints"""
    mock_passages.return_value = [{"text": "Test data", "doc_id": 1, "score": 0.9}]
    mock_openai.return_value = "Legacy response"
    
    # Test ask_question
    payload = {"query": "test question", "top_k": 3}
    response = client.post("/ask_question", json=payload)
    assert response.status_code == 200
    assert "answer" in response.json()
    
    # Test generate_report
    payload = {"title": "Test Report", "query": "test query"}
    response = client.post("/generate_report", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Report"
    assert "executive_summary" in data

def test_prompt_templates():
    from prompts.templates import get_prompt_template, ANALYSIS_PROMPTS
    
    # Test all analysis types have templates
    for analysis_type in ["synthese_executive", "analyse_concurrentielle", "veille_technologique", "analyse_risques", "etude_marche"]:
        template = get_prompt_template(analysis_type)
        assert template is not None
        assert len(template) > 100  # Should be substantial templates
        assert "{context}" in template
        assert "{sources}" in template
    
    # Test unknown type returns default
    default_template = get_prompt_template("unknown_type")
    assert default_template == ANALYSIS_PROMPTS["synthese_executive"]
