"""
Enhanced Report Service - Export PDF avec logo Axial et structure standardisée
"""

import os
import json
from datetime import datetime
from io import BytesIO
from typing import Optional, List, Dict
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
try:
    from svglib.svglib import svg2rlg
except ImportError:
    from svglib.svglib import renderSVG as svg2rlg
from loguru import logger

app = FastAPI(title="Enhanced Report Service", description="Export PDF avec logo Axial")

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@postgres:5432/insight_db")
AXIAL_LOGO_PATH = "/app/data/axial-logo2.svg"

# Database setup avec lazy connection
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    analysis_type = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Fallback: stockage en mémoire si DB indisponible
in_memory_reports = {}
db_available = False

# Fonction d'initialisation DB (appelée au startup)
def init_database():
    global db_available
    try:
        Base.metadata.create_all(bind=engine)
        # Test de connexion
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_available = True
        logger.info("✅ PostgreSQL connecté - Stockage en base de données activé")
    except Exception as e:
        logger.warning(f"⚠️ PostgreSQL indisponible - Basculement sur stockage en mémoire: {e}")
        db_available = False

# Event de démarrage
@app.on_event("startup")
async def startup_event():
    init_database()

def get_db():
    if not db_available:
        # Yield None pour satisfaire FastAPI Depends
        yield None
    else:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

# Pydantic models
class GenerateReportPayload(BaseModel):
    title: str
    content: str
    analysis_type: str
    sources: Optional[List[Dict]] = []
    metadata: Optional[Dict] = {}

class ReportResponse(BaseModel):
    id: int
    title: str
    analysis_type: str
    created_at: str
    metadata: Dict

