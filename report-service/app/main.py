import os
import json
from datetime import datetime
from io import BytesIO
from typing import Optional, List, Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
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
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif pour environnement serveur
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re
import ast


# Configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@postgres:5432/insight_db")
BRAND_LOGO_PATH = os.environ.get("BRAND_LOGO_PATH", "/app/data/logo/logo.svg")
WATERMARK_PATH = "/app/filigrane/watermark.png"  # Chemin vers le filigrane

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

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines exacts
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility functions for chart generation
def parse_chart_blocks(content: str) -> List[Dict]:
    """
    Parse les blocs ```chart``` dans le contenu markdown
    Retourne une liste de dictionnaires contenant les données des graphiques
    """
    charts = []
    chart_pattern = r'```chart\n(.*?)\n```'
    
    matches = re.findall(chart_pattern, content, re.DOTALL)
    
    for idx, match in enumerate(matches):
        try:
            chart_data = {}
            for line in match.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'data':
                        # Parser le dict Python
                        chart_data['data'] = ast.literal_eval(value)
                    else:
                        chart_data[key] = value
            
            chart_data['index'] = idx
            charts.append(chart_data)
            logger.info(f"Chart parsed: {chart_data.get('title', 'Untitled')}")
        except Exception as e:
            logger.error(f"Error parsing chart block: {e}")
            continue
    
    return charts

