# Insight MVP — Strategic Intelligence Platform

## 🎯 MVP de Veille Stratégique avec IA — Production Ready

### Objectif
Plateforme complète de veille stratégique qui transforme vos documents PDF en insights business actionnables grâce à l'IA.

**5 types d'analyses spécialisées :**
1. **Synthèse Exécutive** - Points clés et recommandations stratégiques
2. **Analyse Concurrentielle** - Mapping concurrentiel et positionnement
3. **Veille Technologique** - Innovations émergentes et roadmap tech  
4. **Analyse de Risques** - Cartographie des risques et mitigation
5. **Étude de Marché** - Taille de marché et projections

### ✨ Fonctionnalités Clés
- 📄 **Ingestion PDF automatique** avec extraction de texte et chunking intelligent
- 🔍 **Recherche sémantique** via embeddings OpenAI et Qdrant
- 🤖 **5 analyses IA spécialisées** avec prompts métier pré-configurés
- 📊 **Rapports PDF professionnels** avec formatage consulting
- 🌐 **API REST complète** avec documentation Swagger
- 🐳 **Architecture microservices** containerisée
- ✅ **Tests complets** unitaires et d'intégration

### Structure de projet
```
data/
  pdfs/            # Déposez vos PDF ici
  logo/            # Logo société (ex: logo.svg)
  reports/         # (optionnel) export PDF
backend/           # (alias: services FastAPI ci-dessous)
  gateway-api/
  document-service/
  vector-service/
  rag-service/
  report-service/
  status-service/
frontend/
  nextjs/          # Dashboard moderne (Apple-like)
scripts/
  ingest.py        # Ingestion batch PDFs
docker-compose.yml
.env.example
```

### Workflows
- Ingestion: `scripts/ingest.py` → upload PDF → extraction texte (PyPDF) → DB (Postgres) → embeddings + index (Qdrant)
- Recherche: `POST /search` via gateway → passages pertinents (vector-service)
- Synthèse: `POST /report` via rag-service → prompt OpenAI avec passages → résumé exécutif
- Export: `POST /export_pdf` (report-service) → PDF simple (ReportLab)
- Statut: `GET /status` (status-service) → uptime, CPU/Mem, nb docs/rapports

### Endpoints clés
- gateway-api: `/search`, `/report`, `/status`, `/documents`, `/upload_pdf`, `/ingest_folder`
- document-service: `/upload_pdf`, `/documents`, `/document/{id}`, `/ingest_folder`
- vector-service: `/upsert_embedding`, `/search`, `/collections`
- rag-service: `/ask_question`, `/generate_report`
- report-service: `/export_pdf`, `/reports`, `/reports/{id}`
- status-service: `/status`, `/health`

## 🚀 Quickstart

### 1. Configuration
```bash
# Copier et configurer l'environnement
cp env.example .env

# IMPORTANT: Éditer .env et ajouter votre clé OpenAI
# OPENAI_API_KEY=sk-your-key-here
```

### 2. Installation Docker (si nécessaire)
```bash
# Vérifier Docker
./scripts/check_docker.sh

# Si Docker n'est pas installé :
# Option A: Télécharger Docker Desktop depuis https://www.docker.com/products/docker-desktop/
# Option B: Via Homebrew
brew install --cask docker
```

### 3. Démarrage des services
```bash
# Lancer tous les microservices (Docker moderne)
docker compose up -d --build

# OU si ancienne version Docker :
docker-compose up -d --build

# Vérifier la santé du système
curl -s http://localhost:8000/health/services | jq
```

### 3. Ingestion de documents
```bash
# Copier vos PDFs dans le dossier data/pdfs/
# Puis ingérer via API
curl -X POST "http://localhost:8000/documents/ingest_folder" \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "/app/data/pdfs"}'
```

### 4. Tests et validation
```bash
# Tester tous les services
./scripts/test_all_services.sh

# Test workflow complet
python3 scripts/test_workflow.py

# Exemples d'appels API
./scripts/example_calls.sh
```

