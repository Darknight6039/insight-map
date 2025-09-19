import os
import json
from datetime import datetime
from io import BytesIO
from typing import Optional, List, Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from loguru import logger


# Configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@postgres:5432/insight_db")
BRAND_LOGO_PATH = os.environ.get("BRAND_LOGO_PATH", "/app/data/logo/logo.svg")

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    analysis_type = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=True)  # Store JSON metadata
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models
class ExportPayload(BaseModel):
    title: str
    executive_summary: str
    citations: List[Dict]
    brand: Optional[Dict] = None

class GenerateReportPayload(BaseModel):
    title: str
    content: str
    analysis_type: Optional[str] = None
    sources: List[Dict] = []
    metadata: Optional[Dict] = None

class ReportResponse(BaseModel):
    id: int
    title: str
    analysis_type: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReportDetail(BaseModel):
    id: int
    title: str
    content: str
    analysis_type: Optional[str]
    metadata: Optional[Dict]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)


app = FastAPI(title="Report Service - Professional Report Generation", version="0.1.0")

# Utility functions for PDF generation
class ReportFormatter:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_styles()
    
    def setup_styles(self):
        # Create custom styles
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1a365d'),
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.HexColor('#2d3748'),
            leftIndent=0
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        ))
    
    def create_professional_pdf(self, title: str, content: str, analysis_type: str = None, sources: List[Dict] = None, metadata: Dict = None) -> bytes:
        """Create a professional PDF report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Build the document
        story = []
        
        # Title page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        if analysis_type:
            analysis_type_display = analysis_type.replace('_', ' ').title()
            story.append(Paragraph(f"Type d'analyse: {analysis_type_display}", self.styles['Normal']))
            story.append(Spacer(1, 0.25*inch))
        
        story.append(Paragraph(f"Généré le: {datetime.now().strftime('%d/%m/%Y à %H:%M')}", self.styles['Normal']))
        story.append(Spacer(1, 1*inch))
        
        # Content sections
        self._add_content_sections(story, content)
        
        # Sources section
        if sources:
            story.append(PageBreak())
            story.append(Paragraph("Sources", self.styles['SectionHeader']))
            story.append(Spacer(1, 12))
            self._add_sources_table(story, sources)
        
        # Metadata section
        if metadata:
            story.append(Spacer(1, 24))
            story.append(Paragraph("Métadonnées de l'analyse", self.styles['SectionHeader']))
            story.append(Spacer(1, 12))
            self._add_metadata_section(story, metadata)
        
        # Build PDF
        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
    
    def _add_content_sections(self, story, content):
        """Parse content and add structured sections"""
        lines = content.split('\n')
        current_section = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if it's a section header (starts with **)
            if line.startswith('**') and line.endswith('**'):
                # Add previous section content
                if current_section:
                    story.append(Paragraph(' '.join(current_section), self.styles['BodyText']))
                    current_section = []
                
                # Add new section header
                header_text = line.strip('*').strip()
                story.append(Spacer(1, 12))
                story.append(Paragraph(header_text, self.styles['SectionHeader']))
                story.append(Spacer(1, 6))
            else:
                current_section.append(line)
        
        # Add remaining content
        if current_section:
            story.append(Paragraph(' '.join(current_section), self.styles['BodyText']))
    
    def _add_sources_table(self, story, sources):
        """Add sources as a formatted table"""
        if not sources:
            return
        
        table_data = [['Document ID', 'Score de pertinence']]
        
        for source in sources:
            doc_id = source.get('doc_id', 'N/A')
            score = source.get('score', 0)
            table_data.append([str(doc_id), f"{score:.2f}"])
        
        table = Table(table_data, colWidths=[2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
    
    def _add_metadata_section(self, story, metadata):
        """Add metadata information"""
        for key, value in metadata.items():
            if key != 'query':  # Skip query as it might be redundant
                display_key = key.replace('_', ' ').title()
                story.append(Paragraph(f"<b>{display_key}:</b> {value}", self.styles['BodyText']))

formatter = ReportFormatter()

# Dependencies
from sqlalchemy.orm import Session
from fastapi import Depends

# Endpoints
@app.get("/health")
def health():
    return {"status": "ok", "service": "report-service"}

@app.post("/generate", response_model=ReportResponse)
def generate_report(payload: GenerateReportPayload, db: Session = Depends(get_db)):
    """Generate and store a new report"""
    try:
        # Create new report
        report = Report(
            title=payload.title,
            content=payload.content,
            analysis_type=payload.analysis_type,
            metadata_json=json.dumps(payload.metadata) if payload.metadata else None
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        logger.info(f"Generated report {report.id}: {payload.title}")
        
        return ReportResponse.from_orm(report)
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@app.get("/reports", response_model=List[ReportResponse])
def list_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all reports"""
    reports = db.query(Report).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    return [ReportResponse.from_orm(report) for report in reports]