class AxialReportFormatter:
    """Formatage PDF professionnel avec logo Axial"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_axial_styles()
    
    def setup_axial_styles(self):
        """Styles personnalisés Axial"""
        
        # Style titre principal
        self.styles.add(ParagraphStyle(
            name='AxialTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a365d'),  # Bleu corporate
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Style sous-titre
        self.styles.add(ParagraphStyle(
            name='AxialSubtitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2d3748'),
            spaceBefore=20,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Style section
        self.styles.add(ParagraphStyle(
            name='AxialSection',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#4a5568'),
            spaceBefore=18,
            spaceAfter=10,
            fontName='Helvetica-Bold',
            borderPadding=5,
            leftIndent=10
        ))
        
        # Style body moderne avec espacement amélioré
        self.styles.add(ParagraphStyle(
            name='AxialBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2d3748'),
            alignment=TA_JUSTIFY,
            spaceBefore=8,
            spaceAfter=8,
            leftIndent=20,
            rightIndent=20,
            leading=16,  # Interligne augmenté
            fontName='Helvetica'
        ))
        
        # Style métadonnées / Citations APA
        self.styles.add(ParagraphStyle(
            name='AxialMeta',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#718096'),
            alignment=TA_LEFT,
            spaceBefore=4,
            spaceAfter=4,
            leftIndent=30,
            rightIndent=20,
            fontName='Helvetica-Oblique',
            backColor=colors.HexColor('#f7fafc')  # Fond légèrement gris
        ))
        
        # Style pour listes à puces
        self.styles.add(ParagraphStyle(
            name='AxialBullet',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2d3748'),
            alignment=TA_LEFT,
            spaceBefore=6,
            spaceAfter=6,
            leftIndent=35,
            rightIndent=20,
            fontName='Helvetica'
        ))

    def add_axial_header(self, canvas_obj, doc):
        """Ajoute le header Axial avec logo"""
        try:
            # Logo Axial en haut à gauche
            if os.path.exists(AXIAL_LOGO_PATH):
                try:
                    # Convertir SVG en Drawing
                    drawing = svg2rlg(AXIAL_LOGO_PATH)
                    if drawing:
                        # Redimensionner le logo
                        drawing.width = 80
                        drawing.height = 40
                        drawing.shift(50, A4[1] - 80)  # Position haut gauche
                        renderPDF.draw(drawing, canvas_obj, 0, 0)
                except Exception as e:
                    logger.warning(f"Erreur rendu logo SVG: {e}")
                    # Fallback texte
                    canvas_obj.setFont("Helvetica-Bold", 16)
                    canvas_obj.setFillColor(colors.HexColor('#1a365d'))
                    canvas_obj.drawString(50, A4[1] - 50, "AXIAL")
            else:
                # Logo texte si fichier non trouvé
                canvas_obj.setFont("Helvetica-Bold", 16)
                canvas_obj.setFillColor(colors.HexColor('#1a365d'))
                canvas_obj.drawString(50, A4[1] - 50, "AXIAL")
            
            # Ligne de séparation
            canvas_obj.setStrokeColor(colors.HexColor('#e2e8f0'))
            canvas_obj.setLineWidth(1)
            canvas_obj.line(50, A4[1] - 90, A4[0] - 50, A4[1] - 90)
            
            # Date et numéro de page en haut à droite
            canvas_obj.setFont("Helvetica", 9)
            canvas_obj.setFillColor(colors.HexColor('#718096'))
            date_str = datetime.now().strftime("%d/%m/%Y")
            canvas_obj.drawRightString(A4[0] - 50, A4[1] - 50, f"Généré le {date_str}")
            canvas_obj.drawRightString(A4[0] - 50, A4[1] - 65, f"Page {doc.page}")
            
        except Exception as e:
            logger.error(f"Erreur header Axial: {e}")

    def add_axial_footer(self, canvas_obj, doc):
        """Ajoute le footer Axial"""
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.setFillColor(colors.HexColor('#a0aec0'))
        
        # Footer texte
        footer_text = "Rapport généré par Insight MVP - Intelligence Stratégique"
        canvas_obj.drawCentredString(A4[0] / 2, 30, footer_text)
        
        # Ligne de séparation footer
        canvas_obj.setStrokeColor(colors.HexColor('#e2e8f0'))
        canvas_obj.line(50, 50, A4[0] - 50, 50)

    def parse_markdown_content(self, content: str) -> List:
        """Parse le contenu markdown en éléments PDF avec espacement amélioré"""
        elements = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                # Espacements augmentés pour meilleure lisibilité
                elements.append(Spacer(1, 12))
            elif line.startswith('# '):
                # Titre principal avec espacement renforcé
                title_text = line[2:].strip()
                elements.append(Paragraph(title_text, self.styles['AxialTitle']))
                elements.append(Spacer(1, 20))
            elif line.startswith('## '):
                # Section avec émoji - espacement renforcé
                section_text = line[3:].strip()
                elements.append(Spacer(1, 18))  # Avant
                elements.append(Paragraph(section_text, self.styles['AxialSubtitle']))
                elements.append(Spacer(1, 14))  # Après
            elif line.startswith('### '):
                # Sous-section - espacement amélioré
                subsection_text = line[4:].strip()
                elements.append(Spacer(1, 12))  # Avant
                elements.append(Paragraph(subsection_text, self.styles['AxialSection']))
                elements.append(Spacer(1, 10))  # Après
            elif line.startswith('---'):
                # Séparateur horizontal élégant
                elements.append(Spacer(1, 24))
                sep_table = Table([['']],  colWidths=[A4[0]-120])
                sep_style = TableStyle([
                    ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#cbd5e0'))
                ])
                sep_table.setStyle(sep_style)
                elements.append(sep_table)
                elements.append(Spacer(1, 24))
            elif line.startswith('**') and line.endswith('**'):
                # Texte en gras avec espacement
                elements.append(Spacer(1, 8))
                bold_text = line.replace('**', '').strip()
                elements.append(Paragraph(f"<b>{bold_text}</b>", self.styles['AxialBody']))
                elements.append(Spacer(1, 6))
            elif line.startswith('['):
                # Références/Citations APA
                elements.append(Spacer(1, 4))
                elements.append(Paragraph(line, self.styles['AxialMeta']))
                elements.append(Spacer(1, 4))
            elif line.startswith('- ') or line.startswith('* '):
                # Listes à puces avec style dédié
                list_text = line[2:].strip()
                elements.append(Paragraph(f"• {list_text}", self.styles['AxialBullet']))
                elements.append(Spacer(1, 6))
            elif line.startswith('|'):
                # Tableau markdown (basique)
                # On ignore pour l'instant, mais on ajoute un spacer
                elements.append(Spacer(1, 4))
            else:
                # Texte normal avec espacement intelligent
                if line:
                    elements.append(Paragraph(line, self.styles['AxialBody']))
                    elements.append(Spacer(1, 8))
            
            i += 1
        
        return elements

    def create_axial_pdf(self, title: str, content: str, analysis_type: str = None, 
                        sources: List[Dict] = None, metadata: Dict = None) -> bytes:
        """Génère PDF avec identité visuelle Axial"""
        
        buffer = BytesIO()
        
        # Document avec marges ajustées pour header/footer
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=120,  # Espace pour header
            bottomMargin=80  # Espace pour footer
        )
        
        # Éléments du document
        elements = []
        
        # Page de titre
        elements.append(Spacer(1, 50))
        elements.append(Paragraph(title, self.styles['AxialTitle']))
        elements.append(Spacer(1, 20))
        
        if analysis_type:
            type_display = analysis_type.replace('_', ' ').title()
            elements.append(Paragraph(f"Type d'analyse: {type_display}", self.styles['AxialMeta']))
        
        if metadata and metadata.get('query'):
            elements.append(Paragraph(f"Requête: {metadata['query']}", self.styles['AxialMeta']))
        
        elements.append(Spacer(1, 30))
        
        # Table des matières simulée
        elements.append(Paragraph("SOMMAIRE EXÉCUTIF", self.styles['AxialSubtitle']))
        toc_items = [
            "🎯 Executive Summary",
            "📊 Market Overview", 
            "⚔️ Competitive Landscape",
            "💡 Key Insights",
            "⚡ Recommendations",
            "📚 Appendix"
        ]
        for item in toc_items:
            elements.append(Paragraph(f"• {item}", self.styles['AxialBody']))
        
        elements.append(PageBreak())
        
        # Contenu principal
        content_elements = self.parse_markdown_content(content)
        elements.extend(content_elements)
        
        # Sources si disponibles
        if sources:
            elements.append(PageBreak())
            elements.append(Paragraph("📋 RÉFÉRENCES DOCUMENTAIRES", self.styles['AxialSubtitle']))
            
            for i, source in enumerate(sources[:10], 1):
                doc_id = source.get('doc_id', 'N/A')
                score = source.get('score', 0)
                text_preview = source.get('text', '')[:200]
                
                ref_text = f"[{i}] Document {doc_id} (Score: {score:.3f})"
                elements.append(Paragraph(ref_text, self.styles['AxialSection']))
                elements.append(Paragraph(f'"{text_preview}..."', self.styles['AxialMeta']))
                elements.append(Spacer(1, 8))
        
        # Construction PDF avec header/footer
        def add_page_decorations(canvas_obj, doc):
            self.add_axial_header(canvas_obj, doc)
            self.add_axial_footer(canvas_obj, doc)
        
        doc.build(elements, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
        
        buffer.seek(0)
        return buffer.read()

# Instance formatter
formatter = AxialReportFormatter()

@app.post("/generate", response_model=ReportResponse)
def generate_report(payload: GenerateReportPayload, db: Session = Depends(get_db)):
    """Génère et stocke un rapport avec structure standardisée"""
    try:
        if db_available and db:
            # Stockage en base de données
            db_report = Report(
                title=payload.title,
                content=payload.content,
                analysis_type=payload.analysis_type,
                metadata_json=json.dumps(payload.metadata or {})
            )
            
            db.add(db_report)
            db.commit()
            db.refresh(db_report)
            
            logger.info(f"✅ Rapport généré (DB): {db_report.id} - {payload.title}")
            
            return ReportResponse(
                id=db_report.id,
                title=db_report.title,
                analysis_type=db_report.analysis_type,
                created_at=db_report.created_at.isoformat(),
                metadata=payload.metadata or {}
            )
        else:
            # Fallback: Stockage en mémoire
            report_id = len(in_memory_reports) + 1
            report_data = {
                "id": report_id,
                "title": payload.title,
                "content": payload.content,
                "analysis_type": payload.analysis_type,
                "metadata": payload.metadata or {},
                "created_at": datetime.utcnow()
            }
            in_memory_reports[report_id] = report_data
            
            logger.info(f"⚠️ Rapport généré (Mémoire): {report_id} - {payload.title}")
            
            return ReportResponse(
                id=report_id,
                title=payload.title,
                analysis_type=payload.analysis_type,
                created_at=report_data["created_at"].isoformat(),
                metadata=payload.metadata or {}
            )
        
    except Exception as e:
        logger.error(f"Erreur génération rapport: {e}")
        if db and db_available:
            db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export/{report_id}")
def export_axial_pdf(report_id: int, db: Session = Depends(get_db)):
    """Export PDF avec logo Axial et identité visuelle"""
    try:
        report_data = None
        metadata = {}
        
        if db_available and db:
            # Récupérer depuis DB
            report = db.query(Report).filter(Report.id == report_id).first()
            if not report:
                raise HTTPException(status_code=404, detail="Rapport non trouvé en DB")
            
            report_data = {
                "title": report.title,
                "content": report.content,
                "analysis_type": report.analysis_type
            }
            
            # Parser métadonnées
            if report.metadata_json:
                try:
                    metadata = json.loads(report.metadata_json)
                except:
                    pass
        else:
            # Récupérer depuis mémoire
            if report_id not in in_memory_reports:
                raise HTTPException(status_code=404, detail="Rapport non trouvé en mémoire")
            
            report_data = in_memory_reports[report_id]
            metadata = report_data.get("metadata", {})
        
        # Générer PDF Axial
        pdf_bytes = formatter.create_axial_pdf(
            title=report_data["title"],
            content=report_data["content"],
            analysis_type=report_data.get("analysis_type", ""),
            sources=metadata.get('sources', []),
            metadata=metadata
        )
        
        # Nom de fichier
        safe_title = "".join(c for c in report_data["title"] if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"axial_rapport_{report_id}_{safe_title[:30]}.pdf"
        
        logger.info(f"✅ Export PDF Axial: {filename}")
        
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur export PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports")
def list_reports(db: Session = Depends(get_db)):
    """Liste des rapports générés"""
    if db_available and db:
        reports = db.query(Report).order_by(Report.created_at.desc()).limit(50).all()
        return [{
            "id": r.id,
            "title": r.title,
            "analysis_type": r.analysis_type,
            "created_at": r.created_at.isoformat()
        } for r in reports]
    else:
        # Retourner depuis mémoire
        return [{
            "id": r["id"],
            "title": r["title"],
            "analysis_type": r.get("analysis_type", ""),
            "created_at": r["created_at"].isoformat()
        } for r in sorted(in_memory_reports.values(), key=lambda x: x["created_at"], reverse=True)]

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "enhanced-report-service", 
        "features": ["axial_logo", "standardized_format"],
        "database": "connected" if db_available else "in-memory-fallback",
        "reports_count": len(in_memory_reports) if not db_available else "db"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