### UI Next.js (Apple-like)
- Dashboard: logo, stats système, actions (recherche, documents, rapports)
- Recherche: input, suggestions, résultats avec score
- Dark mode + glassmorphism (blur, panneaux translucides)

### Sécurité & Local-first
- Données + vecteurs en local (Postgres + Qdrant)
- Appel OpenAI uniquement côté backend (`OPENAI_API_KEY`) et uniquement sur extraits pertinents

Modern, local-first MVP for consulting-style insights over your own PDF library. Runs fully on your MacBook Pro with offline-first services (only the optional LLM call uses OpenAI).

### Highlights
- **Local-first**: Postgres + Qdrant locally via Docker
- **Business-ready UX**: Apple/Perplexity-inspired, dark mode, glassmorphism
- **Modular microservices**: gateway, document, vector, RAG, report, status
- **Branding**: Include your SVG logo across UI and exported PDFs

### Folder Structure
```
frontend/
  nextjs/
  streamlit/
gateway-api/
document-service/
vector-service/
rag-service/
report-service/
status-service/
data/
  pdfs/
  logo/
  reports/
vectorstore/
  qdrant/
scripts/
  ingest.py
docker-compose.yml
.env.example
```

### Services & Ports
- frontend-nextjs: 3000
- gateway-api: 8000
- document-service: 8001
- vector-service: 8002
- rag-service: 8003
- report-service: 8004
- status-service: 8005
- qdrant: 6333
- postgres: 5432

### Quickstart
1) Copy and edit env
```bash
cp .env.example .env
```
2) Start stack
```bash
docker compose up -d --build
```
3) Check health
```bash
curl -s http://localhost:8000/health | jq
```
4) Add PDFs
Place your files in `data/pdfs/` then trigger ingestion:
```bash
python3 scripts/ingest.py --folder ./data/pdfs --api http://localhost:8001
```

### API Endpoints (high-level)
- gateway-api: proxies to microservices and hosts OpenAPI docs
- document-service:
  - POST `/upload_pdf` (multipart)
  - GET `/documents`
  - DELETE `/document/{id}`
  - POST `/ingest_folder`
- vector-service:
  - POST `/upsert_embedding`
  - POST `/search`
  - GET `/collections`
- rag-service:
  - POST `/generate_report`
  - POST `/ask_question`
- report-service:
  - POST `/export_pdf`
  - GET `/reports`
  - GET `/reports/{id}`
- status-service:
  - GET `/status`
  - GET `/logs`

## 🎯 Exemples d'Utilisation - Les 5 Analyses

### 1. Synthèse Exécutive
```bash
curl -X POST http://localhost:8000/analysis/synthesize \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Quelles sont les principales opportunités stratégiques identifiées?",
    "title": "Synthèse Stratégique Q4 2024"
  }'
```

### 2. Analyse Concurrentielle
```bash
curl -X POST http://localhost:8000/analysis/competition \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Mapping des concurrents et positionnement marché",
    "title": "Analyse Concurrentielle 2024"
  }'
```

### 3. Veille Technologique
```bash
curl -X POST http://localhost:8000/analysis/tech-watch \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Technologies émergentes et innovations disruptives",
    "title": "Tech Watch IA & Innovation"
  }'
```

### 4. Analyse de Risques
```bash
curl -X POST http://localhost:8000/analysis/risk-analysis \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Cartographie des risques et mesures de mitigation",
    "title": "Risk Assessment Global"
  }'
```

### 5. Étude de Marché
```bash
curl -X POST http://localhost:8000/analysis/market-study \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Taille de marché et perspectives de croissance",
    "title": "Market Research 2024"
  }'
```

### Workflow Complet (Analyse + Rapport)
```bash
curl -X POST 'http://localhost:8000/workflows/analyze-and-report?analysis_type=synthesize&query=Synthèse stratégique complète&title=Rapport Automatisé&auto_export=true'
```

### Development
- Each service: Python 3.11-slim base, `requirements.txt`, `Dockerfile`, `/health`
- Shared DB (Postgres) for `documents`, `users` (future), and `reports_history`
- Qdrant for vector search; interchangeable via adapter design

