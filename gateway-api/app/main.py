from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import httpx
from loguru import logger
import io
from datetime import datetime

# Auth imports - Using Supabase Auth
from app.supabase_auth import (
    SupabaseUser, UserLogin, UserRegister, TokenResponse, UserResponse,
    PasswordResetRequest, PasswordResetConfirm, PasswordChange, ProfileUpdate,
    get_current_user_supabase, get_current_admin_supabase,
    login_user, register_user, logout_user, refresh_session,
    request_password_reset, reset_password, change_password, update_profile,
    list_users, toggle_user_active,
)
from app.supabase_client import get_supabase_admin_client

# Legacy imports for database models and utility functions
from app.auth import (
    User, Invitation, PasswordResetToken, ActivityLog,
    InvitationCreate, InvitationResponse,
    PasswordResetTokenResponse,
    ActivityLogResponse, DashboardStats, DashboardCharts, ActivityChartData, ReportTypeStats,
    get_db, init_db, log_activity, create_invitation,
    create_password_reset_token, validate_reset_token,
    get_password_hash, validate_invitation, create_user, UserCreate,
    create_access_token,  # Required for memory service proxy endpoints
)
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import timedelta

# Alias for compatibility - use Supabase user throughout
get_current_user = get_current_user_supabase
get_current_admin = get_current_admin_supabase

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
        "backend": os.environ.get("BACKEND_URL", "http://backend-service:8006"),
        "scheduler": os.environ.get("SCHEDULER_URL", "http://scheduler-service:8007"),
        "memory": os.environ.get("MEMORY_SERVICE_URL", "http://memory-service:8008"),
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
        "url": "https://github.com/Darknight6039/insight-map",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize auth database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables and default admin"""
    init_db()
    logger.info("Auth database initialized")

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


def is_admin(user: User) -> bool:
    """Check if user has admin role"""
    return user.role == "admin"


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
async def search(
    payload: SearchPayload, 
    urls: dict = Depends(get_service_urls),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Semantic search across document content"""
    # Log activity
    log_activity(
        db, 
        action="search", 
        user_id=current_user.id,
        details=payload.query[:200] if payload.query else None
    )
    
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
    urls: dict = Depends(get_service_urls),
    current_user: User = Depends(get_current_user)
):
    """List all reports with pagination"""
    user_filter = "" if is_admin(current_user) else f"&user_id={current_user.id}"
    response = await call_service("GET", f"{urls['report']}/reports?skip={skip}&limit={limit}{user_filter}")
    return response.json()

@app.get("/reports/{report_id}", tags=["Reports"])
async def get_report(
    report_id: int,
    urls: dict = Depends(get_service_urls),
    current_user: User = Depends(get_current_user)
):
    """Get detailed report information"""
    user_param = "" if is_admin(current_user) else f"?user_id={current_user.id}"
    response = await call_service("GET", f"{urls['report']}/reports/{report_id}{user_param}")
    return response.json()

@app.delete("/reports/{report_id}", tags=["Reports"])
async def delete_report(
    report_id: int,
    urls: dict = Depends(get_service_urls),
    current_user: User = Depends(get_current_user)
):
    """Delete a report"""
    user_param = "" if is_admin(current_user) else f"?user_id={current_user.id}"
    response = await call_service("DELETE", f"{urls['report']}/reports/{report_id}{user_param}")
    return response.json()

