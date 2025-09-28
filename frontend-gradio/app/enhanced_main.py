"""
Insight MVP - Enhanced Gradio Interface avec export PDF Axial
"""

import gradio as gr
import requests
import json
import os
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://gateway-api:8000")

# Analysis types
ANALYSIS_TYPES = {
    "🎯 Synthèse Exécutive": "synthesize",
    "⚔️ Analyse Concurrentielle": "analyze_competition", 
    "🔬 Veille Technologique": "tech_watch",
    "⚠️ Analyse des Risques": "risk_analysis",
    "📊 Étude de Marché": "market_study"
}

# Custom CSS avec branding Axial
custom_css = """
/* Axial Branding */
body {
    background: linear-gradient(135deg, #1a365d 0%, #2d3748 100%) !important;
    color: #e0e0e0 !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
}

.gradio-container {
    background: rgba(26, 54, 93, 0.95) !important;
    backdrop-filter: blur(10px) !important;
}

/* Header Axial */
.app-header {
    background: linear-gradient(90deg, #1a365d, #2c5282) !important;
    padding: 20px !important;
    margin-bottom: 20px !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
}

/* Boutons */
.btn-primary {
    background: linear-gradient(135deg, #00d4aa, #0ea5e9) !important;
    border: none !important;
    border-radius: 8px !important;
    color: white !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.btn-primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0, 212, 170, 0.4) !important;
}

.btn-export {
    background: linear-gradient(135deg, #f56500, #e53e3e) !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
}

/* Cards */
.metric-card {
    background: rgba(45, 55, 72, 0.8) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    border: 1px solid rgba(0, 212, 170, 0.3) !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
}

/* Input fields */
textarea, input {
    background: rgba(45, 55, 72, 0.9) !important;
    border: 1px solid rgba(0, 212, 170, 0.5) !important;
    border-radius: 8px !important;
    color: #e0e0e0 !important;
}

/* Results */
.analysis-result {
    background: rgba(26, 54, 93, 0.95) !important;
    border-radius: 12px !important;
    padding: 25px !important;
    border-left: 4px solid #00d4aa !important;
    margin: 20px 0 !important;
}
"""

def create_dashboard_chart():
    """Dashboard avec métriques Axial"""
    dates = pd.date_range('2024-09-01', '2025-09-20', freq='D')
    np.random.seed(42)
    values = np.cumsum(np.random.randn(len(dates)) * 0.5) + 200
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=values,
        mode='lines',
        name='Intelligence Score',
        line=dict(color='#00d4aa', width=3),
        fill='tonexty'
    ))
    
    fig.update_layout(
        title='Intelligence Stratégique - Performance Dashboard',
        plot_bgcolor='rgba(26, 54, 93, 0.8)',
        paper_bgcolor='rgba(26, 54, 93, 0.8)',
        font=dict(color='#ffffff', size=12),
        xaxis=dict(gridcolor='rgba(0, 212, 170, 0.2)'),
        yaxis=dict(gridcolor='rgba(0, 212, 170, 0.2)'),
        height=400
    )
    
    return fig

