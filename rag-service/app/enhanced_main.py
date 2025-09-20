"""
Enhanced RAG Service - Utilise vraiment le RAG avec formatage professionnel
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import httpx
from datetime import datetime
from loguru import logger

app = FastAPI(title="Enhanced RAG Service", description="RAG avec recherche vectorielle et format professionnel")

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
VECTOR_SERVICE_URL = "http://vector-service:8002"

# Modèles Pydantic
class AnalysisRequest(BaseModel):
    query: str
    title: Optional[str] = None
    top_k: Optional[int] = 8

class AnalysisResponse(BaseModel):
    analysis_type: str
    title: str
    content: str
    sources: List[Dict]
    metadata: Dict
    timestamp: str

async def search_relevant_content(query: str, top_k: int = 8) -> List[Dict]:
    """Recherche dans la base vectorielle"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{VECTOR_SERVICE_URL}/search",
                json={"query": query, "top_k": top_k}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("results", [])
            else:
                logger.warning(f"Vector search failed: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Error in vector search: {e}")
        return []

def format_references(sources: List[Dict]) -> str:
    """Formate les références bibliographiques"""
    if not sources:
        return ""
    
    refs = "\n## 📚 RÉFÉRENCES ET SOURCES\n\n"
    
    seen_docs = set()
    for i, source in enumerate(sources, 1):
        doc_id = source.get('doc_id')
        if doc_id not in seen_docs:
            seen_docs.add(doc_id)
            text_preview = source.get('text', '')[:150]
            score = source.get('score', 0)
            
            refs += f"**[{i}]** Document {doc_id} (Pertinence: {score:.3f})\n"
            refs += f"*Extrait:* \"{text_preview}...\"\n\n"
    
    return refs

def create_professional_prompt(analysis_type: str, query: str, context_passages: List[Dict]) -> str:
    """Crée un prompt structuré pour réponse professionnelle"""
    
    # Formatage du contexte
    context = ""
    if context_passages:
        context = "## CONTEXTE DOCUMENTAIRE\n\n"
        for passage in context_passages:
            context += f"**Source {passage.get('doc_id', 'N/A')}:** {passage.get('text', '')}\n\n"
    
    # Templates par type d'analyse
    templates = {
        "synthese_executive": f"""
Tu es un consultant senior McKinsey. Rédige une SYNTHÈSE EXÉCUTIVE structurée basée sur les documents fournis.

{context}

REQUÊTE: {query}

STRUCTURE OBLIGATOIRE:

# SYNTHÈSE EXÉCUTIVE

## 🎯 RÉSUMÉ STRATÉGIQUE
[3-4 points clés avec données chiffrées issues des documents]

## 💡 INSIGHTS MAJEURS
[2-3 découvertes importantes tirées des sources]

## ⚡ RECOMMANDATIONS PRIORITAIRES
### Actions immédiates (0-3 mois)
[3 actions concrètes avec justifications chiffrées]

### Initiatives moyen terme (3-12 mois)  
[2 initiatives stratégiques]

## 📊 MÉTRIQUES CLÉS
[Indicateurs à suivre avec benchmarks des documents]

## ⚠️ RISQUES ET VIGILANCE
[2-3 points d'attention majeurs]

Utilise EXCLUSIVEMENT les données des documents fournis. Cite les sources avec [Réf. X].
        """,
        
        "analyse_concurrentielle": f"""
Tu es un expert en intelligence concurrentielle BCG. Analyse la concurrence avec les données documentaires.

{context}

REQUÊTE: {query}

STRUCTURE OBLIGATOIRE:

# ANALYSE CONCURRENTIELLE

## 🗺️ CARTOGRAPHIE DU MARCHÉ
[Acteurs identifiés dans les documents avec parts de marché]

## ⚔️ ANALYSE FORCES/FAIBLESSES
### Leaders du marché
[Forces et positionnement des leaders]

### Challengers
[Stratégies et avantages concurrentiels]

### Nouveaux entrants
[Disrupteurs et innovations]

## 📈 DYNAMIQUES CONCURRENTIELLES
[Tendances et mouvements du marché]

## 🎯 OPPORTUNITÉS DE DIFFÉRENCIATION
[Gaps identifiés et recommandations]

## 🔮 PROJECTION CONCURRENTIELLE
[Évolution attendue du paysage]

Cite systématiquement les sources documentaires [Réf. X].
        """,
        
        "veille_technologique": f"""
Tu es un expert en innovation technologique. Identifie les tendances tech avec les données documentaires.

{context}

REQUÊTE: {query}

STRUCTURE OBLIGATOIRE:

# VEILLE TECHNOLOGIQUE

## 🔬 TECHNOLOGIES ÉMERGENTES
[Innovations identifiées dans les documents]

## 🚀 TENDANCES DISRUPTIVES
[Technologies transformatrices avec impact chiffré]

## 💼 APPLICATIONS SECTORIELLES
[Cas d'usage concrets et déploiements]

## 📊 MATURITÉ TECHNOLOGIQUE
[Évaluation du niveau de développement]

## 🔮 PROJECTIONS D'ADOPTION
[Timeline et facteurs d'accélération]

## ⚡ RECOMMANDATIONS TECHNOLOGIQUES
[Technologies à surveiller et investissements]

Appuie-toi sur les données factuelles des documents [Réf. X].
        """,
        
        "analyse_risques": f"""
Tu es un expert en risk management. Évalue les risques avec les données documentaires.

{context}

REQUÊTE: {query}

STRUCTURE OBLIGATOIRE:

# ANALYSE DES RISQUES

## 🚨 CARTOGRAPHIE DES RISQUES
### Risques Stratégiques
[Menaces business identifiées]

### Risques Opérationnels  
[Risques process et systèmes]

### Risques Réglementaires
[Compliance et évolutions légales]

## 📊 ÉVALUATION PROBABILITÉ/IMPACT
[Matrice de risques avec scoring]

## 🛡️ MESURES DE MITIGATION
### Actions préventives
[Mesures proactives recommandées]

### Plans de contingence
[Réponses aux scénarios critiques]

## 📈 MONITORING ET INDICATEURS
[KPIs de suivi des risques]

Utilise les données chiffrées des documents sources [Réf. X].
        """,
        
        "etude_marche": f"""
Tu es un expert en analyse de marché. Réalise une étude complète avec les données documentaires.

{context}

REQUÊTE: {query}

STRUCTURE OBLIGATOIRE:

# ÉTUDE DE MARCHÉ

## 📏 DIMENSIONNEMENT DU MARCHÉ
[Taille, segments, croissance avec chiffres des documents]

## 👥 ANALYSE DE LA DEMANDE
[Comportements clients et tendances]

## 🏢 STRUCTURE DE L'OFFRE
[Acteurs, parts de marché, positionnements]

## 💰 DYNAMIQUES ÉCONOMIQUES
[Pricing, rentabilité, modèles économiques]

## 🔮 PROJECTIONS ET SCÉNARIOS
[Évolution 3-5 ans avec hypothèses]

## 🎯 OPPORTUNITÉS D'INVESTISSEMENT
[Segments porteurs et recommandations]

## ⚠️ BARRIÈRES ET DÉFIS
[Obstacles à l'entrée et risques marché]

Appuie chaque assertion sur les données documentaires [Réf. X].
        """
    }
    
    return templates.get(analysis_type, templates["synthese_executive"])

