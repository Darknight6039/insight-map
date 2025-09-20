"""
Insight MVP - Minimal Gradio Interface
Ultra-simplified version without API schema issues
"""

import gradio as gr
import requests
import json
import os
from datetime import datetime

# Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://gateway-api:8000")

# Simple analysis function
def simple_analysis(analysis_type, query_text):
    """Simple analysis without complex types"""
    if not query_text or not query_text.strip():
        return "❌ Veuillez saisir une requête d'analyse."
    
    try:
        # Map analysis types to endpoints  
        endpoints = {
            "Synthèse Exécutive": "/analysis/synthesize",
            "Analyse Concurrentielle": "/analysis/analyze-competition",
            "Veille Technologique": "/analysis/tech-watch",
            "Analyse des Risques": "/analysis/risk-analysis",
            "Étude de Marché": "/analysis/market-study"
        }
        
        endpoint = endpoints.get(analysis_type, "/analysis/synthesize")
        
        payload = {
            "query": query_text,
            "title": f"{analysis_type} - {datetime.now().strftime('%H:%M')}",
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
            return f"✅ **{analysis_type} terminée**\n\n{content}"
        else:
            return f"❌ Erreur API ({response.status_code}): {response.text[:200]}..."
            
    except requests.exceptions.ConnectionError:
        return "❌ Backend non accessible. Vérifiez que les services sont démarrés."
    except Exception as e:
        return f"❌ Erreur: {str(e)}"

def simple_search(search_query):
    """Simple search function"""
    if not search_query or not search_query.strip():
        return "❌ Veuillez saisir une requête de recherche."
    
    try:
        response = requests.post(
            f"{GATEWAY_URL}/search",
            json={"query": search_query, "top_k": 3},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                return "🔍 Aucun résultat trouvé."
            
            output = f"🔍 **Résultats pour:** '{search_query}'\n\n"
            for i, doc in enumerate(results, 1):
                title = doc.get('title', 'Document sans titre')
                score = doc.get('score', 0)
                text = doc.get('text', '')[:100]
                output += f"**{i}. {title}**\nScore: {score:.3f}\nExtrait: {text}...\n\n"
            
            return output
        else:
            return f"❌ Erreur recherche ({response.status_code})"
            
    except Exception as e:
        return f"❌ Erreur: {str(e)}"

# Custom CSS - simplified
css = """
body, .gradio-container {
    background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%) !important;
    color: #ffffff !important;
    font-family: -apple-system, sans-serif !important;
}
.block {
    background: #1c1c1c !important;
    border: 1px solid #3d3d3d !important;
    border-radius: 8px !important;
}
"""

# Create interface
def create_interface():
    with gr.Blocks(css=css, title="Insight MVP", analytics_enabled=False) as demo:
        
        # Header
        gr.HTML("""
            <div style="text-align: center; padding: 20px; background: #1c1c1c; border-radius: 12px; margin-bottom: 20px;">
                <h1 style="color: #00d4aa; font-size: 28px; margin-bottom: 10px;">
                    🤖 Insight MVP - Intelligence Stratégique
                </h1>
                <p style="color: #a0a0a0; font-size: 16px;">
                    Plateforme d'analyse IA avec 5 types d'analyses spécialisées
                </p>
            </div>
        """)
        
        # Metrics
        gr.HTML("""
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                <div style="background: #1c1c1c; padding: 20px; border-radius: 12px; border: 1px solid #3d3d3d;">
                    <div style="font-size: 32px; font-weight: 700; color: #00d4aa;">98%</div>
                    <div style="font-size: 14px; color: #a0a0a0;">● Uptime</div>
                </div>
                <div style="background: #1c1c1c; padding: 20px; border-radius: 12px; border: 1px solid #3d3d3d;">
                    <div style="font-size: 32px; font-weight: 700; color: #00d4aa;">2.3s</div>
                    <div style="font-size: 14px; color: #a0a0a0;">● Avg Response</div>
                </div>
                <div style="background: #1c1c1c; padding: 20px; border-radius: 12px; border: 1px solid #3d3d3d;">
                    <div style="font-size: 32px; font-weight: 700; color: #00d4aa;">72</div>
                    <div style="font-size: 14px; color: #a0a0a0;">● Indicators</div>
                </div>
                <div style="background: #1c1c1c; padding: 20px; border-radius: 12px; border: 1px solid #3d3d3d;">
                    <div style="font-size: 32px; font-weight: 700; color: #00d4aa;">$204.61</div>
                    <div style="font-size: 14px; color: #a0a0a0;">● AI Prediction (AAPL)</div>
                </div>
            </div>
        """)
        
        with gr.Tab("🤖 Analyses IA"):
            with gr.Row():
                with gr.Column():
                    gr.HTML("<h3 style='color: #00d4aa;'>🤖 Sélection d'Analyse</h3>")
                    
                    analysis_type = gr.Dropdown(
                        choices=[
                            "Synthèse Exécutive",
                            "Analyse Concurrentielle", 
                            "Veille Technologique",
                            "Analyse des Risques",
                            "Étude de Marché"
                        ],
                        label="Type d'Analyse",
                        value="Synthèse Exécutive"
                    )
                    
                    query_text = gr.Textbox(
                        label="Requête d'Analyse",
                        placeholder="Ex: Analysez les tendances du secteur bancaire français...",
                        lines=3
                    )
                    
                    analyze_btn = gr.Button("🚀 Lancer l'Analyse", variant="primary")
                    search_btn = gr.Button("🔍 Rechercher Documents", variant="secondary")
                
                with gr.Column():
                    gr.HTML("<h3 style='color: #00d4aa;'>⚡ Actions Rapides</h3>")
                    
                    quick_exec_btn = gr.Button("🎯 Synthèse Express")
                    quick_risk_btn = gr.Button("⚠️ Analyse Risques")
                    quick_market_btn = gr.Button("📊 Étude Marché") 
                    quick_tech_btn = gr.Button("🔬 Veille Tech")
            
            # Results
            with gr.Row():
                results_output = gr.Markdown("🟢 **Système prêt** - Sélectionnez un type d'analyse")
        
        with gr.Tab("📊 Dashboard"):
            gr.HTML("""
                <div style="background: #1c1c1c; padding: 20px; border-radius: 12px; margin: 20px 0;">
                    <h3 style="color: #00d4aa;">📈 Tendances Marché</h3>
                    <div style="height: 300px; background: #2d2d2d; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                        <div style="color: #a0a0a0;">Graphique des tendances financières</div>
                    </div>
                </div>
                
                <div style="background: #1c1c1c; padding: 20px; border-radius: 12px;">
                    <h3 style="color: #00d4aa;">📚 Documents Récents</h3>
                    <div style="margin: 10px 0;">
                        <div style="padding: 10px; border-left: 3px solid #32d74b; margin: 10px 0;">
                            <strong>Étude Crédit Agricole 2025</strong><br>
                            📅 2025-09-20 | 📄 45 pages | <span style="color: #32d74b;">● Analysé</span>
                        </div>
                        <div style="padding: 10px; border-left: 3px solid #ff9f0a; margin: 10px 0;">
                            <strong>Rapport BNP Paribas Q3</strong><br>
                            📅 2025-09-19 | 📄 32 pages | <span style="color: #ff9f0a;">● En cours</span>
                        </div>
                        <div style="padding: 10px; border-left: 3px solid #32d74b; margin: 10px 0;">
                            <strong>Analyse Secteur Assurance</strong><br>
                            📅 2025-09-18 | 📄 67 pages | <span style="color: #32d74b;">● Analysé</span>
                        </div>
                    </div>
                </div>
            """)
        
        # Event handlers - simplified
        analyze_btn.click(
            fn=simple_analysis,
            inputs=[analysis_type, query_text],
            outputs=results_output
        )
        
        search_btn.click(
            fn=simple_search,
            inputs=query_text,
            outputs=results_output
        )
        
        # Quick buttons
        quick_exec_btn.click(
            lambda: ("Synthèse Exécutive", "Analyse rapide du secteur financier français"),
            outputs=[analysis_type, query_text]
        )
        
        quick_risk_btn.click(
            lambda: ("Analyse des Risques", "Évaluation des risques dans le secteur bancaire"),
            outputs=[analysis_type, query_text]
        )
        
        quick_market_btn.click(
            lambda: ("Étude de Marché", "Analyse du marché des services financiers"),
            outputs=[analysis_type, query_text]
        )
        
        quick_tech_btn.click(
            lambda: ("Veille Technologique", "Innovations technologiques dans la finance"),
            outputs=[analysis_type, query_text]
        )
    
    return demo

if __name__ == "__main__":
    print("🚀 Starting Insight MVP - Minimal Interface...")
    
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        share=False
    )
