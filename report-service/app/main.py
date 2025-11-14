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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.utils import ImageReader
from loguru import logger
from PIL import Image as PILImage


# Configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@postgres:5432/insight_db")
BRAND_LOGO_PATH = os.environ.get("BRAND_LOGO_PATH", "/app/data/logo/logo.svg")
WATERMARK_PATH = "/app/filigrane/Copie de Ebook Veille automatisée.png"  # Chemin vers le filigrane

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
        # Create custom styles - Style Veille Stratégique Professionnelle
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=26,
            fontName='Helvetica-Bold',
            spaceAfter=6,
            spaceBefore=20,
            textColor=colors.HexColor('#0052A5'),  # Bleu corporate
            alignment=TA_CENTER,
            leading=32
        ))
        
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            fontName='Helvetica',
            spaceAfter=20,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            leading=18
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=14,
            fontName='Helvetica-Bold',
            spaceBefore=16,
            spaceAfter=8,
            textColor=colors.HexColor('#0052A5'),
            leftIndent=0,
            borderPadding=6,
            borderColor=colors.HexColor('#0052A5'),
            borderWidth=0,
            leading=18
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.HexColor('#333333'),
            leftIndent=0,
            leading=16
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            spaceAfter=10,
            spaceBefore=2,
            alignment=TA_JUSTIFY,
            leading=14,
            textColor=colors.HexColor('#333333')
        ))
        
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            spaceAfter=6,
            leftIndent=20,
            bulletIndent=10,
            leading=14,
            textColor=colors.HexColor('#333333')
        ))
        
        self.styles.add(ParagraphStyle(
            name='Citation',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica',
            spaceAfter=4,
            leftIndent=15,
            textColor=colors.HexColor('#666666'),
            leading=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            fontName='Helvetica',
            textColor=colors.HexColor('#999999'),
            alignment=TA_CENTER
        ))
    
    def _add_watermark(self, canvas_obj, doc):
        """Ajoute un filigrane avec opacité réduite sur chaque page"""
        try:
            if os.path.exists(WATERMARK_PATH):
                canvas_obj.saveState()
                # Réduire l'opacité à 0.1 (10%) pour que le texte reste lisible
                canvas_obj.setFillAlpha(0.1)
                
                # Charger l'image et la redimensionner
                img = PILImage.open(WATERMARK_PATH)
                img_width, img_height = img.size
                
                # Calculer les dimensions pour centrer le filigrane
                page_width, page_height = A4
                max_width = page_width * 0.6  # 60% de la largeur de la page
                max_height = page_height * 0.6
                
                # Calculer le ratio pour conserver les proportions
                width_ratio = max_width / img_width
                height_ratio = max_height / img_height
                ratio = min(width_ratio, height_ratio)
                
                new_width = img_width * ratio
                new_height = img_height * ratio
                
                # Centrer le filigrane
                x = (page_width - new_width) / 2
                y = (page_height - new_height) / 2
                
                canvas_obj.drawImage(WATERMARK_PATH, x, y, width=new_width, height=new_height, mask='auto', preserveAspectRatio=True)
                canvas_obj.restoreState()
        except Exception as e:
            logger.warning(f"Could not add watermark: {e}")
    
    def _add_header_footer(self, canvas_obj, doc):
        """Ajoute en-tête et pied de page"""
        canvas_obj.saveState()
        page_width, page_height = A4
        
        # Pied de page
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.HexColor('#999999'))
        
        # Date et heure à gauche
        footer_text = f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
        canvas_obj.drawString(2*cm, 1.5*cm, footer_text)
        
        # Numéro de page à droite
        page_num = f"Page {doc.page}"
        canvas_obj.drawRightString(page_width - 2*cm, 1.5*cm, page_num)
        
        # Ligne de séparation en haut
        canvas_obj.setStrokeColor(colors.HexColor('#0052A5'))
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(2*cm, page_height - 2*cm, page_width - 2*cm, page_height - 2*cm)
        
        canvas_obj.restoreState()
    
    def _on_page(self, canvas_obj, doc):
        """Callback appelé pour chaque page"""
        self._add_watermark(canvas_obj, doc)
        self._add_header_footer(canvas_obj, doc)
    
    def create_professional_pdf(self, title: str, content: str, analysis_type: str = None, sources: List[Dict] = None, metadata: Dict = None) -> bytes:
        """Create a professional PDF report with watermark - Style Veille Stratégique"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            rightMargin=2*cm, 
            leftMargin=2*cm, 
            topMargin=3*cm, 
            bottomMargin=2.5*cm
        )
        
        # Build the document
        story = []
        
        # ═══════════════════════════════════════════════════════════════
        # PAGE DE COUVERTURE - Style Veille Stratégique
        # ═══════════════════════════════════════════════════════════════
        story.append(Spacer(1, 3*cm))
        
        # Barre de titre avec fond bleu (simulée avec un tableau)
        title_data = [[Paragraph(title, self.styles['CustomTitle'])]]
        title_table = Table(title_data, colWidths=[doc.width])
        title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0052A5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        story.append(title_table)
        story.append(Spacer(1, 1.5*cm))
        
        # Type d'analyse (si fourni)
        if analysis_type:
            analysis_type_display = analysis_type.replace('_', ' ').title()
            story.append(Paragraph(f"<b>Type d'analyse :</b> {analysis_type_display}", self.styles['Subtitle']))
            story.append(Spacer(1, 0.5*cm))
        
        # Date de génération
        date_str = datetime.now().strftime('%d %B %Y')
        story.append(Paragraph(f"<b>Date :</b> {date_str}", self.styles['Subtitle']))
        story.append(Spacer(1, 0.3*cm))
        
        # Heure
        time_str = datetime.now().strftime('%H:%M')
        story.append(Paragraph(f"<b>Heure :</b> {time_str}", self.styles['Subtitle']))
        
        story.append(Spacer(1, 2*cm))
        
        # Box d'information (optionnel)
        if metadata and metadata.get('business_type'):
            info_data = [[Paragraph(f"<b>Secteur :</b> {metadata['business_type'].replace('_', ' ').title()}", self.styles['Normal'])]]
            info_table = Table(info_data, colWidths=[doc.width])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F4F8')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#0052A5')),
            ]))
            story.append(info_table)
        
        # Saut de page avant le contenu
        story.append(PageBreak())
        
        # ═══════════════════════════════════════════════════════════════
        # CONTENU PRINCIPAL
        # ═══════════════════════════════════════════════════════════════
        self._add_content_sections(story, content)
        
        # ═══════════════════════════════════════════════════════════════
        # SECTION SOURCES (si disponibles)
        # ═══════════════════════════════════════════════════════════════
        if sources and len(sources) > 0:
            story.append(PageBreak())
            story.append(Paragraph("📚 Sources et Références", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.3*cm))
            self._add_sources_section(story, sources)
        
        # ═══════════════════════════════════════════════════════════════
        # MÉTADONNÉES (si disponibles)
        # ═══════════════════════════════════════════════════════════════
        if metadata and len(metadata) > 1:  # Plus que juste business_type
            story.append(Spacer(1, 1*cm))
            story.append(Paragraph("ℹ️ Informations Complémentaires", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.3*cm))
            self._add_metadata_section(story, metadata)
        
        # Build PDF avec filigrane sur chaque page
        doc.build(story, onFirstPage=self._on_page, onLaterPages=self._on_page)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
    
    def _add_content_sections(self, story, content):
        """Parse content and add structured sections with better markdown support"""
        lines = content.split('\n')
        current_section = []
        in_sources = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip sources section (will be handled separately)
            if line_stripped.startswith('## 📚') or line_stripped.startswith('## Sources'):
                in_sources = True
                continue
            
            if in_sources and line_stripped.startswith('['):
                continue  # Skip source citations in content
                
            if not line_stripped:
                if current_section:
                    story.append(Paragraph(' '.join(current_section), self.styles['BodyText']))
                    current_section = []
                story.append(Spacer(1, 8))
                continue
            
            # Check for section headers (## Header)
            if line_stripped.startswith('##'):
                # Add previous section content
                if current_section:
                    story.append(Paragraph(' '.join(current_section), self.styles['BodyText']))
                    current_section = []
                
                # Add new section header
                header_text = line_stripped.lstrip('#').strip()
                story.append(Spacer(1, 0.4*cm))
                story.append(Paragraph(header_text, self.styles['SectionHeader']))
                story.append(Spacer(1, 0.2*cm))
                
            # Check for subsection headers (### or **)
            elif line_stripped.startswith('###') or (line_stripped.startswith('**') and line_stripped.endswith('**')):
                if current_section:
                    story.append(Paragraph(' '.join(current_section), self.styles['BodyText']))
                    current_section = []
                
                header_text = line_stripped.lstrip('#').strip('*').strip()
                story.append(Spacer(1, 0.3*cm))
                story.append(Paragraph(header_text, self.styles['SubsectionHeader']))
                story.append(Spacer(1, 0.1*cm))
                
            # Check for bullet points
            elif line_stripped.startswith(('-', '•', '*')) and not line_stripped.startswith('**'):
                if current_section:
                    story.append(Paragraph(' '.join(current_section), self.styles['BodyText']))
                    current_section = []
                
                bullet_text = line_stripped.lstrip('-•*').strip()
                story.append(Paragraph(f"• {bullet_text}", self.styles['BulletPoint']))
                
            # Regular text
            else:
                current_section.append(line_stripped)
        
        # Add remaining content
        if current_section:
            story.append(Paragraph(' '.join(current_section), self.styles['BodyText']))
    
    def _add_sources_section(self, story, sources):
        """Add sources section with APA-style citations"""
        if not sources:
            return
        
        # Si les sources sont des dictionnaires avec doc_id et score (ancien format)
        if isinstance(sources[0], dict) and 'doc_id' in sources[0]:
            table_data = [['Document ID', 'Pertinence']]
            
            for source in sources:
                doc_id = source.get('doc_id', 'N/A')
                score = source.get('score', 0)
                table_data.append([str(doc_id), f"{score:.2f}"])
            
            table = Table(table_data, colWidths=[3*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0052A5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            story.append(table)
        
        # Si les sources sont des strings (nouveau format avec citations)
        elif isinstance(sources, list) and len(sources) > 0 and isinstance(sources[0], str):
            for source in sources:
                story.append(Paragraph(source, self.styles['Citation']))
                story.append(Spacer(1, 4))
        
        # Si les sources sont dans le contenu (parsing du format Perplexity)
        else:
            for i, source in enumerate(sources, 1):
                if isinstance(source, dict):
                    # Format avec URL
                    citation_text = f"[{i}] {source.get('text', 'Source')}"
                    if source.get('url'):
                        citation_text += f" {source['url']}"
                    story.append(Paragraph(citation_text, self.styles['Citation']))
                else:
                    # Format simple string
                    story.append(Paragraph(f"[{i}] {source}", self.styles['Citation']))
                story.append(Spacer(1, 4))
    
    def _add_sources_table(self, story, sources):
        """Deprecated - use _add_sources_section instead"""
        self._add_sources_section(story, sources)
    
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