@app.get("/reports/{report_id}/export", tags=["Reports"])
async def export_report_pdf(
    report_id: int,
    urls: dict = Depends(get_service_urls),
    current_user: User = Depends(get_current_user)
):
    """Export report as professional PDF"""
    user_param = "" if is_admin(current_user) else f"?user_id={current_user.id}"
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.get(f"{urls['report']}/export/{report_id}{user_param}")
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
    urls: dict = Depends(get_service_urls),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate and store a new report"""
    payload = {
        "user_id": current_user.id,
        "title": title,
        "content": content,
        "analysis_type": analysis_type
    }
    response = await call_service("POST", f"{urls['report']}/generate", json=payload)
    result = response.json()
    
    # Log activity
    report_id = result.get("id") if isinstance(result, dict) else None
    log_activity(
        db, 
        action="report_created", 
        user_id=current_user.id,
        resource_type=analysis_type or "general",
        resource_id=report_id,
        details=title[:200] if title else None
    )
    
    return result

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
# WATCH ENDPOINTS - AUTOMATED MONITORING
# =============================================================================

@app.get("/watches/presets", tags=["Watches"])
async def get_watch_presets(urls: dict = Depends(get_service_urls)):
    """Get available cron expression presets for scheduling watches"""
    response = await call_service("GET", f"{urls['scheduler']}/presets")
    return response.json()


@app.get("/watches", tags=["Watches"])
async def list_watches(
    active_only: bool = False,
    urls: dict = Depends(get_service_urls),
    current_user: User = Depends(get_current_user)
):
    """List all watch configurations"""
    # Admin sees all, regular users see only their own
    user_filter = "" if is_admin(current_user) else f"&user_id={current_user.id}"
    response = await call_service("GET", f"{urls['scheduler']}/watches?active_only={active_only}{user_filter}")
    return response.json()


@app.post("/watches", tags=["Watches"])
async def create_watch(
    name: str,
    topic: str,
    cron_expression: str,
    email_recipients: List[str],
    sector: str = "general",
    report_type: str = "synthese_executive",
    keywords: List[str] = [],
    sources_preference: str = "all",
    is_active: bool = True,
    urls: dict = Depends(get_service_urls),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new automated watch"""
    payload = {
        "user_id": current_user.id,  # Watches always owned by creator
        "name": name,
        "topic": topic,
        "sector": sector,
        "report_type": report_type,
        "keywords": keywords,
        "sources_preference": sources_preference,
        "cron_expression": cron_expression,
        "email_recipients": email_recipients,
        "is_active": is_active
    }
    response = await call_service("POST", f"{urls['scheduler']}/watches", json=payload)
    result = response.json()
    
    # Log activity
    watch_id = result.get("id") if isinstance(result, dict) else None
    log_activity(
        db,
        action="watch_created",
        user_id=current_user.id,
        resource_type="watch",
        resource_id=watch_id,
        details=f"{name}: {topic}"[:200]
    )
    
    return result


@app.get("/watches/{watch_id}", tags=["Watches"])
async def get_watch(
    watch_id: int,
    urls: dict = Depends(get_service_urls),
    current_user: User = Depends(get_current_user)
):
    """Get a specific watch configuration"""
    user_param = "" if is_admin(current_user) else f"?user_id={current_user.id}"
    response = await call_service("GET", f"{urls['scheduler']}/watches/{watch_id}{user_param}")
    return response.json()


