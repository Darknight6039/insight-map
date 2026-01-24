"""
Backend Service - Version robuste sans points d'échec
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from typing import List, Dict, Optional, AsyncGenerator
import os
import re
import requests
import json
import asyncio
from datetime import datetime, timedelta
from loguru import logger
from importlib import metadata
from app.business_prompts import get_business_prompt, get_available_business_types, get_business_type_display_name, get_trusted_sources, TRUSTED_SOURCES_INSTRUCTION
from app.language_detector import detect_query_language
from app.context_manager import (
    save_text_context, save_document_context, get_user_context,
    get_user_context_info, delete_user_context, get_context_for_prompt,
    extract_text_from_file
)
from app.rag_memory import (
    add_conversation, get_history_for_prompt, get_full_history,
    clear_user_memory, search_history
)
from app.app_knowledge import build_context_prompt, ANALYSIS_TYPES, SECTORS, WATCH_FREQUENCIES, GUIDES, FAQ
from app.assistant_actions import (
    ActionType, ProposedAction, ActionResult, execute_action,
    build_action_from_intent, ACTION_DEFINITIONS
)

# Import SDK Perplexity (compatible OpenAI SDK)
try:
    from openai import OpenAI
    OPENAI_SDK_AVAILABLE = True
except ImportError:
    OPENAI_SDK_AVAILABLE = False
    logger.error("SDK OpenAI package not available (required for Perplexity API compatibility)")

app = FastAPI(title="Backend Intelligence Service", description="Rapports longs cabinet de conseil - version robuste")

# Configuration CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,https://prometheus.axial-ia.fr").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Configuration - Perplexity API
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
PERPLEXITY_BASE_URL = "https://api.perplexity.ai"
VECTOR_SERVICE_URL = "http://vector-service:8002"
DOCUMENT_SERVICE_URL = "http://document-service:8001"
MEMORY_SERVICE_URL = os.getenv("MEMORY_SERVICE_URL", "http://memory-service:8008")

# Configuration multi-modèles Sonar optimisée par cas d'usage
# IMPORTANT: Tous les rapports (standards et approfondis) utilisent sonar-pro
PERPLEXITY_MODELS = {
    "chat": os.getenv("PERPLEXITY_MODEL_CHAT", "sonar"),              # Chat court, tests
    "analysis": os.getenv("PERPLEXITY_MODEL_ANALYSIS", "sonar-pro"),  # TOUS les rapports
    "reasoning": os.getenv("PERPLEXITY_MODEL_REASONING", "sonar-reasoning-pro") # Réservé usage futur - Migration depuis sonar-reasoning (déprécié le 15/12/2025)
}

def get_model_for_task(task_type: str) -> str:
    """Sélectionne le modèle Sonar approprié selon la tâche"""
    return PERPLEXITY_MODELS.get(task_type, PERPLEXITY_MODELS["chat"])

# Cache pour les métadonnées des documents
_document_metadata_cache = {}

# Modèles Pydantic
class BusinessAnalysisRequest(BaseModel):
    business_type: Optional[str] = "general"  # Optional, defaults to generic
    analysis_type: str
    query: str
    title: Optional[str] = None
    include_recommendations: Optional[bool] = True  # Option pour inclure/exclure les recommandations
    language: Optional[str] = "fr"  # Langue de réponse: 'fr' ou 'en'
    user_id: Optional[str] = None  # ID utilisateur pour charger ses contextes

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

class SchedulerAnalysisRequest(BaseModel):
    """Request model for scheduler-service watch executions"""
    query: str
    analysis_type: str
    sector: Optional[str] = "general"
    deep_analysis: Optional[bool] = False

class ChatResponse(BaseModel):
    response: str
    business_context: str
    sources: List[Dict]
    metadata: Dict
    timestamp: str

def get_document_metadata(doc_id: int) -> Optional[Dict]:
    """Récupère les métadonnées réelles d'un document depuis le document-service"""
    # Vérifier le cache d'abord
    if doc_id in _document_metadata_cache:
        return _document_metadata_cache[doc_id]
    
    try:
        response = requests.get(
            f"{DOCUMENT_SERVICE_URL}/document/{doc_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            metadata = response.json()
            # Mettre en cache
            _document_metadata_cache[doc_id] = metadata
            return metadata
        else:
            logger.warning(f"Failed to get document metadata for doc_id={doc_id}: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching document metadata for doc_id={doc_id}: {e}")
        return None

async def save_conversation_to_memory(
    user_id: str,
    query: str,
    response: str,
    conversation_type: str = "analysis",
    analysis_type: Optional[str] = None,
    business_type: Optional[str] = None
):
    """
    Save conversation to memory service using internal endpoint (no JWT required)

    user_id: Can be either an integer (as string) or UUID string from Supabase.
             The memory-service will handle the conversion via user_id_mapping table.
    """
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            result = await client.post(
                f"{MEMORY_SERVICE_URL}/internal/conversations",
                params={"user_id": str(user_id)},
                json={
                    "query": query,
                    "response": response,
                    "conversation_type": conversation_type,
                    "analysis_type": analysis_type,
                    "business_type": business_type
                }
            )
            if result.status_code == 201:
                logger.info(f"✅ Conversation saved to memory service for user {user_id}: {conversation_type}")
            else:
                logger.warning(f"⚠️ Memory service returned {result.status_code}: {result.text[:200]}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to save to memory service (non-blocking): {e}")


async def save_document_to_memory(
    user_id: str,
    document_type: str,
    title: str,
    content: Optional[str] = None,
    file_path: Optional[str] = None,
    analysis_type: Optional[str] = None,
    business_type: Optional[str] = None,
    report_id: Optional[int] = None,
    watch_id: Optional[int] = None
):
    """
    Save document to memory service using internal endpoint

    user_id: Can be either an integer (as string) or UUID string from Supabase.
             The memory-service will handle the conversion via user_id_mapping table.
    """
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            result = await client.post(
                f"{MEMORY_SERVICE_URL}/internal/documents",
                json={
                    "user_id": str(user_id),
                    "document_type": document_type,
                    "title": title[:500],
                    "content": (content or "")[:5000],
                    "file_path": file_path or "",
                    "analysis_type": analysis_type or "",
                    "business_type": business_type or "",
                    "report_id": report_id or 0,
                    "watch_id": watch_id or 0,
                    "metadata": {}
                }
            )
            if result.status_code in (200, 201):
                logger.info(f"✅ Document saved to memory service for user {str(user_id)[:16]}...: {title[:50]}")
            else:
                logger.warning(f"Memory service returned {result.status_code}: {result.text}")
    except Exception as e:
        logger.warning(f"Failed to save document to memory service: {e}")

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

def enrich_source_with_apa(doc: Dict, index: int) -> Dict:
    """Enrichit une source avec métadonnées APA pour citations académiques"""
    doc_id = doc.get("doc_id", "N/A")
    text = str(doc.get("text", ""))
    score = doc.get("score", 0)
    segment_index = doc.get("segment_index", 0)
    
    # Récupérer les vraies métadonnées du document
    metadata = None
    if isinstance(doc_id, int):
        metadata = get_document_metadata(doc_id)
    
    # Utiliser les vraies métadonnées si disponibles
    if metadata:
        filename = metadata.get("filename", "Document inconnu")
        title = metadata.get("title", filename)
        upload_date = metadata.get("upload_date", "")
        pages_count = metadata.get("pages_count", 0)
        
        # Extraire l'année de la date d'upload
        try:
            year = datetime.fromisoformat(upload_date.replace('Z', '+00:00')).year if upload_date else 2024
        except:
            year = 2024
        
        # Calculer la page approximative basée sur le segment
        page = min(segment_index + 1, pages_count) if pages_count > 0 else segment_index + 1
        
        # Déterminer l'auteur et le type basés sur le nom du fichier et le contenu
        if "study" in filename.lower() or "étude" in filename.lower():
            author = "Département Études et Recherche"
            doc_type = "Étude de marché"
        elif "report" in filename.lower() or "rapport" in filename.lower():
            author = "Direction Stratégie"
            doc_type = "Rapport stratégique"
        elif "analysis" in filename.lower() or "analyse" in filename.lower():
            author = "Équipe Analyse"
            doc_type = "Analyse sectorielle"
        else:
            # Détermine le type basé sur le contenu
            if "marché" in text.lower() or "market" in text.lower():
                author = "Axial Market Intelligence"
                doc_type = "Rapport de marché"
            elif "tech" in text.lower() or "digital" in text.lower():
                author = "Axial Tech Watch"
                doc_type = "Veille technologique"
            elif "risque" in text.lower() or "risk" in text.lower():
                author = "Axial Risk Assessment"
                doc_type = "Analyse de risques"
            else:
                author = "Axial Intelligence"
                doc_type = "Document d'analyse"
        
        # Format APA: Auteur. (Année). Titre. Type, p. page.
        apa_citation = f"{author}. ({year}). {title}. {doc_type}, p. {page}."
        
    else:
        # Fallback sur les métadonnées génériques si pas de metadata disponible
        year = 2024
        author = "Axial Research"
        title = f"Document d'analyse stratégique #{doc_id}"
        page = (doc_id % 50) + 1 if isinstance(doc_id, int) else 1
        doc_type = "Document interne"
        apa_citation = f"{author}. ({year}). {title}. {doc_type}, p. {page}."
    
    return {
        "id": index,
        "doc_id": doc_id,
        "title": title,
        "author": author,
        "year": year,
        "page": page,
        "doc_type": doc_type,
        "text": text[:300],  # Preview plus long
        "score": score,
        "apa_citation": apa_citation,
        "document_url": f"/documents/{doc_id}.pdf" if doc_id != "N/A" else None
    }

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

async def create_optimized_prompt(business_type: str, analysis_type: str, query: str, context: str, include_recommendations: bool = True, language: str = "fr", user_id: Optional[str] = None) -> str:
    """Crée prompts concis et efficaces pour rapports de cabinet de conseil avec sonar-pro

    Args:
        business_type: Type de métier
        analysis_type: Type d'analyse
        query: Requête d'analyse
        context: Contexte documentaire
        include_recommendations: Si True, inclut les recommandations stratégiques
        language: Langue de réponse ('fr' pour français, 'en' pour anglais)
    """
    
    # Instruction de langue
    language_instruction = ""
    if language == "en":
        language_instruction = """
⚠️ **LANGUAGE INSTRUCTION - RESPOND IN ENGLISH**:
The user query is in English. You MUST respond entirely in English.
All sections, titles, content, and recommendations must be written in English.

"""
    else:
        language_instruction = """
⚠️ **INSTRUCTION DE LANGUE - RÉPONDRE EN FRANÇAIS**:
La requête utilisateur est en français. Tu DOIS répondre entièrement en français.
Toutes les sections, titres, contenus et recommandations doivent être rédigés en français.

"""
    
    # Integration du contexte utilisateur et historique (RAG)
    # Multi-contexte: recupere TOUS les contextes actifs depuis memory-service
    user_context_section = ""
    user_history_section = ""
    if user_id:
        try:
            user_context_section = await get_context_for_prompt(user_id, max_length=4000)
            user_history_section = get_history_for_prompt(user_id, query, max_length=800)
        except Exception as e:
            logger.warning(f"Error fetching user context/history: {e}")
    
    # Calcul des dates pour contrainte temporelle (dernière semaine)
    date_fin = datetime.now().strftime("%d/%m/%Y")
    date_debut = (datetime.now() - timedelta(days=7)).strftime("%d/%m/%Y")
    time_constraint = f"""
## CONTRAINTE TEMPORELLE OBLIGATOIRE
IMPORTANT: Concentre tes recherches sur les sources publiees entre le {date_debut} et le {date_fin} (dernière semaine uniquement).
Privilegie les actualites et donnees les plus recentes. Les sources plus anciennes ne doivent etre utilisees que pour le contexte historique.

"""
    
    # Synthese Executive = Rapport exhaustif (60 sources) avec contrainte temporelle 1 semaine
    if analysis_type.lower() == "synthese_executive":
        prompt_templates_deep = {
            "finance_banque": f"""Tu es un consultant senior McKinsey specialise en strategie bancaire - Synthese Executive.

{time_constraint}

**MISSION** : {query}

**CONTEXTE DOCUMENTAIRE** :
{context[:5000]}

**FORMAT** : Rapport ultra-detaille (8000-10000 mots) avec 60 sources MINIMUM

## EXIGENCES SOURCES (SYNTHESE EXECUTIVE) :
- Utilise recherche web Perplexity exhaustive
- MINIMUM 60 sources organisees par categorie
- FOCUS sur les actualites de la DERNIERE SEMAINE ({date_debut} - {date_fin})

## HIERARCHIE SOURCES STRICTE (60 sources) - INSTITUTIONS ET CABINETS UNIQUEMENT :
- 42 sources institutionnelles (70%) : INSEE, Banque de France, ACPR, AMF, ministeres, BCE, EBA, OCDE, FMI
- 18 sources cabinets de conseil (30%) : McKinsey, BCG, Bain, Deloitte, PwC, EY, KPMG
- AUCUNE source media (Les Echos, Bloomberg, FT, etc.) - STRICTEMENT INTERDIT

## RECHERCHE EN 2 PHASES :
Phase 1 : 42 sources institutionnelles minimum (70%)
Phase 2 : 18 sources cabinets de conseil maximum (30%)

## STRUCTURE RAPPORT EXHAUSTIF :

1. **Executive Summary** (800-1000 mots)
   - 8-10 KPIs cles avec 3-4 sources croisees chacun
   - Top 5 recommandations avec ROI, budget, timeline

2. **Analyse Sectorielle Approfondie** (2500-3000 mots)
   - Dimensionnement marche detaille (10+ metriques)
   - Segmentation complete avec donnees chiffrees
   - Evolutions historiques 5 ans + projections 3 ans
   - MINIMUM 25 donnees chiffrees avec sources croisees

3. **Analyse Concurrentielle Exhaustive** (2000-2500 mots)
   - Tableau comparatif 12+ criteres x 8-10 acteurs
   - Chaque cellule doit avoir sa source
   - Analyse detaillee forces/faiblesses par acteur
   - Cartographie positionnement strategique
   - MINIMUM 3 tableaux comparatifs detailles

4. **Recommandations Strategiques** (2000-2500 mots)
   - 8-10 recommandations ultra-detaillees
   - Chaque recommandation : budget, ROI, timeline, risques, KPIs
   - Plans d'action operationnels concrets
   - Analyses couts-benefices detaillees

5. **Projections et Scenarios** (1500-2000 mots)
   - 3 scenarios modelises (optimiste, central, pessimiste)
   - Analyses de sensibilite sur 4-5 variables
   - Tableaux financiers detailles

6. **References Bibliographiques** (60 sources MINIMUM)
   - Section Sources Institutionnelles Francaises (20 sources)
   - Section Sources Institutionnelles Europeennes/Internationales (22 sources)
   - Section Cabinets de Conseil (18 sources)
   - Format APA obligatoire: Auteur. (Annee). Titre. Publication. URL

## IMPERATIFS QUALITE :
- MINIMUM 60 sources organisees par categorie
- MINIMUM 50 donnees chiffrees avec sources croisees
- MINIMUM 5 tableaux comparatifs detailles
- Croisement 3-4 sources pour chaque donnee strategique
- Citations denses : chaque paragraphe doit avoir 3-5 citations minimum

Genere maintenant ce rapport exhaustif :""",

            "tech_digital": f"""Tu es un consultant BCG expert en transformation digitale - Synthese Executive.

{time_constraint}

**MISSION** : {query}

**CONTEXTE** : {context[:5000]}

**FORMAT** : Rapport ultra-detaille (8000-10000 mots) avec 60 sources MINIMUM

## EXIGENCES SOURCES (SYNTHESE EXECUTIVE) :
- Utilise recherche web Perplexity exhaustive
- MINIMUM 60 sources organisees par categorie
- FOCUS sur les actualites de la DERNIERE SEMAINE ({date_debut} - {date_fin})

## HIERARCHIE SOURCES STRICTE (60 sources) - INSTITUTIONS ET CABINETS UNIQUEMENT :
- 42 sources institutionnelles/analystes (70%) : Gartner, IDC, Forrester, Commission europeenne, OCDE
- 18 sources cabinets de conseil (30%) : McKinsey Digital, BCG Digital Ventures, Accenture, Deloitte
- AUCUNE source media tech (TechCrunch, Wired, ZDNet, etc.) - STRICTEMENT INTERDIT

## IMPERATIFS :
- 50+ donnees chiffrees avec sources croisees
- 5+ tableaux comparatifs detailles
- Rapport 8000-10000 mots

Genere maintenant ce rapport exhaustif :""",

            "retail_commerce": f"""Tu es un consultant Bain expert retail - Synthese Executive.

{time_constraint}

**MISSION** : {query}

**CONTEXTE** : {context[:5000]}

**FORMAT** : Rapport ultra-detaille (8000-10000 mots) avec 60 sources MINIMUM

## EXIGENCES SOURCES (SYNTHESE EXECUTIVE) :
- Utilise recherche web Perplexity exhaustive
- MINIMUM 60 sources organisees par categorie
- FOCUS sur les actualites de la DERNIERE SEMAINE ({date_debut} - {date_fin})

## HIERARCHIE SOURCES STRICTE (60 sources) - INSTITUTIONS ET CABINETS UNIQUEMENT :
- 42 sources institutionnelles (70%) : INSEE, FEVAD, CREDOC, Eurostat, Commission europeenne, OCDE
- 18 sources cabinets de conseil (30%) : McKinsey Retail, BCG Consumer, Bain, Deloitte, PwC
- AUCUNE source media commerce (LSA, e-commerce mag, etc.) - STRICTEMENT INTERDIT

## IMPERATIFS :
- 50+ donnees chiffrees avec sources croisees
- 5+ tableaux comparatifs detailles
- Rapport 8000-10000 mots

Genere maintenant ce rapport exhaustif :"""
        }
        
        deep_prompt = prompt_templates_deep.get(business_type, prompt_templates_deep["finance_banque"])
        # Ajouter contexte utilisateur et historique si disponibles
        full_prompt = language_instruction + user_context_section + user_history_section + deep_prompt
        return full_prompt
    
    # Templates standards (40-60 sources) - code existant
    prompt_templates = {
        "finance_banque": f"""Tu es un consultant senior McKinsey spécialisé en stratégie bancaire.

**MISSION** : {query}

**CONTEXTE DOCUMENTAIRE** :
{context[:5000]}

**FORMAT ATTENDU** :

Génère un rapport stratégique professionnel ultra-détaillé (6000-8000 mots) avec :

## EXIGENCES SOURCES (TOUS RAPPORTS) - INSTITUTIONS ET CABINETS UNIQUEMENT :
- MINIMUM 40-60 sources institutionnelles et cabinets de conseil
- Répartition: 70% institutionnelles (INSEE, BCE, OCDE, etc.), 30% cabinets (McKinsey, BCG, etc.)
- AUCUNE source média, presse, blog - STRICTEMENT INTERDIT
- Utilise recherche web Perplexity exhaustive pour données actuelles

## Structure Obligatoire avec Numérotation Hiérarchique

IMPORTANT: Tous les titres doivent être numérotés hiérarchiquement:
- Niveau ## : 1, 2, 3, 4, etc.
- Niveau ### : 1.1, 1.2, 2.1, 2.2, etc.
- Niveau #### : 1.1.1, 1.1.2, 2.1.1, etc.

Exemple:
## 1. Executive Summary
### 1.1 Synthèse Quantifiée
### 1.2 Recommandations Clés

## 2. Analyse Sectorielle Quantifiée
### 2.1 Dimensionnement Marché
#### 2.1.1 Taille Actuelle
#### 2.1.2 Projections

## Style Rédactionnel - Contenu Enrichi

IMPORTANT: Chaque section doit alterner paragraphes narratifs et bullet points:

STRUCTURE REQUISE POUR CHAQUE SECTION:
1. Paragraphe d'introduction (3-5 phrases) qui contextualise le sujet
2. Développement avec 2-3 paragraphes narratifs détaillés (4-6 phrases chacun)
3. Points clés synthétisés en bullet points pour les données chiffrées
4. Paragraphe de transition ou conclusion (2-3 phrases) avant la section suivante

EXIGENCES DE RÉDACTION:
- Minimum 60% de contenu en paragraphes narratifs complets
- Maximum 40% de contenu en bullet points (réservés aux listes de données/chiffres)
- Chaque paragraphe doit développer une idée complète avec exemples et sources
- Style fluide avec transitions naturelles entre paragraphes
- Phrases variées et bien articulées (pas de style télégraphique)
- Connecteurs logiques pour lier les idées (ainsi, en effet, par conséquent, néanmoins, etc.)

EXEMPLE DE STRUCTURE:
### 2.1 Dimensionnement du Marché

Le marché bancaire français représente aujourd'hui un écosystème dynamique en pleine transformation (INSEE, 2024). L'analyse des données récentes révèle une croissance soutenue portée par la digitalisation et l'évolution des comportements clients (Banque de France, 2024).

L'analyse détaillée révèle plusieurs tendances structurantes qui redéfinissent le paysage concurrentiel. Les néobanques captent désormais 8% du marché des particuliers, une progression de +45% en deux ans (ACPR, 2024). Cette dynamique s'accompagne d'une consolidation du secteur traditionnel, où les cinq premières banques concentrent 65% des parts de marché (BCE, 2024).

Ces évolutions s'accompagnent de transformations profondes des modèles économiques. L'investissement technologique représente désormais 12-15% des budgets, contre 6-8% il y a cinq ans (McKinsey, 2024). Les établissements pionniers observent une amélioration de leur ratio coût/revenu de 5-8 points (BCG, 2024).

**Données clés du marché:**
- Taille: 450 Md€ de revenus (INSEE, 2024)
- Croissance: +3.2% CAGR 2021-2024 (Banque de France, 2024)
- Parts de marché: Top 5 = 65% (ACPR, 2024)
- Marge nette moyenne: 28% (BCE, 2024)

En synthèse, le marché démontre une résilience notable face aux disruptions technologiques. Les acteurs qui réussissent combinent solidité financière historique et agilité numérique, avec des investissements tech atteignant 450-600M€ par an pour les leaders (McKinsey, 2024).

1. **Executive Summary** (500-700 mots)
   - Synthèse quantifiée : 5-8 KPIs clés avec sources APA (Auteur, Année)
   - Top 3 recommandations avec ROI estimé et timeline précis

2. **Analyse Sectorielle Quantifiée** (1500-2000 mots)
   - Dimensionnement marché avec croisement de sources :
     * Taille actuelle en M€/M$ [sources multiples]
     * CAGR 3 dernières années [sources croisées]
     * Prévisions 3 prochaines années avec hypothèses [sources]
     * Parts de marché top 5-10 acteurs avec évolution [sources]
   - Segmentation avec données précises pour chaque segment
   - MINIMUM 10-15 données chiffrées avec dates et sources croisées

3. **Analyse Concurrentielle Comparative** (1200-1500 mots)
   - Tableau comparatif détaillé : minimum 8 critères × 5 concurrents
   - Chaque cellule doit avoir sa source
   - Analyse forces/faiblesses basée sur données factuelles [sources]
   - Évolution parts de marché sur 2-3 ans

4. **Recommandations Stratégiques Chiffrées** (1500-2000 mots)
   - CHAQUE recommandation DOIT inclure :
     * Investissement requis avec fourchette [sources benchmarks]
     * ROI estimé avec calcul détaillé [sources méthodologie]
     * Timeline précis (semaines/mois)
     * Risques quantifiés (probabilité % + impact €)
     * KPIs de suivi (minimum 3 par recommandation)

5. **Projections Financières et Scénarios** (1000-1200 mots)
   - 3 scénarios OBLIGATOIRES avec modélisation complète :
     * Optimiste : hypothèses + 3-5 drivers clés avec impact %
     * Central : hypothèses baseline avec sources
     * Pessimiste : hypothèses + risques quantifiés
   - Tableau de synthèse comparatif des 3 scénarios
   - Analyse de sensibilité sur 2-3 variables clés

6. **Références Bibliographiques** (40-60 sources MINIMUM)
   - Sources Institutionnelles (70%) : INSEE, BCE, Banque de France, ACPR, AMF, OCDE, FMI
   - Cabinets de Conseil (30%) : McKinsey, BCG, Bain, Deloitte, PwC, EY, KPMG
   - Format APA obligatoire: Auteur. (Année). Titre. Publication. URL

## Impératifs qualité STRICTS

✅ QUANTIFICATION SYSTÉMATIQUE :
- MINIMUM 20-25 données chiffrées dans le rapport
- Chaque chiffre avec source ET date
- Comparaisons temporelles (évolution sur 2-3 ans)
- Benchmarks internationaux quand pertinent

✅ CROISEMENT DE SOURCES :
- Données importantes confirmées par 2-3 sources en format APA: (Source1, 2024; Source2, 2024)
- Mention des divergences : "varie entre X (Source1, 2024) et Y (Source2, 2024)"
- Privilégier convergence de sources institutionnelles

✅ PRÉCISION TEMPORELLE :
- Toujours date avec citation APA: "En 2024 (INSEE, 2024)", "Sur 2022-2024 (Banque de France, 2024)"
- Distinguer historique, actuel, projections
- Périmètre avec sources: "En France (INSEE, 2024)", "Europe (BCE, 2024)"

✅ TABLEAUX COMPARATIFS :
- MINIMUM 3 tableaux dans le rapport
- Toutes cellules sourcées
- Minimum 3 colonnes × 5 lignes

✅ GRAPHIQUES ET VISUALISATIONS :
- Inclure 2-4 graphiques pertinents pour illustrer les données clés
- Format markdown pour graphiques:
```chart
type: bar|line|pie
title: Titre du graphique
data: {{labels: ["Label1", "Label2", "Label3"], values: [valeur1, valeur2, valeur3]}}
source: (Auteur, Année)
```
- Types de graphiques appropriés:
  * bar: comparaisons entre catégories, parts de marché
  * line: évolutions temporelles, tendances
  * pie: répartitions, pourcentages
- Chaque graphique doit avoir une source APA

Génère maintenant ce rapport ultra-documenté et précis :""",

        "tech_digital": f"""Tu es un consultant BCG expert en transformation digitale.

**MISSION** : {query}

**CONTEXTE** : {context[:5000]}

**FORMAT** : Rapport stratégique professionnel (6000-8000 mots) avec :

## EXIGENCES SOURCES - INSTITUTIONS ET CABINETS UNIQUEMENT :
- MINIMUM 40-60 sources institutionnelles et cabinets de conseil
- Répartition: 70% analystes/institutions (Gartner, IDC, Forrester, Commission EU), 30% cabinets (McKinsey, BCG, Accenture)
- AUCUNE source média tech (TechCrunch, Wired, ZDNet, etc.) - STRICTEMENT INTERDIT
- Utilise recherche web Perplexity exhaustive pour données actuelles

## Structure Obligatoire avec Numérotation Hiérarchique

IMPORTANT: Tous les titres doivent être numérotés hiérarchiquement:
- Niveau ## : 1, 2, 3, 4, etc.
- Niveau ### : 1.1, 1.2, 2.1, 2.2, etc.
- Niveau #### : 1.1.1, 1.1.2, 2.1.1, etc.

Exemple:
## 1. Vision Exécutive
### 1.1 Enjeux Transformation
### 1.2 ROI Estimé

## 2. État des Lieux Tech
### 2.1 Maturité Digitale
#### 2.1.1 Score Global
#### 2.1.2 Analyse Détaillée

## Style Rédactionnel - Contenu Enrichi

IMPORTANT: Chaque section doit alterner paragraphes narratifs et bullet points:

STRUCTURE REQUISE POUR CHAQUE SECTION:
1. Paragraphe d'introduction (3-5 phrases) qui contextualise le sujet
2. Développement avec 2-3 paragraphes narratifs détaillés (4-6 phrases chacun)
3. Points clés synthétisés en bullet points pour les données chiffrées
4. Paragraphe de transition ou conclusion (2-3 phrases) avant la section suivante

EXIGENCES DE RÉDACTION:
- Minimum 60% de contenu en paragraphes narratifs complets
- Maximum 40% de contenu en bullet points (réservés aux listes de données/chiffres)
- Chaque paragraphe doit développer une idée complète avec exemples et sources
- Style fluide avec transitions naturelles entre paragraphes
- Phrases variées et bien articulées (pas de style télégraphique)
- Connecteurs logiques pour lier les idées (ainsi, en effet, par conséquent, néanmoins, etc.)

EXEMPLE DE STRUCTURE:
### 2.1 Transformation Digitale

La transformation digitale du secteur redéfinit aujourd'hui les standards de compétitivité (Gartner, 2024). Les entreprises leaders investissent massivement dans l'IA et l'automatisation, avec des budgets moyens en hausse de 35% sur deux ans (IDC, 2024).

L'adoption des technologies cloud computing s'accélère de manière exponentielle dans tous les secteurs. Les migrations vers le cloud hybride concernent désormais 68% des grandes entreprises, contre 42% en 2022 (Forrester, 2024). Cette évolution permet des gains de flexibilité et d'efficacité opérationnelle mesurables, avec une réduction des coûts IT de 20-30% en moyenne (McKinsey Digital, 2024).

Les investissements dans l'IA générative explosent littéralement depuis 2023. Les dépenses mondiales atteignent 156 Md$ en 2024, soit une croissance de +78% en un an (IDC, 2024). Les cas d'usage se multiplient : support client automatisé, génération de code, analyse prédictive, personnalisation marketing (Gartner, 2024).

**Indicateurs clés transformation:**
- Budget IT moyen: 4.5% du CA (+0.8pt vs 2022) (Gartner, 2024)
- Adoption cloud: 68% grandes entreprises (Forrester, 2024)
- ROI moyen IA: 18-25% première année (McKinsey, 2024)
- Temps déploiement: -40% avec DevOps (IDC, 2024)

En conclusion, la transformation digitale n'est plus une option mais un impératif stratégique. Les organisations qui excellent combinent vision long terme et capacité d'exécution agile, avec des cycles d'innovation réduits à 3-6 mois contre 12-18 mois historiquement (BCG, 2024).

1. **Vision Exécutive** (500-700 mots)
   - Enjeux transformation avec chiffres clés [sources multiples]
   - ROI estimé avec calcul détaillé [benchmarks sectoriels]
   - Roadmap high-level avec jalons quantifiés

2. **État des Lieux Tech Quantifié** (1500-2000 mots)
   - Maturité digitale : score/10 sur 5-8 dimensions [sources]
   - Gaps identifiés avec impact business chiffré [données]
   - Benchmarks sectoriels et internationaux [sources croisées]
   - MINIMUM 10 KPIs tech avec comparaisons

3. **Innovation et Technologies** (1200-1500 mots)
   - Technologies clés avec taux d'adoption marché [sources]
   - Use cases business avec ROI par use case [benchmarks]
   - Investissements requis par technologie [études]
   - Tableau comparatif technologies (minimum 8 critères × 4 techs)

4. **Plan d'Action Détaillé** (1500-2000 mots)
   - Phases avec timeline précis (semaines/mois)
   - Budget détaillé par phase et poste [benchmarks]
   - Organisation : FTE requis par compétence [données marché]
   - Risques quantifiés avec mitigation [probabilités]
   - MINIMUM 3 tableaux : timeline, budget, ressources

5. **Projections et Business Case** (800-1000 mots)
   - 3 scénarios ROI (optimiste/central/pessimiste)
   - KPIs de suivi avec targets chiffrés
   - Analyse de sensibilité

6. **Références Bibliographiques** (40-60 sources MINIMUM)
   - Sources Analystes/Institutions (70%) : Gartner, IDC, Forrester, Commission européenne, OCDE
   - Cabinets de Conseil (30%) : McKinsey, BCG, Accenture, Deloitte, PwC
   - Format APA obligatoire: Auteur. (Année). Titre. Publication. URL

EXIGENCES: MINIMUM 25 données chiffrées, 3+ tableaux, croisement sources format APA (Auteur, Année)

Génère maintenant ce rapport :""",

        "retail_commerce": f"""Tu es un consultant Bain expert en retail et commerce.

**MISSION** : {query}

**CONTEXTE** : {context[:5000]}

**FORMAT** : Rapport stratégique professionnel (6000-8000 mots) avec :

## EXIGENCES SOURCES - INSTITUTIONS ET CABINETS UNIQUEMENT :
- MINIMUM 40-60 sources institutionnelles et cabinets de conseil
- Répartition: 70% institutionnelles (INSEE, FEVAD, CREDOC, Eurostat), 30% cabinets (McKinsey, BCG, Bain)
- AUCUNE source média commerce (LSA, e-commerce mag, etc.) - STRICTEMENT INTERDIT
- Utilise recherche web Perplexity exhaustive pour données actuelles

## Structure Obligatoire avec Numérotation Hiérarchique

IMPORTANT: Tous les titres doivent être numérotés hiérarchiquement:
- Niveau ## : 1, 2, 3, 4, etc.
- Niveau ### : 1.1, 1.2, 2.1, 2.2, etc.
- Niveau #### : 1.1.1, 1.1.2, 2.1.1, etc.

Exemple:
## 1. Synthèse Retail Quantifiée
### 1.1 Tendances Marché
### 1.2 Stratégies Gagnantes

## 2. Marché et Consommateurs
### 2.1 Évolution Consommation
#### 2.1.1 Chiffres Clés
#### 2.1.2 Segments Clients

## Style Rédactionnel - Contenu Enrichi

IMPORTANT: Chaque section doit alterner paragraphes narratifs et bullet points:

STRUCTURE REQUISE POUR CHAQUE SECTION:
1. Paragraphe d'introduction (3-5 phrases) qui contextualise le sujet
2. Développement avec 2-3 paragraphes narratifs détaillés (4-6 phrases chacun)
3. Points clés synthétisés en bullet points pour les données chiffrées
4. Paragraphe de transition ou conclusion (2-3 phrases) avant la section suivante

EXIGENCES DE RÉDACTION:
- Minimum 60% de contenu en paragraphes narratifs complets
- Maximum 40% de contenu en bullet points (réservés aux listes de données/chiffres)
- Chaque paragraphe doit développer une idée complète avec exemples et sources
- Style fluide avec transitions naturelles entre paragraphes
- Phrases variées et bien articulées (pas de style télégraphique)
- Connecteurs logiques pour lier les idées (ainsi, en effet, par conséquent, néanmoins, etc.)

EXEMPLE DE STRUCTURE:
### 2.1 Évolution Comportements Consommateurs

Le paysage de la consommation française connaît une mutation profonde accélérée par le digital (FEVAD, 2024). Les comportements d'achat se fragmentent entre canaux physiques et digitaux, créant de nouveaux parcours clients hybrides qui défient les modèles traditionnels (INSEE, 2024).

L'e-commerce poursuit sa croissance soutenue avec un taux de pénétration atteignant 15.2% du commerce de détail total en 2024, contre 13.4% en 2023 (FEVAD, 2024). Cette progression s'accompagne d'une sophistication des attentes : livraison express, personnalisation de l'offre, expérience omnicanale fluide (McKinsey, 2024). Les retailers qui excellent sur ces dimensions capturent 25-30% de parts de marché supplémentaires (BCG, 2024).

La dynamique retail s'oriente vers des modèles phygitaux intégrant le meilleur des deux mondes. Les magasins physiques évoluent en showrooms expérientiels avec click & collect, essayage virtuel, et conseillers augmentés par l'IA (Bain, 2024). Les investissements dans ces technologies atteignent 8-12% des budgets marketing des leaders, générant une hausse de trafic de 15-20% (Deloitte, 2024).

**Indicateurs clés e-commerce:**
- CA e-commerce France: 156 Md€ (+11% vs 2023) (FEVAD, 2024)
- Taux pénétration: 15.2% du retail total (INSEE, 2024)
- Panier moyen: 68€ (+3€ vs 2023) (CREDOC, 2024)
- Livraison J+1: 78% des sites top 100 (McKinsey, 2024)

En synthèse, le retail français bascule vers des modèles hybrides où l'excellence opérationnelle digitale devient aussi critique que la présence physique. Les enseignes gagnantes investissent 150-250M€ dans leur transformation omnicanale (BCG, 2024).

1. **Synthèse Retail Quantifiée** (500-700 mots)
   - Tendances marché avec chiffres clés [sources croisées]
   - Stratégies gagnantes avec ROI moyen [benchmarks]
   - Top 3 opportunités quantifiées

2. **Marché et Consommateurs** (1500-2000 mots)
   - Évolution consommation : chiffres sur 3 ans [INSEE, panels]
   - Segments clients avec tailles et potentiel [sources]
   - Parcours d'achat avec taux de conversion par canal [études]
   - Panier moyen et fréquence par segment [données]
   - MINIMUM 12 KPIs clients/marché avec sources

3. **Analyse Concurrentielle Retail** (1200-1500 mots)
   - Tableau comparatif : 8 critères × 5-8 acteurs
   - Players traditionnels vs pure players (CA, croissance, marges)
   - Innovations retail avec impact business [cas d'usage]
   - Parts de marché online vs offline [sources]

4. **Recommandations Omnicanal** (1500-2000 mots)
   - Stratégie omnicanal avec investissements par canal
   - Technologies retail (coûts, ROI, timeline)
   - Plan de déploiement phasé avec KPIs
   - Quick wins vs projets structurants
   - MINIMUM 3 tableaux : investissements, ROI, roadmap

5. **Business Case et Projections** (800-1000 mots)
   - 3 scénarios (pénétration marché, CA, rentabilité)
   - Analyse de sensibilité prix/volume
   - KPIs de suivi omnicanal

6. **Références Bibliographiques** (40-60 sources MINIMUM)
   - Sources Institutionnelles (70%) : INSEE, FEVAD, CREDOC, Eurostat, Commission européenne
   - Cabinets de Conseil (30%) : McKinsey, BCG, Bain, Deloitte, PwC
   - Format APA obligatoire: Auteur. (Année). Titre. Publication. URL

EXIGENCES: MINIMUM 25 données chiffrées, 3+ tableaux, sources format APA (Auteur, Année)

Génère maintenant ce rapport :"""
    }
    
    base_prompt = prompt_templates.get(business_type, prompt_templates["finance_banque"])
    
    # Ajouter instruction de langue
    # Ajouter contexte utilisateur et historique si disponibles
    base_prompt = language_instruction + user_context_section + user_history_section + base_prompt
    
    # Si recommandations désactivées, ajouter instruction explicite
    if not include_recommendations:
        no_reco_instruction = """

⚠️ **INSTRUCTION SPÉCIALE - SANS RECOMMANDATIONS**:
Ce rapport doit être une analyse FACTUELLE UNIQUEMENT.
- NE PAS inclure de section "Recommandations Stratégiques"
- NE PAS inclure de section "Plan d'Action"
- NE PAS inclure de conseils ou suggestions d'amélioration
- Se concentrer UNIQUEMENT sur l'analyse, les données et les constats
- Remplacer la section recommandations par une section "Conclusions et Points Clés" qui résume les faits sans préconisations

"""
        base_prompt = no_reco_instruction + base_prompt
    
    return base_prompt

def call_perplexity_safe(
    prompt: str, 
    business_type: str, 
    rag_context: str = "",
    task_type: str = "chat"  # NOUVEAU PARAMÈTRE
) -> str:
    """Appel Perplexity sécurisé avec RAG interne et recherche web"""
    try:
        if not PERPLEXITY_API_KEY or PERPLEXITY_API_KEY == "":
            return "⚠️ **Configuration Perplexity requise**\n\nVeuillez configurer la variable PERPLEXITY_API_KEY dans votre fichier .env"
        
        # Vérifier SDK OpenAI (compatible Perplexity)
        if not OPENAI_SDK_AVAILABLE:
            return "❌ **SDK OpenAI manquant**\n\nCe SDK est requis pour la compatibilité avec Perplexity API.\nVeuillez installer: pip install openai"
        
        # Sélection dynamique du modèle selon la tâche
        selected_model = get_model_for_task(task_type)
        
        # Ajuster max_tokens selon le modèle
        # sonar-pro (12000 tokens) est utilisé pour TOUS les rapports (40-60 sources)
        max_tokens_config = {
            "sonar": 8000,        # +2000 pour chat enrichi avec paragraphes
            "sonar-pro": 16000,   # +4000 pour rapports détaillés avec contenu narratif
            "sonar-reasoning-pro": 20000  # +4000 pour analyses profondes (migration depuis sonar-reasoning)
        }
        max_tokens = max_tokens_config.get(selected_model, 6000)
        
        logger.info(f"Using model: {selected_model} for task: {task_type} (max_tokens: {max_tokens})")
        
        # System prompt générique avec sources institutionnelles et cabinets conseil uniquement
        system_prompt = f"""Tu es un consultant senior spécialisé en stratégie d'entreprise.

{TRUSTED_SOURCES_INSTRUCTION}

RÈGLES OBLIGATOIRES:

1. TITRE PROFESSIONNEL:
   - Commence TOUJOURS par un titre professionnel de 5-10 mots sur la PREMIÈRE LIGNE
   - Format: # Titre du Rapport
   - Le titre doit résumer le sujet analysé (pas la question posée)

2. CITATIONS APA STRICTES:
   - CHAQUE fait/chiffre DOIT être suivi d'une citation: (Auteur, Année)
   - Exemple: "Le marché croît de 15% (INSEE, 2024)"
   - Pour données importantes: citer 2-3 sources: (INSEE, 2024; BCE, 2024)
   - JAMAIS de chiffre sans source

3. SECTION SOURCES OBLIGATOIRE EN FIN DE RAPPORT:
   TERMINE TOUJOURS par cette section exacte:

   ## 📚 Références Bibliographiques
   
   ### Sources Institutionnelles
   1. INSEE. (2024). Titre du rapport. Rapport officiel. https://insee.fr/...
   2. Banque de France. (2024). Titre. Publication. https://banque-france.fr/...
   3. BCE. (2024). Titre. Rapport. https://ecb.europa.eu/...
   
   ### Cabinets de Conseil
   4. McKinsey & Company. (2024). Titre étude. Rapport. https://mckinsey.com/...
   5. BCG. (2024). Titre. Étude. https://bcg.com/...
   [Continue avec TOUTES les sources utilisées - minimum 20 sources]

4. SOURCES AUTORISÉES EXCLUSIVEMENT:
   - 70% institutionnelles (INSEE, BCE, Banque de France, ACPR, AMF, OCDE, FMI, ministères)
   - 30% cabinets de conseil (McKinsey, BCG, Bain, Deloitte, PwC, EY, KPMG, Gartner, IDC)
   - EXCLURE: médias, presse, blogs, forums, entreprises privées

5. STYLE: Professionnel, générique, sans mention de secteur spécifique."""
        
        # Prompt enrichi avec instructions explicites de citation web
        enhanced_prompt = f"""{prompt}

═══════════════════════════════════════════════════════════════

INSTRUCTIONS DE RECHERCHE - SOURCES INSTITUTIONNELLES ET CABINETS DE CONSEIL UNIQUEMENT :

📌 PHASE 1 - RECHERCHE STRUCTURÉE (sources autorisées exclusivement) :

PHASE 1A - Sources Institutionnelles (70% minimum) :
- France : INSEE, Banque de France, ACPR, AMF, DARES, DGE, France Stratégie, Cour des Comptes
- Europe : BCE, EBA, ESMA, Commission européenne, Eurostat, Parlement européen
- International : OCDE, FMI, BRI (Banque des Règlements Internationaux), Banque Mondiale
- Organismes publics spécialisés (.gov, .gouv.fr, .europa.eu)

PHASE 1B - Cabinets de Conseil (30% maximum) :
- Stratégie : McKinsey & Company, Boston Consulting Group (BCG), Bain & Company
- Audit/Conseil : Deloitte, PwC, EY (Ernst & Young), KPMG
- Spécialisés : Accenture, Oliver Wyman, Roland Berger, AT Kearney, L.E.K. Consulting
- Tech/Digital : Gartner, IDC, Forrester (uniquement pour analyses technologiques)

⛔ SOURCES STRICTEMENT EXCLUES :
- Médias et presse (Les Échos, Bloomberg, Financial Times, Reuters, etc.)
- Blogs, forums et réseaux sociaux
- Entreprises privées (hors cabinets de conseil listés)
- Sites d'actualité et magazines
- Think tanks non gouvernementaux
- Contenus promotionnels ou commerciaux

HIÉRARCHIE FINALE À RESPECTER :
✓ 70% sources institutionnelles (priorité absolue)
✓ 30% cabinets de conseil uniquement

Pour TOUS les rapports (40-60 sources) : 
- Minimum 28-42 sources institutionnelles (70%)
- Maximum 12-18 sources cabinets de conseil (30%)
- AUCUNE source média, presse ou blog

📌 PHASE 2 - CROISEMENT ET VALIDATION DES SOURCES :
- COMPARER systématiquement les chiffres entre sources avec citations APA :
  * Si convergence : "Le marché atteint 50M€ selon l'INSEE (INSEE, 2024) et la Banque de France (Banque de France, 2024)"
  * Si divergence : "Le marché varie entre 45M€ (INSEE, 2024) et 52M€ (Banque de France, 2024), moyenne estimée à 48M€"
- Identifier les sources les plus fiables (institutionnelles > média > blogs)
- Signaler toute contradiction importante entre sources
- Préférer moyenne de plusieurs sources plutôt qu'une seule donnée

📌 PHASE 3 - RÉDACTION AVEC CITATIONS APA DENSES :
- CHAQUE phrase contenant un fait/chiffre DOIT avoir 1-2 citations APA
- Utiliser citations multiples pour données importantes : (Source1, 2024; Source2, 2024)
- Ne JAMAIS affirmer sans source : "X% des entreprises..." → "X% des entreprises (Auteur, 2024)"
- Varier les sources : éviter de tout citer depuis 1-2 sources uniquement

📌 PHASE 4 - ANALYSE CRITIQUE DES DONNÉES :
- Mentionner les limitations des données quand pertinent
- Indiquer la date et le périmètre des études citées avec citation APA
- Exemple: "Selon l'étude INSEE 2024 portant sur 1500 entreprises (INSEE, 2024)..."
- Signaler si les données sont partielles, estimées ou définitives

📌 PHASE 5 - BIBLIOGRAPHIE APA COMPLÈTE ET ORGANISÉE :
Section "## 📚 Références Bibliographiques" structurée par catégorie :

### Sources Institutionnelles Françaises
INSEE. (2024). Panorama économique français Q3 2024. Rapport trimestriel. https://...
Banque de France. (2024). Situation économique France. Bulletin mensuel. https://...
ACPR. (2024). Rapport annuel supervision bancaire. Publication officielle. https://...

### Sources Institutionnelles Européennes et Internationales
BCE. (2024). Rapport stabilité financière. Publication officielle. https://...
OCDE. (2024). Perspectives économiques. Rapport annuel. https://...
FMI. (2024). World Economic Outlook. Publication. https://...

### Cabinets de Conseil - Études et Rapports
McKinsey & Company. (2024). Transformation sectorielle en France. Rapport. https://...
BCG. (2024). Analyse stratégique du marché. Étude. https://...
Deloitte. (2024). Tendances et perspectives. Rapport annuel. https://...

MINIMUM REQUIS (TOUS RAPPORTS):
- 40-60 sources institutionnelles et cabinets de conseil uniquement
- Répartition stricte: 70% institutionnelles, 30% cabinets de conseil
- 28-42 sources institutionnelles + 12-18 sources cabinets conseil
- AUCUNE source média, presse, blog ou entreprise privée

📌 STRUCTURE ET NUMÉROTATION:
- TOUS les titres doivent être numérotés hiérarchiquement
- Format: ## 1. Titre principal, ### 1.1 Sous-titre, #### 1.1.1 Sous-sous-titre
- Numérotation cohérente et continue dans tout le rapport
- Facilite la navigation et les références croisées

📌 STYLE RÉDACTIONNEL:
- Style naturel et professionnel comme les exemples de templates
- Phrases claires et bien structurées (détailler autant que nécessaire pour être complet)
- Développer les éléments importants en profondeur sans contrainte de longueur
- Transitions naturelles entre paragraphes avec connecteurs logiques
- Vocabulaire précis mais accessible, éviter le jargon excessif
- Structure logique et progressive, voix active privilégiée
- Style professionnel mais fluide et agréable à lire, pas robotique

📌 CONTENU ENRICHI - PARAGRAPHES NARRATIFS OBLIGATOIRES:

POUR CHAQUE SECTION/SOUS-SECTION:
1. Paragraphe d'ouverture contextuel (3-5 phrases complètes)
2. Corps du texte en paragraphes narratifs (minimum 2-3 paragraphes de 4-6 phrases)
3. Bullet points uniquement pour synthétiser données chiffrées ou lister des éléments
4. Paragraphe de transition vers section suivante (2-3 phrases)

RATIO IMPÉRATIF:
- 60-70% paragraphes narratifs avec phrases complètes
- 30-40% bullet points pour données/listes
- Éviter les sections composées uniquement de bullet points
- Chaque idée importante mérite un paragraphe de développement

QUALITÉ DU CONTENU:
- Développer les analyses en profondeur
- Expliquer les liens de causalité
- Fournir des exemples concrets
- Contextualiser chaque donnée chiffrée
- Privilégier le fond sur la forme

═══════════════════════════════════════════════════════════════

Réponds maintenant avec recherche approfondie et croisement systématique des sources."""
        
        # Client Perplexity utilisant le SDK OpenAI pour compatibilité
        try:
            client = OpenAI(
                api_key=PERPLEXITY_API_KEY,
                base_url=PERPLEXITY_BASE_URL,
                timeout=600.0  # 10 minutes pour rapports longs avec paragraphes narratifs
            )
            
            # Vérifier taille prompt
            if len(enhanced_prompt) > 15000:
                logger.warning(f"Prompt très long ({len(enhanced_prompt)} chars), troncature appliquée")
                enhanced_prompt = enhanced_prompt[:15000] + "\n\n[...Prompt tronqué pour limites techniques. Continuer l'analyse avec les éléments disponibles...]"
            
            response = client.chat.completions.create(
                model=selected_model,  # ← Modèle dynamique
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=0.2,  # Légèrement plus créatif pour paragraphes narratifs fluides
                max_tokens=max_tokens  # ← Dynamique selon modèle
            )
            
            return response.choices[0].message.content
            
        except Exception as api_error:
            logger.error(f"Perplexity API error with {selected_model}: {api_error}")
            return f"❌ **Erreur API Perplexity ({selected_model})**\n\n{str(api_error)[:300]}\n\nVérifiez votre clé API et votre quota."
        
    except Exception as e:
        logger.error(f"Critical error in Perplexity call: {e}")
        return f"❌ **Erreur critique**\n\n{str(e)[:300]}"

async def generate_business_analysis_safe(business_type: str, analysis_type: str, query: str, title: str = None, user_id: Optional[str] = None) -> AnalysisResponse:
    """Génère analyse avec gestion d'erreurs complète + sauvegarde memory-service"""
    try:
        is_deep_analysis = "approfondi" in analysis_type.lower()
        logger.info(f"Starting analysis: {business_type}/{analysis_type} (Deep: {is_deep_analysis})")
        
        # 1. Recherche documents sécurisée (augmenté à 12 pour plus de contexte)
        logger.info("📊 [1/5] Recherche documents RAG...")
        documents = search_documents_safe(query, top_k=12)
        logger.info(f"✓ [1/5] Trouvé {len(documents)} documents RAG")
        
        # 2. Formatage contexte sécurisé
        logger.info("📝 [2/5] Formatage contexte documentaire...")
        context = format_context_safe(documents)
        logger.info(f"✓ [2/5] Contexte formaté ({len(context)} caractères)")
        
        # 3. Création prompt optimisé avec détection de langue + multi-contexte
        detected_language = detect_query_language(query)
        logger.info(f"🌐 Langue détectée: {detected_language}")
        logger.info("🎯 [3/5] Création prompt optimisé (multi-contexte)...")
        prompt = await create_optimized_prompt(business_type, analysis_type, query, context, include_recommendations=True, language=detected_language, user_id=user_id)
        expected_sources = "60 sources" if is_deep_analysis else "40-60 sources"
        logger.info(f"✓ [3/5] Prompt créé (type: {expected_sources})")
        
        # 4. Appel Perplexity sécurisé avec RAG
        estimated_time = "90-120s" if is_deep_analysis else "45-60s"
        logger.info(f"🌐 [4/5] Appel Perplexity API ({expected_sources}, estimation: {estimated_time})...")
        content = call_perplexity_safe(
            prompt, 
            business_type, 
            rag_context=context,
            task_type="analysis"  # Force sonar-pro pour rapports longs
        )
        logger.info("✓ [4/5] Contenu généré par Perplexity")
        
        # 5. Construction réponse avec sources enrichies APA
        logger.info("✅ [5/5] Finalisation du rapport...")
        enriched_sources = [enrich_source_with_apa(d, i+1) for i, d in enumerate(documents)]
        logger.info(f"✓ [5/5] Rapport finalisé avec {len(enriched_sources)} sources RAG")
        
        final_title = title or f"Rapport {get_business_type_display_name(business_type)} - {analysis_type.replace('_', ' ').title()}"
        
        # 6. Sauvegarde dans memory-service (non-bloquant)
        asyncio.create_task(save_conversation_to_memory(
            user_id=user_id,
            query=query,
            response=content[:8000],  # Limit content size
            conversation_type="analysis",
            analysis_type=analysis_type,
            business_type=business_type
        ))
        logger.info(f"📝 Sauvegarde async dans memory-service pour user {user_id}")
        
        return AnalysisResponse(
            analysis_type=analysis_type,
            business_type=business_type,
            title=final_title,
            content=content,
            sources=enriched_sources,
            metadata={
                "query": query,
                "business_type": business_type,
                "documents_found": len(documents),
                "analysis_length": "extended_report",
                "model": get_model_for_task("analysis"),
                "provider": "Perplexity AI",
                "max_tokens": 8000,
                "status": "success",
                "citation_format": "APA",
                "saved_to_memory": True
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
    """Chat avec Perplexity uniquement (pas de RAG interne)"""
    try:
        # 1. Pas de recherche documents - Perplexity uniquement
        business_context = "Expert IA"  # Toujours générique
        
        # 2. Prompt chat COURT et CONCIS
        chat_prompt = f"""Tu es un assistant expert en intelligence stratégique.

QUESTION: {message}

RÈGLES DE RÉPONSE COURTE:
- Réponds en 2-4 paragraphes MAXIMUM
- Sois DIRECT et CONCIS
- Cite 1-2 sources pour les faits importants: (Source, Année)
- PAS de sections, PAS de listes à puces longues
- Style conversationnel et professionnel
- Va droit au but

Réponds maintenant de façon concise:"""

        # 3. Appel Perplexity direct (pas de RAG interne)
        response_content = call_perplexity_safe(
            chat_prompt, 
            business_type or "finance_banque", 
            rag_context="",
            task_type="chat"  # Force sonar pour chat court
        )
        
        # 4. Sauvegarde dans memory-service (non-bloquant)
        asyncio.create_task(save_conversation_to_memory(
            user_id="1",  # Default user for MVP (string for UUID compatibility)
            query=message,
            response=response_content,
            conversation_type="chat",
            analysis_type=None,
            business_type=business_type
        ))
        
        return ChatResponse(
            response=response_content,
            business_context=business_context,
            sources=[],  # Pas de sources RAG internes
            metadata={
                "message": message,
                "business_type": business_type,
                "documents_found": 0,  # RAG désactivé
                "model": get_model_for_task("chat"),
                "provider": "Perplexity AI",
                "mode": "perplexity_web_only",
                "saved_to_memory": True
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
        "service": "backend-intelligence-perplexity",
        "perplexity_configured": bool(PERPLEXITY_API_KEY),
        "perplexity_models": PERPLEXITY_MODELS,  # Multi-modèles
        "mode": "perplexity_web_only",
        "rag_internal": "disabled",
        "business_types": get_available_business_types(),
        "version": "3.1-multi-model"
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
        request.title,
        user_id=request.user_id
    )

@app.post("/business-analysis", response_model=AnalysisResponse)
async def business_analysis(request: BusinessAnalysisRequest):
    """Alias pour compatibilité"""
    return await generate_business_analysis_safe(
        request.business_type,
        request.analysis_type,
        request.query,
        request.title,
        user_id=request.user_id
    )

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: SchedulerAnalysisRequest):
    """
    Endpoint pour le scheduler-service - Compatible avec le format des veilles automatiques
    Accepte: query, analysis_type, sector, deep_analysis
    """
    try:
        # Mapper sector vers business_type si nécessaire
        business_type = request.sector if request.sector else "general"
        
        # Si deep_analysis est True, s'assurer que analysis_type contient "approfondi"
        analysis_type = request.analysis_type
        if request.deep_analysis and "approfondi" not in analysis_type.lower():
            analysis_type = f"{analysis_type}_approfondie"
        
        # Générer le titre automatiquement
        title = f"Veille Automatisée - {analysis_type.replace('_', ' ').title()}"
        
        logger.info(f"Scheduler analysis request: {business_type}/{analysis_type} (deep: {request.deep_analysis})")
        
        return await generate_business_analysis_safe(
            business_type=business_type,
            analysis_type=analysis_type,
            query=request.query,
            title=title
        )
    except Exception as e:
        logger.error(f"Error in /analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extended-analysis/stream")
async def extended_analysis_stream(request: BusinessAnalysisRequest):
    """Génère rapports avec streaming SSE et barre de progression en temps réel"""
    
    async def generate_sse() -> AsyncGenerator[str, None]:
        try:
            is_deep_analysis = "approfondi" in (request.analysis_type or "").lower()
            
            # Fonction helper pour créer les messages SSE
            def sse_msg(progress: int, step: str, message: str, **kwargs) -> str:
                data = {'progress': progress, 'step': step, 'message': message, **kwargs}
                return f"data: {json.dumps(data)}\n\n"
            
            # Étape 1: Démarrage (5%)
            yield sse_msg(5, 'start', 'Demarrage de analyse...')
            await asyncio.sleep(0.5)
            
            # Étape 2: Recherche documents (15%)
            yield sse_msg(15, 'search', 'Recherche de sources fiables...')
            documents = search_documents_safe(request.query, top_k=12)
            await asyncio.sleep(0.3)
            
            # Étape 3: Formatage contexte (25%)
            yield sse_msg(25, 'context', 'Preparation du contexte...')
            context = format_context_safe(documents)
            await asyncio.sleep(0.3)
            
            # Étape 4: Création prompt (30%)
            include_reco = request.include_recommendations if request.include_recommendations is not None else True
            # Détection automatique de la langue de la query utilisateur
            detected_language = detect_query_language(request.query)
            logger.info(f"🌐 Langue détectée automatiquement: {detected_language} pour query: '{request.query[:50]}...'")
            reco_status = "avec recommandations" if include_reco else "sans recommandations"
            lang_status = "EN" if detected_language == "en" else "FR"
            yield sse_msg(30, 'prompt', f'Construction de la requete ({reco_status}, {lang_status})...')
            prompt = await create_optimized_prompt(
                request.business_type or "general",
                request.analysis_type,
                request.query,
                context,
                include_recommendations=include_reco,
                language=detected_language,
                user_id=getattr(request, 'user_id', None)
            )
            await asyncio.sleep(0.3)
            
            # Étape 5: Appel Perplexity (35-85%)
            estimated_time = "90-120s" if is_deep_analysis else "45-60s"
            gen_msg = f"Generation du rapport ({estimated_time})..."
            yield sse_msg(35, 'generate', gen_msg)
            
            # Simuler progression pendant génération
            progress_task = asyncio.create_task(simulate_progress_updates())
            
            # Appel réel à Perplexity
            content = call_perplexity_safe(
                prompt,
                request.business_type or "general",
                rag_context=context,
                task_type="analysis"
            )
            
            progress_task.cancel()
            
            # Étape 6: Extraction du titre (90%)
            yield sse_msg(90, 'title', 'Extraction du titre...')
            
            # Extraire le titre de la première ligne
            lines = content.strip().split('\n')
            analysis_type_title = request.analysis_type.replace('_', ' ').title() if request.analysis_type else "Analyse"
            generated_title = request.title or analysis_type_title
            for line in lines[:5]:
                if line.startswith('# '):
                    generated_title = line.replace('# ', '').strip()
                    break
            
            await asyncio.sleep(0.3)
            
            # Étape 7: Finalisation (95%)
            yield sse_msg(95, 'finalize', 'Finalisation du rapport...')
            
            # Enrichir les sources
            enriched_sources = [enrich_source_with_apa(d, i+1) for i, d in enumerate(documents)]
            
            # Étape 8: Terminé (100%)
            result = {
                'progress': 100,
                'step': 'done',
                'message': 'Rapport genere avec succes!',
                'done': True,
                'data': {
                    'analysis_type': request.analysis_type,
                    'business_type': request.business_type or 'general',
                    'title': generated_title,
                    'content': content,
                    'sources': enriched_sources,
                    'metadata': {
                        'query': request.query,
                        'documents_found': len(documents),
                        'model': get_model_for_task("analysis"),
                        'provider': 'Perplexity AI'
                    },
                    'timestamp': datetime.now().isoformat()
                }
            }
            yield f"data: {json.dumps(result)}\n\n"
            
        except Exception as e:
            logger.error(f"SSE Analysis error: {e}")
            err_msg = f"Erreur: {str(e)[:200]}"
            yield sse_msg(0, 'error', err_msg, error=True)
    
    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

async def simulate_progress_updates():
    """Simuler des mises à jour de progression pendant la génération"""
    try:
        for i in range(40, 85, 5):
            await asyncio.sleep(3)  # Toutes les 3 secondes
    except asyncio.CancelledError:
        pass

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat intelligent - réponses courtes et concises"""
    return await generate_chat_response_safe(
        request.message,
        request.business_type,
        request.conversation_history
    )

@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """Streaming de la réponse du chat - réponses COURTES et CONCISES."""
    async def token_generator():
        try:
            # Prompt pour réponses COURTES (2-4 paragraphes)
            chat_prompt = f"""QUESTION: {request.message}

RÈGLES:
- Réponds en 2-4 paragraphes MAXIMUM
- Sois DIRECT et CONCIS  
- Style conversationnel
- Cite 1-2 sources pour faits importants: (Source, Année)
- PAS de listes à puces longues
- PAS de sections multiples

Réponds maintenant:"""

            # 2) Streaming Perplexity
            if not PERPLEXITY_API_KEY or not OPENAI_SDK_AVAILABLE:
                # Fallback non‑bloquant
                yield "Le streaming nécessite une configuration PERPLEXITY_API_KEY et le SDK OpenAI.\n"
                yield "[DONE]"
                return

            selected_model = get_model_for_task("chat")
            client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url=PERPLEXITY_BASE_URL, timeout=300.0)
            stream = client.chat.completions.create(
                model=selected_model,  # Modèle dynamique
                messages=[
                    {"role": "system", "content": f"Assistant spécialisé {business_context}. Utilise les documents fournis en priorité."},
                    {"role": "user", "content": chat_prompt}
                ],
                temperature=0.1,  # Réduit pour plus de précision
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

@app.get("/test-perplexity")
async def test_perplexity():
    """Test de connectivité pour tous les modèles Sonar configurés"""
    try:
        if not PERPLEXITY_API_KEY:
            return {"status": "error", "message": "PERPLEXITY_API_KEY not configured"}
        
        client = OpenAI(
            api_key=PERPLEXITY_API_KEY,
            base_url=PERPLEXITY_BASE_URL,
            timeout=30.0
        )
        
        # Tester chaque modèle configuré
        results = {}
        for task_type, model_name in PERPLEXITY_MODELS.items():
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=10
                )
                results[task_type] = {
                    "model": model_name,
                    "status": "✅ OK",
                    "response": response.choices[0].message.content[:50]
                }
            except Exception as e:
                logger.error(f"Test Perplexity error: {e}")
                results[task_type] = {
                    "model": model_name,
                    "status": f"❌ Error: {str(e)[:100]}"
                }
        
        return {
            "status": "success", 
            "models_tested": results,
            "config": PERPLEXITY_MODELS
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/check-api-status")
async def check_api_status():
    """Vérifie le statut de la clé API Perplexity et détecte les erreurs de quota"""
    try:
        if not PERPLEXITY_API_KEY:
            return {
                "status": "error",
                "message": "PERPLEXITY_API_KEY not configured",
                "api_key_configured": False
            }
        
        client = OpenAI(
            api_key=PERPLEXITY_API_KEY,
            base_url=PERPLEXITY_BASE_URL,
            timeout=30.0
        )
        
        # Test avec le modèle chat (le moins coûteux)
        test_model = get_model_for_task("chat")
        
        try:
            response = client.chat.completions.create(
                model=test_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            # Si on arrive ici, la clé fonctionne
            return {
                "status": "success",
                "api_key_configured": True,
                "api_key_valid": True,
                "test_model": test_model,
                "message": "✅ Clé API valide et fonctionnelle",
                "note": "Pour vérifier votre quota exact, consultez https://www.perplexity.ai/settings/api"
            }
            
        except Exception as api_error:
            error_str = str(api_error).lower()
            
            # Détection des erreurs courantes
            if "401" in error_str or "unauthorized" in error_str:
                return {
                    "status": "error",
                    "api_key_configured": True,
                    "api_key_valid": False,
                    "error_type": "unauthorized",
                    "message": "❌ Clé API invalide ou expirée",
                    "suggestion": "Vérifiez votre clé sur https://www.perplexity.ai/settings/api"
                }
            elif "429" in error_str or "rate limit" in error_str or "quota" in error_str:
                return {
                    "status": "error",
                    "api_key_configured": True,
                    "api_key_valid": True,
                    "error_type": "quota_exceeded",
                    "message": "⚠️ Quota dépassé ou limite de taux atteinte",
                    "suggestion": "Consultez votre quota sur https://www.perplexity.ai/settings/api et ajoutez des crédits si nécessaire"
                }
            elif "404" in error_str or "not found" in error_str:
                return {
                    "status": "error",
                    "api_key_configured": True,
                    "api_key_valid": True,
                    "error_type": "model_not_found",
                    "message": f"❌ Modèle '{test_model}' non trouvé",
                    "suggestion": "Vérifiez que le modèle est disponible avec votre plan sur https://www.perplexity.ai/settings/api"
                }
            else:
                return {
                    "status": "error",
                    "api_key_configured": True,
                    "api_key_valid": None,
                    "error_type": "unknown",
                    "message": f"❌ Erreur API: {str(api_error)[:200]}",
                    "suggestion": "Consultez https://www.perplexity.ai/settings/api pour vérifier votre compte"
                }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "api_key_configured": bool(PERPLEXITY_API_KEY)
        }

@app.get("/diagnostics")
async def diagnostics():
    """Diagnostics complets du système"""
    
    diagnostics_result = {
        "timestamp": datetime.now().isoformat(),
        "service": "backend-intelligence-perplexity",
        "version": "2.0-perplexity-rag"
    }
    
    # Versions des libs clés
    # Note: SDK OpenAI utilisé uniquement pour compatibilité avec Perplexity API
    try:
        diagnostics_result["versions"] = {
            "python": os.getenv("PYTHON_VERSION", "unknown"),
            "openai_sdk": metadata.version("openai") if OPENAI_SDK_AVAILABLE else "not-installed",
            "httpx": metadata.version("httpx") if "httpx" in {d.metadata["Name"].lower() for d in map(lambda n: metadata.distribution(n), metadata.packages_distributions().keys()) if False} else metadata.version("httpx")
        }
    except Exception:
        try:
            diagnostics_result["versions"] = {
                "openai_sdk": metadata.version("openai") if OPENAI_SDK_AVAILABLE else "not-installed",
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

    # Test Perplexity
    try:
        if PERPLEXITY_API_KEY:
            client = OpenAI(
                api_key=PERPLEXITY_API_KEY,
                base_url=PERPLEXITY_BASE_URL,
                timeout=300.0
            )
            # Test avec le modèle chat par défaut
            test_model = get_model_for_task("chat")
            test_response = client.chat.completions.create(
                model=test_model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            diagnostics_result["perplexity"] = {
                "status": "✅ Functional", 
                "models": PERPLEXITY_MODELS,
                "test_model": test_model
            }
        else:
            diagnostics_result["perplexity"] = {"status": "❌ Not configured", "models": None}
    except Exception as e:
        diagnostics_result["perplexity"] = {
            "status": f"❌ Error: {str(e)[:100]}", 
            "models": PERPLEXITY_MODELS
        }
    
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


# =============================================================================
# CONTEXT & MEMORY ENDPOINTS (RAG)
# =============================================================================

class TextContextRequest(BaseModel):
    content: str

@app.post("/context/text")
async def save_context_text(request: TextContextRequest, user_id: str = "default_user"):
    """Enregistre un contexte texte pour l'utilisateur"""
    try:
        result = save_text_context(user_id, request.content)
        return {"status": "success", "context": result}
    except Exception as e:
        logger.error(f"Error saving text context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/context/upload")
async def upload_context_document(
    file: UploadFile = File(...),
    user_id: str = "default_user"
):
    """
    Upload un document de contexte (PDF, DOCX, TXT)
    Extrait le texte et le sauvegarde comme contexte utilisateur
    """
    import tempfile
    import os as os_module

    # Validate file type
    filename = file.filename or "document"
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''

    allowed_types = {'pdf', 'docx', 'txt'}
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Type de fichier non supporté: {file_ext}. Types acceptés: {', '.join(allowed_types)}"
        )

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Extract text from file
        extracted_text = extract_text_from_file(tmp_path, file_ext)

        # Clean up temp file
        os_module.unlink(tmp_path)

        if not extracted_text:
            raise HTTPException(
                status_code=400,
                detail="Impossible d'extraire le texte du document. Vérifiez que le fichier n'est pas vide ou corrompu."
            )

        # Save as context
        result = save_document_context(user_id, filename, extracted_text, file_ext)

        logger.info(f"Document context uploaded for user {user_id[:8]}...: {filename}")

        return {"status": "success", "context": result}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document context: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement du document: {str(e)}")


@app.get("/context/current")
async def get_current_context(user_id: str = "default_user"):
    """Recupere les infos du contexte actuel de l'utilisateur"""
    try:
        context_info = get_user_context_info(user_id)
        if context_info:
            return context_info
        return {"type": None, "message": "No context set"}
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/context")
async def remove_context(user_id: str = "default_user"):
    """Supprime le contexte de l'utilisateur"""
    try:
        success = delete_user_context(user_id)
        return {"status": "success" if success else "not_found", "deleted": success}
    except Exception as e:
        logger.error(f"Error deleting context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/history")
async def get_memory_history(user_id: str = "default_user", limit: int = 20):
    """Recupere l'historique des conversations de l'utilisateur"""
    try:
        history = get_full_history(user_id, limit=limit)
        return {"conversations": history, "count": len(history)}
    except Exception as e:
        logger.error(f"Error getting memory history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class SearchMemoryRequest(BaseModel):
    query: str
    max_results: int = 10

@app.post("/memory/search")
async def search_memory(request: SearchMemoryRequest, user_id: str = "default_user"):
    """Recherche dans l'historique des conversations"""
    try:
        results = search_history(user_id, request.query, max_results=request.max_results)
        return {"results": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Error searching memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/memory")
async def clear_memory(user_id: str = "default_user"):
    """Supprime l'historique des conversations de l'utilisateur"""
    try:
        success = clear_user_memory(user_id)
        return {"status": "success" if success else "not_found", "cleared": success}
    except Exception as e:
        logger.error(f"Error clearing memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ASSISTANT INTELLIGENT - Endpoints
# =============================================================================

class AssistantChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default_user"
    user_email: Optional[str] = None
    conversation_history: Optional[List[Dict]] = []
    current_page: Optional[str] = None  # Pour contexte: 'home', 'watches', 'profile'


class AssistantChatResponse(BaseModel):
    message: str


def detect_intent_and_entities(message: str, conversation_history: List[Dict] = None) -> tuple:
    """
    Detecte l'intention de l'utilisateur et extrait les entites pertinentes.
    Retourne (intent, entities)
    """
    # #region agent log H1
    import re as _re_debug
    _email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    _found_emails = _re_debug.findall(_email_pattern, message)
    logger.info(f"[DEBUG-H1] Email extraction: message='{message[:100]}', found_emails={_found_emails}")
    # #endregion
    message_lower = message.lower()
    entities = {}
    
    # Extraire les emails du message et les ajouter aux entites
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    found_emails = re.findall(email_pattern, message)
    if found_emails:
        entities["emails"] = found_emails
    
    # Detection des intentions d'action
    if any(word in message_lower for word in ["creer", "créer", "nouvelle", "ajouter", "configurer"]):
        if any(word in message_lower for word in ["veille", "surveillance", "watch"]):
            intent = "create_watch"
            # Extraction du sujet
            for keyword in ["sur", "concernant", "à propos de", "about"]:
                if keyword in message_lower:
                    idx = message_lower.find(keyword) + len(keyword)
                    topic = message[idx:].strip().split(",")[0].split(".")[0].strip()
                    # Nettoyer le topic: retirer les emails et les mots cles d'envoi
                    if topic:
                        # Retirer les emails du topic
                        for email in found_emails:
                            topic = topic.replace(email, "").strip()
                        # Retirer les patterns "a envoyer a", "envoye a", etc.
                        topic = re.sub(r'\s*(a|à)\s*(envoyer|envoyé|envoyée)\s*(a|à)?\s*$', '', topic, flags=re.IGNORECASE).strip()
                        if topic:
                            entities["topic"] = topic
            # Detection de la frequence
            if "quotidien" in message_lower or "chaque jour" in message_lower:
                entities["frequency"] = "daily"
            elif "hebdomadaire" in message_lower or "chaque semaine" in message_lower:
                entities["frequency"] = "weekly_monday"
            elif "mensuel" in message_lower:
                entities["frequency"] = "monthly"
            return intent, entities
        
        if any(word in message_lower for word in ["rapport", "analyse", "report"]):
            intent = "generate_report"
            for keyword in ["sur", "concernant", "à propos de", "about"]:
                if keyword in message_lower:
                    idx = message_lower.find(keyword) + len(keyword)
                    query = message[idx:].strip().split(",")[0].split(".")[0].strip()
                    if query:
                        entities["query"] = query
            return intent, entities
    
    if any(word in message_lower for word in ["liste", "lister", "voir", "afficher", "montre", "quelles sont"]):
        if any(word in message_lower for word in ["veille", "veilles", "surveillance", "watches"]):
            return "list_watches", {}
    
    if any(word in message_lower for word in ["supprimer", "effacer", "retirer", "delete"]):
        if any(word in message_lower for word in ["veille", "watch"]):
            return "delete_watch", entities
    
    if any(word in message_lower for word in ["modifier", "changer", "mettre à jour", "update", "edit"]):
        if any(word in message_lower for word in ["veille", "watch"]):
            return "update_watch", entities
    
    # Detection des questions
    if any(word in message_lower for word in ["comment", "qu'est-ce", "c'est quoi", "explique", "how", "what", "pourquoi"]):
        return "explanation", entities
    
    # Detection de demande d'aide sur les fonctionnalites
    if any(word in message_lower for word in ["aide", "help", "fonctionnalit", "feature", "peut faire", "capable"]):
        return "explanation", entities
    
    # Par defaut: conversation generale
    return "conversation", entities


async def build_assistant_context(user_id: str, message: str) -> tuple:
    """
    Construit le contexte complet pour l'assistant:
    - Connaissance de l'application
    - Contexte RAG de l'utilisateur
    - Historique des conversations
    - Liste des veilles actuelles
    
    Retourne (context_prompt, sources_used)
    """
    sources_used = []
    context_parts = []
    
    # 1. Connaissance de l'application
    app_context = build_context_prompt()
    context_parts.append(app_context)
    sources_used.append("Documentation Prometheus")
    
    # 2. Contexte RAG de l'entreprise (multi-contexte via memory-service)
    try:
        user_context = await get_context_for_prompt(user_id)
        if user_context and len(user_context) > 50:
            context_parts.append(f"\n## Contexte de l'entreprise de l'utilisateur:\n{user_context[:4000]}")
            sources_used.append("Contexte entreprise")
    except Exception as e:
        logger.warning(f"Could not load user context: {e}")
    
    # 3. Historique des conversations recentes
    try:
        history_context = get_history_for_prompt(user_id, message, max_length=1000)
        if history_context and len(history_context) > 50:
            context_parts.append(f"\n## Historique recent des conversations:\n{history_context[:1000]}")
            sources_used.append("Historique conversations")
    except Exception as e:
        logger.warning(f"Could not load history: {e}")
    
    # 4. Liste des veilles actuelles (via API scheduler)
    try:
        import httpx
        scheduler_url = os.getenv("SCHEDULER_URL", "http://scheduler-service:8007")
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info(f"Fetching watches from {scheduler_url}/watches")
            response = await client.get(f"{scheduler_url}/watches")
            logger.info(f"Watches response status: {response.status_code}")
            if response.status_code == 200:
                watches = response.json()
                logger.info(f"Found {len(watches) if watches else 0} watches")
                if watches:
                    watches_info = "\n## Veilles configurees par l'utilisateur:\n"
                    for w in watches[:10]:  # Max 10
                        status = "Active" if w.get("is_active") else "Inactive"
                        watches_info += f"- {w['name']} (ID: {w['id']}): {w['topic']} - {status}\n"
                    context_parts.append(watches_info)
                    sources_used.append("Veilles utilisateur")
            else:
                logger.warning(f"Failed to fetch watches: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error fetching watches for context: {e}", exc_info=True)
    
    full_context = "\n".join(context_parts)
    return full_context, sources_used


async def generate_assistant_response(
    message: str,
    intent: str,
    entities: Dict,
    context: str,
    conversation_history: List[Dict]
) -> str:
    """
    Genere la reponse de l'assistant via Perplexity
    """
    if not PERPLEXITY_API_KEY or not OPENAI_SDK_AVAILABLE:
        return "Je suis desole, le service d'IA n'est pas disponible pour le moment."
    
    # Construire le prompt selon l'intention
    if intent == "create_watch":
        task_instruction = """
L'utilisateur souhaite creer une veille. Propose les parametres en fonction de ce qu'il a dit.
Si des informations manquent (sujet, frequence, email), demande-les poliment.
Resume les parametres proposes et indique que tu vas creer la veille si confirmee.
"""
    elif intent == "list_watches":
        task_instruction = """
L'utilisateur veut voir ses veilles. Presente la liste de maniere claire et propose des actions.
"""
    elif intent == "generate_report":
        task_instruction = """
L'utilisateur souhaite generer un rapport. Confirme le sujet et le type d'analyse.
Propose de lancer la generation si les parametres sont clairs.
"""
    elif intent == "explanation":
        task_instruction = """
L'utilisateur a une question sur le fonctionnement de Prometheus.
Reponds de maniere claire et concise en utilisant la documentation fournie.
Propose des actions concretes si pertinent.
"""
    else:
        task_instruction = """
Reponds de maniere amicale et professionnelle. Si l'utilisateur semble vouloir effectuer une action,
propose-la explicitement.
"""
    
    system_prompt = f"""{context}

## Ta mission actuelle:
{task_instruction}

## Regles:
- Sois concis (2-4 paragraphes max)
- Propose toujours des actions concretes quand c'est pertinent
- Si tu proposes une action, indique clairement les parametres
- Utilise un ton professionnel mais accessible
"""
    
    messages = [{"role": "system", "content": system_prompt}]

    # Ajouter l'historique de conversation (max 6 derniers)
    # S'assurer que les messages alternent correctement (user/assistant)
    last_role = "system"
    for msg in conversation_history[-6:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if not content:
            continue

        # Ensure alternation: after system/assistant, we need user; after user, we need assistant
        if last_role in ["system", "assistant"] and role == "user":
            messages.append({"role": "user", "content": content})
            last_role = "user"
        elif last_role == "user" and role == "assistant":
            messages.append({"role": "assistant", "content": content})
            last_role = "assistant"
        # Skip messages that would break alternation

    # Add the current user message
    # If the last message was from user, add a placeholder assistant response first
    if last_role == "user":
        messages.append({"role": "assistant", "content": "D'accord."})

    messages.append({"role": "user", "content": message})
    
    try:
        client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url=PERPLEXITY_BASE_URL, timeout=60.0)
        
        response = client.chat.completions.create(
            model=get_model_for_task("chat"),
            messages=messages,
            temperature=0.3,
            max_tokens=800
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        logger.error(f"Error generating assistant response: {e}")
        return "Une erreur s'est produite. Veuillez reessayer."


def is_app_help_question(message: str) -> bool:
    """Detecte si la question concerne l'aide sur l'application Prometheus."""
    message_lower = message.lower()
    app_keywords = [
        "comment", "aide", "help", "expliqu", "tutoriel", "guide",
        "prometheus", "plateforme", "application", "app",
        "veille", "rapport", "creer", "créer", "configurer",
        "fonctionn", "utiliser", "marche", "fonctionne",
        "bouton", "page", "menu", "interface", "etape", "étape"
    ]
    return any(kw in message_lower for kw in app_keywords)


async def generate_smart_chat_response(
    message: str,
    app_context: str,
    conversation_history: List[Dict]
) -> str:
    """
    Genere une reponse intelligente:
    - Questions sur l'app -> guide l'utilisateur avec le contexte app
    - Questions generales -> recherche web via Perplexity
    """
    is_help = is_app_help_question(message)
    
    if is_help:
        # Mode aide: utiliser le contexte de l'application
        system_prompt = f"""{app_context}

## Ta mission:
Tu es l'assistant de la plateforme Prometheus. Tu guides les utilisateurs sur:
- Comment creer et gerer des veilles automatisees
- Comment generer des rapports d'analyse  
- Les fonctionnalites de la plateforme
- Les bonnes pratiques d'utilisation

## Regles:
- Sois concis et clair (2-4 paragraphes max)
- Donne des instructions etape par etape quand c'est une question "comment faire"
- Utilise un ton professionnel mais accessible
- Propose des actions concretes
"""
    else:
        # Mode recherche: repondre avec recherche web
        system_prompt = """Tu es un assistant de recherche intelligent integre a la plateforme Prometheus.

## Ta mission:
Tu reponds aux questions generales de l'utilisateur en effectuant des recherches.
Tu fournis des informations precises, sourcees et a jour.

## Regles:
- Reponds de maniere structuree et claire
- Cite tes sources quand c'est pertinent
- Sois concis (3-5 paragraphes max)
- Si la question est liee a un sujet d'analyse strategique, suggere de generer un rapport complet via Prometheus
- Utilise un ton professionnel

## Contexte:
L'utilisateur utilise Prometheus, une plateforme d'intelligence strategique.
S'il pose une question qui pourrait faire l'objet d'une analyse approfondie, 
rappelle-lui qu'il peut generer un rapport complet depuis la page principale.
"""
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Ajouter l'historique de conversation (paires valides)
    history_pairs = []
    i = 0
    history = conversation_history[-6:] if conversation_history else []
    while i < len(history) - 1:
        user_msg = history[i]
        assistant_msg = history[i + 1]
        if user_msg.get("role") == "user" and assistant_msg.get("role") == "assistant":
            if user_msg.get("content") and assistant_msg.get("content"):
                history_pairs.append(user_msg)
                history_pairs.append(assistant_msg)
        i += 2
    
    for msg in history_pairs:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": message})
    
    try:
        client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url=PERPLEXITY_BASE_URL, timeout=60.0)
        
        # Utiliser un modele avec recherche pour les questions generales
        model = "sonar" if not is_help else get_model_for_task("chat")
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        logger.error(f"Error generating chat response: {e}")
        return "Une erreur s'est produite. Veuillez reessayer."


@app.post("/assistant/chat", response_model=AssistantChatResponse)
async def assistant_chat_endpoint(request: AssistantChatRequest):
    """
    Endpoint du chat assistant intelligent.
    - Questions sur l'app: guide l'utilisateur
    - Questions generales: recherche web via Perplexity
    """
    try:
        # Construire le contexte avec la connaissance de l'app
        context, _ = await build_assistant_context(
            request.user_id,
            request.message
        )
        
        # Generer la reponse (aide ou recherche selon la question)
        response_message = await generate_smart_chat_response(
            request.message,
            context,
            request.conversation_history or []
        )
        
        # Sauvegarder dans l'historique (legacy RAG)
        try:
            add_conversation(request.user_id, request.message, response_message, analysis_type="assistant_chat")
        except Exception as e:
            logger.warning(f"Could not save to RAG memory: {e}")
        
        # Sauvegarder dans memory-service (nouveau système)
        # Pass user_id directly - memory-service handles UUID to INT conversion
        user_id_for_memory = request.user_id if request.user_id else "1"

        asyncio.create_task(save_conversation_to_memory(
            user_id=user_id_for_memory,
            query=request.message,
            response=response_message,
            conversation_type="assistant_chat",
            analysis_type="assistant_chat",
            business_type=None
        ))
        logger.info(f"📝 Sauvegarde async conversation assistant pour user {user_id_for_memory[:16]}...")
        
        return AssistantChatResponse(message=response_message)
        
    except Exception as e:
        logger.error(f"Assistant chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)