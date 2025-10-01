"""
RAG Service Final - Version qui fonctionne avec vraie recherche vectorielle et format professionnel
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import requests
from datetime import datetime
from loguru import logger

app = FastAPI(title="RAG Service Final", description="RAG avec recherche vectorielle")

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
VECTOR_SERVICE_URL = "http://vector-service:8002"

# Modèles
class AnalysisRequest(BaseModel):
    query: str
    title: Optional[str] = None

class AnalysisResponse(BaseModel):
    analysis_type: str
    title: str
    content: str
    sources: List[Dict]
    metadata: Dict
    timestamp: str

def search_documents(query: str, top_k: int = 8) -> List[Dict]:
    """Recherche vectorielle avec fallback"""
    try:
        response = requests.post(
            f"{VECTOR_SERVICE_URL}/search",
            json={"query": query, "top_k": top_k},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            # Vector-service returns a list of results; support both list and dict
            if isinstance(result, list):
                return result
            if isinstance(result, dict):
                return result.get("results", result.get("data", []))
            return []
        else:
            logger.warning(f"Vector search failed: {response.status_code}")
            # Retourner une réponse simulée pour continuer le service
            return []
            
    except Exception as e:
        logger.error(f"Vector search error: {e}")
        return []

def create_rag_prompt(analysis_type: str, query: str, documents: List[Dict]) -> str:
    """Crée un prompt avec contexte documentaire"""
    
    # Contexte des documents
    context = ""
    if documents:
        context = "## DOCUMENTS DE RÉFÉRENCE\n\n"
        for i, doc in enumerate(documents[:5], 1):
            doc_text = doc.get('text', '')[:300]
            context += f"**Document {i}** (Score: {doc.get('score', 0):.3f}):\n{doc_text}...\n\n"
    
    # Templates structurés
    templates = {
        "synthese_executive": f"""
Basé sur les documents de référence, génère une SYNTHÈSE EXÉCUTIVE structurée.

{context}

DEMANDE: {query}

FORMAT OBLIGATOIRE:

# SYNTHÈSE EXÉCUTIVE

## 🎯 RÉSUMÉ STRATÉGIQUE
[Points clés avec données chiffrées des documents]

## 💡 INSIGHTS MAJEURS  
[Découvertes importantes des sources]

## ⚡ RECOMMANDATIONS PRIORITAIRES
### Actions immédiates (0-3 mois)
[Actions concrètes avec justifications]

### Initiatives moyen terme (3-12 mois)
[Initiatives stratégiques]

## 📊 MÉTRIQUES CLÉS
[Indicateurs avec benchmarks]

