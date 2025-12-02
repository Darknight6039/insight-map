"""
APScheduler-based scheduler for automated market watches
"""

import os
import httpx
import asyncio
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from sqlalchemy.orm import Session

from .models import WatchConfig, WatchHistory
from .email_sender import email_sender


class WatchScheduler:
    """Manages scheduled watch executions"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.backend_url = os.getenv("BACKEND_SERVICE_URL", "http://backend-service:8006")
        self.report_url = os.getenv("REPORT_URL", "http://report-service:8004")
        
        # Use in-memory job store - persistence handled by our WatchConfig table
        self.scheduler = AsyncIOScheduler(
            job_defaults={
                'coalesce': True,  # Combine missed runs into one
                'max_instances': 1,  # Only one instance per job
                'misfire_grace_time': 3600  # Allow 1 hour grace period
            }
        )
        
        self._db_session_factory = None

    def set_session_factory(self, session_factory):
        """Set the database session factory"""
        self._db_session_factory = session_factory

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Watch scheduler started")

    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("Watch scheduler shutdown")

    def _parse_cron_expression(self, cron_expr: str) -> dict:
        """
        Parse cron expression into APScheduler trigger kwargs
        Format: minute hour day_of_month month day_of_week
        Example: "0 8 * * 1" = Every Monday at 8:00
        """
        parts = cron_expr.strip().split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {cron_expr}. Expected 5 parts.")
        
        return {
            'minute': parts[0],
            'hour': parts[1],
            'day': parts[2],
            'month': parts[3],
            'day_of_week': parts[4]
        }

    def add_watch_job(self, watch: WatchConfig) -> str:
        """
        Add or update a scheduled job for a watch configuration
        
        Returns:
            Job ID
        """
        job_id = f"watch_{watch.id}"
        
        try:
            cron_kwargs = self._parse_cron_expression(watch.cron_expression)
            trigger = CronTrigger(**cron_kwargs)
            
            # Remove existing job if any
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            # Add new job
            self.scheduler.add_job(
                self._execute_watch,
                trigger=trigger,
                id=job_id,
                args=[watch.id],
                name=f"Watch: {watch.name}",
                replace_existing=True
            )
            
            logger.info(f"Scheduled watch job {job_id} with cron: {watch.cron_expression}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to schedule watch {watch.id}: {e}")
            raise

    def remove_watch_job(self, watch_id: int):
        """Remove a scheduled job for a watch"""
        job_id = f"watch_{watch_id}"
        try:
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info(f"Removed watch job {job_id}")
        except Exception as e:
            logger.error(f"Failed to remove watch job {job_id}: {e}")

    def pause_watch_job(self, watch_id: int):
        """Pause a scheduled job"""
        job_id = f"watch_{watch_id}"
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Paused watch job {job_id}")
        except Exception as e:
            logger.error(f"Failed to pause watch job {job_id}: {e}")

    def resume_watch_job(self, watch_id: int):
        """Resume a paused job"""
        job_id = f"watch_{watch_id}"
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Resumed watch job {job_id}")
        except Exception as e:
            logger.error(f"Failed to resume watch job {job_id}: {e}")

    async def _execute_watch(self, watch_id: int):
        """
        Execute a watch: generate report and send email
        """
        logger.info(f"Executing watch {watch_id}")
        start_time = datetime.utcnow()
        history_entry = None
        
        if not self._db_session_factory:
            logger.error("Database session factory not set")
            return
        
        db: Session = self._db_session_factory()
        
        try:
            # Get watch config
            watch = db.query(WatchConfig).filter(WatchConfig.id == watch_id).first()
            if not watch:
                logger.error(f"Watch {watch_id} not found")
                return
            
            if not watch.is_active:
                logger.info(f"Watch {watch_id} is inactive, skipping")
                return
            
            # Create history entry
            history_entry = WatchHistory(
                watch_id=watch_id,
                status="running",
                executed_at=start_time
            )
            db.add(history_entry)
            db.commit()
            db.refresh(history_entry)
            
            # Build analysis query with keywords
            query = watch.topic
            if watch.keywords:
                keywords_str = ", ".join(watch.keywords)
                query = f"{watch.topic} (focus: {keywords_str})"
            
            # Step 1: Call backend-service to generate analysis
            logger.info(f"Calling backend-service for analysis: {query}")
            async with httpx.AsyncClient(timeout=300.0) as client:
                analysis_response = await client.post(
                    f"{self.backend_url}/analyze",
                    json={
                        "query": query,
                        "analysis_type": watch.report_type,
                        "sector": watch.sector,
                        "deep_analysis": watch.report_type == "analyse_approfondie"
                    }
                )
                analysis_response.raise_for_status()
                analysis_data = analysis_response.json()
            
            analysis_content = analysis_data.get("content", analysis_data.get("response", ""))
            if not analysis_content:
                raise ValueError("No content returned from analysis")
            
            # Step 2: Generate PDF report
            logger.info(f"Generating PDF report")
            async with httpx.AsyncClient(timeout=120.0) as client:
                report_response = await client.post(
                    f"{self.report_url}/generate",
                    json={
                        "title": watch.name,
                        "content": analysis_content,
                        "report_type": watch.report_type,
                        "topic": watch.topic
                    }
                )
                report_response.raise_for_status()
                report_data = report_response.json()
            
            report_id = report_data.get("id")
            
            # Step 3: Export PDF
            logger.info(f"Exporting PDF for report {report_id}")
            async with httpx.AsyncClient(timeout=60.0) as client:
                pdf_response = await client.get(f"{self.report_url}/export/{report_id}")
                pdf_response.raise_for_status()
                pdf_content = pdf_response.content
            
            # Step 4: Send email
            logger.info(f"Sending email to {len(watch.email_recipients)} recipients")
            email_sent = email_sender.send_watch_report(
                recipients=watch.email_recipients,
                watch_name=watch.name,
                topic=watch.topic,
                report_type=watch.report_type,
                pdf_content=pdf_content
            )
            
            if not email_sent:
                raise ValueError("Failed to send email")
            
            # Update history entry as success
            execution_time = int((datetime.utcnow() - start_time).total_seconds())
            history_entry.status = "success"
            history_entry.report_id = report_id
            history_entry.execution_time_seconds = execution_time
            db.commit()
            
            logger.info(f"Watch {watch_id} executed successfully in {execution_time}s")
            
        except Exception as e:
            logger.error(f"Watch {watch_id} execution failed: {e}")
            if history_entry:
                history_entry.status = "failed"
                history_entry.error_message = str(e)[:500]
                history_entry.execution_time_seconds = int((datetime.utcnow() - start_time).total_seconds())
                db.commit()
        finally:
            db.close()

    async def trigger_watch_now(self, watch_id: int):
        """Manually trigger a watch execution"""
        await self._execute_watch(watch_id)

    def get_job_info(self, watch_id: int) -> Optional[dict]:
        """Get information about a scheduled job"""
        job_id = f"watch_{watch_id}"
        job = self.scheduler.get_job(job_id)
        if job:
            return {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "pending": job.pending
            }
        return None


# Cron expression presets for convenience
CRON_PRESETS = {
    "daily_morning": "0 8 * * *",      # Every day at 8:00 AM
    "daily_evening": "0 18 * * *",     # Every day at 6:00 PM
    "weekly_monday": "0 8 * * 1",      # Every Monday at 8:00 AM
    "weekly_friday": "0 17 * * 5",     # Every Friday at 5:00 PM
    "biweekly": "0 8 1,15 * *",        # 1st and 15th of each month at 8:00 AM
    "monthly": "0 8 1 * *",            # 1st of each month at 8:00 AM
    "quarterly": "0 8 1 1,4,7,10 *",   # First day of each quarter at 8:00 AM
}
