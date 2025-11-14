================================================================================
              CAHIER DES CHARGES - AXIAL INTELLIGENCE PLATFORM
                    Intelligence Stratégique par IA
================================================================================

VERSION: 2.1
DATE: Octobre 2024
CLIENT: Axial
PROJET: Migration API OpenAI vers Sonar (Perplexity AI) + RAG Avancé
OBJECTIF: Scale-up développement par prestataire externe

================================================================================
                          RÉSUMÉ EXÉCUTIF
================================================================================

🎯 OBJECTIF PROJET
------------------
Évolution majeure de la plateforme Axial Intelligence avec 3 objectifs clés:
  1. Migration complète OpenAI → Sonar (Perplexity AI)
  2. Implémentation RAG avancé multi-sources (docs + base connaissances + web)
  3. Développement module veille réglementaire automatisée

📊 PÉRIMÈTRE
------------
9 microservices actuels + 3 nouveaux services:
  - Migration: backend-service, rag-service (→ enhanced-rag-service)
  - Nouveaux: knowledge-base-service, regulatory-watch-service
  - Frontend: Nouveaux composants Next.js (dashboard veille, citations)
  
⏱️ DURÉE & BUDGET
------------------
Durée totale: 35 jours ouvrés (7 semaines)
  • Phase 1-6 (Migration Sonar): 18 jours
  • Phase 7 (Base connaissances): 5 jours
  • Phase 8 (RAG hybride): 6 jours
  • Phase 9 (Veille réglementaire): 7 jours (1 jour chevauchement)

Budget: [À définir] - Option forfait modulaire possible

🚀 BÉNÉFICES ATTENDUS
----------------------
Performance:
  ✓ Latence analyses: -20% (Sonar plus rapide)
  ✓ Coûts API: -30% vs OpenAI
  ✓ First token streaming: -40%

Fonctionnalités:
  ✓ RAG hybride: pertinence +20%, couverture sujets pointus
  ✓ Veille réglementaire: monitoring 20+ sources officielles
  ✓ Alertes temps réel: email + Slack <5 min
  ✓ Base connaissances: 600+ entrées métier (6 secteurs × 100)
  ✓ Citations traçables multi-sources: [Doc], [KB], [Web]

🔑 JALONS MAJEURS
-----------------
J+3   → Stratégie validée (embeddings, RAG, sources réglementaires)
J+18  → Migration Sonar complète en production
J+29  → RAG hybride opérationnel avec benchmarks
J+35  → Sign-off final v2.1 (veille réglementaire + dashboard)

🎓 LIVRABLES
------------
Code:
  • 3 nouveaux microservices (knowledge-base, enhanced-rag, regulatory-watch)
  • Frontend: 6 nouveaux composants React (veille, citations, timeline)
  • Modules réutilisables: sonar_client, rag_fusion, scrapers, alert_manager

Documentation:
  • Architecture RAG multi-sources (diagrammes + specs)
  • Guide sources réglementaires (20+ URLs par secteur)
  • Documentation Swagger 3 nouveaux services
  • Benchmarks comparatifs (OpenAI vs Sonar, RAG simple vs hybride)

Tests:
  • Suite tests >80% coverage (pytest)
  • Tests scrapers sources officielles (mocks)
  • Tests end-to-end RAG hybride
  • Validation qualitative 30 analyses métiers

Formation:
  • Session 2h équipe Axial (visio enregistrée)
  • Guide admin veille réglementaire (PDF 20 pages)
  • Troubleshooting scraping & alertes (FAQ)

⚠️ RISQUES & MITIGATIONS
-------------------------
Risque ÉLEVÉ: Scrapers bloqués par sources officielles (robots.txt, rate limit)
  → Mitigation: API officielles quand disponibles, fallback Sonar search

Risque MOYEN: RAG hybride latence >20s (3 sources parallèles)
  → Mitigation: Async/await, timeout 5s par source, fallback RAG simple

Risque FAIBLE: Coûts Sonar supérieurs prévisions
  → Mitigation: Monitoring tokens, alertes budgétaires, cache analyses fréquentes

================================================================================
                        1. CONTEXTE ET OBJECTIFS
================================================================================

1.1 PRÉSENTATION DU PROJET
---------------------------
Axial Intelligence Platform est une plateforme de veille stratégique et 
d'intelligence business qui transforme des documents PDF en insights 
actionnables grâce à l'IA. La plateforme propose 5 types d'analyses 
spécialisées avec rapports professionnels exportables en PDF.

1.2 PÉRIMÈTRE ACTUEL (MVP v1.1)
--------------------------------
✅ Architecture microservices complète (9 services)
✅ Ingestion et indexation automatique de PDFs
✅ Recherche sémantique (embeddings + vector search)
✅ 5 types d'analyses IA spécialisées par secteur
✅ Génération de rapports PDF professionnels
✅ Frontend moderne Next.js avec design "Liquid Glass"
✅ Chat intégré au dashboard avec streaming
✅ 6 secteurs d'activité pré-configurés

1.3 OBJECTIF DE LA MISSION (VERSION 2.1)
-----------------------------------------
MIGRATION CRITIQUE: Remplacer l'API OpenAI par l'API Sonar (Perplexity AI)
pour toutes les fonctionnalités d'analyse et de génération de contenu.

NOUVELLES FONCTIONNALITÉS MAJEURES (v2.1):
🆕 VEILLE RÉGLEMENTAIRE - Module dédié monitoring réglementations
🆕 RAG AVANCÉ - Architecture hybride Sonar + base de données spécialisée
🆕 BASE CONNAISSANCES MÉTIER - Repository sujets pointus (réglementaire, technique)

RAISONS DE LA MIGRATION:
- Coûts API réduits
- Performances accrues (latence)
- Recherche web intégrée (sources temps réel via Sonar)
- Meilleure fraîcheur des données (veille réglementaire automatique)
- Support multi-modèles (sonar-pro, sonar-small)
- RAG hybride (documents internes + web + base métier)

================================================================================
                    2. ARCHITECTURE TECHNIQUE ACTUELLE
================================================================================

2.1 STACK TECHNOLOGIQUE
------------------------
Backend:
  - Python 3.11
  - FastAPI (framework API REST)
  - SQLAlchemy (ORM PostgreSQL)
  - Pydantic (validation données)
  - Loguru (logging)
  - OpenAI Python SDK 1.54.4 (À REMPLACER)

Frontend:
  - Next.js 14.0.3 (App Router)
  - React 18
  - TypeScript
  - Tailwind CSS + Framer Motion
  - Design: Liquid Glass / Glassmorphism

Base de données:
  - PostgreSQL 15 (documents, rapports, métadonnées)
  - Qdrant v1.5.1 (embeddings vectoriels, recherche sémantique)

Conteneurisation:
  - Docker + Docker Compose
  - Volumes persistants (postgres_data, qdrant_data)

2.2 MICROSERVICES EXISTANTS
----------------------------
Services Backend (ports):
  1. gateway-api (8000) - Point d'entrée unifié, routing, Swagger
  2. document-service (8001) - Ingestion PDFs, extraction texte, chunking
  3. vector-service (8002) - Embeddings OpenAI, indexation Qdrant
  4. rag-service (8003) - Recherche sémantique + synthèse IA
  5. report-service (8004) - Génération rapports PDF (ReportLab)
  6. status-service (8005) - Monitoring, health checks, stats
  7. backend-service (8006) - Orchestration analyses business, chat streaming

Services Frontend (ports):
  8. frontend-gradio (7860) - Interface Gradio (legacy, optionnel)
  9. frontend-openwebui (3000) - Interface Next.js moderne (principale)

Services Infrastructure:
  - postgres (5432) - Base relationnelle
  - qdrant (6333) - Vector database

2.3 FLUX DE DONNÉES PRINCIPAUX
-------------------------------
Ingestion Documents:
  User Upload PDF → document-service (extraction texte)
    → vector-service (embeddings OpenAI) → Qdrant (indexation)
    → PostgreSQL (métadonnées)

Analyse Stratégique:
  User Query → backend-service (sélection prompt métier)
    → rag-service (recherche vectorielle Qdrant)
    → OpenAI API (génération analyse) ← **POINT DE MIGRATION**
    → Formatage réponse → Frontend

Chat Expert:
  User Message → backend-service (/chat ou /chat/stream)
    → rag-service (contexte documentaire)
    → OpenAI API streaming ← **POINT DE MIGRATION**
    → Frontend (affichage progressif)

Export PDF:
  Analyse complétée → report-service
    → ReportLab (génération PDF consulting-style)
    → Stockage data/reports/ → Téléchargement user