## ⚠️ RISQUES À SURVEILLER
[Points d'attention majeurs]

IMPORTANT: Utilise UNIQUEMENT les informations des documents fournis. Cite [Réf. X] pour chaque donnée.
        """,
        
        "analyse_concurrentielle": f"""
Analyse concurrentielle basée sur les documents de référence.

{context}

DEMANDE: {query}

FORMAT OBLIGATOIRE:

# ANALYSE CONCURRENTIELLE

## 🗺️ CARTOGRAPHIE DU MARCHÉ
[Acteurs et parts de marché des documents]

## ⚔️ FORCES/FAIBLESSES
### Leaders
[Analyse des leaders]

### Challengers  
[Positionnement challengers]

## 📈 DYNAMIQUES MARCHÉ
[Tendances concurrentielles]

## 🎯 OPPORTUNITÉS
[Gaps et recommandations]

Cite systématiquement [Réf. X] pour chaque information.
        """,
        
        "veille_technologique": f"""
Veille technologique basée sur les documents.

{context}

DEMANDE: {query}

FORMAT OBLIGATOIRE:

# VEILLE TECHNOLOGIQUE

## 🔬 TECHNOLOGIES ÉMERGENTES
[Innovations des documents]

## 🚀 TENDANCES DISRUPTIVES
[Technologies transformatrices]

## 💼 APPLICATIONS SECTORIELLES
[Cas d'usage concrets]

## 🔮 PROJECTIONS
[Timeline et adoption]

Référence chaque information [Réf. X].
        """,
        
        "analyse_risques": f"""
Analyse des risques basée sur les documents.

{context}

DEMANDE: {query}

FORMAT OBLIGATOIRE:

# ANALYSE DES RISQUES

## 🚨 CARTOGRAPHIE RISQUES
### Risques Stratégiques
[Menaces business]

### Risques Opérationnels
[Risques process]

### Risques Réglementaires
[Compliance]

## 📊 ÉVALUATION IMPACT
[Matrice probabilité/impact]

## 🛡️ MITIGATION
[Mesures préventives et contingence]

Cite [Réf. X] pour chaque risque identifié.
        """,
        
        "etude_marche": f"""
Étude de marché basée sur les documents.

{context}

DEMANDE: {query}

FORMAT OBLIGATOIRE:

# ÉTUDE DE MARCHÉ

## 📏 TAILLE DU MARCHÉ
[Dimensionnement avec chiffres]

## 👥 ANALYSE DEMANDE
[Comportements clients]

## 🏢 STRUCTURE OFFRE
[Acteurs et parts]

## 💰 DYNAMIQUES ÉCONOMIQUES
[Pricing et rentabilité]

## 🔮 PROJECTIONS
[Évolution 3-5 ans]

## 🎯 OPPORTUNITÉS
[Recommandations d'investissement]

Référence [Réf. X] pour chaque donnée marché.
        """
    }
    
    return templates.get(analysis_type, templates["synthese_executive"])

def call_openai(prompt: str) -> str:
    """Appel OpenAI avec gestion d'erreur"""
    try:
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
            return "⚠️ Configuration OpenAI requise pour analyses avec vos documents."
        
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un consultant expert qui génère des rapports professionnels basés UNIQUEMENT sur les documents fournis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return f"Erreur d'analyse: {str(e)}"

def format_sources(documents: List[Dict]) -> str:
    """Formate les sources"""
    if not documents:
        return ""
    
    sources = "\n\n## 📚 SOURCES ET RÉFÉRENCES\n\n"
    for i, doc in enumerate(documents[:5], 1):
        text_preview = doc.get('text', '')[:100]
        score = doc.get('score', 0)
        sources += f"**[Réf. {i}]** Score: {score:.3f} - \"{text_preview}...\"\n\n"
    
    return sources

async def generate_analysis(analysis_type: str, query: str, title: str = None) -> AnalysisResponse:
    """Génère analyse avec RAG"""
    try:
        # 1. Recherche vectorielle
        logger.info(f"Recherche pour: {query}")
        documents = search_documents(query, top_k=8)
        
        # 2. Création du prompt RAG
        prompt = create_rag_prompt(analysis_type, query, documents)
        
        # 3. Appel OpenAI
        content = call_openai(prompt)
        
        # 4. Ajout des sources
        if documents and content:
            content += format_sources(documents)
        
        return AnalysisResponse(
            analysis_type=analysis_type,
            title=title or f"Analyse {analysis_type.replace('_', ' ').title()}",
            content=content,
            sources=[{
                "doc_id": d.get("doc_id"),
                "score": d.get("score"),
                "text": d.get("text", "")[:200]
            } for d in documents],
            metadata={
                "query": query,
                "documents_found": len(documents),
                "vector_search": "active" if documents else "no_results",
                "model": "gpt-4o-mini"
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints
@app.get("/health")
def health():
    return {"status": "healthy", "service": "rag-final", "model": "gpt-4o-mini"}

@app.post("/synthesize", response_model=AnalysisResponse)
async def synthesize(request: AnalysisRequest):
    """Synthèse exécutive avec RAG"""
    return await generate_analysis("synthese_executive", request.query, request.title)

@app.post("/analyze_competition", response_model=AnalysisResponse)
async def analyze_competition(request: AnalysisRequest):
    """Analyse concurrentielle avec RAG"""
    return await generate_analysis("analyse_concurrentielle", request.query, request.title)

@app.post("/tech_watch", response_model=AnalysisResponse)
async def tech_watch(request: AnalysisRequest):
    """Veille technologique avec RAG"""
    return await generate_analysis("veille_technologique", request.query, request.title)

@app.post("/risk_analysis", response_model=AnalysisResponse)
async def risk_analysis(request: AnalysisRequest):
    """Analyse des risques avec RAG"""
    return await generate_analysis("analyse_risques", request.query, request.title)

@app.post("/market_study", response_model=AnalysisResponse)
async def market_study(request: AnalysisRequest):
    """Étude de marché avec RAG"""
    return await generate_analysis("etude_marche", request.query, request.title)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
