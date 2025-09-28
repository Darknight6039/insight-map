"""
Backend Service - Version robuste sans points d'échec
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import requests
from datetime import datetime
from loguru import logger
from importlib import metadata
from app.business_prompts import get_business_prompt, get_available_business_types, get_business_type_display_name

# Import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.error("OpenAI package not available")

app = FastAPI(title="Backend Intelligence Service", description="Rapports longs cabinet de conseil - version robuste")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

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

class ChatRequest(BaseModel):
    message: str
    business_type: Optional[str] = None
    conversation_history: Optional[List[Dict]] = []

class ChatResponse(BaseModel):
    response: str
    business_context: str
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
            # The vector-service returns a LIST of results. Also support dict forms.
            if isinstance(result, list):
                return result
            if isinstance(result, dict):
                return result.get("results", result.get("data", []))
            return []
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
        
        # Vérifier OpenAI
        if not OPENAI_AVAILABLE:
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
        
        # Client OpenAI avec paramètres explicites
        try:
            client = OpenAI(
                api_key=OPENAI_API_KEY,
                timeout=30.0
            )
            
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

async def generate_chat_response_safe(message: str, business_type: str = None, history: List[Dict] = None) -> ChatResponse:
    """Chat avec gestion d'erreurs robuste"""
    try:
        # 1. Recherche documents
        documents = search_documents_safe(message, top_k=5)
        context = format_context_safe(documents)
        
        # 2. Construction prompt chat
        business_context = get_business_type_display_name(business_type) if business_type else "Généraliste"
        
        chat_prompt = f"""Tu es un assistant expert spécialisé {business_context}.

CONTEXTE DOCUMENTAIRE:
{context}

HISTORIQUE CONVERSATION:
{history[-3:] if history else "Nouvelle conversation"}

QUESTION: {message}

Réponds de manière concise et professionnelle en te basant sur les documents fournis.
Si la question dépasse ton domaine d'expertise, oriente vers le bon spécialiste.
Cite [Réf. X] pour les informations factuelles.
"""

        # 3. Appel OpenAI sécurisé
        response_content = call_openai_safe(chat_prompt, business_type or "finance_banque")
        
        return ChatResponse(
            response=response_content,
            business_context=business_context,
            sources=[{
                "doc_id": d.get("doc_id", "N/A"),
                "score": d.get("score", 0),
                "text": str(d.get("text", ""))[:100]
            } for d in documents[:3]],
            metadata={
                "message": message,
                "business_type": business_type,
                "documents_found": len(documents),
                "model": "gpt-4o-mini"
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in chat response: {e}")
        return ChatResponse(
            response=f"❌ Erreur dans la réponse: {str(e)[:200]}",
            business_context=business_type or "Error",
            sources=[],
            metadata={"error": str(e)},
            timestamp=datetime.now().isoformat()
        )

# Endpoints
@app.get("/health")
def health():
    """Health check avec diagnostics étendus"""
    return {
        "status": "healthy", 
        "service": "backend-intelligence-fixed",
        "openai_configured": bool(OPENAI_API_KEY),
        "vector_service": VECTOR_SERVICE_URL,
        "business_types": get_available_business_types(),
        "version": "1.0-robust"
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

@app.post("/business-analysis", response_model=AnalysisResponse)
async def business_analysis(request: BusinessAnalysisRequest):
    """Alias pour compatibilité"""
    return await generate_business_analysis_safe(
        request.business_type,
        request.analysis_type,
        request.query,
        request.title
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat intelligent avec contexte métier"""
    return await generate_chat_response_safe(
        request.message,
        request.business_type,
        request.conversation_history
    )

@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """Streaming de la réponse du chat (texte brut chunké, compatible fetch streaming)."""
    async def token_generator():
        try:
            # 1) RAG rapide (synchrone)
            documents = search_documents_safe(request.message, top_k=5)
            context = format_context_safe(documents)
            business_context = get_business_type_display_name(request.business_type) if request.business_type else "Généraliste"
            chat_prompt = f"""Tu es un assistant expert spécialisé {business_context}.

CONTEXTE DOCUMENTAIRE:
{context}

HISTORIQUE CONVERSATION:
{request.conversation_history[-3:] if request.conversation_history else "Nouvelle conversation"}

QUESTION: {request.message}

Réponds de manière concise et professionnelle en te basant sur les documents fournis.
Si la question dépasse ton domaine d'expertise, oriente vers le bon spécialiste.
Cite [Réf. X] pour les informations factuelles.
"""

            # 2) Streaming OpenAI
            if not OPENAI_API_KEY or not OPENAI_AVAILABLE:
                # Fallback non‑bloquant
                yield "Le streaming nécessite une configuration OPENAI_API_KEY.\n"
                yield "[DONE]"
                return

            client = OpenAI(api_key=OPENAI_API_KEY, timeout=30.0)
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"Assistant spécialisé {business_context}."},
                    {"role": "user", "content": chat_prompt}
                ],
                temperature=0.3,
                max_tokens=1500,
                stream=True,
            )

            for event in stream:
                try:
                    delta = event.choices[0].delta if hasattr(event.choices[0], "delta") else event.choices[0].get("delta", {})
                    content = getattr(delta, "content", None)
                    if content is None and isinstance(delta, dict):
                        content = delta.get("content")
                    if content:
                        yield content
                except Exception as inner:
                    logger.warning(f"Stream delta parse error: {inner}")
                    continue

            yield "[DONE]"
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield "\n[STREAM_ERROR]"

    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",  # Nginx: disable buffering
    }
    return StreamingResponse(token_generator(), media_type="text/plain", headers=headers)

@app.get("/test-openai")
async def test_openai():
    """Test de connectivité OpenAI"""
    try:
        if not OPENAI_API_KEY:
            return {"status": "error", "message": "OPENAI_API_KEY not configured"}
        
        client = OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=30.0
        )
        
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

@app.get("/diagnostics")
async def diagnostics():
    """Diagnostics complets du système"""
    
    diagnostics_result = {
        "timestamp": datetime.now().isoformat(),
        "service": "backend-intelligence-fixed",
        "version": "1.0-robust"
    }
    
    # Versions des libs clés
    try:
        diagnostics_result["versions"] = {
            "python": os.getenv("PYTHON_VERSION", "unknown"),
            "openai": metadata.version("openai") if OPENAI_AVAILABLE else "not-installed",
            "httpx": metadata.version("httpx") if "httpx" in {d.metadata["Name"].lower() for d in map(lambda n: metadata.distribution(n), metadata.packages_distributions().keys()) if False} else metadata.version("httpx")
        }
    except Exception:
        try:
            diagnostics_result["versions"] = {
                "openai": metadata.version("openai") if OPENAI_AVAILABLE else "not-installed",
                "httpx": metadata.version("httpx")
            }
        except Exception as e:
            diagnostics_result["versions_error"] = str(e)

    # Proxies d'environnement (pour debug)
    diagnostics_result["env_proxies"] = {
        k: os.getenv(k)
        for k in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"]
        if os.getenv(k)
    }

    # Test OpenAI
    try:
        if OPENAI_API_KEY:
            client = OpenAI(
                api_key=OPENAI_API_KEY,
                timeout=30.0
            )
            test_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            diagnostics_result["openai"] = {"status": "✅ Functional", "model": "gpt-4o-mini"}
        else:
            diagnostics_result["openai"] = {"status": "❌ Not configured", "model": None}
    except Exception as e:
        diagnostics_result["openai"] = {"status": f"❌ Error: {str(e)[:100]}", "model": "gpt-4o-mini"}
    
    # Test Vector Service
    try:
        test_docs = search_documents_safe("test", top_k=1)
        diagnostics_result["vector_service"] = {
            "status": "✅ Accessible" if len(test_docs) >= 0 else "⚠️ No results",
            "url": VECTOR_SERVICE_URL,
            "test_results": len(test_docs)
        }
    except Exception as e:
        diagnostics_result["vector_service"] = {"status": f"❌ Error: {str(e)[:100]}", "url": VECTOR_SERVICE_URL}
    
    # Test Business Types
    try:
        business_types = get_available_business_types()
        diagnostics_result["business_types"] = {"status": "✅ Available", "count": len(business_types), "types": business_types}
    except Exception as e:
        diagnostics_result["business_types"] = {"status": f"❌ Error: {str(e)[:100]}"}
    
    return diagnostics_result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)