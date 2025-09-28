"""
RAG Service Standardisé - Structure uniforme pour tous les rapports professionnels
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import requests
from datetime import datetime
from loguru import logger

app = FastAPI(title="RAG Service Standardisé", description="RAG avec structure rapport standardisée")

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
            return result.get("results", [])
        else:
            logger.warning(f"Vector search failed: {response.status_code}")
            return []
            
    except Exception as e:
        logger.error(f"Vector search error: {e}")
        return []

def create_standardized_prompt(analysis_type: str, query: str, documents: List[Dict]) -> str:
    """Crée un prompt standardisé selon le pattern défini"""
    
    # Contexte des documents
    context = ""
    if documents:
        context = "## DOCUMENTS DE RÉFÉRENCE\n\n"
        for i, doc in enumerate(documents[:5], 1):
            doc_text = doc.get('text', '')[:300]
            score = doc.get('score', 0)
            context += f"**[Réf. {i}]** (Score: {score:.3f}):\n{doc_text}...\n\n"
    
    # Spécialisations par type d'analyse
    analysis_specifics = {
        "synthese_executive": {
            "focus": "synthèse stratégique et recommandations exécutives",
            "key_sections": "opportunités stratégiques, risques majeurs, recommandations prioritaires"
        },
        "analyse_concurrentielle": {
            "focus": "paysage concurrentiel et positionnements stratégiques", 
            "key_sections": "parts de marché, forces/faiblesses concurrentielles, benchmarking"
        },
        "veille_technologique": {
            "focus": "innovations technologiques et tendances émergentes",
            "key_sections": "technologies disruptives, adoption market, roadmap innovation"
        },
        "analyse_risques": {
            "focus": "identification et mitigation des risques",
            "key_sections": "cartographie risques, probabilité/impact, mesures préventives"
        },
        "etude_marche": {
            "focus": "dynamiques de marché et projections business",
            "key_sections": "taille de marché, segments clients, projections croissance"
        }
    }
    
    specific = analysis_specifics.get(analysis_type, analysis_specifics["synthese_executive"])
    
    # Prompt standardisé uniforme
    standardized_prompt = f"""
Tu es un consultant senior de McKinsey/BCG. Génère un rapport professionnel basé EXCLUSIVEMENT sur les documents fournis.

{context}

DEMANDE D'ANALYSE: {query}
FOCUS SPÉCIALISÉ: {specific['focus']}

STRUCTURE OBLIGATOIRE À RESPECTER EXACTEMENT:

# RAPPORT PROFESSIONNEL - {analysis_type.replace('_', ' ').upper()}

## 🎯 EXECUTIVE SUMMARY
### Key Findings
[3-4 découvertes majeures avec données chiffrées des documents [Réf. X]]

### Recommandations Prioritaires  
[2-3 actions stratégiques immédiates avec justifications]

### Métriques Clés
[Indicateurs de performance avec benchmarks tirés des sources]

---

## 📊 MARKET OVERVIEW
### Taille et Croissance
[Dimensionnement du marché avec chiffres précis [Réf. X]]

### Segmentation
[Segments principaux et caractéristiques [Réf. X]]

### Tendances Macro
[Forces macro-économiques influençant le secteur [Réf. X]]

---

## ⚔️ COMPETITIVE LANDSCAPE  
### Leaders du Marché
[Acteurs dominants avec parts de marché [Réf. X]]

### Positionnements Stratégiques
[Différenciation et stratégies concurrentielles [Réf. X]]

### Analyse Forces/Faiblesses
[Avantages concurrentiels et vulnérabilités [Réf. X]]

---

## 💡 KEY INSIGHTS
### Découvertes Majeures
[{specific['key_sections']} basés sur les documents [Réf. X]]

### Patterns Identifiés  
[Tendances et corrélations importantes [Réf. X]]

### Opportunités Stratégiques
[Gaps de marché et potentiel de croissance [Réf. X]]

---

## ⚡ RECOMMENDATIONS
### Actions Court Terme (0-6 mois)
[3 initiatives immédiates avec ROI attendu]

### Initiatives Moyen Terme (6-18 mois)
[2 projets structurants avec jalons]

### Vision Long Terme (+18 mois)
[1 transformation majeure avec vision 3-5 ans]

---

