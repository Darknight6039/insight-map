# ✅ CONFIGURATION FINALE - Perplexity AI Uniquement

**Date** : 14 Novembre 2024, 17:00  
**Status** : ✅ CONFIGURATION OPTIMALE

---

## 🎯 CONFIGURATION ACTUELLE

### Mode de Fonctionnement

**✅ PERPLEXITY UNIQUEMENT** - Recherche Web Pure

- **Modèle** : `sonar`
- **Provider** : Perplexity AI
- **Mode** : `perplexity_web_only`
- **RAG Interne** : `disabled` (désactivé)
- **Recherche** : Web uniquement via Perplexity

---

## 🔧 SERVICES CONFIGURÉS

### 1. Backend Service (Port 8006)

**Configuration :**
```bash
PERPLEXITY_API_KEY=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
PERPLEXITY_MODEL=sonar
PERPLEXITY_BASE_URL=https://api.perplexity.ai
```

**Mode** : RAG Hybride (documents internes + Perplexity)
- Priorité 1: Documents Qdrant internes
- Priorité 2: Enrichissement web Perplexity

**Endpoints :**
- `/health` - Status
- `/test-perplexity` - Test API
- `/chat` - Chat avec RAG hybride
- `/extended-analysis` - Rapports longs

### 2. RAG Service (Port 8003)

**Configuration :**
```bash
PERPLEXITY_API_KEY=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
PERPLEXITY_MODEL=sonar
PERPLEXITY_BASE_URL=https://api.perplexity.ai
```

**Mode** : ✅ **PERPLEXITY WEB UNIQUEMENT**
- ❌ Pas de recherche vectorielle interne
- ✅ Recherche web Perplexity uniquement
- ✅ Citations avec URLs
- ✅ Données toujours à jour

**Endpoints :**
- `/synthesize` - Synthèse exécutive
- `/analyze_competition` - Analyse concurrentielle  
- `/tech_watch` - Veille technologique
- `/risk_analysis` - Analyse des risques
- `/market_study` - Étude de marché

---

## 📊 DIFFÉRENCES ENTRE LES SERVICES

| Aspect | Backend (8006) | RAG Service (8003) |
|--------|----------------|-------------------|
| **Modèle** | `sonar` | `sonar` |
| **RAG Interne** | ✅ Activé | ❌ Désactivé |
| **Recherche Web** | ✅ Complément | ✅ Uniquement |
| **Documents Qdrant** | ✅ Utilisés | ❌ Ignorés |
| **Mode** | Hybride | Web Only |
| **Cas d'usage** | Chat avec contexte interne | Analyses avec données web récentes |

---

## 🎯 QUAND UTILISER CHAQUE SERVICE ?

### Backend Service (Port 8006) - RAG Hybride

**Utiliser pour :**
- 💬 Chat interactif avec vos documents internes
- 📊 Analyses basées sur VOS données propriétaires
- 🔍 Questions sur vos documents spécifiques
- 📚 Quand vous voulez citer vos propres sources

**Exemple :**
```bash
curl -X POST http://localhost:8006/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyse nos rapports internes sur le marché",
    "business_type": "finance_banque"
  }'
```

### RAG Service (Port 8003) - Perplexity Web Only

**Utiliser pour :**
- 🌐 Analyses avec données web les plus récentes
- 📈 Veille marché et tendances actuelles
- 🔬 Recherches nécessitant des sources externes
- 📰 Informations d'actualité

**Exemple :**
```bash
curl -X POST http://localhost:8003/tech_watch \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Dernières innovations IA 2024",
    "title": "AI Innovations 2024"
  }'
```

---

## 🧪 TESTS DE VALIDATION

### Test 1 : Backend Service (RAG Hybride)

```bash
curl -s http://localhost:8006/health | python3 -m json.tool
```

**Résultat attendu :**
```json
{
    "status": "healthy",
    "service": "backend-intelligence-perplexity",
    "perplexity_configured": true,
    "perplexity_model": "sonar",
    "version": "2.0-perplexity-rag"
}
```

### Test 2 : RAG Service (Perplexity Only)

```bash
curl -s http://localhost:8003/health | python3 -m json.tool
```

**Résultat attendu :**
```json
{
    "status": "ok",
    "service": "rag-service",
    "ai_provider": "Perplexity AI",
    "model": "sonar",
    "perplexity_configured": true,
    "mode": "perplexity_web_only",
    "rag_internal": "disabled"
}
```

### Test 3 : Analyse Web Only

```bash
curl -X POST http://localhost:8003/synthesize \
  -H "Content-Type: application/json" \
  -d '{"query": "Tendances fintech 2024", "title": "Fintech 2024"}'
```

**Vérification :**
- ✅ `mode: "perplexity_web_only"`
- ✅ `passages_count: 0` (pas de RAG interne)
- ✅ Contenu avec données web récentes
- ✅ Citations d'URLs externes

---

## 📱 ACCÈS AUX INTERFACES

### Frontend OpenWebUI (Port 3000)

**URL :** http://localhost:3000

**Configuration :**
- Se connecte au Backend Service (Port 8006)
- Mode : RAG Hybride
- Chat avec documents internes + web

### Tests API Directs

**Backend (RAG Hybride) :**
```bash
# Chat avec vos documents
curl -X POST http://localhost:8006/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Question", "business_type": "finance_banque"}'
```

**RAG Service (Web Only) :**
```bash
# Analyse web pure
curl -X POST http://localhost:8003/market_study \
  -H "Content-Type: application/json" \
  -d '{"query": "Marché fintech France", "title": "Étude Fintech"}'
```

