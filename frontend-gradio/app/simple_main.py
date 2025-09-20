"""
Insight MVP - Simple Gradio Interface
Simplified version to ensure functionality
"""

import gradio as gr
import requests
import json
import os
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://gateway-api:8000")

# Analysis types
ANALYSIS_TYPES = {
    "🎯 Synthèse Exécutive": "synthese_executive",
    "⚔️ Analyse Concurrentielle": "analyse_concurrentielle", 
    "🔬 Veille Technologique": "veille_technologique",
    "⚠️ Analyse des Risques": "analyse_risques",
    "📊 Étude de Marché": "etude_marche"
}

def create_market_chart():
    """Create market trend chart"""
    dates = pd.date_range('2024-09-01', '2025-09-20', freq='D')
    np.random.seed(42)
    prices = np.cumsum(np.random.randn(len(dates)) * 0.5) + 200
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=prices,
        mode='lines',
        name='Market Trend',
        line=dict(color='#00d4aa', width=2)
    ))
    
    fig.update_layout(
        title='Market Trends - Financial Sector',
        plot_bgcolor='#1c1c1c',
        paper_bgcolor='#1c1c1c',
        font=dict(color='#ffffff'),
        xaxis=dict(gridcolor='#3d3d3d'),
        yaxis=dict(gridcolor='#3d3d3d')
    )
    
    return fig