def generate_chart_image(chart_data: Dict) -> Optional[BytesIO]:
    """
    Génère une image de graphique à partir des données
    Retourne un BytesIO contenant l'image PNG
    """
    try:
        chart_type = chart_data.get('type', 'bar')
        title = chart_data.get('title', 'Graphique')
        data = chart_data.get('data', {})
        source = chart_data.get('source', '')
        
        labels = data.get('labels', [])
        values = data.get('values', [])
        
        if not labels or not values:
            logger.warning(f"Chart {title} has no data")
            return None
        
        # Créer la figure avec style professionnel
        plt.figure(figsize=(10, 6))
        plt.style.use('seaborn-v0_8-darkgrid')
        
        if chart_type == 'bar':
            plt.bar(labels, values, color='#0052A5', alpha=0.8, edgecolor='black')
            plt.ylabel('Valeurs')
        elif chart_type == 'line':
            plt.plot(labels, values, marker='o', color='#0052A5', linewidth=2, markersize=8)
            plt.ylabel('Valeurs')
            plt.grid(True, alpha=0.3)
        elif chart_type == 'pie':
            colors_pie = plt.cm.Blues(range(50, 250, int(200/len(values))))
            plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors_pie)
            plt.axis('equal')
        
        plt.title(title, fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('', fontsize=10)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Ajouter la source en bas
        if source:
            plt.figtext(0.99, 0.01, f'Source: {source}', ha='right', fontsize=8, style='italic')
        
        # Sauvegarder dans BytesIO
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        img_buffer.seek(0)
        plt.close()
        
        logger.info(f"Chart generated: {title}")
        return img_buffer
    except Exception as e:
        logger.error(f"Error generating chart: {e}")
        plt.close()  # Fermer la figure en cas d'erreur
        return None

def remove_chart_blocks(content: str) -> str:
    """
    Retire les blocs ```chart``` du contenu markdown
    """
    chart_pattern = r'```chart\n.*?\n```'
    return re.sub(chart_pattern, '', content, flags=re.DOTALL)

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
            fontSize=15,  # Légèrement plus grand comme dans le template
            fontName='Helvetica-Bold',
            spaceBefore=14,
            spaceAfter=8,
            textColor=colors.HexColor('#000000'),  # Noir comme dans le template
            alignment=TA_LEFT,
            leftIndent=0,
            borderPadding=0,
            borderWidth=0,
            leading=18
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=13,  # Légèrement plus grand comme dans le template
            fontName='Helvetica-Bold',
            spaceBefore=10,
            spaceAfter=6,
            textColor=colors.HexColor('#000000'),  # Noir comme dans le template
            alignment=TA_LEFT,
            leftIndent=0,
            leading=16
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['Normal'],
            fontSize=10.5,  # Légèrement plus grand pour meilleure lisibilité
            fontName='Helvetica',
            spaceAfter=8,
            spaceBefore=2,
            alignment=TA_JUSTIFY,
            leading=14,
            textColor=colors.HexColor('#000000')  # Noir pur comme dans le template
        ))
        
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=10.5,  # Même taille que le corps de texte
            fontName='Helvetica',
            spaceAfter=5,
            leftIndent=20,
            bulletIndent=10,
            leading=14,
            textColor=colors.HexColor('#000000')  # Noir comme dans le template
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
        
        # Styles pour les tableaux (nécessaires pour les rapports longs)
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=colors.whitesmoke,
            alignment=TA_LEFT,
            leading=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableCell',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica',
            textColor=colors.HexColor('#333333'),
            alignment=TA_LEFT,
            leading=11
        ))
    
    def _add_watermark(self, canvas_obj, doc):
        """Ajoute un filigrane avec opacité réduite sur chaque page en arrière-plan"""
        try:
            logger.info(f"Attempting to add watermark from: {WATERMARK_PATH}")
            
            if not os.path.exists(WATERMARK_PATH):
                logger.warning(f"Watermark file not found at: {WATERMARK_PATH}")
                return
            
            canvas_obj.saveState()
            
            # Calculer les dimensions pour centrer le filigrane
            page_width, page_height = A4
            
            # Ajouter fond légèrement teinté (bleu/gris clair) comme dans les templates AXIAL
            canvas_obj.setFillColor(colors.HexColor('#E8EEF7'))  # Bleu très clair
            canvas_obj.rect(0, 0, page_width, page_height, fill=1, stroke=0)
            
            # Charger l'image et la redimensionner
            img = PILImage.open(WATERMARK_PATH)
            img_width, img_height = img.size
            logger.info(f"Watermark image loaded: {img_width}x{img_height}")
            
            # Filigrane en pleine page (100% pour couvrir toute la page)
            max_width = page_width * 1.0
            max_height = page_height * 1.0
            
            # Calculer le ratio pour conserver les proportions
            width_ratio = max_width / img_width
            height_ratio = max_height / img_height
            ratio = min(width_ratio, height_ratio)
            
            new_width = img_width * ratio
            new_height = img_height * ratio
            
            # Centrer le filigrane sur la page
            x = (page_width - new_width) / 2
            y = (page_height - new_height) / 2
            
            # Dessiner l'image en arrière-plan avec opacité visible comme dans les templates
            # Important: définir l'opacité AVANT de dessiner
            canvas_obj.setFillAlpha(0.15)  # 15% d'opacité comme dans les templates AXIAL
            canvas_obj.setStrokeAlpha(0.15)
            
            # Dessiner l'image en arrière-plan
            canvas_obj.drawImage(
                WATERMARK_PATH, 
                x, y, 
                width=new_width, 
                height=new_height, 
                mask='auto',
                preserveAspectRatio=True
            )
            
            canvas_obj.restoreState()
            logger.info(f"✅ Watermark added at ({x:.2f}, {y:.2f}) size ({new_width:.2f}x{new_height:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Error adding watermark: {e}", exc_info=True)
    
    def _add_header_footer(self, canvas_obj, doc):
        """Ajoute pied de page discret et professionnel"""
        canvas_obj.saveState()
        page_width, page_height = A4
        
        # Pied de page style template AXIAL
        canvas_obj.setFont('Helvetica', 7.5)
        canvas_obj.setFillColor(colors.HexColor('#FFFFFF'))  # Texte blanc sur fond coloré
        
        # Créer un rectangle coloré pour le footer (comme dans le template)
        canvas_obj.setFillColor(colors.HexColor('#6B8FC1'))  # Bleu moyen pour le fond
        canvas_obj.rect(0, 0, page_width, 1*cm, fill=1, stroke=0)
        
        # Texte du footer en blanc
        canvas_obj.setFillColor(colors.HexColor('#FFFFFF'))
        footer_text = f"© AXIAL {datetime.now().year}. Tous droits réservés. www.axial-ia.com"
        canvas_obj.drawString(2*cm, 0.4*cm, footer_text)
        
        # Numéro de page à droite en blanc
        page_num = f"Page {doc.page}"
        canvas_obj.drawRightString(page_width - 2*cm, 0.4*cm, page_num)
        
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
            topMargin=2*cm,  # Réduit pour plus de contenu (comme dans le template)
            bottomMargin=1.5*cm  # Réduit pour le footer compact
        )
        
        # Build the document
        story = []
        
        # ═══════════════════════════════════════════════════════════════
        # PAGE DE COUVERTURE - Style Veille Stratégique
        # ═══════════════════════════════════════════════════════════════
        story.append(Spacer(1, 3*cm))
        
        # Titre principal - Style épuré sans bloc bleu
        # CORRECTION: Nettoyer les emojis et limiter à 150 caractères
        import re
        # Supprimer tous les emojis et caractères non-latin
        clean_title = re.sub(r'[^\x00-\x7F\u00C0-\u00FF]+', '', title)
        # Limiter la longueur
        clean_title = clean_title[:150] + "..." if len(clean_title) > 150 else clean_title
        story.append(Paragraph(clean_title, self.styles['CustomTitle']))
        story.append(Spacer(1, 1*cm))
        
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
        # CONTENU PRINCIPAL (avec citations APA et graphiques)
        # ═══════════════════════════════════════════════════════════════
        # Extraire et générer les graphiques
        logger.info("Parsing chart blocks...")
        charts = parse_chart_blocks(content)
        chart_images = {}
        for chart_data in charts:
            chart_img = generate_chart_image(chart_data)
            if chart_img:
                chart_images[chart_data['index']] = chart_img
        logger.info(f"Generated {len(chart_images)} charts")
        
        # Retirer les blocs chart du contenu
        content_without_charts = remove_chart_blocks(content)
        
        # Extraire le mapping des citations pour conversion APA
        citations_map = self._extract_apa_citations_map(content_without_charts)
        logger.info(f"Extracted {len(citations_map)} APA citations for conversion")
        
        sources_from_content = self._add_content_sections(story, content_without_charts, citations_map, chart_images)
        
        # Extraire les sources du contenu si elles n'ont pas été fournies
        if not sources or len(sources) == 0:
            sources = self._extract_sources_from_content(content)
        
        # ═══════════════════════════════════════════════════════════════
        # SECTION SOURCES (si disponibles) - Format Bibliographie Professionnelle
        # ═══════════════════════════════════════════════════════════════
        if sources and len(sources) > 0:
            story.append(PageBreak())
            story.append(Paragraph("Références Bibliographiques", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.5*cm))
            
            # Ajouter les sources en format APA propre avec liens hypertextes
            for i, source in enumerate(sources, 1):
                # Gérer différents formats de sources (chaîne ou dictionnaire)
                import re
                if isinstance(source, dict):
                    # Format dictionnaire (ex: {'text': '...', 'url': '...'})
                    source_text_raw = source.get('text', str(source))
                else:
                    # Format chaîne
                    source_text_raw = source
                
                # Nettoyer la source des markdown et emojis
                cleaned_source = self._clean_markdown(source_text_raw)
                # Enlever les emojis résiduels
                cleaned_source = re.sub(r'[^\x00-\x7F\u00C0-\u00FF\u2013\u2014]+', '', cleaned_source).strip()
                
                # Extraire l'URL pour créer un lien hypertexte
                url = self._extract_source_url(cleaned_source)
                
                if url:
                    # Séparer le texte de l'URL
                    text_without_url = cleaned_source.replace(url, '').strip()
                    # Créer lien hypertexte cliquable en bleu
                    source_text = f'{text_without_url} <a href="{url}" color="blue"><u>{url}</u></a>'
                else:
                    # Pas d'URL trouvée, format standard
                    source_text = f"{cleaned_source}"
                
                story.append(Paragraph(source_text, self.styles['Citation']))
                story.append(Spacer(1, 8))
        
        # ═══════════════════════════════════════════════════════════════
        # MÉTADONNÉES (si disponibles)
        # ═══════════════════════════════════════════════════════════════
        if metadata and len(metadata) > 1:  # Plus que juste business_type
            story.append(Spacer(1, 1*cm))
            story.append(Paragraph("ℹ️ Informations Complémentaires", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.3*cm))
            self._add_metadata_section(story, metadata)
        
        # Build PDF avec filigrane sur chaque page
        # Utiliser des lambdas pour s'assurer que les callbacks fonctionnent
        logger.info("Building PDF with watermark callbacks...")
        doc.build(
            story, 
            onFirstPage=lambda canvas, doc: self._on_page(canvas, doc),
            onLaterPages=lambda canvas, doc: self._on_page(canvas, doc)
        )
        logger.info("PDF built successfully")
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
    
    def _extract_apa_citations_map(self, content):
        """Extrait les sources et crée un mapping [1] → (Auteur, année) pour citations APA"""
        import re
        citations_map = {}
        in_sources = False
        
        for line in content.split('\n'):
            line_stripped = line.strip()
            
            # Détecter le début de la section sources
            if line_stripped.startswith('## 📚') or line_stripped.startswith('## Sources'):
                in_sources = True
                continue
            
            # Si on est dans la section sources
            if in_sources and line_stripped.startswith('['):
                # Format: [1] Auteur/Organisation. (2024). Titre. URL
                match = re.match(r'\[(\d+)\]\s*([^.]+)\.?\s*\((\d{4})\)', line_stripped)
                if match:
                    num = match.group(1)
                    author = match.group(2).strip()
                    year = match.group(3)
                    # Raccourcir le nom si trop long
                    if len(author) > 30:
                        author = author[:27] + "..."
                    citations_map[num] = f"({author}, {year})"
                else:
                    # Format alternatif sans année visible
                    match2 = re.match(r'\[(\d+)\]\s*([^.]+)', line_stripped)
                    if match2:
                        num = match2.group(1)
                        author = match2.group(2).strip()
                        if len(author) > 30:
                            author = author[:27] + "..."
                        citations_map[num] = f"({author})"
            
            # Si on rencontre une nouvelle section majeure, on sort
            if in_sources and line_stripped.startswith('## ') and not line_stripped.startswith('## 📚') and not line_stripped.startswith('## Sources'):
                break
        
        return citations_map
    
    def _extract_source_url(self, source_text: str) -> Optional[str]:
        """
        Extrait l'URL d'une source APA format.
        Formats supportés:
        - Auteur. (Année). Titre. Type. https://example.com
        - Auteur. (Année). Titre. http://example.com
        """
        import re
        # Regex pour extraire URL (http:// ou https://)
        url_pattern = r'(https?://[^\s]+)'
        match = re.search(url_pattern, source_text)
        if match:
            url = match.group(1)
            # Nettoyer l'URL des caractères de ponctuation finaux
            url = url.rstrip('.,;:')
            return url
        return None
    
    def _clean_markdown(self, text, citations_map=None):
        """Nettoie le texte des symboles markdown et convertit citations en format APA"""
        import re
        from html import escape
        
        # IMPORTANT: D'abord échapper les caractères HTML spéciaux AVANT de créer nos balises
        # Ceci évite les erreurs "unclosed tags" quand le texte contient < ou >
        # On utilise une approche qui préserve les patterns markdown qu'on va convertir
        
        # Protéger temporairement les patterns markdown qu'on veut garder
        # avec des placeholders uniques
        placeholders = {}
        placeholder_counter = [0]
        
        def protect_pattern(match):
            key = f"__PLACEHOLDER_{placeholder_counter[0]}__"
            placeholders[key] = match.group(0)
            placeholder_counter[0] += 1
            return key
        
        # Protéger les patterns markdown
        text = re.sub(r'\*\*(.+?)\*\*', protect_pattern, text)  # **bold**
        text = re.sub(r'\*([^*]+?)\*', protect_pattern, text)   # *italic*
        text = re.sub(r'`([^`]+?)`', protect_pattern, text)     # `code`
        
        # Maintenant échapper les caractères HTML dans le reste du texte
        text = escape(text)
        
        # Restaurer et convertir les patterns markdown protégés
        for key, original in placeholders.items():
            # Convertir le pattern markdown en HTML
            if original.startswith('**'):
                # Bold: **text** -> <b>text</b>
                inner = escape(original[2:-2])
                replacement = f'<b>{inner}</b>'
            elif original.startswith('*'):
                # Italic: *text* -> <i>text</i>
                inner = escape(original[1:-1])
                replacement = f'<i>{inner}</i>'
            elif original.startswith('`'):
                # Code: `text` -> <font name="Courier">text</font>
                inner = escape(original[1:-1])
                replacement = f'<font name="Courier">{inner}</font>'
            else:
                replacement = escape(original)
            
            text = text.replace(key, replacement)
        
        # Convertir citations [1], [2], [3] en format APA (Auteur, année)
        if citations_map:
            def replace_citation(match):
                num = match.group(1)
                if num in citations_map:
                    citation_text = escape(citations_map[num])
                    return f'<font size="9" color="#666666">{citation_text}</font>'
                return match.group(0)
            
            # Remplacer les citations simples [1]
            text = re.sub(r'\[(\d+)\]', replace_citation, text)
        else:
            # Fallback : conserver les citations [1], [2], etc. en format réduit
            text = re.sub(r'\[(\d+)\]', r'<sup><font size="8">[\1]</font></sup>', text)
        
        return text
    
    def _extract_sources_from_content(self, content):
        """Extrait les sources formatées en APA depuis le contenu"""
        import re
        sources = []
        in_sources = False
        
        for line in content.split('\n'):
            line_stripped = line.strip()
            
            # Détecter le début de la section sources (formats variés)
            if (line_stripped.startswith('## 📚') or 
                line_stripped.startswith('## Sources') or
                line_stripped.startswith('## Références') or
                'bibliographie' in line_stripped.lower() or
                'sources' in line_stripped.lower() and line_stripped.startswith('##')):
                in_sources = True
                logger.info(f"Found sources section: {line_stripped}")
                continue
            
            # Si on est dans la section sources et qu'on trouve une citation
            if in_sources and line_stripped:
                # Format [N] Auteur. (Année). Titre. URL
                if line_stripped.startswith('['):
                    match = re.match(r'\[(\d+)\]\s*(.+)', line_stripped)
                    if match:
                        sources.append(match.group(2).strip())
                # Format sans [N] - juste la source
                elif not line_stripped.startswith('#'):
                    sources.append(line_stripped)
            
            # Si on rencontre une nouvelle section majeure, on sort des sources
            if in_sources and line_stripped.startswith('## ') and not any(x in line_stripped.lower() for x in ['sources', 'référence', 'bibliographie', '📚']):
                logger.info(f"Exiting sources section at: {line_stripped}, found {len(sources)} sources")
                break
        
        logger.info(f"Total sources extracted: {len(sources)}")
        return sources
    
    def _is_table_row(self, line):
        """Détecte si une ligne est une ligne de tableau markdown"""
        line = line.strip()
        return line.startswith('|') and line.endswith('|') and line.count('|') >= 2
    
    def _parse_table(self, lines, start_idx, citations_map=None):
        """Parse un tableau markdown et retourne l'objet Table et l'index suivant"""
        table_lines = []
        i = start_idx
        
        # Collecter toutes les lignes du tableau
        while i < len(lines) and self._is_table_row(lines[i]):
            table_lines.append(lines[i])
            i += 1
        
        if len(table_lines) < 2:  # Au moins en-tête + une ligne
            return None, start_idx
        
        # Parser les lignes
        table_data = []
        for idx, line in enumerate(table_lines):
            # Skip les lignes de séparation (|---|---|)
            if idx == 1 and all(c in '|-: ' for c in line):
                continue
            
            # Extraire les cellules
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            # Nettoyer le markdown dans les cellules (avec citations APA)
            cells = [self._clean_markdown(cell, citations_map) for cell in cells]
            
            # CORRECTION: Convertir chaque cellule en Paragraph pour permettre le word wrapping
            # Limiter drastiquement la longueur des cellules pour éviter les erreurs ReportLab
            paragraph_cells = []
            for cell in cells:
                # Limiter à 200 caractères par cellule max (pour éviter débordement page)
                if len(cell) > 200:
                    cell = cell[:197] + "..."
                
                # Utiliser Paragraph pour le wrapping automatique
                if idx == 0:  # En-tête
                    p = Paragraph(cell, self.styles['TableHeader'])
                else:  # Corps
                    p = Paragraph(cell, self.styles['TableCell'])
                paragraph_cells.append(p)
            
            table_data.append(paragraph_cells)
        
        if len(table_data) < 2:
            return None, start_idx
        
        # PROTECTION: Si trop de lignes, limiter à 20 max pour éviter débordement
        if len(table_data) > 21:  # 1 header + 20 lignes max
            logger.warning(f"Table too large ({len(table_data)} rows), truncating to 20 rows")
            table_data = [table_data[0]] + table_data[1:21]
        
        # Créer le tableau avec style professionnel
        # CORRECTION: Ne pas spécifier colWidths, laisser ReportLab les calculer
        try:
            table = Table(table_data)
            table_style = TableStyle([
                # En-tête (première ligne)
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0052A5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # TOP au lieu de MIDDLE pour mieux gérer les longues cellules
                
                # Lignes du corps
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333333')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                
                # Bordures
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#0052A5')),
                
                # Padding
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                
                # Alternance de couleur pour les lignes
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ])
            table.setStyle(table_style)
            
            return table, i
        except Exception as e:
            # Si le tableau est trop complexe, retourner None pour le skipper
            logger.warning(f"Failed to create table, will render as text: {str(e)[:100]}")
            return None, start_idx
    
    def _add_content_sections(self, story, content, citations_map=None, chart_images=None):
        """Parse content and add structured sections with better markdown support + APA citations + charts"""
        if chart_images is None:
            chart_images = {}
        
        lines = content.split('\n')
        current_section = []
        in_sources = False
        sources_found = []
        chart_counter = 0  # Pour insérer les graphiques au bon endroit
        i = 0
        
        while i < len(lines):
            line = lines[i]
            line_stripped = line.strip()
            
            # Skip sources section (will be handled separately)
            if line_stripped.startswith('## 📚') or line_stripped.startswith('## Sources'):
                in_sources = True
                i += 1
                continue
            
            if in_sources and line_stripped.startswith('['):
                sources_found.append(line_stripped)
                i += 1
                continue  # Skip source citations in content
            
            # Si on rencontre une autre section majeure, on sort des sources
            if in_sources and line_stripped.startswith('## '):
                in_sources = False
            
            # Détecter les tableaux
            if self._is_table_row(line_stripped) and not in_sources:
                # Ajouter le contenu en cours
                if current_section:
                    cleaned_text = self._clean_markdown(' '.join(current_section), citations_map)
                    story.append(Paragraph(cleaned_text, self.styles['CustomBodyText']))
                    current_section = []
                
                # Parser et ajouter le tableau
                table, next_idx = self._parse_table(lines, i, citations_map)
                if table:
                    story.append(Spacer(1, 0.3*cm))
                    story.append(table)
                    story.append(Spacer(1, 0.3*cm))
                    i = next_idx
                    continue
                
            if not line_stripped:
                if current_section:
                    cleaned_text = self._clean_markdown(' '.join(current_section), citations_map)
                    story.append(Paragraph(cleaned_text, self.styles['CustomBodyText']))
                    current_section = []
                story.append(Spacer(1, 8))
                i += 1
                continue
            
            # Check for headers (ordre important: ### avant ## avant #)
            # Check for subsection headers (###)
            if line_stripped.startswith('###') and not in_sources:
                if current_section:
                    cleaned_text = self._clean_markdown(' '.join(current_section), citations_map)
                    story.append(Paragraph(cleaned_text, self.styles['CustomBodyText']))
                    current_section = []
                
                header_text = line_stripped.lstrip('#').strip()
                # Enlever les emojis des titres
                header_text = header_text.replace('📚', '').replace('ℹ️', '').strip()
                # Log pour vérifier préservation numérotation sous-sections
                logger.debug(f"Processing subsection (###): {header_text}")
                story.append(Spacer(1, 0.3*cm))
                story.append(Paragraph(header_text, self.styles['SubsectionHeader']))
                story.append(Spacer(1, 0.1*cm))
                
            # Check for section headers (##)
            elif line_stripped.startswith('##') and not in_sources:
                # Add previous section content
                if current_section:
                    cleaned_text = self._clean_markdown(' '.join(current_section), citations_map)
                    story.append(Paragraph(cleaned_text, self.styles['CustomBodyText']))
                    current_section = []
                
                # Add new section header
                header_text = line_stripped.lstrip('#').strip()
                # Enlever les emojis des titres
                header_text = header_text.replace('📚', '').replace('ℹ️', '').strip()
                # Log pour vérifier préservation numérotation (ex: "1. Titre", "1.1 Sous-titre")
                logger.debug(f"Processing header (##): {header_text}")
                story.append(Spacer(1, 0.4*cm))
                story.append(Paragraph(header_text, self.styles['SectionHeader']))
                story.append(Spacer(1, 0.2*cm))
                
                # Insérer un graphique si disponible
                if chart_counter in chart_images:
                    try:
                        img = Image(chart_images[chart_counter], width=15*cm, height=9*cm)
                        story.append(Spacer(1, 0.3*cm))
                        story.append(img)
                        story.append(Spacer(1, 0.3*cm))
                        chart_counter += 1
                        logger.info(f"Inserted chart {chart_counter} after section: {header_text}")
                    except Exception as e:
                        logger.error(f"Error inserting chart: {e}")
                
            # Check for main title (#)
            elif line_stripped.startswith('#') and not line_stripped.startswith('##') and not in_sources:
                if current_section:
                    cleaned_text = self._clean_markdown(' '.join(current_section), citations_map)
                    story.append(Paragraph(cleaned_text, self.styles['CustomBodyText']))
                    current_section = []
                
                header_text = line_stripped.lstrip('#').strip()
                # Enlever les emojis des titres
                header_text = header_text.replace('📚', '').replace('ℹ️', '').strip()
                # Log pour vérifier préservation numérotation
                logger.debug(f"Processing main title (#): {header_text}")
                story.append(Spacer(1, 0.5*cm))
                story.append(Paragraph(header_text, self.styles['CustomTitle']))
                story.append(Spacer(1, 0.3*cm))
                
            # Check for bullet points
            elif line_stripped.startswith(('- ', '• ', '* ')) and not line_stripped.startswith('**'):
                if current_section:
                    cleaned_text = self._clean_markdown(' '.join(current_section), citations_map)
                    story.append(Paragraph(cleaned_text, self.styles['CustomBodyText']))
                    current_section = []
                
                bullet_text = line_stripped.lstrip('-•*').strip()
                cleaned_bullet = self._clean_markdown(bullet_text, citations_map)
                story.append(Paragraph(f"• {cleaned_bullet}", self.styles['BulletPoint']))
                
            # Regular text
            else:
                if not in_sources:
                    current_section.append(line_stripped)
            
            i += 1
        
        # Add remaining content
        if current_section:
            cleaned_text = self._clean_markdown(' '.join(current_section), citations_map)
            story.append(Paragraph(cleaned_text, self.styles['CustomBodyText']))
        
        return sources_found
    
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
                story.append(Paragraph(f"<b>{display_key}:</b> {value}", self.styles['CustomBodyText']))

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
        # CORRECTION: Nettoyer les emojis et limiter le titre à 200 caractères max
        import re
        clean_title = payload.title if payload.title else "Rapport sans titre"
        # Supprimer les emojis
        clean_title = re.sub(r'[^\x00-\x7F\u00C0-\u00FF]+', '', clean_title)
        # Limiter la longueur
        clean_title = clean_title[:200] if len(clean_title) > 200 else clean_title
        
        # Create new report
        report = Report(
            title=clean_title,
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


