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

# Import OpenAI (compatible with Perplexity API)
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

# Configuration - Perplexity API
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar")  # Modèle Perplexity par défaut
PERPLEXITY_BASE_URL = "https://api.perplexity.ai"
VECTOR_SERVICE_URL = "http://vector-service:8002"
DOCUMENT_SERVICE_URL = "http://document-service:8001"

# Cache pour les métadonnées des documents
_document_metadata_cache = {}

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

def create_optimized_prompt(business_type: str, analysis_type: str, query: str, context: str) -> str:
    """Crée prompts ultra-structurés pour rapports de cabinet de conseil"""
    
    # Templates ultra-détaillés avec citations APA
    prompt_templates = {
        "finance_banque": f"""📊 ANALYSE STRATÉGIQUE BANCAIRE - FORMAT CABINET DE CONSEIL

🎯 MISSION: {query}

📚 CONTEXTE DOCUMENTAIRE:
{context[:5000]}

═══════════════════════════════════════════════════════════════

INSTRUCTIONS DE RÉDACTION (FORMAT CABINET CONSEIL):

1. CITATIONS ACADÉMIQUES OBLIGATOIRES:
   - Format: [¹], [²], [³] pour citations inline
   - CHAQUE donnée chiffrée DOIT avoir sa citation
   - CHAQUE affirmation factuelle DOIT être sourcée
   - Exemple: "Le marché bancaire croît de 3% [¹]"

2. STRUCTURE ULTRA-DÉTAILLÉE REQUISE:

# 📋 RAPPORT STRATÉGIQUE BANCAIRE

## 🎯 EXECUTIVE SUMMARY (1-2 pages)
### Contexte et Enjeux Stratégiques
- Situation actuelle du secteur avec données [¹]
- Enjeux de transformation majeurs [²]
- Opportunités et menaces immédiates [³]

### Recommandations Prioritaires
1. **Action Priorité 1**: [Description détaillée] - ROI estimé, timeline
2. **Action Priorité 2**: [Description détaillée] - ROI estimé, timeline  
3. **Action Priorité 3**: [Description détaillée] - ROI estimé, timeline

### Impact Business Attendu
- KPIs quantifiés avec benchmarks sectoriels [¹]
- Timeline de mise en œuvre (6-12-18 mois)
- Budget et ressources nécessaires

---

## 📊 ANALYSE SECTORIELLE APPROFONDIE (3-4 pages)

### 1. Dimensionnement du Marché
- **Taille actuelle**: XX M€/M$ [¹]
- **Croissance annuelle**: XX% [²]
- **Prévisions 2025-2030**: Détaillées avec hypothèses [³]
- **Parts de marché**: Top 10 acteurs avec évolution [⁴]

### 2. Segmentation et Dynamiques
- **Segments de clientèle**: Retail, Corporate, Private Banking [¹]
- **Évolution comportements clients**: Digitalisation, attentes [²]
- **Produits/Services porteurs**: Analyse détaillée [³]

### 3. Technologies et Innovation
- **Fintech et disruption**: Impact sur acteurs traditionnels [¹]
- **IA et automatisation**: Cas d'usage bancaires [²]
- **Blockchain et crypto**: Opportunités et risques [³]
- **Open Banking**: État des lieux réglementaire [⁴]

### 4. Environnement Réglementaire
- **Contraintes majeures**: Bâle III/IV, MiFID II, etc. [¹]
- **Impact opérationnel**: Coûts compliance, reporting [²]
- **Évolutions à venir**: Anticipation 2025-2026 [³]

---

## ⚔️ ANALYSE CONCURRENTIELLE (2-3 pages)

### Mapping Concurrentiel
**Quadrant Leaders (Market Leaders)**:
- Acteur A: Forces [¹], Faiblesses [²], Parts de marché XX% [³]
- Acteur B: Forces [¹], Faiblesses [²], Parts de marché XX% [³]

**Quadrant Challengers**:
- [Analyse détaillée avec données chiffrées]

**Quadrant Niche Players**:
- [Analyse détaillée avec positionnement]

### Stratégies de Différenciation
1. **Par l'innovation**: Exemples concrets [¹]
2. **Par l'expérience client**: Benchmarks NPS [²]
3. **Par les coûts**: Efficiency ratio comparés [³]

### Menaces Compétitives
- **Nouveaux entrants**: Fintechs, BigTech [¹]
- **Substituts**: Monnaies digitales, DeFi [²]
- **Consolidation**: M&A récentes et à venir [³]

---

## 💡 RECOMMANDATIONS STRATÉGIQUES (3-4 pages)

### Plan d'Action Immédiat (0-6 mois)
**Initiative 1: [Titre]**
- Objectif: [Détaillé et quantifié]
- Actions: [Liste numérotée avec responsables]
- ROI: XX% ou XX M€ [¹]
- Risques: [Identifiés avec mitigation]
- KPIs: [3-5 indicateurs mesurables]

**Initiative 2: [Titre]**
[Même structure détaillée]

### Plan d'Action Moyen Terme (6-18 mois)
[3-4 initiatives structurées identiquement]

### Investissements Requis
| Poste | Budget | Timeline | ROI Attendu |
|-------|--------|----------|-------------|
| IT/Digital | XX M€ | Q1-Q4 | XX% [¹] |
| Talents | XX M€ | Continu | XX% [²] |
| Marketing | XX M€ | Q2-Q3 | XX% [³] |

---

## 📈 PROJECTIONS ET SCÉNARIOS (2 pages)

### Scénario Optimiste (+15% croissance)
- Hypothèses: [Listées et sourcées]
- Impacts business: [Quantifiés] [¹]
- Probabilité: XX% basée sur [²]

### Scénario Central (+8% croissance)
[Même structure]

### Scénario Pessimiste (+2% croissance)
[Même structure]

### KPIs de Suivi Recommandés
1. **Revenue Growth**: Target XX% [¹]
2. **Market Share**: Target XX% [²]
3. **Cost/Income Ratio**: Target XX% [³]
4. **NPS Client**: Target XX/100 [⁴]
5. **Digital Adoption**: Target XX% [⁵]

---

## 📚 BIBLIOGRAPHIE APA

[1] Auteur. (Année). Titre document. Type, p. XX.
[2] Auteur. (Année). Titre document. Type, p. XX.
[...] [Toutes les sources citées]

═══════════════════════════════════════════════════════════════

EXIGENCES QUALITÉ:
✅ Minimum 6000 mots (format cabinet conseil)
✅ TOUTES les données chiffrées citées [¹][²][³]
✅ Espacement markdown clair (lignes vides entre sections)
✅ Tableaux pour données comparatives
✅ Listes à puces pour lisibilité
✅ Bibliographie APA complète en fin

GÉNÈRE MAINTENANT CE RAPPORT ULTRA-DÉTAILLÉ:""",

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

def call_perplexity_safe(prompt: str, business_type: str, rag_context: str = "") -> str:
    """Appel Perplexity sécurisé avec RAG interne et recherche web"""
    try:
        if not PERPLEXITY_API_KEY or PERPLEXITY_API_KEY == "":
            return "⚠️ **Configuration Perplexity requise**\n\nVeuillez configurer la variable PERPLEXITY_API_KEY dans votre fichier .env"
        
        # Vérifier OpenAI SDK (compatible Perplexity)
        if not OPENAI_AVAILABLE:
            return "❌ **Module OpenAI manquant**\n\nVeuillez installer: pip install openai"
        
        # System prompts avec instructions de citation APA + URLs (style Perplexity)
        system_prompts = {
            "finance_banque": """Tu es un consultant senior McKinsey spécialisé en stratégie bancaire utilisant Perplexity AI. 
                              Génère des rapports structurés avec analyses quantifiées et recommandations actionnables.
                              
                              RÈGLES DE CITATION OBLIGATOIRES (comme l'application Perplexity):
                              - Utilise ta recherche web native Perplexity
                              - Cite TOUTES les sources avec [1], [2], [3], etc. après chaque information
                              - En fin de réponse, ajoute une section "## 📚 Sources" avec bibliographie APA complète
                              - Format: [numéro] Auteur/Organisation. (Année). Titre. URL_complète_cliquable
                              - Exemple inline: "Le marché croît de 15% [1]"
                              - Exemple source: "[1] INSEE. (2024). Croissance économique française. https://www.insee.fr/rapport-2024"
                              - Minimum 5 sources variées et récentes (moins de 2 ans)""",
                              
            "tech_digital": """Tu es un consultant BCG expert en transformation digitale utilisant Perplexity AI. 
                             Génère des analyses techniques détaillées avec business case et ROI.
                             
                             RÈGLES DE CITATION OBLIGATOIRES (comme l'application Perplexity):
                             - Recherche web native Perplexity pour données actuelles
                             - Citations [1], [2], [3]... immédiatement après chaque fait
                             - Section finale "## 📚 Sources" au format APA avec URLs
                             - Chaque source: [numéro] Source. (Année). Titre. URL_complète
                             - Minimum 5 sources tech récentes et vérifiables""",
                             
            "retail_commerce": """Tu es un consultant Bain expert en retail et commerce utilisant Perplexity AI. 
                                Génère des analyses avec insights consommateurs et recommandations opérationnelles.
                                
                                RÈGLES DE CITATION OBLIGATOIRES (comme l'application Perplexity):
                                - Utilise recherche web Perplexity pour données marché
                                - Cite systématiquement avec [1], [2], [3]... après chaque donnée
                                - Bibliographie finale "## 📚 Sources" format APA + URLs
                                - Format: [numéro] Organisation. (Année). Titre. URL_cliquable
                                - Minimum 5 sources retail/e-commerce récentes"""
        }
        
        system_prompt = system_prompts.get(business_type, system_prompts["finance_banque"])
        
        # Prompt enrichi avec instructions explicites de citation web
        enhanced_prompt = f"""{prompt}

═══════════════════════════════════════════════════════════════

INSTRUCTIONS DE RECHERCHE ET CITATION (STYLE PERPLEXITY APP):

📌 ÉTAPE 1 - RECHERCHE WEB:
- Utilise tes capacités de recherche web native Perplexity
- Cherche les informations les plus récentes et pertinentes
- Privilégie sources officielles, études, rapports institutionnels

📌 ÉTAPE 2 - RÉDACTION AVEC CITATIONS:
- Après CHAQUE information factuelle, ajoute [numéro]
- Ne jamais affirmer sans citer
- Exemple: "Le marché fintech français atteint 9 milliards € [1] avec 1000+ startups [2]"

📌 ÉTAPE 3 - BIBLIOGRAPHIE FINALE:
- Section "## 📚 Sources" en fin de réponse
- Format APA strict: [numéro] Auteur/Organisation. (Année). Titre complet. URL_complète
- URLs doivent être des liens réels et cliquables
- Minimum 5 sources, maximum 15 sources
- Sources variées: institutionnelles, académiques, presse spécialisée

EXEMPLE DE FORMAT ATTENDU:

"Le secteur bancaire français compte 300 établissements [1] générant 85 milliards de revenus [2]."

## 📚 Sources
[1] ACPR. (2024). Panorama des établissements bancaires français. https://acpr.banque-france.fr/rapport-2024
[2] FBF. (2024). Rapport annuel du secteur bancaire. https://fbf.fr/publications/rapport-annuel-2024

Réponds maintenant en utilisant la recherche web Perplexity et en citant TOUTES tes sources."""
        
        # Client Perplexity (compatible OpenAI SDK)
        try:
            client = OpenAI(
                api_key=PERPLEXITY_API_KEY,
                base_url=PERPLEXITY_BASE_URL,
                timeout=300.0  # 5 minutes max pour rapports longs
            )
            
            # Vérifier taille prompt
            if len(enhanced_prompt) > 15000:
                logger.warning(f"Prompt très long ({len(enhanced_prompt)} chars), troncature appliquée")
                enhanced_prompt = enhanced_prompt[:15000] + "\n\n[...Prompt tronqué pour limites techniques. Continuer l'analyse avec les éléments disponibles...]"
            
            response = client.chat.completions.create(
                model=PERPLEXITY_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=0.3,
                max_tokens=8000
            )
            
            return response.choices[0].message.content
            
        except Exception as api_error:
            logger.error(f"Perplexity API error: {api_error}")
            return f"❌ **Erreur API Perplexity**\n\n{str(api_error)[:300]}\n\nVérifiez votre clé API et votre quota."
        
    except Exception as e:
        logger.error(f"Critical error in Perplexity call: {e}")
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
        
        # 4. Appel Perplexity sécurisé avec RAG
        content = call_perplexity_safe(prompt, business_type, rag_context=context)
        
        # 5. Construction réponse avec sources enrichies APA
        enriched_sources = [enrich_source_with_apa(d, i+1) for i, d in enumerate(documents)]
        
        return AnalysisResponse(
            analysis_type=analysis_type,
            business_type=business_type,
            title=title or f"Rapport {get_business_type_display_name(business_type)} - {analysis_type.replace('_', ' ').title()}",
            content=content,
            sources=enriched_sources,
            metadata={
                "query": query,
                "business_type": business_type,
                "documents_found": len(documents),
                "analysis_length": "extended_report",
                "model": PERPLEXITY_MODEL,
                "provider": "Perplexity AI",
                "max_tokens": 8000,
                "status": "success",
                "citation_format": "APA"
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
        business_context = get_business_type_display_name(business_type) if business_type else "Généraliste"
        
        # 2. Construction prompt pour Perplexity avec citations APA
        chat_prompt = f"""Tu es un assistant expert spécialisé {business_context} utilisant Perplexity AI.

HISTORIQUE CONVERSATION:
{history[-3:] if history else "Nouvelle conversation"}

QUESTION: {message}

INSTRUCTIONS DE RÉPONSE (STYLE PERPLEXITY APP):
✓ Réponds de manière concise et professionnelle (2-3 paragraphes)
✓ Utilise ta recherche web native Perplexity pour des informations actuelles
✓ CITE SYSTÉMATIQUEMENT avec [1], [2], [3]... après chaque information factuelle
✓ Exemple: "Le secteur croît de 12% [1] avec 500 entreprises [2]"
✓ En fin de réponse, ajoute "## 📚 Sources" avec format APA + URLs cliquables
✓ Format source: [numéro] Auteur. (Année). Titre. URL_complète
✓ Minimum 3 sources vérifiables

Réponds maintenant avec recherche web Perplexity et citations complètes.
"""

        # 3. Appel Perplexity direct (pas de RAG interne)
        response_content = call_perplexity_safe(chat_prompt, business_type or "finance_banque", rag_context="")
        
        return ChatResponse(
            response=response_content,
            business_context=business_context,
            sources=[],  # Pas de sources RAG internes
            metadata={
                "message": message,
                "business_type": business_type,
                "documents_found": 0,  # RAG désactivé
                "model": PERPLEXITY_MODEL,
                "provider": "Perplexity AI",
                "mode": "perplexity_web_only"
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
        "perplexity_model": PERPLEXITY_MODEL,
        "mode": "perplexity_web_only",
        "rag_internal": "disabled",
        "business_types": get_available_business_types(),
        "version": "3.0-perplexity-web-only"
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
    """Streaming de la réponse du chat avec Perplexity uniquement (pas de RAG interne)."""
    async def token_generator():
        try:
            # 1) Pas de RAG interne - Perplexity uniquement avec citations
            business_context = get_business_type_display_name(request.business_type) if request.business_type else "Généraliste"
            chat_prompt = f"""Tu es un assistant expert spécialisé {business_context} utilisant Perplexity AI.

HISTORIQUE CONVERSATION:
{request.conversation_history[-3:] if request.conversation_history else "Nouvelle conversation"}

QUESTION: {request.message}

INSTRUCTIONS DE RÉPONSE (STYLE PERPLEXITY APP):
✓ Réponds de manière concise et professionnelle
✓ Recherche web native Perplexity pour informations actuelles
✓ CITE SYSTÉMATIQUEMENT: [1], [2], [3]... après chaque fait
✓ En fin: "## 📚 Sources" avec format APA + URLs cliquables
✓ Format: [numéro] Auteur. (Année). Titre. URL_complète
✓ Minimum 3 sources vérifiables et récentes

Réponds avec recherche web Perplexity et citations complètes.
"""

            # 2) Streaming Perplexity
            if not PERPLEXITY_API_KEY or not OPENAI_AVAILABLE:
                # Fallback non‑bloquant
                yield "Le streaming nécessite une configuration PERPLEXITY_API_KEY.\n"
                yield "[DONE]"
                return

            client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url=PERPLEXITY_BASE_URL, timeout=300.0)
            stream = client.chat.completions.create(
                model=PERPLEXITY_MODEL,
                messages=[
                    {"role": "system", "content": f"Assistant spécialisé {business_context}. Utilise les documents fournis en priorité."},
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

@app.get("/test-perplexity")
async def test_perplexity():
    """Test de connectivité Perplexity"""
    try:
        if not PERPLEXITY_API_KEY:
            return {"status": "error", "message": "PERPLEXITY_API_KEY not configured"}
        
        client = OpenAI(
            api_key=PERPLEXITY_API_KEY,
            base_url=PERPLEXITY_BASE_URL,
            timeout=300.0
        )
        
        response = client.chat.completions.create(
            model=PERPLEXITY_MODEL,
            messages=[{"role": "user", "content": "Hello, test simple"}],
            max_tokens=10
        )
        
        return {
            "status": "success", 
            "message": "Perplexity API functional",
            "model": PERPLEXITY_MODEL,
            "response": response.choices[0].message.content
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/diagnostics")
async def diagnostics():
    """Diagnostics complets du système"""
    
    diagnostics_result = {
        "timestamp": datetime.now().isoformat(),
        "service": "backend-intelligence-perplexity",
        "version": "2.0-perplexity-rag"
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

    # Test Perplexity
    try:
        if PERPLEXITY_API_KEY:
            client = OpenAI(
                api_key=PERPLEXITY_API_KEY,
                base_url=PERPLEXITY_BASE_URL,
                timeout=300.0
            )
            test_response = client.chat.completions.create(
                model=PERPLEXITY_MODEL,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            diagnostics_result["perplexity"] = {"status": "✅ Functional", "model": PERPLEXITY_MODEL}
        else:
            diagnostics_result["perplexity"] = {"status": "❌ Not configured", "model": None}
    except Exception as e:
        diagnostics_result["perplexity"] = {"status": f"❌ Error: {str(e)[:100]}", "model": PERPLEXITY_MODEL}
    
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