### Frontend
- Next.js (app router) with Apple-like styling and dark mode
- Optional Streamlit skeleton under `frontend/streamlit`

## 🏗️ Architecture Technique

### Stack Technologique
- **Backend**: Python 3.11 + FastAPI + SQLAlchemy
- **Base de données**: PostgreSQL (documents, rapports)
- **Vector DB**: Qdrant (embeddings et recherche sémantique)
- **IA**: OpenAI API (GPT-4o-mini + text-embedding-3-small)
- **PDF Processing**: PyPDF + pdfplumber
- **Reports**: ReportLab (génération PDF professionnelle)
- **Container**: Docker + Docker Compose
- **Tests**: Pytest + httpx

### Microservices
- **gateway-api** (8000): Point d'entrée unique avec Swagger
- **document-service** (8001): Ingestion et gestion des PDFs
- **vector-service** (8002): Embeddings OpenAI + recherche Qdrant
- **rag-service** (8003): 5 prompts d'analyse IA spécialisés
- **report-service** (8004): Génération rapports PDF professionnels
- **status-service** (8005): Monitoring et santé système

### Données et Volumes
```
data/
├── pdfs/        # Documents PDF source
├── reports/     # Rapports générés  
└── logo/        # Assets de branding
```

### Variables d'Environnement Clés
```bash
OPENAI_API_KEY=sk-...              # Clé API OpenAI (requis)
DATABASE_URL=postgresql://...      # Base PostgreSQL
QDRANT_HOST=qdrant                 # Service Qdrant
EMBEDDING_MODEL=text-embedding-3-small
```

## 🧪 Tests et Validation

### Suite de Tests Complète
```bash
# Tests unitaires par service
docker-compose exec document-service pytest
docker-compose exec vector-service pytest  
docker-compose exec rag-service pytest
docker-compose exec report-service pytest
docker-compose exec gateway-api pytest

# Tests d'intégration complets
./scripts/test_all_services.sh

# Tests workflow end-to-end
python3 scripts/test_workflow.py
```

### Couverture de Tests
- ✅ Tests unitaires pour chaque service
- ✅ Tests d'intégration des API  
- ✅ Tests des 5 types d'analyse IA
- ✅ Tests de génération de rapports PDF
- ✅ Tests de workflow complet
- ✅ Tests de santé des services
- ✅ Mocks OpenAI pour tests hors ligne

## 📊 Monitoring et Observabilité

### Health Checks
```bash
# Santé globale du système
curl http://localhost:8000/health/services

# Statistiques par service
curl http://localhost:8000/documents/stats
curl http://localhost:8000/reports/stats
```

### Logs Structurés
- **Loguru** pour logging Python structuré
- Logs par container avec `docker-compose logs [service]`
- Niveaux: DEBUG, INFO, WARNING, ERROR

### Métriques Business
- Nombre de documents ingérés
- Analyses IA générées par type
- Rapports PDF produits
- Temps de réponse par endpoint

## 🚀 Roadmap V2/V3

### Fonctionnalités Avancées
- 🤖 **LLM local** via Ollama (alternative à OpenAI)
- 📈 **Analytics avancées** (tendances, benchmarks, heatmaps)
- 🔐 **Authentification** multi-tenant (JWT/OAuth)
- 📱 **Interface web** React/Next.js moderne
- 🔄 **Ingestion temps réel** avec daemon de surveillance
- 👁️ **OCR pipeline** pour PDFs scannés
- 📑 **Export avancé** vers PPTX/Keynote
- 🌍 **Multi-langue** et internationalisation
- ⚡ **Cache intelligent** pour performances
- 📊 **Tableaux de bord** exécutifs temps réel

### Déploiement Production
- 🐳 **Kubernetes** manifests
- 🔒 **Sécurité renforcée** (HTTPS, secrets management)
- 📈 **Auto-scaling** basé sur la charge
- 💾 **Backup automatique** bases de données
- 🌐 **CDN** pour assets et rapports
- 📱 **API mobile** dédiée


