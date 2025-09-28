"""
Backend Service Fixed - Rapports longs sans erreurs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import requests
from datetime import datetime
from loguru import logger
from app.business_prompts import get_business_prompt, get_available_business_types, get_business_type_display_name

app = FastAPI(title="Fixed Backend Intelligence", description="Rapports longs cabinet de conseil - version stable")

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
VECTOR_SERVICE_URL = "http://vector-service:8002"

# Modèles Pydantic
class BusinessAnalysisRequest(BaseModel):
    business_type: str
    analysis_type: str
    query: str
    title: Optional[str] = None

class AnalysisResponse(BaseModel):
    analysis_type: str
    business_type: str
    title: str
    content: str
    sources: List[Dict]
    metadata: Dict
    timestamp: str

def search_documents_safe(query: str, top_k: int = 10) -> List[Dict]:
    """Recherche vectorielle avec gestion d'erreurs robuste"""
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
            
    except requests.exceptions.Timeout:
        logger.error("Vector search timeout")
        return []
    except requests.exceptions.ConnectionError:
        logger.error("Vector search connection error")
        return []
    except Exception as e:
        logger.error(f"Vector search error: {e}")
        return []

def format_context_safe(documents: List[Dict]) -> str:
    """Formate contexte de manière sécurisée"""
    if not documents:
        return "Aucun document de référence disponible."
    
    context = "## DOCUMENTS DE RÉFÉRENCE\n\n"
    for i, doc in enumerate(documents[:6], 1):  # Limiter à 6 docs
        try:
            doc_text = str(doc.get('text', ''))[:500]  # Limiter texte
            score = float(doc.get('score', 0))
            doc_id = str(doc.get('doc_id', 'N/A'))
            context += f"**[Réf. {i}]** (Score: {score:.3f}):\n{doc_text}...\n\n"
        except Exception as e:
            logger.warning(f"Error formatting document {i}: {e}")
            continue
    
    return context

def create_optimized_prompt(business_type: str, analysis_type: str, query: str, context: str) -> str:
    """Crée prompts optimisés pour éviter les erreurs"""
    
    # Templates courts et efficaces
    prompt_templates = {
        "finance_banque": f"""ANALYSE BANCAIRE STRATÉGIQUE

MISSION: {query}

CONTEXTE:
{context[:4000]}  

GÉNÈRE UN RAPPORT PROFESSIONNEL STRUCTURÉ (10+ pages):

# RAPPORT STRATÉGIQUE BANCAIRE

## 🎯 SYNTHÈSE EXÉCUTIVE
- Enjeux transformation sectorielle [Réf. X]
- Recommandations prioritaires avec ROI
- Timeline et investissements

## 📊 ANALYSE SECTORIELLE  
- Taille marché et croissance [Réf. X]
- Segmentation clients [Réf. X]
- Performance secteur [Réf. X]
- Technologies émergentes [Réf. X]

## ⚔️ CONCURRENCE
- Leaders vs challengers [Réf. X]
- Forces/faiblesses [Réf. X]
- Stratégies différenciation [Réf. X]

## 💡 RECOMMANDATIONS
- Plan action 12-18 mois [Réf. X]
- Business case ROI [Réf. X]
- Gestion risques [Réf. X]

## 📈 PROJECTIONS
- Scenarios 2025-2030 [Réf. X]
- KPIs de suivi [Réf. X]

Minimum 5000 mots. Cite [Réf. X] pour toute donnée factuelle.""",

        "tech_digital": f"""ANALYSE TRANSFORMATION DIGITALE

MISSION: {query}

CONTEXTE:
{context[:4000]}

GÉNÈRE RAPPORT TECHNIQUE STRATÉGIQUE (10+ pages):

# RAPPORT TRANSFORMATION DIGITALE

## 🎯 VISION EXÉCUTIVE
- Enjeux transformation [Réf. X]
- ROI digital [Réf. X]
- Roadmap stratégique

## 🔧 ÉTAT DES LIEUX TECH
- Maturité technologique [Réf. X]
- Gaps et opportunités [Réf. X]
- Benchmark secteur [Réf. X]

## 🚀 INNOVATION
- Technologies clés [Réf. X]
- Use cases business [Réf. X]
- Investissements [Réf. X]

## 📋 PLAN D'ACTION
- Phases transformation [Réf. X]
- Budget et timeline [Réf. X]
- Organisation et skills [Réf. X]

Minimum 5000 mots. Référencer [Réf. X] systématiquement.""",

        "retail_commerce": f"""ANALYSE RETAIL STRATÉGIQUE

MISSION: {query}

CONTEXTE:
{context[:4000]}

GÉNÈRE RAPPORT RETAIL COMPLET (10+ pages):

# RAPPORT STRATÉGIE RETAIL

## 🎯 SYNTHÈSE RETAIL
- Tendances marché [Réf. X]
- Transformation omnicanal [Réf. X]
- Stratégies gagnantes

## 🛍️ MARCHÉ ET CLIENTS
- Évolution consommation [Réf. X]
- Segments clients [Réf. X]
- Parcours d'achat [Réf. X]

## 🏪 CONCURRENCE
- Players traditionnels vs pure players [Réf. X]
- Innovations retail [Réf. X]
- Différenciation [Réf. X]

## 💡 RECOMMANDATIONS
- Stratégie omnicanal [Réf. X]
- Technologies retail [Réf. X]
- Plan déploiement [Réf. X]

Minimum 5000 mots. Citer [Réf. X] pour données factuelles."""
    }
    
    return prompt_templates.get(business_type, prompt_templates["finance_banque"])