---

## ⚙️ ARCHITECTURE TECHNIQUE

### Backend Service - RAG Hybride

```
Requête Utilisateur
       ↓
1. Recherche Vectorielle (Qdrant)
   → Documents internes Top-K
       ↓
2. Contexte RAG créé
   → Passages pertinents extraits
       ↓
3. Perplexity AI (modèle "sonar")
   → PRIORITÉ 1: Documents internes [Réf. X]
   → PRIORITÉ 2: Enrichissement web si nécessaire
       ↓
4. Réponse Enrichie
   → Citations internes + web
   → Format APA professionnel
```

### RAG Service - Perplexity Web Only

```
Requête Utilisateur
       ↓
1. ❌ PAS de recherche vectorielle
       ↓
2. Prompt direct pour Perplexity
   → Instructions de recherche web
       ↓
3. Perplexity AI (modèle "sonar")
   → Recherche web uniquement
   → Capacités natives de Perplexity
       ↓
4. Réponse Web Pure
   → Citations URLs externes
   → Données actualisées
```

---

## 🔑 VARIABLES D'ENVIRONNEMENT (.env)

```bash
# Perplexity AI Configuration
PERPLEXITY_API_KEY=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
PERPLEXITY_MODEL=sonar

# Services URLs
VECTOR_URL=http://vector-service:8002
RAG_URL=http://rag-service:8003

# Database
POSTGRES_USER=insight_user
POSTGRES_PASSWORD=insight_password_2024
POSTGRES_DB=insight_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333
```

---

## 🎯 AVANTAGES DE CETTE CONFIGURATION

### Backend Service (RAG Hybride)

✅ **Confidentialité** - Vos documents restent privés  
✅ **Précision** - Répond avec VOS données exactes  
✅ **Traçabilité** - Citations de vos documents  
✅ **Contrôle** - Vous gérez votre base de connaissances  

### RAG Service (Perplexity Only)

✅ **Actualité** - Toujours les données les plus récentes  
✅ **Couverture** - Accès à tout le web  
✅ **Simplicité** - Pas de maintenance de base de données  
✅ **Citations** - URLs externes vérifiables  

---

## 📊 EXEMPLES D'UTILISATION

### Exemple 1 : Chat avec Documents Internes

**Service** : Backend (8006)  
**Use Case** : Question sur vos propres documents

```bash
curl -X POST http://localhost:8006/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Résume nos stratégies de 2023",
    "business_type": "finance_banque"
  }'
```

**Résultat** :
- Recherche dans VOS documents
- Citations [Réf. 1], [Réf. 2] de vos PDFs
- Enrichissement web si pertinent

### Exemple 2 : Veille Technologique Actuelle

**Service** : RAG (8003)  
**Use Case** : Tendances tech récentes

```bash
curl -X POST http://localhost:8003/tech_watch \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Innovations IA novembre 2024",
    "title": "AI Watch Nov 2024"
  }'
```

**Résultat** :
- Recherche web pure via Perplexity
- Données du web les plus récentes
- Citations d'URLs externes

### Exemple 3 : Analyse Mixte

**Étape 1** : Consulter documents internes (Backend)
```bash
curl -X POST http://localhost:8006/chat \
  -d '{"message": "Nos positions actuelles sur l IA"}'
```

**Étape 2** : Compléter avec veille externe (RAG)
```bash
curl -X POST http://localhost:8003/market_study \
  -d '{"query": "Marché IA entreprise 2024"}'
```

---

## 🛠️ COMMANDES DE MAINTENANCE

### Redémarrer les Services

```bash
# Redémarrer backend
docker compose restart backend-service

# Redémarrer RAG service
docker compose restart rag-service

# Redémarrer tous les services
docker compose restart
```

### Reconstruire après Modification

```bash
# Backend
docker compose build --no-cache backend-service
docker compose up -d backend-service

# RAG service
docker compose build --no-cache rag-service
docker compose up -d rag-service
```

### Voir les Logs

```bash
# Backend logs
docker compose logs -f backend-service

# RAG service logs
docker compose logs -f rag-service

# Tous les logs
docker compose logs -f
```

---

## 📚 DOCUMENTATION COMPLÈTE

1. **`SETUP_COMPLET.md`** - Guide complet de setup
2. **`CONFIGURATION_FINALE.md`** - Ce fichier (configuration détaillée)
3. **`PERPLEXITY_MIGRATION.md`** - Documentation de migration
4. **`QUICKSTART_PERPLEXITY.md`** - Démarrage rapide

---

## ✅ CHECKLIST FINALE

- [x] Clé API Perplexity configurée
- [x] Modèle "sonar" défini partout
- [x] Backend Service en mode RAG Hybride
- [x] RAG Service en mode Web Only
- [x] Frontend connecté au backend
- [x] Tous les services testés et fonctionnels
- [x] Documentation complète créée

---

## 🎉 RÉSUMÉ

Votre système Insight MVP est maintenant configuré avec **deux modes complémentaires** :

1. **Backend Service (Port 8006)** : RAG Hybride
   - Documents internes + enrichissement Perplexity
   - Pour questions sur VOS données

2. **RAG Service (Port 8003)** : Perplexity Web Only
   - Recherche web pure via Perplexity
   - Pour veille et tendances actuelles

**Les deux utilisent le modèle `sonar` de Perplexity AI** ✅

---

**Status** : ✅ OPÉRATIONNEL  
**Version** : 2.0-perplexity-dual-mode  
**Date** : 14 Novembre 2024, 17:00