2.4 VARIABLES D'ENVIRONNEMENT CLÉS
-----------------------------------
Fichier: .env
```
OPENAI_API_KEY=sk-proj-...                    # ← À REMPLACER par SONAR_API_KEY
EMBEDDING_MODEL=text-embedding-3-small        # OpenAI embeddings
CHAT_MODEL=gpt-4o-mini                        # ← À REMPLACER par sonar-pro

DATABASE_URL=postgresql://user:password@postgres:5432/insight_db
QDRANT_URL=http://qdrant:6333
VECTOR_SERVICE_URL=http://vector-service:8002

COMPOSE_PROJECT_NAME=insight_mvp              # Nom projet Docker (important!)
```

================================================================================
                    3. SPÉCIFICATIONS MIGRATION SONAR
================================================================================

3.1 API SONAR (PERPLEXITY AI) - CARACTÉRISTIQUES
-------------------------------------------------
Documentation: https://docs.perplexity.ai/docs/getting-started

Endpoint principal:
  POST https://api.perplexity.ai/chat/completions

Headers requis:
  Authorization: Bearer $SONAR_API_KEY
  Content-Type: application/json

Modèles disponibles:
  - sonar-pro (recommandé analyses longues, qualité max)
  - sonar (équilibré coût/performance)
  - sonar-small (rapide, économique)

Avantages vs OpenAI:
  ✓ Recherche web intégrée (sources actualisées)
  ✓ Citations automatiques avec URLs
  ✓ Latence réduite ~30%
  ✓ Coûts inférieurs ~40%
  ✓ Pas de rate limiting agressif

3.2 POINTS DE MIGRATION CRITIQUES
----------------------------------

A. EMBEDDINGS (vector-service)
-------------------------------
État actuel:
  - Utilise openai.embeddings.create()
  - Modèle: text-embedding-3-small (1536 dimensions)
  - Fichier: vector-service/app/fixed_main.py

ACTION REQUISE:
  ⚠️ SONAR N'A PAS D'API EMBEDDINGS PROPRE
  
  OPTION 1 (Recommandée): Garder OpenAI pour embeddings uniquement
    → Ajouter variable EMBEDDING_PROVIDER=openai dans .env
    → Créer client OpenAI séparé pour embeddings
    → Permet cohérence index Qdrant existant
  
  OPTION 2: Migration vers embeddings open-source
    → Sentence-Transformers (multilingual-e5-large)
    → Nécessite ré-indexation COMPLÈTE de Qdrant
    → Impact: perte données vectorielles actuelles

DÉCISION ATTENDUE DU CLIENT.

B. GÉNÉRATION DE CONTENU (rag-service)
---------------------------------------
État actuel:
  - Fichier: rag-service/app/rag_main.py
  - Fonction: call_openai_safe()
  - Endpoints: /synthesize, /ask_question, /generate_report

Code actuel (ligne ~180):
```python
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY, timeout=30.0)

def call_openai_safe(prompt: str, context: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": context}
        ],
        temperature=0.3,
        max_tokens=4000
    )
    return response.choices[0].message.content
```

Migration vers Sonar:
```python
import requests

SONAR_API_KEY = os.getenv("SONAR_API_KEY")
SONAR_MODEL = os.getenv("SONAR_MODEL", "sonar-pro")

def call_sonar_safe(prompt: str, context: str) -> str:
    headers = {
        "Authorization": f"Bearer {SONAR_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": SONAR_MODEL,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": context}
        ],
        "temperature": 0.3,
        "max_tokens": 4000,
        "search_domain_filter": ["perplexity.ai"],  # Optionnel
        "return_citations": True                    # Activer sources
    }
    
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code != 200:
        raise Exception(f"Sonar API error: {response.text}")
    
    data = response.json()
    return data['choices'][0]['message']['content']
```

FICHIERS À MODIFIER:
  - rag-service/app/rag_main.py (priorité 1)
  - rag-service/requirements.txt (retirer openai, ajouter requests si absent)

C. CHAT STREAMING (backend-service)
------------------------------------
État actuel:
  - Fichier: backend-service/app/main.py
  - Endpoints: POST /chat (non-streaming), POST /chat/stream (streaming)
  - Utilise openai.chat.completions.create(stream=True)

Code streaming actuel (ligne ~350):
```python
@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    client = OpenAI(api_key=OPENAI_API_KEY, timeout=60.0)
    
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=2000,
        stream=True  # ← Streaming activé
    )
    
    async def generate():
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
        yield "[DONE]"
    
    return StreamingResponse(generate(), media_type="text/plain")
```

Migration Sonar streaming:
```python
@app.post("/chat/stream")
async def chat_stream_sonar(request: ChatRequest):
    headers = {
        "Authorization": f"Bearer {SONAR_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": SONAR_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000,
        "stream": True  # Sonar supporte streaming SSE
    }
    
    async def generate():
        with requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            stream=True,
            timeout=60
        ) as response:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            content = data['choices'][0]['delta'].get('content', '')
                            if content:
                                yield content
                        except:
                            continue
        yield "[DONE]"
    
    return StreamingResponse(generate(), media_type="text/plain")
```

FICHIERS À MODIFIER:
  - backend-service/app/main.py (priorité 1)
  - backend-service/requirements.txt