@app.put("/watches/{watch_id}", tags=["Watches"])
async def update_watch(
    watch_id: int,
    name: Optional[str] = None,
    topic: Optional[str] = None,
    sector: Optional[str] = None,
    report_type: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    sources_preference: Optional[str] = None,
    cron_expression: Optional[str] = None,
    email_recipients: Optional[List[str]] = None,
    is_active: Optional[bool] = None,
    urls: dict = Depends(get_service_urls),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing watch"""
    payload = {}
    if name is not None: payload["name"] = name
    if topic is not None: payload["topic"] = topic
    if sector is not None: payload["sector"] = sector
    if report_type is not None: payload["report_type"] = report_type
    if keywords is not None: payload["keywords"] = keywords
    if sources_preference is not None: payload["sources_preference"] = sources_preference
    if cron_expression is not None: payload["cron_expression"] = cron_expression
    if email_recipients is not None: payload["email_recipients"] = email_recipients
    if is_active is not None: payload["is_active"] = is_active

    user_param = "" if is_admin(current_user) else f"?user_id={current_user.id}"
    response = await call_service("PUT", f"{urls['scheduler']}/watches/{watch_id}{user_param}", json=payload)
    result = response.json()
    
    # Log activity
    log_activity(
        db,
        action="watch_updated",
        user_id=current_user.id,
        resource_type="watch",
        resource_id=watch_id,
        details=f"Updated watch {watch_id}"
    )
    
    return result


@app.delete("/watches/{watch_id}", tags=["Watches"])
async def delete_watch(
    watch_id: int,
    urls: dict = Depends(get_service_urls),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a watch"""
    user_param = "" if is_admin(current_user) else f"?user_id={current_user.id}"
    response = await call_service("DELETE", f"{urls['scheduler']}/watches/{watch_id}{user_param}")
    
    # Log activity
    log_activity(
        db,
        action="watch_deleted",
        user_id=current_user.id,
        resource_type="watch",
        resource_id=watch_id
    )
    
    return response.json()


@app.post("/watches/{watch_id}/trigger", tags=["Watches"])
async def trigger_watch(
    watch_id: int,
    urls: dict = Depends(get_service_urls),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger a watch execution"""
    user_param = "" if is_admin(current_user) else f"?user_id={current_user.id}"
    response = await call_service("POST", f"{urls['scheduler']}/watches/{watch_id}/trigger{user_param}")
    
    # Log activity
    log_activity(
        db,
        action="watch_triggered",
        user_id=current_user.id,
        resource_type="watch",
        resource_id=watch_id
    )
    
    return response.json()


@app.get("/watches/{watch_id}/history", tags=["Watches"])
async def get_watch_history(
    watch_id: int,
    limit: int = 10,
    urls: dict = Depends(get_service_urls),
    current_user: User = Depends(get_current_user)
):
    """Get execution history for a watch"""
    user_param = "" if is_admin(current_user) else f"&user_id={current_user.id}"
    response = await call_service("GET", f"{urls['scheduler']}/watches/{watch_id}/history?limit={limit}{user_param}")
    return response.json()


# =============================================================================
# WORKFLOW ENDPOINTS - COMMON PATTERNS
# =============================================================================

@app.post("/workflows/analyze-and-report", tags=["Workflows"])
async def analyze_and_report(
    analysis_type: str,
    query: str,
    title: str,
    auto_export: bool = False,
    urls: dict = Depends(get_service_urls),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    
    # Log activity
    report_id = report_result.get("id") if isinstance(report_result, dict) else None
    log_activity(
        db, 
        action="report_created", 
        user_id=current_user.id,
        resource_type=analysis_type,
        resource_id=report_id,
        details=title[:200] if title else None
    )
    
    result = {
        "analysis": analysis_result,
        "report": report_result
    }
    
    # Auto-export if requested
    if auto_export:
        export_url = f"/reports/{report_result['id']}/export"
        result["export_url"] = export_url
    
    return result


# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@app.post("/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user via Supabase Auth and return JWT token
    """
    return await login_user(credentials, db)


@app.post("/auth/register", response_model=TokenResponse, tags=["Authentication"])
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register new user via Supabase Auth with invitation code
    """
    return await register_user(user_data, db)


@app.get("/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_me(current_user: SupabaseUser = Depends(get_current_user)):
    """
    Get current authenticated user info
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


# =============================================================================
# ADMIN ENDPOINTS
# =============================================================================

@app.post("/admin/invite", response_model=InvitationResponse, tags=["Admin"])
async def create_invite(
    data: InvitationCreate,
    current_user: SupabaseUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new invitation (admin only)
    """
    invitation = create_invitation(db, current_user.id, data)
    return InvitationResponse.model_validate(invitation)


@app.get("/admin/invitations", response_model=List[InvitationResponse], tags=["Admin"])
async def admin_list_invitations(
    current_user: SupabaseUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    List all invitations (admin only)
    """
    invitations = db.query(Invitation).order_by(Invitation.created_at.desc()).all()
    return [InvitationResponse.model_validate(inv) for inv in invitations]


@app.get("/admin/users", response_model=List[UserResponse], tags=["Admin"])
async def admin_list_users(
    current_user: SupabaseUser = Depends(get_current_admin)
):
    """
    List all users from Supabase Auth (admin only)
    """
    return await list_users()


@app.patch("/admin/users/{user_id}/toggle-active", response_model=UserResponse, tags=["Admin"])
async def admin_toggle_user_active(
    user_id: str,
    current_user: SupabaseUser = Depends(get_current_admin)
):
    """
    Toggle user active status in Supabase Auth (admin only)
    """
    # Empêcher l'admin de désactiver son propre compte
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Impossible de désactiver votre propre compte")

    # Récupérer l'état actuel de l'utilisateur
    try:
        client = get_supabase_admin_client()
        user_response = client.auth.admin.get_user_by_id(user_id)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        current_active = (user_response.user.app_metadata or {}).get("is_active", True)
        new_active = not current_active

        return await toggle_user_active(user_id, new_active)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling user active: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour du statut")


@app.get("/admin/password-resets", response_model=List[PasswordResetTokenResponse], tags=["Admin"])
async def admin_list_password_resets(
    current_user: SupabaseUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    List all password reset requests (admin only)
    """
    tokens = db.query(PasswordResetToken).order_by(PasswordResetToken.created_at.desc()).limit(50).all()
    result = []
    for t in tokens:
        response = PasswordResetTokenResponse.model_validate(t)
        # Show token to admin for pending requests
        if not t.used_at and t.expires_at > datetime.utcnow():
            response.token = t.token
        result.append(response)
    return result


@app.patch("/admin/users/{user_id}/reset-password", tags=["Admin"])
async def admin_reset_user_password(
    user_id: str,
    current_user: SupabaseUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin force reset a user's password via Supabase and return the reset token
    """
    # Récupérer l'utilisateur depuis Supabase pour avoir son email
    try:
        client = get_supabase_admin_client()
        user_response = client.auth.admin.get_user_by_id(user_id)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        user_email = user_response.user.email
        if not user_email:
            raise HTTPException(status_code=400, detail="L'utilisateur n'a pas d'email")

        reset_token = create_password_reset_token(db, user_email)
        if not reset_token:
            raise HTTPException(status_code=400, detail="Impossible de créer le token")

        return {
            "message": "Token de réinitialisation créé",
            "token": reset_token.token,
            "expires_at": reset_token.expires_at,
            "reset_url": f"/reset-password?token={reset_token.token}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating password reset: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création du token")


# =============================================================================
# PASSWORD MANAGEMENT ENDPOINTS
# =============================================================================

@app.post("/auth/forgot-password", tags=["Authentication"])
async def forgot_password(data: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Request a password reset. Creates a token that can be used to reset the password.
    For security, always returns success even if email doesn't exist.
    """
    reset_token = create_password_reset_token(db, data.email)
    
    # In production, you would send an email here
    # For now, we just return a success message
    # The admin can see pending reset requests in the admin panel
    
    return {
        "message": "Si cet email existe, un lien de réinitialisation a été créé.",
        "info": "Contactez un administrateur pour obtenir votre lien de réinitialisation."
    }


@app.post("/auth/reset-password", tags=["Authentication"])
async def do_reset_password(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """
    Reset password using a valid token
    """
    if len(data.new_password) < 6:
        raise HTTPException(
            status_code=400, 
            detail="Le mot de passe doit contenir au moins 6 caractères"
        )
    
    success = reset_password(db, data.token, data.new_password)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Token invalide ou expiré"
        )
    
    return {"message": "Mot de passe réinitialisé avec succès"}


@app.get("/auth/validate-reset-token", tags=["Authentication"])
async def check_reset_token(token: str, db: Session = Depends(get_db)):
    """
    Validate a reset token before showing the reset form
    """
    reset_token = validate_reset_token(db, token)
    if not reset_token:
        raise HTTPException(
            status_code=400,
            detail="Token invalide ou expiré"
        )
    
    return {
        "valid": True,
        "email": reset_token.email
    }


@app.post("/auth/change-password", tags=["Authentication"])
async def do_change_password(
    data: PasswordChange,
    current_user: SupabaseUser = Depends(get_current_user)
):
    """
    Change password for authenticated user via Supabase (requires current password)
    """
    if len(data.new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Le mot de passe doit contenir au moins 6 caractères"
        )

    return await change_password(current_user, data.current_password, data.new_password)


@app.patch("/auth/profile", response_model=UserResponse, tags=["Authentication"])
async def do_update_profile(
    full_name: Optional[str] = None,
    current_user: SupabaseUser = Depends(get_current_user)
):
    """
    Update user profile information via Supabase
    """
    if full_name is not None:
        profile_data = ProfileUpdate(full_name=full_name)
        updated_user = await update_profile(current_user, profile_data)
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            full_name=updated_user.full_name,
            role=updated_user.role,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at
        )

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


# =============================================================================
# ADMIN DASHBOARD ENDPOINTS
# =============================================================================

@app.get("/admin/dashboard/stats", response_model=DashboardStats, tags=["Admin Dashboard"])
async def get_dashboard_stats(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: SupabaseUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics for admin
    """
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)

    # Parse dates if provided
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            start = week_ago
    else:
        start = week_ago

    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            end = today
    else:
        end = today

    # Total users from Supabase Auth
    try:
        client = get_supabase_admin_client()
        supabase_users = client.auth.admin.list_users()
        total_users = len(supabase_users) if supabase_users else 0
        active_users = sum(1 for u in supabase_users if (u.app_metadata or {}).get("is_active", True))
    except Exception as e:
        logger.warning(f"Could not fetch Supabase users for stats: {e}")
        total_users = 0
        active_users = 0
    
    # Count activities
    total_logins_today = db.query(ActivityLog).filter(
        ActivityLog.action == "login",
        cast(ActivityLog.created_at, Date) == today
    ).count()
    
    total_logins_week = db.query(ActivityLog).filter(
        ActivityLog.action == "login",
        cast(ActivityLog.created_at, Date) >= week_ago
    ).count()
    
    total_activities_today = db.query(ActivityLog).filter(
        cast(ActivityLog.created_at, Date) == today
    ).count()
    
    # Reports (from activity logs)
    reports_today = db.query(ActivityLog).filter(
        ActivityLog.action == "report_created",
        cast(ActivityLog.created_at, Date) == today
    ).count()
    
    reports_week = db.query(ActivityLog).filter(
        ActivityLog.action == "report_created",
        cast(ActivityLog.created_at, Date) >= week_ago
    ).count()
    
    # Total reports from report service (approximate from logs)
    total_reports = db.query(ActivityLog).filter(
        ActivityLog.action == "report_created"
    ).count()
    
    # Watch statistics
    total_watches = db.query(ActivityLog).filter(
        ActivityLog.action == "watch_created"
    ).count()
    
    watches_created_week = db.query(ActivityLog).filter(
        ActivityLog.action == "watch_created",
        cast(ActivityLog.created_at, Date) >= week_ago
    ).count()
    
    watches_triggered_week = db.query(ActivityLog).filter(
        ActivityLog.action == "watch_triggered",
        cast(ActivityLog.created_at, Date) >= week_ago
    ).count()
    
    return DashboardStats(
        total_users=total_users,
        active_users=active_users,
        total_reports=total_reports,
        total_logins_today=total_logins_today,
        total_logins_week=total_logins_week,
        total_activities_today=total_activities_today,
        reports_today=reports_today,
        reports_week=reports_week,
        total_watches=total_watches,
        watches_created_week=watches_created_week,
        watches_triggered_week=watches_triggered_week
    )


@app.get("/admin/dashboard/activities", response_model=List[ActivityLogResponse], tags=["Admin Dashboard"])
async def get_dashboard_activities(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID (UUID)"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(50, description="Maximum number of records"),
    current_user: SupabaseUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get recent activities for admin dashboard
    """
    query = db.query(ActivityLog)

    # Apply filters
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(ActivityLog.created_at >= start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(ActivityLog.created_at < end)
        except ValueError:
            pass

    if action:
        query = query.filter(ActivityLog.action == action)

    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)

    # Get activities
    activities = query.order_by(ActivityLog.created_at.desc()).offset(skip).limit(limit).all()

    # Build cache of user info from Supabase
    user_cache = {}
    try:
        client = get_supabase_admin_client()
        supabase_users = client.auth.admin.list_users()
        for u in supabase_users:
            user_cache[str(u.id)] = {
                "email": u.email,
                "full_name": (u.user_metadata or {}).get("full_name")
            }
    except Exception as e:
        logger.warning(f"Could not fetch Supabase users for activity log: {e}")

    # Build response with user info
    result = []
    for activity in activities:
        user_email = None
        user_name = None
        if activity.user_id:
            user_info = user_cache.get(str(activity.user_id))
            if user_info:
                user_email = user_info["email"]
                user_name = user_info["full_name"]

        result.append(ActivityLogResponse(
            id=activity.id,
            user_id=activity.user_id,
            user_email=user_email,
            user_name=user_name,
            action=activity.action,
            resource_type=activity.resource_type,
            resource_id=activity.resource_id,
            details=activity.details,
            created_at=activity.created_at
        ))

    return result


@app.get("/admin/dashboard/charts", response_model=DashboardCharts, tags=["Admin Dashboard"])
async def get_dashboard_charts(
    days: int = Query(7, description="Number of days to include"),
    current_user: SupabaseUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get chart data for admin dashboard
    """
    today = datetime.utcnow().date()
    
    # Activity by day
    activity_by_day = []
    for i in range(days - 1, -1, -1):
        day = today - timedelta(days=i)
        
        logins = db.query(ActivityLog).filter(
            ActivityLog.action == "login",
            cast(ActivityLog.created_at, Date) == day
        ).count()
        
        reports = db.query(ActivityLog).filter(
            ActivityLog.action == "report_created",
            cast(ActivityLog.created_at, Date) == day
        ).count()
        
        chats = db.query(ActivityLog).filter(
            ActivityLog.action == "chat_message",
            cast(ActivityLog.created_at, Date) == day
        ).count()
        
        searches = db.query(ActivityLog).filter(
            ActivityLog.action == "search",
            cast(ActivityLog.created_at, Date) == day
        ).count()
        
        watches = db.query(ActivityLog).filter(
            ActivityLog.action.in_(["watch_created", "watch_triggered", "watch_updated"]),
            cast(ActivityLog.created_at, Date) == day
        ).count()
        
        activity_by_day.append(ActivityChartData(
            date=day.strftime("%Y-%m-%d"),
            logins=logins,
            reports=reports,
            chats=chats,
            searches=searches,
            watches=watches
        ))
    
    # Reports by type
    report_types = db.query(
        ActivityLog.resource_type,
        func.count(ActivityLog.id)
    ).filter(
        ActivityLog.action == "report_created",
        ActivityLog.resource_type != None
    ).group_by(ActivityLog.resource_type).all()
    
    reports_by_type = [
        ReportTypeStats(type=rt[0] or "Autre", count=rt[1])
        for rt in report_types
    ]
    
    # If no report types, add a placeholder
    if not reports_by_type:
        reports_by_type = [ReportTypeStats(type="Aucun rapport", count=0)]
    
    return DashboardCharts(
        activity_by_day=activity_by_day,
        reports_by_type=reports_by_type
    )


# ============================================================================
# MEMORY SERVICE PROXY ENDPOINTS
# ============================================================================

@app.get("/api/memory/conversations")
async def get_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    conversation_type: Optional[str] = Query(None),
    analysis_type: Optional[str] = Query(None),
    business_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """
    Proxy endpoint to list user's conversations from memory service
    """
    services = get_service_urls()
    token = create_access_token(data={"sub": str(current_user.id)})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {"skip": skip, "limit": limit}
            if conversation_type:
                params["conversation_type"] = conversation_type
            if analysis_type:
                params["analysis_type"] = analysis_type
            if business_type:
                params["business_type"] = business_type
            if search:
                params["search"] = search

            response = await client.get(
                f"{services['memory']}/api/v1/conversations",
                params=params,
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error fetching conversations from memory service: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")


@app.get("/api/memory/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Proxy endpoint to get a specific conversation from memory service
    """
    services = get_service_urls()
    token = create_access_token(data={"sub": str(current_user.id)})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{services['memory']}/api/v1/conversations/{conversation_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error fetching conversation {conversation_id}: {e}")
        if hasattr(e, 'response') and e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Conversation not found")
        raise HTTPException(status_code=500, detail="Failed to fetch conversation")


@app.delete("/api/memory/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Proxy endpoint to delete a conversation from memory service
    """
    services = get_service_urls()
    token = create_access_token(data={"sub": str(current_user.id)})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                f"{services['memory']}/api/v1/conversations/{conversation_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return {"status": "deleted"}

    except httpx.HTTPError as e:
        logger.error(f"Error deleting conversation {conversation_id}: {e}")
        if hasattr(e, 'response') and e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Conversation not found")
        raise HTTPException(status_code=500, detail="Failed to delete conversation")


@app.get("/api/memory/documents")
async def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    document_type: Optional[str] = Query(None, alias="type"),
    analysis_type: Optional[str] = Query(None),
    business_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """
    Proxy endpoint to list user's documents from memory service
    """
    services = get_service_urls()
    token = create_access_token(data={"sub": str(current_user.id)})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {"skip": skip, "limit": limit}
            if document_type:
                params["type"] = document_type
            if analysis_type:
                params["analysis_type"] = analysis_type
            if business_type:
                params["business_type"] = business_type
            if search:
                params["search"] = search

            response = await client.get(
                f"{services['memory']}/api/v1/documents",
                params=params,
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error fetching documents from memory service: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")


@app.get("/api/memory/documents/{document_id}")
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Proxy endpoint to get a specific document from memory service
    """
    services = get_service_urls()
    token = create_access_token(data={"sub": str(current_user.id)})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{services['memory']}/api/v1/documents/{document_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error fetching document {document_id}: {e}")
        if hasattr(e, 'response') and e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Document not found")
        raise HTTPException(status_code=500, detail="Failed to fetch document")


@app.delete("/api/memory/documents/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Proxy endpoint to delete a document from memory service
    """
    services = get_service_urls()
    token = create_access_token(data={"sub": str(current_user.id)})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                f"{services['memory']}/api/v1/documents/{document_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return {"status": "deleted"}

    except httpx.HTTPError as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        if hasattr(e, 'response') and e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Document not found")
        raise HTTPException(status_code=500, detail="Failed to delete document")


@app.get("/api/memory/migrate/status")
async def get_migration_status(current_user: User = Depends(get_current_user)):
    """
    Proxy endpoint to check migration status from legacy system
    """
    services = get_service_urls()
    token = create_access_token(data={"sub": str(current_user.id)})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{services['memory']}/api/v1/migrate/status",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error fetching migration status: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch migration status")


@app.post("/api/memory/migrate")
async def trigger_migration(current_user: User = Depends(get_current_user)):
    """
    Proxy endpoint to trigger migration from legacy system
    """
    services = get_service_urls()
    token = create_access_token(data={"sub": str(current_user.id)})

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{services['memory']}/api/v1/migrate",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error triggering migration: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger migration")


# ============================================================================
# CONTEXT PROXY ENDPOINTS
# ============================================================================

@app.get("/context/current")
async def get_context_current(current_user: SupabaseUser = Depends(get_current_user)):
    """
    Proxy endpoint to get current user context from backend-service
    """
    services = get_service_urls()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{services['backend']}/context/current",
                params={"user_id": current_user.id}
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error fetching context for user {current_user.id}: {e}")
        # Return empty context instead of error for better UX
        return {"type": None, "message": "No context set"}


@app.post("/context/text")
async def save_context_text(
    request: Request,
    current_user: SupabaseUser = Depends(get_current_user)
):
    """
    Proxy endpoint to save text context for current user
    """
    services = get_service_urls()

    try:
        body = await request.json()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{services['backend']}/context/text",
                params={"user_id": current_user.id},
                json=body
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error saving context for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save context")


@app.delete("/context")
async def delete_context(current_user: SupabaseUser = Depends(get_current_user)):
    """
    Proxy endpoint to delete user context
    """
    services = get_service_urls()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                f"{services['backend']}/context",
                params={"user_id": current_user.id}
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Error deleting context for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete context")


@app.post("/context/upload")
async def upload_context_document(
    file: UploadFile = File(...),
    current_user: SupabaseUser = Depends(get_current_user)
):
    """
    Proxy endpoint to upload document context (PDF, DOCX, TXT)
    Forwards the file to backend-service for text extraction and storage,
    then syncs the document to memory-service for unified context management.
    """
    services = get_service_urls()

    try:
        # Read file content
        file_content = await file.read()

        # Forward to backend-service as multipart form data
        async with httpx.AsyncClient(timeout=60.0) as client:
            files = {
                "file": (file.filename, file_content, file.content_type or "application/octet-stream")
            }
            response = await client.post(
                f"{services['backend']}/context/upload",
                params={"user_id": current_user.id},
                files=files
            )
            response.raise_for_status()
            legacy_result = response.json()

        # Sync document to memory-service for unified context listing
        try:
            extracted_content = legacy_result.get("content", "")
            if extracted_content:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    await client.post(
                        f"{services['memory']}/api/v1/contexts",
                        json={
                            "name": file.filename or "Document uploadé",
                            "context_type": "document",
                            "content": extracted_content,
                            "filename": file.filename,
                            "file_type": file.content_type,
                            "is_active": True
                        },
                        headers={"Authorization": f"Bearer {create_access_token(data={'sub': str(current_user.id)})}"}
                    )
                    logger.info(f"Document synced to memory-service for user {current_user.id}: {file.filename}")
        except Exception as e:
            # Log warning but don't fail the request - legacy upload succeeded
            logger.warning(f"Failed to sync document to memory-service for user {current_user.id}: {e}")

        return legacy_result

    except httpx.HTTPStatusError as e:
        # Forward backend error message to client
        try:
            error_detail = e.response.json().get("detail", "Erreur lors de l'upload")
        except Exception:
            error_detail = "Erreur lors de l'upload du document"
        logger.error(f"Error uploading context document for user {current_user.id}: {error_detail}")
        raise HTTPException(status_code=e.response.status_code, detail=error_detail)

    except httpx.HTTPError as e:
        logger.error(f"Error uploading context document for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload document")


# ============================================================================
# MULTI-CONTEXT MANAGEMENT PROXY ENDPOINTS (New API)
# ============================================================================

@app.get("/api/contexts")
async def list_contexts(
    active_only: bool = Query(False),
    context_type: Optional[str] = Query(None),
    current_user: SupabaseUser = Depends(get_current_user)
):
    """List all user contexts"""
    services = get_service_urls()

    params = {"active_only": active_only}
    if context_type:
        params["context_type"] = context_type

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{services['memory']}/api/v1/contexts",
            params=params,
            headers={"Authorization": f"Bearer {create_access_token(data={'sub': str(current_user.id)})}"}
        )
        response.raise_for_status()
        return response.json()


@app.post("/api/contexts")
async def create_context(
    request: Request,
    current_user: SupabaseUser = Depends(get_current_user)
):
    """Create a new context"""
    services = get_service_urls()
    body = await request.json()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{services['memory']}/api/v1/contexts",
                json=body,
                headers={"Authorization": f"Bearer {create_access_token(data={'sub': str(current_user.id)})}"}
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json().get("detail", "Erreur lors de la création")
        except Exception:
            error_detail = "Erreur lors de la création du contexte"
        raise HTTPException(status_code=e.response.status_code, detail=error_detail)


@app.get("/api/contexts/quota")
async def get_storage_quota(current_user: SupabaseUser = Depends(get_current_user)):
    """Get user's storage quota"""
    services = get_service_urls()

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{services['memory']}/api/v1/contexts/quota",
            headers={"Authorization": f"Bearer {create_access_token(data={'sub': str(current_user.id)})}"}
        )
        response.raise_for_status()
        return response.json()


@app.get("/api/contexts/{context_id}")
async def get_context_detail(
    context_id: int,
    current_user: SupabaseUser = Depends(get_current_user)
):
    """Get full context by ID"""
    services = get_service_urls()

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{services['memory']}/api/v1/contexts/{context_id}",
            headers={"Authorization": f"Bearer {create_access_token(data={'sub': str(current_user.id)})}"}
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Contexte non trouvé")
        response.raise_for_status()
        return response.json()


@app.patch("/api/contexts/{context_id}")
async def update_context(
    context_id: int,
    request: Request,
    current_user: SupabaseUser = Depends(get_current_user)
):
    """Update a context"""
    services = get_service_urls()
    body = await request.json()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.patch(
                f"{services['memory']}/api/v1/contexts/{context_id}",
                json=body,
                headers={"Authorization": f"Bearer {create_access_token(data={'sub': str(current_user.id)})}"}
            )
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Contexte non trouvé")
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json().get("detail", "Erreur lors de la mise à jour")
        except Exception:
            error_detail = "Erreur lors de la mise à jour du contexte"
        raise HTTPException(status_code=e.response.status_code, detail=error_detail)


@app.delete("/api/contexts/{context_id}", status_code=204)
async def delete_context_item(
    context_id: int,
    current_user: SupabaseUser = Depends(get_current_user)
):
    """Delete a context"""
    services = get_service_urls()

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.delete(
            f"{services['memory']}/api/v1/contexts/{context_id}",
            headers={"Authorization": f"Bearer {create_access_token(data={'sub': str(current_user.id)})}"}
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Contexte non trouvé")
        response.raise_for_status()


