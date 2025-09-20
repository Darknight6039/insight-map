"""
Insight MVP - Modern Financial Analysis Dashboard
Frontend interface using Gradio with dark theme and professional styling
"""

import gradio as gr
import plotly.graph_objects as go
import pandas as pd
import os
import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from components.dashboard import MarketDashboard
from components.api_client import InsightAPIClient
from loguru import logger

# Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
THEME = "dark"

# Initialize components
dashboard = MarketDashboard(GATEWAY_URL)
api_client = InsightAPIClient(GATEWAY_URL)

# Analysis type mappings
ANALYSIS_TYPES = {
    "🎯 Synthèse Exécutive": {
        "key": "synthese_executive",
        "description": "Générer un résumé stratégique et des recommandations exécutives",
        "color": "executive"
    },
    "⚔️ Analyse Concurrentielle": {
        "key": "analyse_concurrentielle", 
        "description": "Analyser la concurrence et le positionnement marché",
        "color": "competitive"
    },
    "🔬 Veille Technologique": {
        "key": "veille_technologique",
        "description": "Identifier les innovations et tendances technologiques",
        "color": "tech"
    },
    "⚠️ Analyse des Risques": {
        "key": "analyse_risques",
        "description": "Évaluer les risques et proposer des stratégies de mitigation",
        "color": "risk"
    },
    "📊 Étude de Marché": {
        "key": "etude_marche",
        "description": "Analyser le marché, la demande et les opportunités",
        "color": "market"
    }
}

def load_custom_css():
    """Load custom CSS for styling"""
    css_path = Path(__file__).parent.parent / "assets" / "custom.css"
    if css_path.exists():
        return css_path.read_text()
    return ""

def create_header():
    """Create the main header with title and status"""
    return gr.HTML(f"""
        <div class="header-container fade-in-up">
            <h1 class="header-title">🤖 Insight MVP - Intelligence Stratégique</h1>
            <p class="header-subtitle">
                Plateforme d'analyse IA avec 5 types d'analyses spécialisées | 
                <span class="status-indicator status-active"></span> Système opérationnel
            </p>
        </div>
    """)