@app.get("/reports/{report_id}", response_model=ReportDetail)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get detailed report information"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Parse metadata
    metadata = None
    if report.metadata_json:
        try:
            metadata = json.loads(report.metadata_json)
        except:
            logger.warning(f"Failed to parse metadata for report {report_id}")
    
    return ReportDetail(
        id=report.id,
        title=report.title,
        content=report.content,
        analysis_type=report.analysis_type,
        metadata=metadata,
        created_at=report.created_at
    )

@app.delete("/reports/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    """Delete a report"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db.delete(report)
    db.commit()
    
    logger.info(f"Deleted report {report_id}")
    return {"message": f"Report {report_id} deleted successfully"}

@app.get("/export/{report_id}")
def export_report_pdf(report_id: int, db: Session = Depends(get_db)):
    """Export report as professional PDF"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    try:
        # Parse metadata
        metadata = None
        if report.metadata_json:
            try:
                metadata = json.loads(report.metadata_json)
            except:
                logger.warning(f"Failed to parse metadata for report {report_id}")
        
        # Generate PDF
        pdf_bytes = formatter.create_professional_pdf(
            title=report.title,
            content=report.content,
            analysis_type=report.analysis_type,
            sources=[],  # Sources would need to be stored separately
            metadata=metadata
        )
        
        # Return PDF as download
        filename = f"report_{report.id}_{report.title[:20].replace(' ', '_')}.pdf"
        headers = {"Content-Disposition": f"attachment; filename={filename}"}
        
        logger.info(f"Exported report {report_id} as PDF")
        
        return StreamingResponse(
            BytesIO(pdf_bytes), 
            media_type="application/pdf", 
            headers=headers
        )
        
    except Exception as e:
        logger.error(f"Error exporting report {report_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

@app.post("/export_pdf")
def export_pdf_legacy(payload: ExportPayload):
    """Legacy endpoint for backward compatibility"""
    try:
        pdf_bytes = formatter.create_professional_pdf(
            title=payload.title,
            content=payload.executive_summary,
            sources=payload.citations,
            metadata=payload.brand
        )
        
        headers = {"Content-Disposition": f"attachment; filename=report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"}
        
        return StreamingResponse(
            BytesIO(pdf_bytes), 
            media_type="application/pdf", 
            headers=headers
        )
        
    except Exception as e:
        logger.error(f"Error in legacy PDF export: {e}")
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get report statistics"""
    total_reports = db.query(Report).count()
    
    # Count by analysis type
    analysis_types = db.query(Report.analysis_type).distinct().all()
    type_counts = {}
    for (analysis_type,) in analysis_types:
        if analysis_type:
            count = db.query(Report).filter(Report.analysis_type == analysis_type).count()
            type_counts[analysis_type] = count
    
    return {
        "total_reports": total_reports,
        "by_analysis_type": type_counts,
        "available_analysis_types": list(type_counts.keys())
    }


