"""
RAG Service for Insight MVP - Simplified version with direct analysis
Handles AI analysis without vector service dependency for testing
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import sys
from datetime import datetime
from loguru import logger

# Add prompts to path
sys.path.append("/app")

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="RAG Service", description="Retrieval Augmented Generation for analysis")

# Pydantic models
class AnalysisPayload(BaseModel):
    query: str
    title: Optional[str] = None
    top_k: Optional[int] = 8
    context_override: Optional[str] = None

class AnalysisResponse(BaseModel):
    analysis_type: str
    title: str
    content: str
    sources: List[Dict]
    metadata: Dict
    timestamp: str

def call_openai_simple(prompt: str, analysis_type: str = "general") -> str:
    """Call OpenAI API with error handling"""
    try:
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
            return generate_fallback_analysis(analysis_type, prompt)
        
        # Try OpenAI import
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
        except Exception as e:
            logger.warning(f"OpenAI import failed: {e}")
            return generate_fallback_analysis(analysis_type, prompt)
        
        # System prompts based on analysis type
        system_prompts = {
            "synthese_executive": "Tu es un consultant senior expert en synthèse stratégique. Génère des recommandations exécutives claires et actionnables.",
            "analyse_concurrentielle": "Tu es un expert en intelligence concurrentielle. Analyse les forces et faiblesses des acteurs du marché.",
            "veille_technologique": "Tu es un expert en innovation technologique. Identifie les tendances et disruptions émergentes.",
            "analyse_risques": "Tu es un expert en gestion des risques. Évalue les menaces et propose des stratégies de mitigation.",
            "etude_marche": "Tu es un expert en analyse de marché. Fournis des insights sur la taille, la croissance et les opportunités."
        }
        
        system_prompt = system_prompts.get(analysis_type, "Tu es un consultant expert en analyse stratégique.")
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500,
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error calling OpenAI: {e}")
        return generate_fallback_analysis(analysis_type, prompt)

def generate_fallback_analysis(analysis_type: str, query: str) -> str:
    """Generate fallback analysis when OpenAI is not available"""
    
    fallback_templates = {
        "synthese_executive": f"""
**SYNTHÈSE EXÉCUTIVE - {query}**

**POINTS CLÉS STRATÉGIQUES:**
• Position concurrentielle forte mais défis émergents à surveiller
• Opportunités de croissance identifiées dans les segments premium
• Nécessité d'adaptation aux nouvelles réglementations sectorielles

**RECOMMANDATIONS IMMÉDIATES:**
• Renforcer la présence digitale et l'expérience client
• Diversifier les sources de revenus pour réduire les risques
• Investir dans l'innovation et les partenariats stratégiques

**MÉTRIQUES CLÉS À SUIVRE:**
• Taux de croissance du CA, part de marché, satisfaction client
• Coût d'acquisition client et lifetime value
• Indicateurs de performance opérationnelle

*Note: Analyse générée en mode dégradé - Configurez la clé OpenAI pour des insights personnalisés.*
        """,
        
        "analyse_concurrentielle": f"""
**ANALYSE CONCURRENTIELLE - {query}**

**PAYSAGE CONCURRENTIEL:**
• Marché mature avec quelques acteurs dominants
• Émergence de nouveaux entrants disruptifs
• Consolidation en cours dans certains segments

**FORCES ET FAIBLESSES:**
• Leaders: Innovation, marque, distribution
• Challengers: Agilité, prix, niches spécialisées
• Nouveaux entrants: Technologies, modèles économiques

**OPPORTUNITÉS DE DIFFÉRENCIATION:**
• Service client personnalisé
• Innovation produit/service
• Partenariats stratégiques

*Note: Analyse générée en mode dégradé - Configurez la clé OpenAI pour une analyse concurrentielle détaillée.*
        """,
        
        "veille_technologique": f"""
**VEILLE TECHNOLOGIQUE - {query}**

**TENDANCES ÉMERGENTES:**
• Intelligence artificielle et automatisation
• Technologies cloud et edge computing
• Blockchain et technologies décentralisées

**INNOVATIONS DISRUPTIVES:**
• Nouvelles interfaces utilisateur (AR/VR)
• IoT et capteurs intelligents
• Technologies vertes et durables

**IMPACT SECTORIEL:**
• Transformation des processus métier
• Nouveaux modèles économiques
• Évolution des attentes clients

*Note: Analyse générée en mode dégradé - Configurez la clé OpenAI pour une veille technologique personnalisée.*
        """,
        
        "analyse_risques": f"""
**ANALYSE DES RISQUES - {query}**

**RISQUES STRATÉGIQUES:**
• Évolution réglementaire et compliance
• Disruption technologique
• Changements de comportement consommateur

**RISQUES OPÉRATIONNELS:**
• Cybersécurité et protection des données
• Chaîne d'approvisionnement
• Ressources humaines et compétences

**MESURES DE MITIGATION:**
• Diversification et plans de contingence
• Investissement en sécurité et formation
• Monitoring continu des indicateurs de risque