def create_metrics_cards():
    """Create dashboard metrics cards"""
    metrics = dashboard.get_system_metrics()
    prediction = dashboard.create_prediction_card()
    
    return gr.HTML(f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
            <div class="metric-card fade-in-up">
                <div class="metric-value">98%</div>
                <div class="metric-label">
                    <span class="status-indicator status-active"></span>Uptime
                </div>
            </div>
            <div class="metric-card fade-in-up">
                <div class="metric-value">2.3s</div>
                <div class="metric-label">
                    <span class="status-indicator status-active"></span>Avg Response
                </div>
            </div>
            <div class="metric-card fade-in-up">
                <div class="metric-value">72</div>
                <div class="metric-label">
                    <span class="status-indicator status-active"></span>Indicators
                </div>
            </div>
            <div class="metric-card fade-in-up">
                <div class="metric-value">${prediction['predicted_price']:.2f}</div>
                <div class="metric-label">
                    <span class="status-indicator status-warning"></span>AI Prediction (AAPL)
                </div>
                <div style="font-size: 12px; color: #a0a0a0; margin-top: 5px;">
                    {prediction['signal']} | Confidence: {prediction['confidence']}
                </div>
            </div>
        </div>
    """)

def run_analysis_action(analysis_name: str, query: str, file_upload):
    """Execute an AI analysis"""
    if not query.strip():
        return "❌ Veuillez saisir une requête d'analyse.", ""
    
    if analysis_name not in ANALYSIS_TYPES:
        return "❌ Type d'analyse non reconnu.", ""
    
    analysis_config = ANALYSIS_TYPES[analysis_name]
    analysis_key = analysis_config["key"]
    
    try:
        # If file uploaded, upload it first
        doc_id = None
        if file_upload:
            upload_result = api_client.upload_document_sync(
                file_upload.name,
                f"Document pour {analysis_name}",
                f"Document uploadé pour analyse {analysis_key}"
            )
            
            if upload_result.get("success"):
                doc_id = upload_result["data"].get("id")
                logger.info(f"Document uploaded with ID: {doc_id}")
            else:
                return f"❌ Erreur upload: {upload_result.get('error', 'Erreur inconnue')}", ""
        
        # Run the analysis
        result = api_client.run_analysis_sync(
            analysis_key,
            query,
            f"{analysis_name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            doc_id
        )
        
        if result.get("success"):
            analysis_data = result["data"]
            
            # Format the response
            content = analysis_data.get("content", "Aucun contenu généré")
            metadata = analysis_data.get("metadata", {})
            
            status_msg = f"""
            ✅ **Analyse {analysis_name} terminée avec succès**
            
            📊 **Métadonnées:**
            - Type: {analysis_data.get('analysis_type', 'N/A')}
            - Passages analysés: {metadata.get('passages_count', 0)}
            - Timestamp: {analysis_data.get('timestamp', 'N/A')}
            """
            
            return status_msg, content
            
        else:
            error_msg = result.get("error", "Erreur inconnue")
            return f"❌ Erreur lors de l'analyse: {error_msg}", ""
            
    except Exception as e:
        logger.error(f"Error in analysis: {e}")
        return f"❌ Erreur système: {str(e)}", ""

def search_documents_action(query: str):
    """Search through uploaded documents"""
    if not query.strip():
        return "❌ Veuillez saisir une requête de recherche."
    
    try:
        result = api_client.search_documents_sync(query, top_k=5)
        
        if result.get("success"):
            search_data = result["data"]
            results = search_data.get("results", [])
            
            if not results:
                return "🔍 Aucun résultat trouvé pour cette requête."
            
            output = f"🔍 **Résultats de recherche pour:** '{query}'\n\n"
            
            for i, doc in enumerate(results, 1):
                output += f"""
                **{i}. {doc.get('title', 'Document sans titre')}**
                - Score: {doc.get('score', 0):.3f}
                - Extrait: {doc.get('text', 'Pas de texte')[:200]}...
                
                """
            
            return output
            
        else:
            return f"❌ Erreur de recherche: {result.get('error', 'Erreur inconnue')}"
            
    except Exception as e:
        logger.error(f"Error in search: {e}")
        return f"❌ Erreur système: {str(e)}"

def create_analysis_interface():
    """Create the main analysis interface"""
    
    with gr.Row():
        with gr.Column(scale=3):
            
            # Analysis Selection
            with gr.Group():
                gr.HTML("<h3 style='color: #00d4aa; margin-bottom: 15px;'>🤖 Sélection d'Analyse IA</h3>")
                
                analysis_dropdown = gr.Dropdown(
                    choices=list(ANALYSIS_TYPES.keys()),
                    label="Type d'Analyse",
                    value=list(ANALYSIS_TYPES.keys())[0],
                    interactive=True
                )
                
                query_input = gr.Textbox(
                    label="Requête d'Analyse",
                    placeholder="Ex: Analysez les tendances du secteur bancaire français...",
                    lines=3,
                    max_lines=5
                )
                
                file_upload = gr.File(
                    label="📄 Document PDF (Optionnel)",
                    file_types=[".pdf"],
                    type="filepath"
                )
            
            # Action Buttons
            with gr.Row():
                analyze_btn = gr.Button(
                    "🚀 Lancer l'Analyse",
                    variant="primary",
                    size="lg",
                    elem_classes=["analysis-btn"]
                )
                
                search_btn = gr.Button(
                    "🔍 Rechercher",
                    variant="secondary",
                    size="lg"
                )
        
        with gr.Column(scale=2):
            # Quick Actions
            gr.HTML("<h3 style='color: #00d4aa; margin-bottom: 15px;'>⚡ Actions Rapides</h3>")
            
            with gr.Row():
                quick_executive = gr.Button("🎯 Synthèse Express", size="sm", elem_classes=["analysis-btn", "executive"])
                quick_risk = gr.Button("⚠️ Analyse Risques", size="sm", elem_classes=["analysis-btn", "risk"])
            
            with gr.Row():
                quick_market = gr.Button("📊 Étude Marché", size="sm", elem_classes=["analysis-btn", "market"])
                quick_tech = gr.Button("🔬 Veille Tech", size="sm", elem_classes=["analysis-btn", "tech"])
    
    # Results Section
    with gr.Row():
        with gr.Column():
            status_output = gr.Markdown(
                "🟢 **Système prêt** - Sélectionnez un type d'analyse et saisissez votre requête.",
                elem_classes=["results-container"]
            )
            
            analysis_output = gr.Markdown(
                "Les résultats d'analyse s'afficheront ici...",
                elem_classes=["results-container"]
            )
    
    # Search Results
    with gr.Row():
        search_output = gr.Markdown(
            "Les résultats de recherche s'afficheront ici...",
            elem_classes=["results-container"]
        )
    
    # Event handlers
    analyze_btn.click(
        fn=run_analysis_action,
        inputs=[analysis_dropdown, query_input, file_upload],
        outputs=[status_output, analysis_output]
    )
    
    search_btn.click(
        fn=search_documents_action,
        inputs=[query_input],
        outputs=[search_output]
    )
    
    # Quick action handlers
    def quick_analysis_handler(analysis_type: str):
        def handler():
            return (
                analysis_type,
                f"Analyse rapide {analysis_type} sur les documents disponibles",
                "🔄 Analyse rapide en cours..."
            )
        return handler
    
    quick_executive.click(
        fn=quick_analysis_handler("🎯 Synthèse Exécutive"),
        outputs=[analysis_dropdown, query_input, status_output]
    )
    
    quick_risk.click(
        fn=quick_analysis_handler("⚠️ Analyse des Risques"),
        outputs=[analysis_dropdown, query_input, status_output]
    )
    
    quick_market.click(
        fn=quick_analysis_handler("📊 Étude de Marché"),
        outputs=[analysis_dropdown, query_input, status_output]
    )
    
    quick_tech.click(
        fn=quick_analysis_handler("🔬 Veille Technologique"),
        outputs=[analysis_dropdown, query_input, status_output]
    )

def create_dashboard_tab():
    """Create the dashboard tab with charts and metrics"""
    
    with gr.Row():
        with gr.Column():
            # Market trend chart
            market_chart = gr.Plot(
                dashboard.create_market_trend_chart(),
                elem_classes=["chart-container"]
            )
        
        with gr.Column():
            # Analysis distribution chart  
            distribution_chart = gr.Plot(
                dashboard.create_analysis_distribution_chart(),
                elem_classes=["chart-container"]
            )
    
    with gr.Row():
        with gr.Column():
            # Performance metrics chart
            performance_chart = gr.Plot(
                dashboard.create_performance_metrics_chart(),
                elem_classes=["chart-container"]
            )
        
        with gr.Column():
            # Recent documents
            documents = dashboard.get_recent_documents()
            docs_html = "<h3 style='color: #00d4aa;'>📚 Documents Récents</h3>"
            
            for doc in documents[:5]:
                status_color = "#32d74b" if doc["status"] == "Analysé" else "#ff9f0a"
                docs_html += f"""
                <div class="metric-card" style="margin: 10px 0; padding: 15px;">
                    <div style="font-weight: 600; color: #ffffff;">{doc['title']}</div>
                    <div style="font-size: 12px; color: #a0a0a0; margin: 5px 0;">
                        📅 {doc['upload_date']} | 📄 {doc['pages']} pages
                    </div>
                    <div style="font-size: 12px;">
                        <span style="color: {status_color};">● {doc['status']}</span>
                    </div>
                </div>
                """
            
            gr.HTML(docs_html)

def main():
    """Main application entry point"""
    
    # Custom CSS
    custom_css = load_custom_css()
    
    # Create Gradio interface
    with gr.Blocks(
        theme=gr.themes.Base(),
        css=custom_css,
        title="Insight MVP - Intelligence Stratégique",
        analytics_enabled=False
    ) as app:
        
        # Header
        create_header()
        
        # Metrics cards
        create_metrics_cards()
        
        # Main tabs
        with gr.Tabs():
            
            with gr.Tab("🤖 Analyses IA", elem_id="analysis-tab"):
                create_analysis_interface()
            
            with gr.Tab("📊 Dashboard", elem_id="dashboard-tab"):
                create_dashboard_tab()
            
            with gr.Tab("📚 Documents", elem_id="documents-tab"):
                with gr.Row():
                    with gr.Column():
                        gr.HTML("<h3 style='color: #00d4aa;'>📄 Gestion des Documents</h3>")
                        
                        upload_area = gr.File(
                            label="Uploader des PDFs",
                            file_count="multiple",
                            file_types=[".pdf"],
                            elem_classes=["upload-area"]
                        )
                        
                        upload_btn = gr.Button("📤 Traiter les Documents", variant="primary")
                        
                        upload_status = gr.Markdown("Prêt à recevoir des documents...")
                    
                    with gr.Column():
                        # Document list would go here
                        gr.HTML("""
                        <div class="metric-card">
                            <h4 style="color: #00d4aa;">📈 Statistiques</h4>
                            <div style="margin: 10px 0;">
                                <div>Documents traités: <strong>87</strong></div>
                                <div>Analyses effectuées: <strong>156</strong></div>
                                <div>Rapports générés: <strong>43</strong></div>
                            </div>
                        </div>
                        """)
    
    return app

if __name__ == "__main__":
    logger.info("Starting Insight MVP Frontend...")
    
    app = main()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True,
        quiet=False
    )
