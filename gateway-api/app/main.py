from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import httpx
from loguru import logger
import io

# Pydantic models for all analysis types
class SearchPayload(BaseModel):
    query: str
    top_k: Optional[int] = 5

class ReportPayload(BaseModel):
    title: str
    query: str
    brand: Optional[Dict] = None

# Analysis payloads for the 5 main analysis types
class AnalysisPayload(BaseModel):
    query: str
    title: Optional[str] = None
    top_k: Optional[int] = 8
    context_override: Optional[str] = None

class SyntheseExecutivePayload(AnalysisPayload):
    pass

class AnalyseConcurrentiellePayload(AnalysisPayload):
    pass

class VeilleTechnologiquePayload(AnalysisPayload):
    pass

class AnalyseRisquesPayload(AnalysisPayload):
    pass

class EtudeMarchePayload(AnalysisPayload):
    pass

class IngestFolderPayload(BaseModel):
    folder_path: str


def get_service_urls():
    return {
        "document": os.environ.get("DOCUMENT_URL", "http://document-service:8001"),
        "vector": os.environ.get("VECTOR_URL", "http://vector-service:8002"),
        "rag": os.environ.get("RAG_URL", "http://rag-service:8003"),
        "report": os.environ.get("REPORT_URL", "http://report-service:8004"),
        "status": os.environ.get("STATUS_URL", "http://status-service:8005"),
    }

