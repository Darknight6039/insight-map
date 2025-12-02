"""
Scheduler Service - FastAPI application for automated market watches
"""

import os
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger
from datetime import datetime

from .models import Base, WatchConfig, WatchHistory
from .scheduler import WatchScheduler, CRON_PRESETS
from .email_sender import email_sender

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://insight_user:insight_password_2024@postgres:5432/insight_db"
)

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize scheduler
watch_scheduler = WatchScheduler(DATABASE_URL)


# Pydantic models for API
class WatchCreate(BaseModel):
    name: str
    topic: str
    sector: str = "general"
    report_type: str = "synthese_executive"
    keywords: List[str] = []
    sources_preference: str = "all"
    cron_expression: str
    email_recipients: List[str]
    is_active: bool = True

    @field_validator('cron_expression')
    @classmethod
    def validate_cron(cls, v):
        parts = v.strip().split()
        if len(parts) != 5:
            raise ValueError("Cron expression must have 5 parts: minute hour day month day_of_week")
        return v

    @field_validator('email_recipients')
    @classmethod
    def validate_recipients(cls, v):
        if not v:
            raise ValueError("At least one email recipient is required")
        return v


class WatchUpdate(BaseModel):
    name: Optional[str] = None
    topic: Optional[str] = None
    sector: Optional[str] = None
    report_type: Optional[str] = None
    keywords: Optional[List[str]] = None
    sources_preference: Optional[str] = None
    cron_expression: Optional[str] = None
    email_recipients: Optional[List[str]] = None
    is_active: Optional[bool] = None

    @field_validator('cron_expression')
    @classmethod
    def validate_cron(cls, v):
        if v is not None:
            parts = v.strip().split()
            if len(parts) != 5:
                raise ValueError("Cron expression must have 5 parts")
        return v


class WatchResponse(BaseModel):
    id: int
    name: str
    topic: str
    sector: str
    report_type: str
    keywords: List[str]
    sources_preference: str
    cron_expression: str
    email_recipients: List[str]
    is_active: bool
    created_at: Optional[str]
    updated_at: Optional[str]
    next_run: Optional[str] = None

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    id: int
    watch_id: int
    executed_at: Optional[str]
    status: str
    report_id: Optional[int]
    error_message: Optional[str]
    execution_time_seconds: Optional[int]

    class Config:
        from_attributes = True


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting scheduler service...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Set session factory and start scheduler
    watch_scheduler.set_session_factory(SessionLocal)
    watch_scheduler.start()
    
    # Reload existing active watches
    db = SessionLocal()
    try:
        active_watches = db.query(WatchConfig).filter(WatchConfig.is_active == True).all()
        for watch in active_watches:
            try:
                watch_scheduler.add_watch_job(watch)
                logger.info(f"Reloaded watch job: {watch.name}")
            except Exception as e:
                logger.error(f"Failed to reload watch {watch.id}: {e}")
    finally:
        db.close()
    
    logger.info("Scheduler service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down scheduler service...")
    watch_scheduler.shutdown()


# Create FastAPI app
app = FastAPI(
    title="Scheduler Service",
    description="Service de planification des veilles automatisées",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== API Endpoints ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "scheduler-service",
        "scheduler_running": watch_scheduler.scheduler.running,
        "smtp_configured": email_sender.is_configured()
    }


@app.get("/presets")
async def get_cron_presets():
    """Get available cron expression presets"""
    presets = [
        {"id": "daily_morning", "name": "Quotidien (8h)", "cron": "0 8 * * *", "description": "Tous les jours à 8h00"},
        {"id": "daily_evening", "name": "Quotidien (18h)", "cron": "0 18 * * *", "description": "Tous les jours à 18h00"},
        {"id": "weekly_monday", "name": "Hebdo (Lundi)", "cron": "0 8 * * 1", "description": "Chaque lundi à 8h00"},
        {"id": "weekly_friday", "name": "Hebdo (Vendredi)", "cron": "0 17 * * 5", "description": "Chaque vendredi à 17h00"},
        {"id": "biweekly", "name": "Bi-mensuel", "cron": "0 8 1,15 * *", "description": "Le 1er et 15 du mois à 8h00"},
        {"id": "monthly", "name": "Mensuel", "cron": "0 8 1 * *", "description": "Le 1er du mois à 8h00"},
    ]
    return {"presets": presets}