D. ANALYSES MÉTIERS SPÉCIALISÉES
---------------------------------
État actuel:
  - 6 secteurs: finance_banque, sante_pharma, industrie_manufacturing, 
    energie_utilities, tech_digital, retail_commerce
  - 5 types d'analyses par secteur:
    1. synthese_executive (vue d'ensemble stratégique)
    2. analyse_concurrentielle (mapping concurrent, parts de marché)
    3. tech_watch (innovations, tendances technologiques)
    4. risk_analysis (cartographie risques, mitigation)
    5. market_study (taille marché, projections croissance)

Prompts stockés:
  - Fichier: backend-service/app/business_prompts.py
  - Dictionnaire: BUSINESS_PROMPTS[secteur][type_analyse]
  - Longueur moyenne: 800-1200 tokens par prompt
  - Format: Markdown structuré avec sections obligatoires

ENJEU MIGRATION:
  Les prompts actuels sont calibrés pour GPT-4o-mini. Sonar peut avoir
  des comportements légèrement différents (ton, structure).

ACTION REQUISE:
  1. Tester chaque type d'analyse avec Sonar
  2. Ajuster prompts si nécessaire (reformulation, exemples)
  3. Valider output structuré (Markdown, sections)
  4. Vérifier citations [Réf. X] → adaptation si Sonar retourne URLs

3.3 GESTION DES CITATIONS ET SOURCES
-------------------------------------
OpenAI actuel:
  - Pas de citations automatiques
  - Références manuelles [Réf. 1], [Réf. 2] dans prompt
  - Sources issues uniquement de Qdrant (documents indexés)

Sonar natif:
  - Retourne "citations" array avec URLs web
  - Format: [1], [2]... avec liens externes
  - Mélange potentiel sources internes + web

STRATÉGIE RECOMMANDÉE:
  Option A (Cohérence actuelle):
    - Désactiver recherche web Sonar (search_domain_filter=[])
    - Garder système citations actuel [Réf. X]
    - Sources = uniquement documents Qdrant
  
  Option B (Hybride):
    - Activer recherche web Sonar
    - Fusionner citations internes + externes
    - Frontend affiche 2 types de sources distinctes
    - Nécessite modification ChatInterface.tsx

DÉCISION ATTENDUE DU CLIENT.

================================================================================
                    4. SPÉCIFICATIONS FONCTIONNELLES
================================================================================

4.1 FONCTIONNALITÉS À PRÉSERVER (NON-NÉGOCIABLES)
--------------------------------------------------
✓ Ingestion PDF automatique (extraction, chunking, indexation)
✓ Recherche sémantique dans documents indexés
✓ 5 types d'analyses stratégiques par secteur
✓ 6 secteurs d'activité configurés
✓ Génération rapports PDF professionnels
✓ Chat expert avec streaming temps réel
✓ Export PDF avec logo Axial
✓ Interface frontend complète (dashboard + chat)
✓ Historique conversations (stockage local navigateur)
✓ Sélection secteur dynamique
✓ Design Liquid Glass responsive

4.2 NOUVELLES FONCTIONNALITÉS ATTENDUES (VERSION 2.1)
------------------------------------------------------

A. VEILLE RÉGLEMENTAIRE (Nouvelle fonctionnalité majeure)
----------------------------------------------------------
🆕 **Module Regulatory Watch Service** (nouveau microservice)
   - Monitoring automatique sources réglementaires (JO, EUR-Lex, autorités sectorielles)
   - Alertes temps réel sur nouvelles réglementations par secteur
   - Analyse impact réglementaire via Sonar (recherche web spécialisée)
   - Base de données dédiée textes réglementaires (PostgreSQL + indexation Qdrant)
   - Timeline réglementaire (historique + évolutions futures)
   - Export rapports conformité (PDF)

🆕 **Sources réglementaires intégrées par secteur:**
   Finance/Banque: AMF, ACPR, BCE, EBA, Banque de France
   Santé/Pharma: ANSM, HAS, EMA, CNIL (données santé)
   Industrie: DREAL, ICPE, normes ISO
   Énergie: CRE, DGEC, directives européennes
   Tech/Digital: CNIL, ARCEP, DSA/DMA
   Retail: DGCCRF, normes commerciales

🆕 **Dashboard Veille Réglementaire:**
   - Widget "Actualités Réglementaires" (top 5 changements récents)
   - Filtres par secteur, date, impact (majeur/mineur)
   - Notifications push (email/Slack) sur changements critiques
   - Analyse différentielle (avant/après nouvelle réglementation)

B. RAG AVANCÉ (Architecture hybride)
-------------------------------------
🆕 **Système RAG multi-sources:**
   1. **Documents internes** (existant): PDFs indexés Qdrant
   2. **Recherche web Sonar** (nouveau): Sources temps réel Internet
   3. **Base connaissances métier** (nouveau): Repository structuré sujets pointus

🆕 **Base de données connaissances métier:**
   - Structure: PostgreSQL avec tables spécialisées
     * regulatory_texts (textes réglementaires complets)
     * technical_standards (normes, certifications ISO, etc.)
     * industry_glossary (définitions termes techniques)
     * case_studies (études de cas sectorielles)
     * best_practices (bonnes pratiques métier)
   
   - Indexation vectorielle: Qdrant collection séparée "knowledge_base"
   - Mise à jour: Manuelle (import batch) + automatique (veille réglementaire)
   - Versioning: Historique modifications (audit trail)

🆕 **Pipeline RAG hybride:**
   Requête utilisateur
     ↓
   1. Recherche vectorielle documents internes (Qdrant)
   2. Recherche base connaissances métier (Qdrant knowledge_base)
   3. Recherche web temps réel (Sonar API avec search_domain_filter)
     ↓
   Fusion intelligente résultats (scoring + déduplication)
     ↓
   Génération réponse Sonar avec contexte enrichi
     ↓
   Citations multi-sources: [Doc], [KB], [Web]

🆕 **Avantages RAG avancé:**
   ✓ Réponses plus précises (contexte enrichi multi-sources)
   ✓ Couverture sujets pointus (base connaissances spécialisée)
   ✓ Fraîcheur données (recherche web Sonar)
   ✓ Conformité réglementaire (textes officiels base métier)
   ✓ Traçabilité sources (citations multi-niveaux)

C. AUTRES NOUVELLES FONCTIONNALITÉS
------------------------------------
🆕 Intégration sources web temps réel (Sonar search)
🆕 Citations avec liens cliquables multi-sources
🆕 Métriques comparatives coûts/latence OpenAI vs Sonar
🆕 Fallback automatique OpenAI si Sonar indisponible
🆕 Dashboard admin: logs API calls, tokens consommés, stats RAG
🆕 Import batch base connaissances (CSV, JSON, API)

4.3 ENDPOINTS API À MAINTENIR ET NOUVEAUX (v2.1)
-------------------------------------------------

ENDPOINTS EXISTANTS (à maintenir):
-----------------------------------
gateway-api (8000):
  GET  /health - Santé globale système
  GET  /health/services - Statut tous microservices
  POST /analysis/synthesize - Synthèse exécutive
  POST /analysis/competition - Analyse concurrentielle
  POST /analysis/tech-watch - Veille technologique
  POST /analysis/risk-analysis - Analyse risques
  POST /analysis/market-study - Étude de marché
  POST /workflows/analyze-and-report - Workflow complet

backend-service (8006):
  POST /chat - Chat standard (réponse complète)
  POST /chat/stream - Chat streaming (SSE)
  POST /extended-analysis - Analyse longue format
  GET  /diagnostics - Diagnostics Sonar (adapté)

rag-service (8003):
  POST /synthesize - Synthèse générique
  POST /ask_question - Question-réponse documentaire
  GET  /health - Santé service

NOUVEAUX ENDPOINTS (v2.1):
---------------------------

🆕 regulatory-watch-service (8007):
  GET  /regulatory/latest - Dernières réglementations (limit, sector)
  GET  /regulatory/sector/{sector_id} - Réglementations par secteur
  GET  /regulatory/timeline - Timeline réglementaire
  POST /regulatory/analyze-impact - Analyse impact nouvelle régulation
  GET  /regulatory/alerts - Alertes actives
  POST /regulatory/alerts/subscribe - Abonnement alertes (email/webhook)
  GET  /regulatory/sources - Sources réglementaires configurées
  POST /regulatory/scrape - Déclenchement scraping manuel (admin)
  GET  /health - Santé service

🆕 knowledge-base-service (8008):
  POST /kb/import - Import batch connaissances (CSV, JSON)
  GET  /kb/search - Recherche base connaissances
  POST /kb/add - Ajout entrée manuelle
  PUT  /kb/update/{id} - Mise à jour entrée
  DELETE /kb/delete/{id} - Suppression entrée
  GET  /kb/categories - Catégories disponibles
  GET  /kb/stats - Statistiques base connaissances
  GET  /kb/version-history/{id} - Historique versions
  POST /kb/reindex - Ré-indexation Qdrant (admin)
  GET  /health - Santé service

🆕 enhanced-rag-service (remplace/étend rag-service):
  POST /rag/hybrid-search - Recherche multi-sources (docs + KB + web)
  POST /rag/synthesize-enhanced - Synthèse avec RAG avancé
  POST /rag/explain-sources - Explication sources utilisées
  GET  /rag/config - Configuration RAG (poids sources, etc.)
  PUT  /rag/config - Modification config RAG (admin)
  GET  /rag/metrics - Métriques RAG (latence, sources, qualité)
  GET  /health - Santé service

🆕 gateway-api (8000) - Nouveaux endpoints:
  POST /analysis/regulatory-compliance - Analyse conformité réglementaire
  GET  /regulatory/dashboard - Dashboard veille réglementaire
  POST /kb/query - Requête base connaissances
  GET  /admin/rag-stats - Statistiques RAG avancé

TOUS LES ENDPOINTS EXISTANTS RESTENT COMPATIBLES (mêmes inputs/outputs).
LES NOUVEAUX ENDPOINTS SUIVENT LES MÊMES CONVENTIONS (JSON, Pydantic, Swagger).

================================================================================
              4.4 ARCHITECTURE RAG AVANCÉ ET VEILLE RÉGLEMENTAIRE
================================================================================

4.4.1 ARCHITECTURE RAG HYBRIDE MULTI-SOURCES
---------------------------------------------

COMPOSANTS ARCHITECTURE:
------------------------
┌─────────────────────────────────────────────────────────────────────┐
│                         USER QUERY                                  │
│                              ↓                                      │
│                    Enhanced RAG Service                             │
│                              ↓                                      │
│    ┌──────────────────┬─────────────────┬──────────────────┐      │
│    │   Source 1:      │   Source 2:     │   Source 3:      │      │
│    │  Documents PDF   │ Knowledge Base  │   Web Search     │      │
│    │   (Qdrant)       │   (Qdrant KB)   │  (Sonar API)     │      │
│    └──────┬───────────┴────────┬────────┴────────┬─────────┘      │
│           │                     │                  │                │
│           └──────────┬──────────┴──────────────────┘                │
│                      ↓                                              │
│            Result Fusion & Ranking                                 │
│         (Weighted scoring + Deduplication)                         │
│                      ↓                                              │
│          Context Builder (max 8000 tokens)                         │
│                      ↓                                              │
│            Sonar API Call (generation)                             │
│                      ↓                                              │
│      Response with Multi-Source Citations                          │
│           [Doc:X], [KB:Y], [Web:Z]                                 │
└─────────────────────────────────────────────────────────────────────┘

STRATÉGIE FUSION MULTI-SOURCES:
--------------------------------
1. Recherche parallèle dans les 3 sources (concurrent async calls)
2. Scoring pondéré par source:
   - Documents internes: poids 0.5 (priorité max, données entreprise)
   - Knowledge Base: poids 0.3 (fiabilité, expertise métier)
   - Web Sonar: poids 0.2 (fraîcheur, complément)

3. Déduplication intelligente:
   - Similarité cosinus entre chunks (seuil 0.85)
   - Prioriser source avec poids plus élevé si doublon

4. Limitation contexte:
   - Top 5 chunks par source (max 15 total)
   - Budget tokens: 8000 max (contexte Sonar)
   - Truncation intelligente si dépassement

5. Citation traçable:
   - Format: [Doc:file.pdf p.3], [KB:ISO9001], [Web:url.com]
   - Métadonnées: source_type, source_id, score, excerpt

BASE DE DONNÉES CONNAISSANCES MÉTIER:
--------------------------------------
Schema PostgreSQL (nouvelle DB: knowledge_base_db):

Table: regulatory_texts
  - id (PK, UUID)
  - title (VARCHAR 500)
  - content (TEXT, full text search)
  - source_org (VARCHAR 200) ex: AMF, ACPR
  - publication_date (DATE)
  - effective_date (DATE)
  - sector (ENUM: finance, sante, industrie, energie, tech, retail)
  - impact_level (ENUM: critique, majeur, mineur, informatif)
  - url (VARCHAR 1000)
  - document_type (ENUM: loi, décret, arrêté, directive, règlement)
  - version (INT)
  - created_at, updated_at (TIMESTAMP)

Table: technical_standards
  - id (PK, UUID)
  - standard_code (VARCHAR 100, UNIQUE) ex: ISO 9001, ISO 27001
  - title (VARCHAR 500)
  - description (TEXT)
  - category (ENUM: quality, security, environmental, safety)
  - sector (same as above)
  - certification_body (VARCHAR 200)
  - latest_version (VARCHAR 50)
  - revision_date (DATE)
  - content (TEXT, full specifications)
  - created_at, updated_at

Table: industry_glossary
  - id (PK, UUID)
  - term (VARCHAR 200, indexed)
  - definition (TEXT)
  - sector (same as above)
  - related_terms (JSON array)
  - acronyms (JSON array)
  - examples (TEXT)
  - sources (JSON array of URLs)
  - created_at, updated_at

Table: case_studies
  - id (PK, UUID)
  - title (VARCHAR 500)
  - company_sector (VARCHAR 200)
  - challenge (TEXT)
  - solution (TEXT)
  - results (TEXT)
  - key_metrics (JSON)
  - sector (same as above)
  - tags (JSON array)
  - publication_year (INT)
  - source (VARCHAR 500)
  - created_at, updated_at

Table: best_practices
  - id (PK, UUID)
  - category (VARCHAR 200)
  - title (VARCHAR 500)
  - description (TEXT)
  - steps (JSON array)
  - prerequisites (TEXT)
  - expected_benefits (TEXT)
  - risks (TEXT)
  - sector (same as above)
  - maturity_level (ENUM: beginner, intermediate, advanced)
  - source (VARCHAR 500)
  - created_at, updated_at

Indexation Qdrant:
  - Collection: "knowledge_base" (séparée de "documents")
  - Embedding model: text-embedding-3-small (cohérence avec existant)
  - Vecteurs: 1536 dimensions
  - Payload: {type, id, title, sector, score_boost}
  - Filtres: sector, type, date_range

4.4.2 SERVICE VEILLE RÉGLEMENTAIRE
-----------------------------------

ARCHITECTURE MONITORING:
------------------------
┌─────────────────────────────────────────────────────────────────────┐
│                   Regulatory Watch Service                          │
│                              ↓                                      │
│         Scheduler (APScheduler - cron jobs)                         │
│                              ↓                                      │
│    ┌──────────────────┬─────────────────┬──────────────────┐      │
│    │  Scraper 1:      │   Scraper 2:    │   Scraper 3:     │      │
│    │  Official Sites  │   RSS Feeds     │   Sonar Search   │      │
│    │  (BeautifulSoup) │  (feedparser)   │  (API calls)     │      │
│    └──────┬───────────┴────────┬────────┴────────┬─────────┘      │
│           │                     │                  │                │
│           └──────────┬──────────┴──────────────────┘                │
│                      ↓                                              │
│            Change Detection (diff analysis)                        │
│                      ↓                                              │
│       Store in regulatory_texts (PostgreSQL)                       │
│                      ↓                                              │
│       Index in knowledge_base (Qdrant)                             │
│                      ↓                                              │
│      Alert Manager (email, Slack, webhook)                         │
│                      ↓                                              │
│    Impact Analysis (Sonar API: compare before/after)               │
│                      ↓                                              │
│      Dashboard Update (real-time WebSocket)                        │
└─────────────────────────────────────────────────────────────────────┘

SOURCES RÉGLEMENTAIRES PAR SECTEUR:
------------------------------------
Finance/Banque:
  - AMF (Autorité des Marchés Financiers): https://www.amf-france.org
  - ACPR (Autorité de Contrôle Prudentiel): https://acpr.banque-france.fr
  - Banque de France: https://www.banque-france.fr/reglementation
  - EBA (European Banking Authority): https://www.eba.europa.eu
  - BCE (Banque Centrale Européenne): https://www.ecb.europa.eu
  - Journal Officiel (JO): https://www.legifrance.gouv.fr

Santé/Pharma:
  - ANSM (Agence Nationale Sécurité Médicament): https://ansm.sante.fr
  - HAS (Haute Autorité de Santé): https://www.has-sante.fr
  - EMA (European Medicines Agency): https://www.ema.europa.eu
  - CNIL (données santé): https://www.cnil.fr
  - Ministère Santé: https://sante.gouv.fr

Industrie/Manufacturing:
  - DREAL (Direction Régionale Environnement): https://www.ecologie.gouv.fr
  - ICPE (Installations Classées): https://www.installationsclassees.gouv.fr
  - ISO (normes internationales): https://www.iso.org
  - INRS (Santé Sécurité Travail): https://www.inrs.fr

Énergie/Utilities:
  - CRE (Commission Régulation Énergie): https://www.cre.fr
  - DGEC (Direction Générale Énergie Climat): https://www.ecologie.gouv.fr
  - EUR-Lex (directives européennes): https://eur-lex.europa.eu

Tech/Digital:
  - CNIL (Protection Données): https://www.cnil.fr
  - ARCEP (Télécoms): https://www.arcep.fr
  - DSA/DMA (Digital Services/Markets Act): EUR-Lex
  - ANSSI (Cybersécurité): https://www.ssi.gouv.fr

Retail/Commerce:
  - DGCCRF (Concurrence Consommation): https://www.economie.gouv.fr/dgccrf
  - Journal Officiel (lois commerciales): Legifrance
  - Normes commerce: AFNOR

SCHEDULING MONITORING:
----------------------
Fréquences scraping (configurables):
  - Sources critiques (AMF, CNIL): Toutes les 6 heures
  - Sources importantes: Quotidien (1x/jour, 6h du matin)
  - Sources secondaires: Hebdomadaire (lundi 8h)
  - Sonar web search: Quotidien (complément sources officielles)

Détection changements:
  - Comparaison hash MD5 pages HTML
  - Analyse diff contenu (difflib Python)
  - Détection nouveaux documents (title + date)
  - Versioning automatique (trigger update regulatory_texts)

ALERTES ET NOTIFICATIONS:
-------------------------
Niveaux d'alerte:
  - CRITIQUE: Nouvelle loi/décret avec impact majeur → Email + Slack immédiat
  - MAJEUR: Nouvelle directive/règlement → Email quotidien digest
  - MINEUR: Modification mineure texte → Dashboard uniquement
  - INFORMATIF: Consultation publique, FAQ → Notification hebdomadaire

Canaux notification:
  - Email: SMTP (SendGrid/AWS SES) avec templates HTML
  - Slack: Webhook intégration canal #veille-reglementaire
  - Webhook custom: POST JSON vers URL client (optionnel)
  - Frontend: WebSocket temps réel (toast notifications)

Format alerte:
```json
{
  "alert_id": "uuid",
  "timestamp": "2024-10-03T12:00:00Z",
  "level": "CRITIQUE",
  "sector": "finance_banque",
  "title": "Nouvelle directive AMF sur crypto-actifs",
  "summary": "...",
  "source_url": "https://...",
  "effective_date": "2024-12-01",
  "impact_analysis": "Sonar generated summary...",
  "actions_required": ["Review compliance", "Update procedures"]
}
```

ANALYSE IMPACT AUTOMATIQUE (SONAR):
------------------------------------
Pipeline analyse:
  1. Détection nouvelle réglementation
  2. Extraction texte complet
  3. Requête Sonar API:
     Prompt: "Analyser l'impact de cette nouvelle réglementation sur le 
              secteur [X]. Identifier: changements clés, obligations nouvelles,
              délais conformité, sanctions potentielles."
     Context: Texte réglementation + documents internes pertinents (RAG)
  4. Génération résumé impact (format structuré)
  5. Stockage regulatory_texts.impact_analysis
  6. Affichage dashboard + alerte

DASHBOARD VEILLE RÉGLEMENTAIRE (FRONTEND):
-------------------------------------------
Composants UI:
  - Widget "Actualités Réglementaires" (homepage)
    * Top 5 changements derniers 7 jours
    * Badge niveau impact (couleur: rouge/orange/jaune/vert)
    * Lien vers page détail
  
  - Page dédiée /regulatory
    * Timeline réglementaire (vue chronologique)
    * Filtres: secteur, date, niveau impact, source
    * Recherche full-text
    * Export PDF rapport compliance
  
  - Alertes actives (bell icon navbar)
    * Dropdown notifications non lues
    * Badge count
    * Mark as read / Archive
  
  - Page /regulatory/{id}
    * Détail réglementation complète
    * Analyse impact (Sonar generated)
    * Documents liés (cross-references)
    * Timeline évolutions (versioning)
    * Actions recommandées
    * Export PDF rapport

INTÉGRATION FRONTEND NEXT.JS:
------------------------------
Nouveaux composants:
  - <RegulatoryWidget /> - Homepage widget
  - <RegulatoryTimeline /> - Timeline interactive
  - <RegulatoryAlerts /> - Système notifications
  - <RegulatoryDetail /> - Page détail réglementation
  - <ImpactAnalysis /> - Affichage analyse Sonar
  - <ComplianceReport /> - Générateur rapport PDF

API Calls (frontend):
  - GET /regulatory/latest?limit=5&sector=finance
  - GET /regulatory/timeline?start_date=2024-01-01
  - GET /regulatory/alerts?unread=true
  - POST /regulatory/analyze-impact (trigger analyse manuelle)
  - GET /regulatory/{id}

WebSocket real-time:
  - ws://localhost:8007/ws/regulatory-updates
  - Events: new_regulation, alert_triggered, impact_analyzed
  - Frontend écoute + update UI en temps réel

================================================================================
                    5. SPÉCIFICATIONS TECHNIQUES
================================================================================

5.1 CONTRAINTES TECHNIQUES
---------------------------
✓ Python 3.11 minimum
✓ FastAPI (pas de changement framework)
✓ Docker Compose pour orchestration
✓ Volumes persistants préservés (données existantes)
✓ Compatibilité macOS ARM64 (Apple Silicon)
✓ Logs structurés JSON (Loguru)
✓ Retry logic pour appels API (3 tentatives)
✓ Timeouts configurables (30s génération, 60s streaming)
✓ Health checks tous services (/health endpoint)

5.2 GESTION DES ERREURS
------------------------
Scénarios critiques:
  1. API Sonar indisponible (503)
     → Retry 3x avec backoff exponentiel (1s, 2s, 4s)
     → Si échec: retourner erreur HTTP 502 + message clair
  
  2. Rate limiting Sonar (429)
     → Retry après délai header "Retry-After"
     → Log warning + métriques
  
  3. Timeout génération (>30s)
     → Annulation requête + HTTP 504
     → Message user: "L'analyse prend trop de temps, réessayez"
  
  4. Token limit dépassé (context trop long)
     → Truncation automatique contexte documentaire
     → Prioriser chunks avec meilleurs scores Qdrant
  
  5. Clé API invalide/expirée
     → HTTP 401 + log error critique
     → Notification admin (email/Slack si configuré)

5.3 PERFORMANCE ET SCALABILITÉ
-------------------------------
Benchmarks attendus (post-migration):
  - Latence analyse complète: <15s (vs ~20s OpenAI)
  - Streaming first token: <1s (vs ~2s OpenAI)
  - Coût par analyse: <$0.10 (vs ~$0.15 OpenAI)
  - Throughput: 10 req/s par service (avec load balancing)

Optimisations requises:
  ✓ Cache Redis pour analyses identiques (optionnel, future)
  ✓ Pooling connections HTTP (requests.Session)
  ✓ Async/await pour I/O-bound operations
  ✓ Compression réponses API (gzip)

5.4 SÉCURITÉ
------------
✓ Clés API stockées .env uniquement (jamais en codebase)
✓ HTTPS pour appels Sonar (certificats valides)
✓ Validation inputs Pydantic (injection prompt prevention)
✓ Rate limiting frontend (max 20 req/min par user)
✓ Logs sanitisés (pas de secrets/PII)
✓ CORS configuré (origins autorisées uniquement)

================================================================================
                    6. PLAN DE MIGRATION ET DÉVELOPPEMENT (VERSION 2.1)
================================================================================

NOUVELLE DURÉE ESTIMÉE: 35 jours ouvrés (7 semaines)
  - Migration Sonar: 17 jours (identique v2.0)
  - Développement RAG avancé + Veille réglementaire: 18 jours (nouveau)

6.1 PHASE 1: PRÉPARATION GLOBALE (Durée: 3 jours - ÉTENDU)
-----------------------------------------------------------
Tâches migration Sonar:
  □ Obtenir clé API Sonar (Perplexity AI)
  □ Audit code: identifier tous appels OpenAI
  □ Documentation API Sonar (lecture complète)
  □ Tests manuels API Sonar (Postman/curl)
  □ Définir stratégie embeddings (garder OpenAI? migrer?)
  □ Définir stratégie citations (internes? web? hybride?)

Tâches RAG avancé + Veille (NOUVEAU):
  □ Design architecture RAG multi-sources (diagrammes)
  □ Spec schema PostgreSQL knowledge_base_db (5 tables)
  □ Spec collections Qdrant (knowledge_base séparée)
  □ Définir sources réglementaires par secteur (URLs, fréquences)
  □ Stratégie scraping (BeautifulSoup vs Scrapy vs API natives)
  □ Setup environnement dev: branches Git feature/rag-advanced + feature/regulatory-watch

Livrables:
  - Document stratégie migration Sonar (embeddings + citations)
  - Compte Sonar API configuré + clé valide
  - Architecture RAG multi-sources (diagramme Mermaid/draw.io)
  - Schema SQL knowledge_base_db (DDL complet)
  - Liste sources réglementaires validée par secteur
  - Environment variables template (.env.v2.1)

6.2 PHASE 2: MIGRATION RAG-SERVICE (Durée: 3 jours)
----------------------------------------------------
Tâches:
  □ Créer module sonar_client.py (encapsulation API)
  □ Remplacer call_openai_safe() → call_sonar_safe()
  □ Adapter gestion erreurs Sonar
  □ Tests unitaires: mocks Sonar API
  □ Tests intégration: appels réels Sonar
  □ Validation output format (Markdown, structure)
  □ Logs détaillés (latence, tokens, coûts)
  □ Documentation code (docstrings, comments)

Endpoints impactés:
  - POST /synthesize
  - POST /ask_question
  - POST /generate_report

Tests de validation:
  ✓ Analyse synthèse exécutive (finance_banque)
  ✓ Question simple documentaire
  ✓ Génération rapport long (4000 tokens)
  ✓ Gestion timeout (requête >30s)
  ✓ Gestion erreur 429 (rate limit)

Livrables:
  - rag-service migré Sonar 100%
  - Tests passants (pytest)
  - Logs migration (comparaison avant/après)

6.3 PHASE 3: MIGRATION BACKEND-SERVICE (Durée: 3 jours)
--------------------------------------------------------
Tâches:
  □ Migrer endpoint /chat (réponse complète)
  □ Migrer endpoint /chat/stream (streaming SSE)
  □ Adapter /extended-analysis
  □ Tester streaming frontend (ChatInterface.tsx)
  □ Validation bouton Stop (annulation streaming)
  □ Gestion historique conversations
  □ Tests end-to-end chat complet
  □ Performance benchmarks (latence first token)

Endpoints impactés:
  - POST /chat
  - POST /chat/stream
  - POST /extended-analysis
  - GET /diagnostics

Tests de validation:
  ✓ Chat question simple (secteur finance)
  ✓ Chat streaming long (réponse 2000 tokens)
  ✓ Annulation streaming (bouton Stop frontend)
  ✓ Historique 10 messages (contexte conversation)
  ✓ Changement secteur dynamique

Livrables:
  - backend-service migré Sonar 100%
  - Chat frontend opérationnel
  - Benchmarks latence streaming

6.4 PHASE 4: MIGRATION ANALYSES MÉTIERS (Durée: 4 jours)
---------------------------------------------------------
Tâches:
  □ Tester chaque type d'analyse (5 types × 6 secteurs = 30 tests)
  □ Ajuster prompts si nécessaire (business_prompts.py)
  □ Validation format Markdown output
  □ Vérifier citations [Réf. X] cohérentes
  □ Tests génération PDF (report-service)
  □ Validation exports PDF (logo, formatage)
  □ Tests workflow complet (analyse → export PDF)
  □ Documentation ajustements prompts

Analyses à valider:
  Secteur finance_banque:
    ✓ Synthèse exécutive
    ✓ Analyse concurrentielle
    ✓ Veille technologique
    ✓ Analyse risques
    ✓ Étude de marché
  
  (Répéter pour 5 autres secteurs)

Livrables:
  - 30 analyses validées qualité
  - Prompts ajustés si nécessaire
  - Rapports PDF générés exemple
  - Grille validation qualitative

6.5 PHASE 5: TESTS & VALIDATION GLOBALE (Durée: 3 jours)
---------------------------------------------------------
Tâches:
  □ Tests régression complets (tous endpoints)
  □ Tests charge (100 req simultanées)
  □ Tests edge cases (timeout, erreurs, inputs invalides)
  □ Validation frontend (toutes pages, tous flows)
  □ Tests mobile responsive (iPhone, iPad)
  □ Audit logs (pas d'erreurs critiques)
  □ Benchmarks performance (avant/après migration)
  □ Documentation technique finale
  □ Guide déploiement production

Tests critiques:
  ✓ Workflow complet: Upload PDF → Indexation → Analyse → Export PDF
  ✓ 10 utilisateurs simultanés (chat + analyses)
  ✓ Fallback graceful si Sonar indisponible
  ✓ Logs structurés lisibles (JSON)
  ✓ Health checks tous services OK
  ✓ Volumes Docker persistants intacts

Livrables:
  - Rapport tests global (pass/fail par feature)
  - Benchmarks comparatifs OpenAI vs Sonar
  - Documentation déploiement production
  - Vidéo démo application post-migration

6.6 PHASE 6: DÉPLOIEMENT & FORMATION (Durée: 2 jours)
------------------------------------------------------
Tâches:
  □ Mise en production (environnement staging d'abord)
  □ Tests smoke production (endpoints critiques)
  □ Monitoring logs temps réel (1h surveillance)
  □ Formation équipe Axial (2h session)
  □ Handover documentation technique
  □ Support post-déploiement (2 semaines)

Formation incluse:
  - Présentation architecture Sonar
  - Gestion clés API (rotation, monitoring)
  - Debugging commun (logs, erreurs API)
  - Procédure rollback si problème critique
  - Maintenance routine (updates, patches)

Livrables:
  - Application en production opérationnelle
  - Équipe formée (certificat formation)
  - Documentation support (FAQ, troubleshooting)
  - Contrat support maintenance (optionnel)

DURÉE TOTALE ESTIMÉE v2.0: 17 jours ouvrés (3,5 semaines) - MIGRATION SONAR UNIQUEMENT
DURÉE TOTALE ESTIMÉE v2.1: 35 jours ouvrés (7 semaines) - SONAR + RAG AVANCÉ + VEILLE

6.7 PHASE 7: DÉVELOPPEMENT BASE CONNAISSANCES (Durée: 5 jours - NOUVEAU)
--------------------------------------------------------------------------
Tâches:
  □ Créer knowledge-base-service (nouveau microservice port 8008)
  □ Setup PostgreSQL knowledge_base_db (5 tables)
  □ Implémentation ORM SQLAlchemy (models + schemas)
  □ Endpoints CRUD base connaissances (/kb/*)
  □ Import batch CSV/JSON (regulatory_texts, technical_standards, etc.)
  □ Indexation automatique Qdrant collection "knowledge_base"
  □ Versioning historique (audit trail modifications)
  □ API recherche full-text + vectorielle
  □ Tests unitaires + intégration
  □ Documentation Swagger endpoints

Livrables:
  - knowledge-base-service opérationnel
  - Base données knowledge_base_db peuplée (100+ entrées test)
  - Collection Qdrant "knowledge_base" indexée
  - Tests passants (pytest >80%)
  - Documentation API complète

6.8 PHASE 8: DÉVELOPPEMENT RAG HYBRIDE (Durée: 6 jours - NOUVEAU)
------------------------------------------------------------------
Tâches:
  □ Upgrade rag-service → enhanced-rag-service
  □ Implémentation recherche multi-sources parallèle (async)
  □ Fusion résultats pondérée (scoring + déduplication)
  □ Gestion contexte 8000 tokens (truncation intelligente)
  □ Citations multi-sources [Doc], [KB], [Web]
  □ Configuration poids sources (admin endpoint)
  □ Métriques RAG (latence par source, qualité, coûts)
  □ Tests A/B (RAG simple vs RAG hybride)
  □ Validation qualité réponses (grille évaluation)
  □ Performance benchmarks (latence, throughput)

Tests validation:
  ✓ Requête finance: docs internes + base connaissances + web Sonar
  ✓ Fusion 15 chunks (5 par source) sans doublons
  ✓ Citations traçables avec métadonnées complètes
  ✓ Latence <20s pour requête complexe
  ✓ Déduplication similarité cosinus >0.85

Livrables:
  - enhanced-rag-service fonctionnel
  - Pipeline RAG hybride validé
  - Benchmarks comparatifs (RAG simple vs hybride)
  - Documentation architecture RAG
  - Tests end-to-end passants

6.9 PHASE 9: DÉVELOPPEMENT VEILLE RÉGLEMENTAIRE (Durée: 7 jours - NOUVEAU)
---------------------------------------------------------------------------
Tâches:
  □ Créer regulatory-watch-service (nouveau microservice port 8007)
  □ Implémentation scrapers sources officielles (BeautifulSoup)
  □ Parser RSS feeds réglementaires (feedparser)
  □ Intégration Sonar search complémentaire
  □ Scheduler APScheduler (cron jobs configurables)
  □ Détection changements (hash MD5 + diff analysis)
  □ Stockage regulatory_texts (PostgreSQL + Qdrant)
  □ Système alertes multi-canaux (Email SMTP, Slack webhook)
  □ Analyse impact automatique Sonar
  □ WebSocket notifications temps réel
  □ Endpoints API veille (/regulatory/*)
  □ Tests scrapers (mocks HTML sources officielles)
  □ Configuration sources par secteur (YAML/JSON)

Composants frontend (Next.js):
  □ <RegulatoryWidget /> - Widget homepage
  □ <RegulatoryTimeline /> - Timeline interactive
  □ <RegulatoryAlerts /> - Système notifications
  □ Page /regulatory - Dashboard veille
  □ Page /regulatory/{id} - Détail réglementation
  □ WebSocket client - Real-time updates

Tests validation:
  ✓ Scraping AMF (Finance): détection nouvelle publication
  ✓ Alerte CRITIQUE: email + Slack envoyés <5 min
  ✓ Analyse impact Sonar: résumé structuré généré
  ✓ WebSocket: notification reçue frontend temps réel
  ✓ Timeline: affichage chronologique 100 réglementations

Livrables:
  - regulatory-watch-service opérationnel
  - Scrapers 20+ sources configurés et testés
  - Système alertes fonctionnel (email + Slack)
  - Dashboard frontend complet
  - Tests end-to-end passants
  - Documentation setup sources réglementaires

================================================================================
                    7. LIVRABLES ATTENDUS (VERSION 2.1)
================================================================================

7.1 CODE SOURCE
---------------
Structure Git:
  main (production actuelle OpenAI v1.1)
  ├── feature/sonar-migration (migration Sonar)
  ├── feature/rag-advanced (RAG multi-sources)
  ├── feature/regulatory-watch (veille réglementaire)
  └── develop (intégration 3 branches) → merge main après validation

Fichiers modifiés:
  ✓ rag-service/app/rag_main.py → enhanced-rag-service
  ✓ backend-service/app/main.py (chat + streaming Sonar)
  ✓ backend-service/app/business_prompts.py (ajustements)
  ✓ docker-compose.yml (+3 services: knowledge-base, enhanced-rag, regulatory-watch)
  ✓ .env (+variables SONAR, KB_DB, REGULATORY sources)
  ✓ frontend-openwebui/app/* (nouveaux composants UI)

Nouveaux services:
  + knowledge-base-service/ (microservice complet)
  + regulatory-watch-service/ (microservice complet)
  + enhanced-rag-service/ (upgrade rag-service)

Nouveaux fichiers:
  + sonar_client.py (module réutilisable appels Sonar)
  + rag_fusion.py (logique fusion multi-sources)
  + scrapers/ (modules scraping réglementaire)
  + alert_manager.py (système notifications)
  + schema_kb.sql (DDL knowledge_base_db)
  + tests/test_rag_hybrid.py (tests RAG avancé)
  + tests/test_regulatory_scrapers.py (tests scraping)
  + docs/RAG_ARCHITECTURE.md (documentation RAG)
  + docs/REGULATORY_SOURCES.md (guide sources)
  + benchmarks/rag_simple_vs_hybrid.json (comparatifs)

7.2 DOCUMENTATION
-----------------
Documents requis:
  ✓ README.md mis à jour (instructions Sonar)
  ✓ MIGRATION_GUIDE.md (étapes migration détaillées)
  ✓ API_COMPARISON.md (OpenAI vs Sonar, breaking changes)
  ✓ PROMPT_ADJUSTMENTS.md (changements prompts métiers)
  ✓ TROUBLESHOOTING.md (problèmes fréquents + solutions)
  ✓ DEPLOYMENT.md (procédure déploiement production)

Format documentation:
  - Markdown (.md)
  - Diagrammes architecture (Mermaid ou draw.io)
  - Captures écran interface
  - Exemples code (Python, bash, JSON)

7.3 TESTS
---------
Suite tests complète:
  ✓ Tests unitaires (pytest) - couverture >80%
  ✓ Tests intégration (API endpoints)
  ✓ Tests end-to-end (workflows complets)
  ✓ Tests charge (locust ou k6) - 100 users simultanés
  ✓ Tests régression (tous endpoints legacy)

Rapport tests:
  - Fichier: test_report.html (pytest-html)
  - Contenu: pass/fail par test, logs erreurs, durée exécution
  - Benchmarks: latence, throughput, coûts

7.4 ENVIRONNEMENTS
------------------
Configurations Docker:
  ✓ .env.development (dev local)
  ✓ .env.staging (pré-production)
  ✓ .env.production (production)

Scripts helper:
  ✓ docker-helper.sh (start/stop/rebuild/logs)
  ✓ migration_check.sh (validation pré-migration)
  ✓ rollback.sh (retour OpenAI si urgence)

7.5 FORMATION
-------------
Support formation:
  ✓ Slides présentation (PDF, 30 slides)
  ✓ Vidéo démo migration (15 min, screencast)
  ✓ Guide admin (PDF, 20 pages)
  ✓ FAQ troubleshooting (Markdown)

Session formation:
  - Durée: 2 heures
  - Format: visio + screen sharing
  - Participants: équipe technique Axial (max 5 personnes)
  - Enregistrement: oui (pour référence future)

================================================================================
                    8. CRITÈRES D'ACCEPTATION (VERSION 2.1)
================================================================================

8.1 FONCTIONNELS (EXISTANTS)
-----------------------------
✓ Toutes analyses métiers fonctionnelles (5 types × 6 secteurs = 30)
✓ Chat expert opérationnel (standard + streaming Sonar)
✓ Export PDF conserve formatage professionnel
✓ Recherche sémantique inchangée (résultats cohérents)
✓ Interface frontend sans régression visuelle/UX
✓ Temps réponse analyses ≤ 20s (95e percentile)
✓ Streaming first token < 2s
✓ Citations/sources correctement formatées

8.1.2 FONCTIONNELS (NOUVEAUX v2.1)
-----------------------------------
RAG AVANCÉ:
✓ Recherche hybride opérationnelle (3 sources parallèles)
✓ Fusion résultats sans doublons (déduplication >85%)
✓ Citations multi-sources traçables [Doc], [KB], [Web]
✓ Base connaissances peuplée (>100 entrées par secteur)
✓ Poids sources configurables (admin endpoint)
✓ Métriques RAG disponibles (latence, qualité par source)

VEILLE RÉGLEMENTAIRE:
✓ Scrapers 20+ sources opérationnels (6 secteurs)
✓ Détection changements fonctionnelle (diff analysis)
✓ Alertes multi-canaux (Email + Slack) <5 min
✓ Analyse impact Sonar automatique
✓ Dashboard veille accessible /regulatory
✓ Timeline réglementaire affiche historique
✓ WebSocket notifications temps réel
✓ Export rapport conformité PDF

FRONTEND:
✓ Widget veille visible homepage (top 5 changements)
✓ Page /regulatory fonctionnelle (filtres, recherche)
✓ Notifications bell icon (badge count)
✓ Page détail /regulatory/{id} complète
✓ Composants responsive mobile (iPhone/iPad)

QUALITÉ RAG HYBRIDE (critères qualitatifs):
✓ Pertinence réponses améliorée vs RAG simple (+20% satisfaction user)
✓ Couverture sujets pointus (base connaissances utilisée >30% requêtes)
✓ Fraîcheur données (web Sonar apporte info <7 jours dans 40% cas)
✓ Cohérence citations (pas de sources inventées, vérifiabilité 100%)

8.2 TECHNIQUES
--------------
✓ Pas d'erreurs critiques logs (ERROR, CRITICAL)
✓ Health checks tous services retournent 200 OK
✓ Tests automatisés passent 100% (pytest)
✓ Couverture code >80% (pytest-cov)
✓ Docker build sans warnings
✓ Volumes persistants intacts (données préservées)
✓ Compatible macOS ARM64 (Apple Silicon)
✓ Pas de dépendances cassées (pip check)

8.3 PERFORMANCE
---------------
Benchmarks vs OpenAI (amélioration attendue):
  ✓ Latence moyenne: -20% minimum
  ✓ Coût par requête: -30% minimum
  ✓ First token streaming: -40% minimum
  ✓ Throughput: +20% minimum

Métriques absolues:
  ✓ Analyse complète: <15s (p95)
  ✓ Chat streaming: <1s first token
  ✓ Export PDF: <3s
  ✓ Disponibilité: >99.5% (uptime services)

8.4 QUALITÉ
-----------
✓ Code PEP8 compliant (flake8, black)
✓ Type hints Python (mypy validation)
✓ Docstrings complètes (Google style)
✓ Logs structurés JSON (Loguru)
✓ Gestion erreurs robuste (try/except + retry)
✓ Pas de secrets hardcodés (scan avec truffleHog)
✓ Dependencies à jour (pip-audit, safety)

8.5 DOCUMENTATION
-----------------
✓ README.md clair pour setup développeur
✓ API docs Swagger à jour (tous endpoints)
✓ Diagrammes architecture actualisés
✓ Exemples curl pour chaque endpoint
✓ Troubleshooting guide (10 problèmes + solutions)
✓ Vidéo démo 10-15 min (qualité professionnelle)

================================================================================
                    9. CONTRAINTES ET RISQUES
================================================================================

9.1 CONTRAINTES PROJET
-----------------------
Délai: 3,5 semaines maximum (17 jours ouvrés)
Budget: [À définir par Axial]
Équipe: 1 développeur senior full-time
Environnement: macOS (développement) + Docker (production)
Disponibilité: Accès équipe Axial pour questions (Slack/Email)

9.2 RISQUES IDENTIFIÉS
-----------------------
RISQUE 1: API Sonar incompatible avec prompts existants
  Probabilité: Moyenne (40%)
  Impact: Élevé (nécessite réécriture prompts)
  Mitigation: Tests précoces phase 1, ajustements progressifs phase 4

RISQUE 2: Performance Sonar inférieure à OpenAI (latence)
  Probabilité: Faible (20%)
  Impact: Critique (objectif migration non atteint)
  Mitigation: Benchmarks phase 1, clause rollback contrat

RISQUE 3: Embeddings incompatibles (ré-indexation Qdrant requise)
  Probabilité: Élevée (60%) si migration embeddings
  Impact: Élevé (perte données, temps ré-indexation)
  Mitigation: Garder OpenAI pour embeddings (décision phase 1)

RISQUE 4: Rate limiting Sonar plus restrictif que prévu
  Probabilité: Moyenne (30%)
  Impact: Moyen (limite scaling utilisateurs)
  Mitigation: Cache Redis analyses fréquentes (phase future)

RISQUE 5: Streaming Sonar instable (SSE dropouts)
  Probabilité: Faible (15%)
  Impact: Élevé (UX chat dégradée)
  Mitigation: Retry logic robuste, fallback mode non-streaming

RISQUE 6: Coûts Sonar supérieurs estimations
  Probabilité: Faible (10%)
  Impact: Moyen (ROI migration réduit)
  Mitigation: Monitoring tokens consommés, alertes budgétaires

9.3 PLAN DE CONTINGENCE
------------------------
Scénario A: Migration échoue tests validation (phase 5)
  Action: Rollback branche main (OpenAI)
  Délai rollback: 1 heure
  Impact: Aucun (production non impactée)

Scénario B: Problème critique production post-déploiement
  Action: Script rollback.sh automatisé
  Délai rollback: 15 minutes
  Communication: Email équipe + post-mortem 48h

Scénario C: API Sonar indisponible prolongée (>1h)
  Action: Fallback automatique OpenAI (mode dégradé)
  Configuration: Variable FALLBACK_TO_OPENAI=true
  Monitoring: Alertes Slack temps réel

================================================================================
                    10. ORGANISATION ET COMMUNICATION
================================================================================

10.1 INTERLOCUTEURS
-------------------
Côté Axial:
  - Product Owner: [Nom + Email]
  - Tech Lead: [Nom + Email]
  - Responsable Infrastructure: [Nom + Email]

Côté Prestataire:
  - Chef de projet: [Nom + Email]
  - Développeur senior: [Nom + Email]
  - QA Engineer: [Nom + Email]

10.2 RITUELS PROJET
-------------------
Daily standup:
  - Fréquence: Quotidien (jours ouvrés)
  - Durée: 15 min
  - Format: Slack written + visio si bloquant
  - Contenu: Avancement J-1, plan J, bloquants

Weekly review:
  - Fréquence: Chaque vendredi
  - Durée: 1 heure
  - Format: Visio + slides
  - Contenu: Démo avancement, métriques, risques, next steps

10.3 OUTILS COLLABORATION
--------------------------
Code:
  - Git: GitHub/GitLab (repository Axial)
  - Branches: feature/sonar-migration → main
  - Pull Requests: review obligatoire avant merge
  - CI/CD: GitHub Actions (tests automatisés)

Communication:
  - Slack: Canal dédié #sonar-migration
  - Email: rapports hebdomadaires
  - Visio: Google Meet / Zoom
  - Documentation: Notion / Confluence

Gestion projet:
  - Tâches: Jira / Linear / GitHub Projects
  - Time tracking: Toggl / Harvest
  - Documents: Google Drive partagé

10.4 JALONS PROJET (VERSION 2.1)
---------------------------------
Jalon 1: Stratégie globale validée (Fin phase 1)
  Date: J+3
  Livrable: Architecture RAG + sources réglementaires + stratégie Sonar
  Validation: Product Owner Axial

Jalon 2: RAG-service migré Sonar (Fin phase 2)
  Date: J+6
  Livrable: rag-service fonctionnel Sonar + tests
  Validation: Tech Lead Axial

Jalon 3: Backend-service migré Sonar (Fin phase 3)
  Date: J+9
  Livrable: Chat streaming opérationnel frontend
  Validation: Product Owner + tests utilisateurs

Jalon 4: Analyses métiers validées (Fin phase 4)
  Date: J+13
  Livrable: 30 analyses testées + rapports PDF
  Validation: Équipe métier Axial

Jalon 5: Recette migration Sonar (Fin phase 5)
  Date: J+16
  Livrable: Rapport tests global Sonar + benchmarks
  Validation: Comité technique Axial

Jalon 6: Production migration Sonar (Fin phase 6)
  Date: J+18
  Livrable: Application Sonar déployée + équipe formée
  Validation: Product Owner Axial

Jalon 7: Base connaissances opérationnelle (Fin phase 7 - NOUVEAU)
  Date: J+23
  Livrable: knowledge-base-service + 100+ entrées
  Validation: Tech Lead Axial

Jalon 8: RAG hybride validé (Fin phase 8 - NOUVEAU)
  Date: J+29
  Livrable: enhanced-rag-service + benchmarks
  Validation: Product Owner + tests A/B

Jalon 9: Veille réglementaire opérationnelle (Fin phase 9 - NOUVEAU)
  Date: J+35
  Livrable: regulatory-watch-service + dashboard frontend
  Validation: Product Owner + équipe métier

Jalon FINAL: Sign-off global v2.1
  Date: J+35
  Livrable: Application complète v2.1 en production
  Validation: Comité de direction Axial

================================================================================
                    11. CONDITIONS FINANCIÈRES (VERSION 2.1)
================================================================================

11.1 MODALITÉS DE PAIEMENT (PROPOSITION)
-----------------------------------------
Montant total: [À définir selon profil prestataire]

Échelonnement suggéré VERSION 2.1 (35 jours):
  - 20% signature contrat (acompte)
  - 20% jalon 4 validé (analyses métiers Sonar OK)
  - 20% jalon 6 validé (migration Sonar complète)
  - 20% jalon 8 validé (RAG hybride opérationnel)
  - 20% livraison finale + formation (jalon FINAL)

Forfait ou régie:
  - Option A: Forfait global (35 jours × tarif jour prestataire)
  - Option B: Régie au temps passé (max 35 jours)
  - Option C: Forfait modulaire:
    * Module 1 (Migration Sonar): 17 jours × tarif
    * Module 2 (RAG avancé + Base connaissances): 11 jours × tarif
    * Module 3 (Veille réglementaire): 7 jours × tarif
    * Total: 35 jours (possibilité commande par modules)

Frais annexes:
  - Compte Sonar API: ~$50/mois (pris en charge Axial)
  - Infrastructure cloud (si staging externe): [Si applicable]
  - Licences outils (si nécessaire): [À préciser]

11.2 GARANTIES
--------------
Support post-livraison:
  - Durée: 2 semaines (inclus forfait)
  - Hotfixes bugs critiques: 4h response time
  - Support email/Slack: heures ouvrées
  - 1 session debugging visio (max 2h) si nécessaire

Maintenance évolutive (optionnelle):
  - Forfait mensuel: [À définir]
  - Inclut: mises à jour Sonar API, patches sécurité, support
  - SLA: 24h bugs mineurs, 4h bugs critiques

11.3 PÉNALITÉS / BONUS (OPTIONNEL)
-----------------------------------
Pénalité retard:
  - Si livraison finale >J+17: [%] montant par jour retard
  - Max pénalités: 10% montant total

Bonus performance:
  - Si latence Sonar <OpenAI de 30%: [Montant bonus]
  - Si livraison anticipée 3 jours: [Montant bonus]

================================================================================
                    12. PROPRIÉTÉ INTELLECTUELLE
================================================================================

12.1 CODE SOURCE
----------------
Propriété: Axial (code développé dans cadre mission)
Licence: Code fermé (propriétaire Axial)
Réutilisation prestataire: Interdite (clause confidentialité)

Exceptions (open-source):
  - Bibliothèques publiques (requests, FastAPI, etc.): licences respectives
  - Modules génériques réutilisables: négociable (sonar_client.py?)

12.2 DOCUMENTATION
------------------
Propriété: Axial (documentation projet)
Diffusion: Interne équipe Axial uniquement
Reproduction: Interdite sans autorisation écrite

12.3 DONNÉES
------------
Données clients: Propriété exclusive Axial
Données tests: Anonymisées, suppression fin mission
Logs projet: Conservés 90 jours puis suppression

================================================================================
                    13. ANNEXES
================================================================================

ANNEXE A: Architecture système actuelle (diagramme)
ANNEXE B: Exemples prompts métiers (extraits business_prompts.py)
ANNEXE C: Format réponses API attendu (JSON schemas)
ANNEXE D: Grille validation analyses (checklist qualité)
ANNEXE E: Procédure rollback détaillée (script + étapes)
ANNEXE F: Glossaire technique (termes métier + tech)

================================================================================
                        FIN DU CAHIER DES CHARGES
================================================================================

Document rédigé le: Octobre 2024
Version: 2.0
Statut: DRAFT (validation Axial en attente)

Contact prestataire:
  Nom: [À compléter]
  Email: [À compléter]
  Téléphone: [À compléter]
  LinkedIn: [À compléter]

Contact Axial:
  Nom: Isaïa Ebongue
  Email: [À compléter]
  Téléphone: [À compléter]

Prochaines étapes:
  1. Review cahier des charges Axial (deadline: [Date])
  2. Réponse prestataire avec devis (deadline: [Date])
  3. Sélection prestataire + signature contrat (deadline: [Date])
  4. Kick-off projet (date: [Date])

================================================================================

