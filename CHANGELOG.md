# 📝 CHANGELOG - Insight MVP

## [v1.1.0] - 2025-09-20 - RAG Amélioré + Interface Gradio

### 🎯 **Milestone: RAG Professionnel avec Formatage McKinsey/BCG**

#### ✨ **Nouvelles Fonctionnalités**

**🧠 Service RAG Amélioré**
- Vraie recherche vectorielle avec scores de pertinence
- Formatage professionnel style consultant (McKinsey/BCG)
- Templates structurés pour les 5 types d'analyses
- Citations et références documentaires automatiques
- GPT-4o-mini avec 4000 tokens pour réponses complètes

**🎨 Interface Gradio Moderne**
- Dashboard interactif avec métriques temps réel
- Interface utilisateur dark theme professionnelle
- Boutons d'actions rapides pour chaque analyse
- Composants modulaires (api_client, dashboard)

**📚 Indexation Documentaire**
- Scripts d'indexation automatique des PDFs
- Gestion 87 documents financiers
- Timeout optimisé pour gros fichiers
- Indexation par batch avec retry

#### 🔧 **Améliorations Techniques**

**Backend**
- Multiple versions RAG (working, enhanced, final) pour stabilité
- Gestion robuste erreurs OpenAI avec fallbacks
- Recherche vectorielle Qdrant + OpenAI embeddings
- Architecture microservices maintenue

**Frontend**
- Composants Gradio réutilisables
- CSS personnalisé pour branding
- API client asynchrone avec httpx

#### 🐛 **Corrections**
- Fix paramètres OpenAI (max_tokens vs max_completion_tokens)
- Ajout dépendance `requests` manquante dans rag-service
- Dockerfiles vector-service et rag-service mis à jour
- Timeout indexation optimisé pour stabilité

#### 📁 **Nouvelle Structure**
```
insight-mvp/
├── frontend-gradio/          # Interface Gradio moderne
│   ├── app/                  # Applications (main, simple, minimal)
│   ├── components/           # Composants réutilisables
│   └── assets/               # CSS et ressources
├── scripts/                  # Indexation et tests
│   ├── index_all_pdfs.py     # Indexation complète
│   └── index_quick.py        # Test rapide 3 PDFs
└── rag-service/app/          # Multiple versions RAG
    ├── rag_main.py           # Version finale optimisée
    ├── enhanced_main.py      # Version améliorée
    └── working_main.py       # Version stable
```

## [v1.0.0] - 2024-09-20 - Initial MVP Release

### 🎯 **Milestone: Backend Microservices MVP Complet**

#### ✅ **Features Implémentées**

**🏗️ Architecture Microservices**
- Gateway API centralisé (port 8000) avec Swagger
- 5 microservices spécialisés (ports 8001-8005)
- Docker Compose orchestration complète
- PostgreSQL + Qdrant pour persistance et recherche vectorielle

**🤖 Intelligence Artificielle - 5 Analyses Spécialisées**
- ✅ Synthèse Exécutive - Recommandations stratégiques
- ✅ Analyse Concurrentielle - Mapping concurrentiel  
- ✅ Veille Technologique - Innovations et tendances tech
- ✅ Analyse de Risques - Cartographie et mitigation
- ✅ Étude de Marché - Projections et scénarios

**📄 Gestion Documentaire**
- Ingestion PDF automatique avec PyPDF2
- Chunking intelligent avec overlap
- Extraction et indexation de contenu
- API CRUD complète pour documents

**🔍 Recherche Sémantique**
- Embeddings OpenAI (text-embedding-3-small)
- Stockage vectoriel Qdrant optimisé
- Recherche par similarité sémantique

**📊 Génération de Rapports**
- Formatage PDF professionnel avec ReportLab
- Templates consulting personnalisables
- Métadonnées et sources intégrées

**✅ Tests et Validation**
- Tests unitaires pour chaque service
- Scripts de validation E2E
- Health checks complets
- Documentation API interactive

#### 🔧 **Services Déployés**

| Service | Port | Status | Description |
|---------|------|---------|-------------|
| **gateway-api** | 8000 | ✅ | Point d'entrée unique + Swagger |
| **document-service** | 8001 | ✅ | Ingestion et gestion PDFs |
| **vector-service** | 8002 | ⚠️ | Embeddings + recherche Qdrant |
| **rag-service** | 8003 | ✅ | 5 analyses IA spécialisées |
| **report-service** | 8004 | ⚠️ | Génération rapports PDF |
| **status-service** | 8005 | ✅ | Monitoring système |

#### 📁 **Structure Projet**
```
insight-mvp/
├── gateway-api/           # Point d'entrée API
├── document-service/      # Gestion documents PDF
├── vector-service/        # Recherche sémantique
├── rag-service/          # 5 prompts IA spécialisés
├── report-service/       # Génération rapports
├── status-service/       # Monitoring
├── scripts/              # Tests et validation
├── data/                 # Documents et rapports
└── docker-compose.yml    # Orchestration complète
```

#### 🚀 **Commandes de Démarrage**
```bash
# Configuration
cp env.example .env
# Ajouter OPENAI_API_KEY dans .env

# Lancement
docker compose up -d --build

# Validation
python3 scripts/final_validation.py
```

#### 📚 **Documentation**
- Swagger UI: http://localhost:8000/docs
- API Gateway: http://localhost:8000
- Tests complets: `./scripts/test_all_services.sh`

#### 🔮 **Prochaines Versions**
- [ ] v1.1.0 - Correction vector-service et report-service
- [ ] v1.2.0 - Interface web React/Next.js
- [ ] v2.0.0 - LLM local avec Ollama
- [ ] v2.1.0 - Authentification multi-tenant

---

## [v0.9.0] - 2024-09-20 - Pre-Release

### 🛠️ **Setup Initial**
- Configuration Docker et microservices
- Développement des 5 services backend
- Intégration OpenAI et Qdrant
- Tests et validation système

---

## 📋 **Format de Versioning**

**Semantic Versioning (SemVer):** `MAJOR.MINOR.PATCH`

- **MAJOR** : Changements incompatibles
- **MINOR** : Nouvelles fonctionnalités compatibles  
- **PATCH** : Corrections de bugs compatibles

**Tags de Développement:**
- `feat:` Nouvelle fonctionnalité
- `fix:` Correction de bug
- `docs:` Documentation
- `refactor:` Refactoring code
- `test:` Tests
- `chore:` Maintenance