@app.post("/watches", response_model=WatchResponse)
async def create_watch(watch_data: WatchCreate, db: Session = Depends(get_db)):
    """Create a new watch configuration"""
    try:
        # Create watch in database
        watch = WatchConfig(
            name=watch_data.name,
            topic=watch_data.topic,
            sector=watch_data.sector,
            report_type=watch_data.report_type,
            keywords=watch_data.keywords,
            sources_preference=watch_data.sources_preference,
            cron_expression=watch_data.cron_expression,
            email_recipients=watch_data.email_recipients,
            is_active=watch_data.is_active
        )
        db.add(watch)
        db.commit()
        db.refresh(watch)
        
        # Schedule job if active
        if watch.is_active:
            watch_scheduler.add_watch_job(watch)
        
        # Get next run time
        job_info = watch_scheduler.get_job_info(watch.id)
        
        response = watch.to_dict()
        response["next_run"] = job_info["next_run_time"] if job_info else None
        
        logger.info(f"Created watch: {watch.name} (ID: {watch.id})")
        return response
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create watch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/watches", response_model=List[WatchResponse])
async def list_watches(
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """List all watch configurations"""
    query = db.query(WatchConfig)
    if active_only:
        query = query.filter(WatchConfig.is_active == True)
    
    watches = query.order_by(WatchConfig.created_at.desc()).all()
    
    result = []
    for watch in watches:
        watch_dict = watch.to_dict()
        job_info = watch_scheduler.get_job_info(watch.id)
        watch_dict["next_run"] = job_info["next_run_time"] if job_info else None
        result.append(watch_dict)
    
    return result


@app.get("/watches/{watch_id}", response_model=WatchResponse)
async def get_watch(watch_id: int, db: Session = Depends(get_db)):
    """Get a specific watch configuration"""
    watch = db.query(WatchConfig).filter(WatchConfig.id == watch_id).first()
    if not watch:
        raise HTTPException(status_code=404, detail="Watch not found")
    
    watch_dict = watch.to_dict()
    job_info = watch_scheduler.get_job_info(watch.id)
    watch_dict["next_run"] = job_info["next_run_time"] if job_info else None
    
    return watch_dict


@app.put("/watches/{watch_id}", response_model=WatchResponse)
async def update_watch(
    watch_id: int,
    watch_data: WatchUpdate,
    db: Session = Depends(get_db)
):
    """Update a watch configuration"""
    watch = db.query(WatchConfig).filter(WatchConfig.id == watch_id).first()
    if not watch:
        raise HTTPException(status_code=404, detail="Watch not found")
    
    try:
        # Update fields
        update_data = watch_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(watch, field, value)
        
        watch.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(watch)
        
        # Update scheduler
        if watch.is_active:
            watch_scheduler.add_watch_job(watch)
        else:
            watch_scheduler.remove_watch_job(watch.id)
        
        job_info = watch_scheduler.get_job_info(watch.id)
        
        response = watch.to_dict()
        response["next_run"] = job_info["next_run_time"] if job_info else None
        
        logger.info(f"Updated watch: {watch.name} (ID: {watch.id})")
        return response
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update watch {watch_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/watches/{watch_id}")
async def delete_watch(watch_id: int, db: Session = Depends(get_db)):
    """Delete a watch configuration"""
    watch = db.query(WatchConfig).filter(WatchConfig.id == watch_id).first()
    if not watch:
        raise HTTPException(status_code=404, detail="Watch not found")
    
    try:
        watch_name = watch.name
        
        # Remove from scheduler
        watch_scheduler.remove_watch_job(watch.id)
        
        # Delete from database
        db.delete(watch)
        db.commit()
        
        logger.info(f"Deleted watch: {watch_name} (ID: {watch_id})")
        return {"message": f"Watch '{watch_name}' deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete watch {watch_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/watches/{watch_id}/trigger")
async def trigger_watch(watch_id: int, db: Session = Depends(get_db)):
    """Manually trigger a watch execution"""
    watch = db.query(WatchConfig).filter(WatchConfig.id == watch_id).first()
    if not watch:
        raise HTTPException(status_code=404, detail="Watch not found")
    
    try:
        logger.info(f"Manually triggering watch: {watch.name} (ID: {watch_id})")
        await watch_scheduler.trigger_watch_now(watch_id)
        return {"message": f"Watch '{watch.name}' triggered successfully"}
        
    except Exception as e:
        logger.error(f"Failed to trigger watch {watch_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/watches/{watch_id}/toggle")
async def toggle_watch(watch_id: int, db: Session = Depends(get_db)):
    """Toggle watch active/inactive status"""
    watch = db.query(WatchConfig).filter(WatchConfig.id == watch_id).first()
    if not watch:
        raise HTTPException(status_code=404, detail="Watch not found")
    
    try:
        watch.is_active = not watch.is_active
        watch.updated_at = datetime.utcnow()
        db.commit()
        
        if watch.is_active:
            watch_scheduler.add_watch_job(watch)
            status = "activated"
        else:
            watch_scheduler.remove_watch_job(watch.id)
            status = "deactivated"
        
        logger.info(f"Watch {watch.name} (ID: {watch_id}) {status}")
        return {
            "message": f"Watch '{watch.name}' {status}",
            "is_active": watch.is_active
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to toggle watch {watch_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/watches/{watch_id}/history", response_model=List[HistoryResponse])
async def get_watch_history(
    watch_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get execution history for a watch"""
    watch = db.query(WatchConfig).filter(WatchConfig.id == watch_id).first()
    if not watch:
        raise HTTPException(status_code=404, detail="Watch not found")
    
    history = db.query(WatchHistory)\
        .filter(WatchHistory.watch_id == watch_id)\
        .order_by(WatchHistory.executed_at.desc())\
        .limit(limit)\
        .all()
    
    return [h.to_dict() for h in history]


@app.get("/history", response_model=List[HistoryResponse])
async def get_all_history(
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get execution history for all watches"""
    query = db.query(WatchHistory)
    if status:
        query = query.filter(WatchHistory.status == status)
    
    history = query.order_by(WatchHistory.executed_at.desc()).limit(limit).all()
    return [h.to_dict() for h in history]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