*Note: Analyse générée en mode dégradé - Configurez la clé OpenAI pour une analyse de risques approfondie.*
        """,
        
        "etude_marche": f"""
**ÉTUDE DE MARCHÉ - {query}**

**TAILLE ET CROISSANCE:**
• Marché en expansion avec croissance annuelle estimée à 8-12%
• Segments porteurs: digital, premium, services
• Géographie: concentration urbaine, expansion internationale

**DYNAMIQUES SECTORIELLES:**
• Consolidation des acteurs traditionnels
• Émergence de nouveaux modèles économiques
• Importance croissante de la durabilité

**OPPORTUNITÉS D'INVESTISSEMENT:**
• Innovation produit et service
• Expansion géographique
• Acquisitions stratégiques

*Note: Analyse générée en mode dégradé - Configurez la clé OpenAI pour une étude de marché détaillée.*
        """
    }
    
    return fallback_templates.get(analysis_type, f"Analyse de base pour: {query}")

def build_analysis_prompt(analysis_type: str, query: str, context: str = None) -> str:
    """Build prompt for analysis"""
    
    base_context = context or f"Contexte d'analyse pour: {query}"
    
    prompt_templates = {
        "synthese_executive": f"""
Analyse le contexte suivant et génère une synthèse exécutive structurée:

CONTEXTE: {base_context}

REQUÊTE: {query}

Produis une synthèse exécutive avec:
- Résumé des points clés (3-4 points)
- Opportunités prioritaires (2-3 items)
- Risques principaux (2-3 items)
- Recommandations actionnables (3-5 actions)
- Métriques de suivi importantes
        """,
        
        "analyse_concurrentielle": f"""
Analyse concurrentielle basée sur:

CONTEXTE: {base_context}

REQUÊTE: {query}

Fournis:
- Mapping des acteurs principaux
- Forces/faiblesses de chaque segment
- Positionnement concurrentiel
- Opportunités de différenciation
- Menaces concurrentielles
        """,
        
        "veille_technologique": f"""
Veille technologique pour:

CONTEXTE: {base_context}

REQUÊTE: {query}

Identifie:
- Technologies émergentes pertinentes
- Innovations disruptives potentielles
- Impact sur le secteur
- Opportunités d'adoption
- Risques de disruption
        """,
        
        "analyse_risques": f"""
Analyse des risques pour:

CONTEXTE: {base_context}

REQUÊTE: {query}

Évalue:
- Risques stratégiques et opérationnels
- Probabilité et impact de chaque risque
- Facteurs déclencheurs à surveiller
- Mesures de mitigation recommandées
- Plan de contingence
        """,
        
        "etude_marche": f"""
Étude de marché complète:

CONTEXTE: {base_context}

REQUÊTE: {query}

Analyse:
- Taille et croissance du marché
- Segmentation et dynamiques
- Tendances et facteurs de croissance
- Barrières à l'entrée et opportunités
- Projections et recommandations
        """
    }
    
    return prompt_templates.get(analysis_type, f"Analyse générale pour: {query}")

async def perform_analysis(analysis_type: str, payload: AnalysisPayload) -> AnalysisResponse:
    """Perform analysis with simplified logic"""
    try:
        # Build prompt
        context = payload.context_override or "Contexte d'analyse général"
        prompt = build_analysis_prompt(analysis_type, payload.query, context)
        
        # Call OpenAI or fallback
        content = call_openai_simple(prompt, analysis_type)
        
        # Build response
        return AnalysisResponse(
            analysis_type=analysis_type,
            title=payload.title or f"Analyse {analysis_type}",
            content=content,
            sources=[],
            metadata={
                "query": payload.query,
                "passages_count": 0,
                "top_k": payload.top_k or 8,
                "used_context_override": bool(payload.context_override)
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in {analysis_type} analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "rag-service"}

# Analysis endpoints
@app.post("/synthesize", response_model=AnalysisResponse)
async def synthesize(payload: AnalysisPayload):
    """PROMPT 1: Génère une synthèse exécutive stratégique"""
    return await perform_analysis("synthese_executive", payload)

@app.post("/analyze_competition", response_model=AnalysisResponse)
async def analyze_competition(payload: AnalysisPayload):
    """PROMPT 2: Analyse concurrentielle et mapping du marché"""
    return await perform_analysis("analyse_concurrentielle", payload)

@app.post("/tech_watch", response_model=AnalysisResponse)
async def tech_watch(payload: AnalysisPayload):
    """PROMPT 3: Veille technologique et innovation"""
    return await perform_analysis("veille_technologique", payload)

@app.post("/risk_analysis", response_model=AnalysisResponse)
async def risk_analysis(payload: AnalysisPayload):
    """PROMPT 4: Analyse des risques méthodique"""
    return await perform_analysis("analyse_risques", payload)

@app.post("/market_study", response_model=AnalysisResponse)
async def market_study(payload: AnalysisPayload):
    """PROMPT 5: Étude de marché complète"""
    return await perform_analysis("etude_marche", payload)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