## 📚 APPENDIX
### Méthodologie
[Approche d'analyse utilisée]

### Sources Principales
[Documents de référence avec scores de pertinence]

### Limitations
[Biais potentiels et données manquantes]

CRITÈRES QUALITÉ:
- Utilise UNIQUEMENT les données des documents fournis
- Cite [Réf. X] pour chaque affirmation chiffrée
- Structure rigoureusement respectée
- Style professionnel consultant senior
- Données quantifiées prioritaires
- Recommandations actionables et mesurables
"""
    
    return standardized_prompt

def call_openai_standardized(prompt: str) -> str:
    """Appel OpenAI avec système prompt renforcé"""
    try:
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
            return "⚠️ Configuration OpenAI requise pour analyses avec vos documents."
        
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Système prompt renforcé pour structure standardisée
        system_prompt = """Tu es un consultant expert McKinsey/BCG spécialisé dans la génération de rapports professionnels structurés.

IMPÉRATIFS ABSOLUS:
1. RESPECTER EXACTEMENT la structure fournie dans le prompt
2. UTILISER UNIQUEMENT les informations des documents de référence
3. CITER systématiquement [Réf. X] pour chaque donnée
4. QUANTIFIER toutes les affirmations avec des chiffres précis
5. FORMATER en markdown professionnel avec émojis de section
6. RESTER FACTUEL et éviter les généralités

QUALITÉ ATTENDUE:
- Niveau consultant senior McKinsey/BCG
- Données 100% issues des documents fournis
- Structure rigoureusement respectée
- Recommandations actionables et mesurables
- Style professionnel et concis"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Plus déterministe pour structure
            max_tokens=4000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return f"Erreur d'analyse: {str(e)}"

def format_sources_standardized(documents: List[Dict]) -> str:
    """Formate les sources de manière standardisée"""
    if not documents:
        return ""
    
    sources = "\n\n---\n## 📋 RÉFÉRENCES DOCUMENTAIRES\n\n"
    for i, doc in enumerate(documents[:5], 1):
        text_preview = doc.get('text', '')[:150]
        score = doc.get('score', 0)
        doc_id = doc.get('doc_id', 'N/A')
        sources += f"**[Réf. {i}]** Document {doc_id} | Score: {score:.3f}\n"
        sources += f"*Extrait:* \"{text_preview}...\"\n\n"
    
    return sources

async def generate_standardized_analysis(analysis_type: str, query: str, title: str = None) -> AnalysisResponse:
    """Génère analyse avec structure standardisée"""
    try:
        # 1. Recherche vectorielle
        logger.info(f"Recherche vectorielle pour: {query}")
        documents = search_documents(query, top_k=8)
        
        # 2. Création du prompt standardisé
        prompt = create_standardized_prompt(analysis_type, query, documents)
        
        # 3. Appel OpenAI avec système renforcé
        content = call_openai_standardized(prompt)
        
        # 4. Ajout des sources standardisées
        if documents and content:
            content += format_sources_standardized(documents)
        
        return AnalysisResponse(
            analysis_type=analysis_type,
            title=title or f"Rapport {analysis_type.replace('_', ' ').title()}",
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
                "model": "gpt-4o-mini",
                "structure": "standardized_v1",
                "quality_level": "mckinsey_bcg"
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in standardized analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints avec structure standardisée
@app.get("/health")
def health():
    return {"status": "healthy", "service": "rag-standardized", "structure": "mckinsey_bcg_v1"}

@app.post("/synthesize", response_model=AnalysisResponse)
async def synthesize(request: AnalysisRequest):
    """Synthèse exécutive standardisée"""
    return await generate_standardized_analysis("synthese_executive", request.query, request.title)

@app.post("/analyze_competition", response_model=AnalysisResponse)
async def analyze_competition(request: AnalysisRequest):
    """Analyse concurrentielle standardisée"""
    return await generate_standardized_analysis("analyse_concurrentielle", request.query, request.title)

@app.post("/tech_watch", response_model=AnalysisResponse)
async def tech_watch(request: AnalysisRequest):
    """Veille technologique standardisée"""
    return await generate_standardized_analysis("veille_technologique", request.query, request.title)

@app.post("/risk_analysis", response_model=AnalysisResponse)
async def risk_analysis(request: AnalysisRequest):
    """Analyse des risques standardisée"""
    return await generate_standardized_analysis("analyse_risques", request.query, request.title)

@app.post("/market_study", response_model=AnalysisResponse)
async def market_study(request: AnalysisRequest):
    """Étude de marché standardisée"""
    return await generate_standardized_analysis("etude_marche", request.query, request.title)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