def call_openai_safe(prompt: str, business_type: str) -> str:
    """Appel OpenAI sécurisé avec gestion d'erreurs complète"""
    try:
        if not OPENAI_API_KEY or OPENAI_API_KEY == "":
            return "⚠️ **Configuration OpenAI requise**\n\nVeuillez configurer la variable OPENAI_API_KEY dans votre fichier .env"
        
        # Import OpenAI
        try:
            import openai
        except ImportError:
            return "❌ **Module OpenAI manquant**\n\nVeuillez installer: pip install openai"
        
        # System prompts par métier
        system_prompts = {
            "finance_banque": """Tu es un consultant senior McKinsey spécialisé en stratégie bancaire. 
                              Génère des rapports structurés avec analyses quantifiées et recommandations actionnables.
                              Utilise exclusivement les données des documents fournis avec références [Réf. X].""",
                              
            "tech_digital": """Tu es un consultant BCG expert en transformation digitale. 
                             Génère des analyses techniques détaillées avec business case et ROI.
                             Base tes analyses sur les documents fournis avec références [Réf. X].""",
                             
            "retail_commerce": """Tu es un consultant Bain expert en retail et commerce. 
                                Génère des analyses avec insights consommateurs et recommandations opérationnelles.
                                Utilise les documents fournis avec références [Réf. X]."""
        }
        
        system_prompt = system_prompts.get(business_type, system_prompts["finance_banque"])
        
        # Client OpenAI
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            # Vérifier taille prompt
            if len(prompt) > 15000:
                logger.warning(f"Prompt très long ({len(prompt)} chars), troncature appliquée")
                prompt = prompt[:15000] + "\n\n[...Prompt tronqué pour limites techniques. Continuer l'analyse avec les éléments disponibles...]"
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=8000
            )
            
            return response.choices[0].message.content
            
        except Exception as api_error:
            logger.error(f"OpenAI API error: {api_error}")
            return f"❌ **Erreur API OpenAI**\n\n{str(api_error)[:300]}\n\nVérifiez votre clé API et votre quota."
        
    except Exception as e:
        logger.error(f"Critical error in OpenAI call: {e}")
        return f"❌ **Erreur critique**\n\n{str(e)[:300]}"

async def generate_business_analysis_safe(business_type: str, analysis_type: str, query: str, title: str = None) -> AnalysisResponse:
    """Génère analyse avec gestion d'erreurs complète"""
    try:
        logger.info(f"Starting analysis: {business_type}/{analysis_type}")
        
        # 1. Recherche documents sécurisée
        documents = search_documents_safe(query, top_k=8)
        logger.info(f"Found {len(documents)} documents")
        
        # 2. Formatage contexte sécurisé
        context = format_context_safe(documents)
        
        # 3. Création prompt optimisé
        prompt = create_optimized_prompt(business_type, analysis_type, query, context)
        
        # 4. Appel OpenAI sécurisé
        content = call_openai_safe(prompt, business_type)
        
        # 5. Construction réponse
        return AnalysisResponse(
            analysis_type=analysis_type,
            business_type=business_type,
            title=title or f"Rapport {get_business_type_display_name(business_type)} - {analysis_type.replace('_', ' ').title()}",
            content=content,
            sources=[{
                "doc_id": d.get("doc_id", "N/A"),
                "score": d.get("score", 0),
                "text": str(d.get("text", ""))[:200]
            } for d in documents],
            metadata={
                "query": query,
                "business_type": business_type,
                "documents_found": len(documents),
                "analysis_length": "extended_report",
                "model": "gpt-4o-mini",
                "max_tokens": 8000,
                "status": "success"
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in business analysis: {e}")
        # Retourner une réponse d'erreur plutôt qu'une exception
        return AnalysisResponse(
            analysis_type=analysis_type,
            business_type=business_type,
            title=title or "Analyse échouée",
            content=f"❌ **Erreur lors de l'analyse**\n\n{str(e)[:500]}\n\nVeuillez réessayer ou contacter le support.",
            sources=[],
            metadata={
                "query": query,
                "business_type": business_type,
                "error": str(e),
                "status": "failed"
            },
            timestamp=datetime.now().isoformat()
        )

# Endpoints
@app.get("/health")
def health():
    """Health check avec diagnostics"""
    return {
        "status": "healthy", 
        "service": "fixed-backend",
        "openai_configured": bool(OPENAI_API_KEY),
        "vector_service": VECTOR_SERVICE_URL,
        "business_types": get_available_business_types()
    }

@app.get("/business-types")
def get_business_types():
    """Types de métier disponibles"""
    try:
        return {
            "business_types": [
                {"key": bt, "display_name": get_business_type_display_name(bt)} 
                for bt in get_available_business_types()
            ]
        }
    except Exception as e:
        logger.error(f"Error getting business types: {e}")
        return {
            "business_types": [
                {"key": "finance_banque", "display_name": "🏦 Finance & Banque"},
                {"key": "tech_digital", "display_name": "💻 Tech & Digital"},
                {"key": "retail_commerce", "display_name": "🛍️ Retail & Commerce"}
            ]
        }

@app.post("/extended-analysis", response_model=AnalysisResponse)
async def extended_analysis(request: BusinessAnalysisRequest):
    """Génère rapports longs style cabinet conseil - Version robuste"""
    return await generate_business_analysis_safe(
        request.business_type,
        request.analysis_type,
        request.query,
        request.title
    )

@app.get("/test-openai")
async def test_openai():
    """Test de connectivité OpenAI"""
    try:
        if not OPENAI_API_KEY:
            return {"status": "error", "message": "OPENAI_API_KEY not configured"}
        
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello, test simple"}],
            max_tokens=10
        )
        
        return {
            "status": "success", 
            "message": "OpenAI API functional",
            "model": "gpt-4o-mini",
            "response": response.choices[0].message.content
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