async def generate_enhanced_analysis(analysis_type: str, query: str, title: str = None) -> AnalysisResponse:
    """Génère une analyse avec RAG et formatage professionnel"""
    
    try:
        # 1. Recherche vectorielle
        logger.info(f"Recherche vectorielle pour: {query}")
        relevant_passages = await search_relevant_content(query, top_k=8)
        
        if not relevant_passages:
            logger.warning("Aucun contenu vectoriel trouvé, utilisation fallback")
        
        # 2. Construction du prompt professionnel
        prompt = create_professional_prompt(analysis_type, query, relevant_passages)
        
        # 3. Appel GPT-5-mini
        content = await call_gpt5_mini(prompt)
        
        # 4. Formatage des références
        references = format_references(relevant_passages)
        if references:
            content += f"\n\n{references}"
        
        # 5. Construction de la réponse
        return AnalysisResponse(
            analysis_type=analysis_type,
            title=title or f"Analyse {analysis_type.replace('_', ' ').title()}",
            content=content,
            sources=[
                {
                    "doc_id": p.get("doc_id"),
                    "score": p.get("score"),
                    "text": p.get("text", "")[:200]
                } for p in relevant_passages
            ],
            metadata={
                "query": query,
                "passages_found": len(relevant_passages),
                "vector_search": "active" if relevant_passages else "no_results",
                "model": "gpt-5-mini"
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in enhanced analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def call_gpt5_mini(prompt: str) -> str:
    """Appel à GPT-5-mini avec gestion d'erreur"""
    try:
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
            return "⚠️ Configuration OpenAI requise pour analyses personnalisées avec vos documents."
        
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "Tu es un consultant expert qui génère des rapports professionnels basés sur des données documentaires. Utilise UNIQUEMENT les informations fournies dans le contexte documentaire."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return f"Erreur d'analyse: {str(e)}"

# Endpoints d'analyse
@app.get("/health")
def health():
    return {"status": "healthy", "service": "enhanced-rag-service", "model": "gpt-5-mini"}

@app.post("/synthesize", response_model=AnalysisResponse)
async def synthesize(request: AnalysisRequest):
    """Synthèse exécutive avec RAG"""
    return await generate_enhanced_analysis("synthese_executive", request.query, request.title)

@app.post("/analyze_competition", response_model=AnalysisResponse)
async def analyze_competition(request: AnalysisRequest):
    """Analyse concurrentielle avec RAG"""
    return await generate_enhanced_analysis("analyse_concurrentielle", request.query, request.title)

@app.post("/tech_watch", response_model=AnalysisResponse)
async def tech_watch(request: AnalysisRequest):
    """Veille technologique avec RAG"""
    return await generate_enhanced_analysis("veille_technologique", request.query, request.title)

@app.post("/risk_analysis", response_model=AnalysisResponse)
async def risk_analysis(request: AnalysisRequest):
    """Analyse des risques avec RAG"""
    return await generate_enhanced_analysis("analyse_risques", request.query, request.title)

@app.post("/market_study", response_model=AnalysisResponse)
async def market_study(request: AnalysisRequest):
    """Étude de marché avec RAG"""
    return await generate_enhanced_analysis("etude_marche", request.query, request.title)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