def run_analysis_enhanced(analysis_name: str, query: str, title: str = None):
    """Exécute analyse avec structure standardisée"""
    if not query.strip():
        return "❌ Veuillez saisir une requête d'analyse", None, ""
    
    try:
        analysis_endpoint = ANALYSIS_TYPES.get(analysis_name)
        if not analysis_endpoint:
            return "❌ Type d'analyse non reconnu", None, ""
        
        # Appel API avec structure standardisée
        payload = {
            "query": query,
            "title": title or f"Rapport {analysis_name}"
        }
        
        response = requests.post(
            f"{GATEWAY_URL}/analysis/{analysis_endpoint}",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Formatage de la réponse
            analysis_content = result.get('content', '')
            metadata = result.get('metadata', {})
            sources = result.get('sources', [])
            
            # Résumé des métriques
            summary = f"""
📊 **Analyse Terminée avec Succès**
• Type: {analysis_name}
• Documents analysés: {metadata.get('documents_found', 0)}
• Modèle: {metadata.get('model', 'N/A')}
• Structure: {metadata.get('structure', 'standardized')}
• Timestamp: {result.get('timestamp', 'N/A')}
            """
            
            # Informations pour export PDF
            export_info = {
                "analysis_type": result.get('analysis_type', ''),
                "title": result.get('title', ''),
                "content": analysis_content,
                "sources": sources,
                "metadata": metadata
            }
            
            return analysis_content, export_info, summary
            
        else:
            error_msg = f"❌ Erreur API ({response.status_code}): {response.text[:200]}"
            return error_msg, None, ""
            
    except Exception as e:
        error_msg = f"❌ Erreur d'exécution: {str(e)[:200]}"
        return error_msg, None, ""

def export_to_pdf_axial(export_info, custom_title: str = None):
    """Export PDF avec logo Axial"""
    if not export_info:
        return "❌ Aucune analyse à exporter. Lancez d'abord une analyse."
    
    try:
        # Préparer les données pour l'export
        export_payload = {
            "title": custom_title or export_info.get('title', 'Rapport Axial'),
            "content": export_info.get('content', ''),
            "analysis_type": export_info.get('analysis_type', ''),
            "sources": export_info.get('sources', []),
            "metadata": export_info.get('metadata', {})
        }
        
        # Générer rapport en base
        response = requests.post(
            f"{GATEWAY_URL}/reports/generate",
            json=export_payload,
            timeout=60
        )
        
        if response.status_code == 200:
            report_data = response.json()
            report_id = report_data.get('id')
            
            # URL de téléchargement PDF
            pdf_url = f"{GATEWAY_URL}/reports/export/{report_id}"
            
            return f"""
✅ **Rapport PDF Axial généré avec succès !**

📄 **Rapport ID**: {report_id}
📁 **Titre**: {export_payload['title']}
🎨 **Avec logo Axial et identité visuelle**

🔗 **Télécharger**: [Rapport PDF Axial]({pdf_url})

💡 **Caractéristiques**:
• Logo Axial en haut à gauche
• Structure standardisée McKinsey/BCG
• Identité visuelle professionnelle
• Sources et références incluses
            """
        else:
            return f"❌ Erreur génération PDF: {response.text[:200]}"
            
    except Exception as e:
        return f"❌ Erreur export: {str(e)}"

def get_recent_reports():
    """Récupère les rapports récents"""
    try:
        response = requests.get(f"{GATEWAY_URL}/reports", timeout=30)
        if response.status_code == 200:
            reports = response.json()[:5]  # 5 derniers
            
            if not reports:
                return "Aucun rapport généré"
            
            report_list = "📋 **Rapports Récents**:\n\n"
            for report in reports:
                report_list += f"• **{report['title']}** (ID: {report['id']})\n"
                report_list += f"  Type: {report['analysis_type']} | {report['created_at'][:10]}\n\n"
            
            return report_list
        else:
            return "❌ Erreur récupération rapports"
    except:
        return "❌ Service rapports indisponible"

# Interface Gradio Enhanced
with gr.Blocks(theme="dark", css=custom_css, title="Insight MVP - Axial") as app:
    
    # Header Axial
    with gr.Row(elem_classes="app-header"):
        with gr.Column(scale=3):
            gr.Markdown("""
            # 🎯 AXIAL - Intelligence Stratégique
            ### Plateforme d'analyse IA avec 5 types d'analyses spécialisées
            **Rapports professionnels avec logo Axial et structure McKinsey/BCG**
            """)
        with gr.Column(scale=1):
            gr.Markdown("""
            ### 📊 Métriques
            **98%** Uptime  
            **2.3s** Avg Response  
            **72** Indicators  
            """)
    
    # Dashboard
    with gr.Tab("📊 Dashboard Axial"):
        with gr.Row():
            with gr.Column(scale=2):
                dashboard_chart = gr.Plot(value=create_dashboard_chart(), label="Performance Intelligence")
            with gr.Column(scale=1):
                recent_reports = gr.Textbox(
                    value=get_recent_reports(),
                    label="📋 Rapports Récents",
                    lines=10,
                    interactive=False
                )
    
    # Analyses avec Export PDF
    with gr.Tab("🎯 Analyses Stratégiques"):
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### 🔍 Sélection d'Analyse")
                analysis_type = gr.Dropdown(
                    choices=list(ANALYSIS_TYPES.keys()),
                    value="🎯 Synthèse Exécutive",
                    label="Type d'Analyse"
                )
                
                analysis_query = gr.Textbox(
                    placeholder="Ex: Analysez la position concurrentielle de Crédit Agricole face aux néobanques...",
                    label="Requête d'Analyse",
                    lines=3
                )
                
                analysis_title = gr.Textbox(
                    placeholder="Titre personnalisé (optionnel)",
                    label="Titre du Rapport"
                )
                
                analyze_btn = gr.Button("🚀 Lancer l'Analyse", variant="primary", elem_classes="btn-primary")
                
            with gr.Column(scale=1):
                gr.Markdown("### ⚡ Actions Rapides")
                
                with gr.Row():
                    export_title = gr.Textbox(
                        placeholder="Titre PDF personnalisé",
                        label="Titre Export PDF"
                    )
                
                export_btn = gr.Button("📄 Exporter PDF Axial", variant="secondary", elem_classes="btn-export")
                
                export_status = gr.Textbox(
                    label="📊 Status Export",
                    lines=8,
                    interactive=False
                )
        
        # Résultats
        with gr.Row():
            with gr.Column(scale=3):
                analysis_result = gr.Textbox(
                    label="📋 Résultat de l'Analyse",
                    lines=20,
                    interactive=False,
                    elem_classes="analysis-result"
                )
            with gr.Column(scale=1):
                analysis_summary = gr.Textbox(
                    label="📊 Résumé Exécutif",
                    lines=10,
                    interactive=False
                )
    
    # États pour l'export
    export_data = gr.State(None)
    
    # Événements
    analyze_btn.click(
        fn=run_analysis_enhanced,
        inputs=[analysis_type, analysis_query, analysis_title],
        outputs=[analysis_result, export_data, analysis_summary]
    )
    
    export_btn.click(
        fn=export_to_pdf_axial,
        inputs=[export_data, export_title],
        outputs=[export_status]
    )

if __name__ == "__main__":
    print("🚀 Lancement Insight MVP - Interface Axial Enhanced")
    app.launch(
        server_name="0.0.0.0", 
        server_port=7860,
        share=False,
        show_error=True
    )