app = FastAPI(
    title="Insight MVP - Strategic Intelligence Gateway", 
    version="0.1.0",
    description="""
    Gateway API for Strategic Intelligence MVP - Orchestrates microservices for document analysis and reporting.
    
    ## Features
    
    * **Document Management**: Upload, ingest, and manage PDF documents
    * **Vector Search**: Semantic search across document content  
    * **Strategic Analysis**: 5 specialized analysis types with AI-powered insights
    * **Professional Reports**: Generate and export formatted PDF reports
    * **System Monitoring**: Health checks and system status
    
    ## Analysis Types
    
    1. **Synthèse Exécutive** (`/analysis/synthesize`) - Executive summary with strategic recommendations
    2. **Analyse Concurrentielle** (`/analysis/competition`) - Competitive intelligence and market positioning  
    3. **Veille Technologique** (`/analysis/tech-watch`) - Technology trends and innovation monitoring
    4. **Analyse de Risques** (`/analysis/risk-analysis`) - Risk assessment and mitigation strategies
    5. **Étude de Marché** (`/analysis/market-study`) - Comprehensive market research and projections
    """,
    contact={
        "name": "Insight MVP",
        "url": "https://github.com/your-repo/insight-mvp",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def call_service(method: str, url: str, **kwargs):
    """Helper function to call microservices with error handling"""
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error calling {url}: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error calling {url}: {e}")
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")


# =============================================================================
# HEALTH AND STATUS ENDPOINTS
# =============================================================================

@app.get("/health", tags=["System"])
async def health():
    """System health check"""
    return {"status": "ok", "service": "gateway-api"}

@app.get("/health/services", tags=["System"])
async def health_services(urls: dict = Depends(get_service_urls)):
    """Check health of all microservices"""
    health_status = {}
    
    for service_name, service_url in urls.items():
        try:
            response = await call_service("GET", f"{service_url}/health")
            health_status[service_name] = {
                "status": "healthy",
                "url": service_url,
                "response": response.json()
            }
        except Exception as e:
            health_status[service_name] = {
                "status": "unhealthy", 
                "url": service_url,
                "error": str(e)
            }
    
    all_healthy = all(status["status"] == "healthy" for status in health_status.values())
    
    return {
        "overall_status": "healthy" if all_healthy else "degraded",
        "services": health_status
    }

@app.get("/status", tags=["System"])
async def system_status(urls: dict = Depends(get_service_urls)):
    """Get detailed system status from status service"""
    response = await call_service("GET", f"{urls['status']}/status")
    return response.json()

# =============================================================================
# DOCUMENT MANAGEMENT ENDPOINTS  
# =============================================================================

@app.get("/documents", tags=["Documents"])
async def list_documents(
    skip: int = Query(0, description="Number of documents to skip"),
    limit: int = Query(100, description="Maximum number of documents to return"),
    urls: dict = Depends(get_service_urls)
):
    """List all documents with pagination"""
    response = await call_service("GET", f"{urls['document']}/documents?skip={skip}&limit={limit}")
    return response.json()

@app.get("/documents/{document_id}", tags=["Documents"])
async def get_document(document_id: int, urls: dict = Depends(get_service_urls)):
    """Get detailed document information"""
    response = await call_service("GET", f"{urls['document']}/document/{document_id}")
    return response.json()

@app.post("/documents/upload", tags=["Documents"])
async def upload_pdf(
    file: UploadFile = File(..., description="PDF file to upload"),
    title: Optional[str] = None,
    urls: dict = Depends(get_service_urls)
):
    """Upload a single PDF document"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    files = {"file": (file.filename, await file.read(), file.content_type or "application/pdf")}
    data = {"title": title} if title else {}
    
    response = await call_service("POST", f"{urls['document']}/ingest", files=files, data=data)
    return response.json()

@app.delete("/documents/{document_id}", tags=["Documents"])
async def delete_document(document_id: int, urls: dict = Depends(get_service_urls)):
    """Delete a document"""
    response = await call_service("DELETE", f"{urls['document']}/document/{document_id}")
    return response.json()

@app.post("/documents/ingest_folder", tags=["Documents"])
async def ingest_folder(payload: IngestFolderPayload, urls: dict = Depends(get_service_urls)):
    """Ingest all PDF files from a folder"""
    response = await call_service("POST", f"{urls['document']}/ingest_folder", json=payload.dict())
    return response.json()

@app.get("/documents/stats", tags=["Documents"])
async def document_stats(urls: dict = Depends(get_service_urls)):
    """Get document statistics"""
    response = await call_service("GET", f"{urls['document']}/stats")
    return response.json()

# =============================================================================
# VECTOR SEARCH ENDPOINTS
# =============================================================================

@app.post("/search", tags=["Search"])
async def search(payload: SearchPayload, urls: dict = Depends(get_service_urls)):
    """Semantic search across document content"""
    response = await call_service("POST", f"{urls['vector']}/search", json=payload.dict())
    return response.json()

@app.get("/search/collections", tags=["Search"])
async def get_collections(urls: dict = Depends(get_service_urls)):
    """Get information about vector collections"""
    response = await call_service("GET", f"{urls['vector']}/collections")
    return response.json()

# =============================================================================
# STRATEGIC ANALYSIS ENDPOINTS - THE 5 MAIN ANALYSIS TYPES
# =============================================================================

@app.post("/analysis/synthesize", tags=["Strategic Analysis"])
async def synthesize_executive(payload: SyntheseExecutivePayload, urls: dict = Depends(get_service_urls)):
    """
    **PROMPT 1: Synthèse Exécutive**
    
    Génère une synthèse exécutive structurée avec:
    - Points clés stratégiques
    - Opportunités prioritaires  
    - Risques majeurs à surveiller
    - Recommandations actionnables
    """
    response = await call_service("POST", f"{urls['rag']}/synthesize", json=payload.dict())
    return response.json()

@app.post("/analysis/competition", tags=["Strategic Analysis"])
async def analyze_competition(payload: AnalyseConcurrentiellePayload, urls: dict = Depends(get_service_urls)):
    """
    **PROMPT 2: Analyse Concurrentielle**
    
    Analyse de la concurrence et du positionnement marché:
    - Mapping concurrentiel
    - Tendances sectorielles
    - Opportunités de différenciation
    """
    response = await call_service("POST", f"{urls['rag']}/analyze_competition", json=payload.dict())
    return response.json()

@app.post("/analysis/tech-watch", tags=["Strategic Analysis"])  
async def tech_watch(payload: VeilleTechnologiquePayload, urls: dict = Depends(get_service_urls)):
    """
    **PROMPT 3: Veille Technologique**
    
    Veille des innovations et tendances technologiques:
    - Innovations émergentes
    - Tendances tech et convergences
    - Implications business et roadmap
    """
    response = await call_service("POST", f"{urls['rag']}/tech_watch", json=payload.dict())
    return response.json()

@app.post("/analysis/risk-analysis", tags=["Strategic Analysis"])
async def risk_analysis(payload: AnalyseRisquesPayload, urls: dict = Depends(get_service_urls)):
    """
    **PROMPT 4: Analyse de Risques**
    
    Analyse méthodique des risques:
    - Cartographie des risques (opérationnels, stratégiques, réglementaires, technologiques)
    - Évaluation probabilité/impact
    - Mesures de mitigation et priorisation
    """
    response = await call_service("POST", f"{urls['rag']}/risk_analysis", json=payload.dict())
    return response.json()

@app.post("/analysis/market-study", tags=["Strategic Analysis"])
async def market_study(payload: EtudeMarchePayload, urls: dict = Depends(get_service_urls)):
    """
    **PROMPT 5: Étude de Marché**
    
    Étude de marché complète:
    - Taille et dynamique du marché
    - Analyse de la demande
    - Chaîne de valeur et barrières à l'entrée
    - Projections et scénarios
    """
    response = await call_service("POST", f"{urls['rag']}/market_study", json=payload.dict())
    return response.json()

@app.get("/analysis/types", tags=["Strategic Analysis"])
async def get_analysis_types(urls: dict = Depends(get_service_urls)):
    """Get available analysis types and descriptions"""
    response = await call_service("GET", f"{urls['rag']}/analysis_types")
    return response.json()

# =============================================================================
# REPORT MANAGEMENT ENDPOINTS
# =============================================================================

@app.get("/reports", tags=["Reports"])
async def list_reports(
    skip: int = Query(0, description="Number of reports to skip"),
    limit: int = Query(100, description="Maximum number of reports to return"),
    urls: dict = Depends(get_service_urls)
):
    """List all reports with pagination"""
    response = await call_service("GET", f"{urls['report']}/reports?skip={skip}&limit={limit}")
    return response.json()

@app.get("/reports/{report_id}", tags=["Reports"])
async def get_report(report_id: int, urls: dict = Depends(get_service_urls)):
    """Get detailed report information"""
    response = await call_service("GET", f"{urls['report']}/reports/{report_id}")
    return response.json()

@app.delete("/reports/{report_id}", tags=["Reports"])
async def delete_report(report_id: int, urls: dict = Depends(get_service_urls)):
    """Delete a report"""
    response = await call_service("DELETE", f"{urls['report']}/reports/{report_id}")
    return response.json()

@app.get("/reports/{report_id}/export", tags=["Reports"])
async def export_report_pdf(report_id: int, urls: dict = Depends(get_service_urls)):
    """Export report as professional PDF"""
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.get(f"{urls['report']}/export/{report_id}")
        response.raise_for_status()
        
        return StreamingResponse(
            io.BytesIO(response.content),
            media_type="application/pdf",
            headers=response.headers
        )

@app.post("/reports/generate", tags=["Reports"])
async def generate_report(
    title: str,
    content: str,
    analysis_type: Optional[str] = None,
    urls: dict = Depends(get_service_urls)
):
    """Generate and store a new report"""
    payload = {
        "title": title,
        "content": content,
        "analysis_type": analysis_type
    }
    response = await call_service("POST", f"{urls['report']}/generate", json=payload)
    return response.json()

@app.get("/reports/stats", tags=["Reports"])
async def report_stats(urls: dict = Depends(get_service_urls)):
    """Get report statistics"""
    response = await call_service("GET", f"{urls['report']}/stats")
    return response.json()

# =============================================================================
# LEGACY ENDPOINTS FOR BACKWARD COMPATIBILITY
# =============================================================================

@app.post("/report", tags=["Legacy"])
async def legacy_report(payload: ReportPayload, urls: dict = Depends(get_service_urls)):
    """Legacy endpoint - generate basic report"""
    response = await call_service("POST", f"{urls['rag']}/generate_report", json=payload.dict())
    return response.json()

@app.post("/upload_pdf", tags=["Legacy"]) 
async def legacy_upload_pdf(file: UploadFile = File(...), urls: dict = Depends(get_service_urls)):
    """Legacy endpoint - upload PDF"""
    return await upload_pdf(file, None, urls)

@app.get("/download/{report_id}", tags=["Legacy"])
async def legacy_download_report(report_id: int, urls: dict = Depends(get_service_urls)):
    """Legacy endpoint - get report details"""
    return await get_report(report_id, urls)

# =============================================================================
# WORKFLOW ENDPOINTS - COMMON PATTERNS
# =============================================================================

@app.post("/workflows/analyze-and-report", tags=["Workflows"])
async def analyze_and_report(
    analysis_type: str,
    query: str,
    title: str,
    auto_export: bool = False,
    urls: dict = Depends(get_service_urls)
):
    """
    Complete workflow: Run analysis and automatically generate report
    
    Analysis types: synthesize, competition, tech-watch, risk-analysis, market-study
    """
    # Map analysis type to endpoint
    analysis_endpoints = {
        "synthesize": "/analysis/synthesize",
        "competition": "/analysis/competition", 
        "tech-watch": "/analysis/tech-watch",
        "risk-analysis": "/analysis/risk-analysis",
        "market-study": "/analysis/market-study"
    }
    
    if analysis_type not in analysis_endpoints:
        raise HTTPException(status_code=400, detail=f"Invalid analysis type: {analysis_type}")
    
    # Run analysis
    analysis_payload = {"query": query, "title": title}
    analysis_response = await call_service(
        "POST", 
        f"{urls['rag']}{analysis_endpoints[analysis_type].replace('/analysis', '')}",
        json=analysis_payload
    )
    analysis_result = analysis_response.json()
    
    # Generate report
    report_payload = {
        "title": analysis_result.get("title", title),
        "content": analysis_result.get("content", ""),
        "analysis_type": analysis_type
    }
    report_response = await call_service("POST", f"{urls['report']}/generate", json=report_payload)
    report_result = report_response.json()
    
    result = {
        "analysis": analysis_result,
        "report": report_result
    }
    
    # Auto-export if requested
    if auto_export:
        export_url = f"/reports/{report_result['id']}/export"
        result["export_url"] = export_url
    
    return result