def run_analysis(analysis_type, query, file_upload):
    """Run analysis with backend API"""
    try:
        if not query.strip():
            return "❌ Veuillez saisir une requête", ""
        
        analysis_key = ANALYSIS_TYPES.get(analysis_type)
        if not analysis_key:
            return "❌ Type d'analyse invalide", ""
        
        # Map to API endpoints
        endpoints = {
            "synthese_executive": "/analysis/synthesize",
            "analyse_concurrentielle": "/analysis/analyze-competition",
            "veille_technologique": "/analysis/tech-watch", 
            "analyse_risques": "/analysis/risk-analysis",
            "etude_marche": "/analysis/market-study"
        }
        
        endpoint = endpoints.get(analysis_key, "/analysis/synthesize")
        
        payload = {
            "query": query,
            "title": f"{analysis_type} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "top_k": 5
        }
        
        response = requests.post(
            f"{GATEWAY_URL}{endpoint}",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get('content', 'Aucun contenu généré')
            
            status = f"✅ **Analyse {analysis_type} terminée**\n\nType: {data.get('analysis_type', 'N/A')}"
            return status, content
        else:
            return f"❌ Erreur API: {response.status_code}", f"Erreur: {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Impossible de connecter au backend", "Vérifiez que les services sont démarrés"
    except Exception as e:
        return f"❌ Erreur: {str(e)}", ""

def search_documents(query):
    """Search in documents"""
    try:
        if not query.strip():
            return "❌ Veuillez saisir une requête de recherche"
        
        response = requests.post(
            f"{GATEWAY_URL}/search",
            json={"query": query, "top_k": 5},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                return "🔍 Aucun résultat trouvé"
            
            output = f"🔍 **Résultats pour:** '{query}'\n\n"
            for i, doc in enumerate(results[:3], 1):
                output += f"**{i}. {doc.get('title', 'Document')}**\n"
                output += f"Score: {doc.get('score', 0):.3f}\n"
                output += f"Extrait: {doc.get('text', '')[:150]}...\n\n"
            
            return output
        else:
            return f"❌ Erreur recherche: {response.status_code}"
            
    except Exception as e:
        return f"❌ Erreur: {str(e)}"

def get_system_status():
    """Get system status"""
    try:
        response = requests.get(f"{GATEWAY_URL}/status", timeout=10)
        if response.status_code == 200:
            return "🟢 Système opérationnel"
        else:
            return f"🟡 Statut: {response.status_code}"
    except:
        return "🔴 Backend non accessible"

# Custom CSS
custom_css = """
/* Dark theme styling */
.gradio-container {
    background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%) !important;
    color: #ffffff !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

.metric-card {
    background: #1c1c1c !important;
    border: 1px solid #3d3d3d !important;
    border-radius: 12px !important;
    padding: 20px !important;
    margin: 10px !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2) !important;
}

.metric-value {
    font-size: 32px !important;
    font-weight: 700 !important;
    color: #00d4aa !important;
}

.metric-label {
    font-size: 14px !important;
    color: #a0a0a0 !important;
    margin-top: 5px !important;
}

.analysis-btn {
    background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%) !important;
    border: none !important;
    border-radius: 8px !important;
    color: white !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}
"""

# Main interface
with gr.Blocks(theme="dark", css=custom_css, title="Insight MVP") as app:
    
    # Header
    gr.HTML("""
        <div style="text-align: center; padding: 20px; background: #1c1c1c; border-radius: 12px; margin-bottom: 20px;">
            <h1 style="color: #00d4aa; font-size: 28px; margin-bottom: 10px;">
                🤖 Insight MVP - Intelligence Stratégique
            </h1>
            <p style="color: #a0a0a0; font-size: 16px;">
                Plateforme d'analyse IA avec 5 types d'analyses spécialisées | 
                <span style="color: #32d74b;">● Système opérationnel</span>
            </p>
        </div>
    """)
    
    # Metrics
    gr.HTML("""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
            <div class="metric-card">
                <div class="metric-value">98%</div>
                <div class="metric-label">● Uptime</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">2.3s</div>
                <div class="metric-label">● Avg Response</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">72</div>
                <div class="metric-label">● Indicators</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">$204.61</div>
                <div class="metric-label">● AI Prediction (AAPL)</div>
                <div style="font-size: 12px; color: #a0a0a0;">SELL | Confidence: Low (37%)</div>
            </div>
        </div>
    """)
    
    # Main interface
    with gr.Tabs():
        with gr.Tab("🤖 Analyses IA"):
            with gr.Row():
                with gr.Column():
                    gr.HTML("<h3 style='color: #00d4aa;'>🤖 Sélection d'Analyse IA</h3>")
                    
                    analysis_dropdown = gr.Dropdown(
                        choices=list(ANALYSIS_TYPES.keys()),
                        label="Type d'Analyse",
                        value=list(ANALYSIS_TYPES.keys())[0]
                    )
                    
                    query_input = gr.Textbox(
                        label="Requête d'Analyse",
                        placeholder="Ex: Analysez les tendances du secteur bancaire français...",
                        lines=3
                    )
                    
                    file_upload = gr.File(
                        label="📄 Document PDF (Optionnel)",
                        file_types=[".pdf"]
                    )
                    
                    with gr.Row():
                        analyze_btn = gr.Button("🚀 Lancer l'Analyse", variant="primary")
                        search_btn = gr.Button("🔍 Rechercher", variant="secondary")
                
                with gr.Column():
                    gr.HTML("<h3 style='color: #00d4aa;'>⚡ Actions Rapides</h3>")
                    
                    quick_executive = gr.Button("🎯 Synthèse Express")
                    quick_risk = gr.Button("⚠️ Analyse Risques") 
                    quick_market = gr.Button("📊 Étude Marché")
                    quick_tech = gr.Button("🔬 Veille Tech")
            
            # Results
            status_output = gr.Markdown("🟢 **Système prêt** - Sélectionnez un type d'analyse")
            analysis_output = gr.Markdown("Les résultats s'afficheront ici...")
            search_output = gr.Markdown("Les résultats de recherche s'afficheront ici...")
        
        with gr.Tab("📊 Dashboard"):
            market_plot = gr.Plot(create_market_chart())
            
            gr.HTML("""
                <div style="background: #1c1c1c; padding: 20px; border-radius: 12px; margin-top: 20px;">
                    <h3 style="color: #00d4aa;">📚 Documents Récents</h3>
                    <div style="margin: 10px 0;">
                        <div style="padding: 10px; border-left: 3px solid #32d74b;">
                            <strong>Étude Crédit Agricole 2025</strong><br>
                            📅 2025-09-20 | 📄 45 pages | <span style="color: #32d74b;">● Analysé</span>
                        </div>
                        <div style="padding: 10px; border-left: 3px solid #ff9f0a; margin-top: 10px;">
                            <strong>Rapport BNP Paribas Q3</strong><br>
                            📅 2025-09-19 | 📄 32 pages | <span style="color: #ff9f0a;">● En cours</span>
                        </div>
                        <div style="padding: 10px; border-left: 3px solid #32d74b; margin-top: 10px;">
                            <strong>Analyse Secteur Assurance</strong><br>
                            📅 2025-09-18 | 📄 67 pages | <span style="color: #32d74b;">● Analysé</span>
                        </div>
                    </div>
                </div>
            """)
    
    # Event handlers
    analyze_btn.click(
        fn=run_analysis,
        inputs=[analysis_dropdown, query_input, file_upload],
        outputs=[status_output, analysis_output]
    )
    
    search_btn.click(
        fn=search_documents,
        inputs=[query_input],
        outputs=[search_output]
    )
    
    # Quick actions
    quick_executive.click(
        lambda: ("🎯 Synthèse Exécutive", "Analyse rapide du secteur financier français"),
        outputs=[analysis_dropdown, query_input]
    )
    
    quick_risk.click(
        lambda: ("⚠️ Analyse des Risques", "Évaluation des risques dans le secteur bancaire"),
        outputs=[analysis_dropdown, query_input]
    )
    
    quick_market.click(
        lambda: ("📊 Étude de Marché", "Analyse du marché des services financiers"),
        outputs=[analysis_dropdown, query_input]
    )
    
    quick_tech.click(
        lambda: ("🔬 Veille Technologique", "Innovations technologiques dans la finance"),
        outputs=[analysis_dropdown, query_input]
    )

if __name__ == "__main__":
    print("🚀 Starting Insight MVP - Simple Interface...")
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
