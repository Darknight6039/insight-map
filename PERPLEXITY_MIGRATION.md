# Migration vers Perplexity AI - Guide Complet

## 🚀 Aperçu

Le système Insight MVP a été migré de l'API OpenAI vers l'API Perplexity AI. Cette migration apporte deux avantages majeurs :

1. **RAG Interne Prioritaire** : Les documents internes de votre base de connaissances sont utilisés en priorité
2. **Enrichissement Web** : Perplexity complète automatiquement avec des données web récentes et pertinentes

## 🔑 Configuration de l'API Perplexity

### 1. Obtenir votre clé API

1. Visitez [https://www.perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)
2. Créez un compte ou connectez-vous
3. Générez une nouvelle clé API
4. Copiez la clé (format: `pplx-xxxxx...`)

### 2. Configuration de l'environnement

La clé API a déjà été configurée dans votre fichier `.env` :

```bash
PERPLEXITY_API_KEY=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
PERPLEXITY_MODEL=llama-3.1-sonar-large-128k-online
```

### 3. Modèles disponibles

Vous pouvez choisir parmi plusieurs modèles Perplexity :

- **`llama-3.1-sonar-large-128k-online`** (recommandé) - Modèle le plus puissant avec recherche web
- **`llama-3.1-sonar-small-128k-online`** - Plus rapide, moins coûteux
- **`llama-3.1-sonar-huge-128k-online`** - Performance maximale

Pour changer de modèle, modifiez la variable `PERPLEXITY_MODEL` dans `.env`.

## 📚 Fonctionnement du RAG Hybride

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Requête Utilisateur                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│           1. Recherche Vectorielle Interne              │
│        (Qdrant - Base de documents internes)            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│    2. Contexte RAG Enrichi avec Documents Internes      │
│         - Top 5-10 passages les plus pertinents         │
│         - Métadonnées et citations APA                  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│           3. Perplexity AI avec Instructions            │
│    PRIORITÉ 1: Documents internes [Réf. X]              │
│    PRIORITÉ 2: Enrichissement web si nécessaire         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│               4. Réponse Enrichie                        │
│    - Sources internes citées [Réf. 1], [Réf. 2]...     │
│    - Données web récentes (si pertinent)                │
│    - Recommandations actionnables                       │
└─────────────────────────────────────────────────────────┘
```

### Priorités de Recherche

Le système est configuré pour :

1. **TOUJOURS prioriser vos documents internes** avec citations [Réf. X]
2. **Compléter avec le web** uniquement quand nécessaire (statistiques récentes, benchmarks, etc.)
3. **Distinguer clairement** les sources internes des sources web

## 🧪 Tests et Validation

### 1. Tester la connexion Perplexity

```bash
# Démarrer les services
docker-compose up -d

# Tester l'endpoint de santé
curl http://localhost:8006/health

# Réponse attendue :
{
  "status": "healthy",
  "service": "backend-intelligence-perplexity",
  "perplexity_configured": true,
  "perplexity_model": "llama-3.1-sonar-large-128k-online",
  "version": "2.0-perplexity-rag"
}

# Test direct de Perplexity
curl http://localhost:8006/test-perplexity
```

### 2. Tester le RAG Service

```bash
curl http://localhost:8003/health

# Réponse attendue :
{
  "status": "ok",
  "service": "rag-service",
  "ai_provider": "Perplexity AI",
  "model": "llama-3.1-sonar-large-128k-online",
  "perplexity_configured": true
}
```

### 3. Test complet d'analyse

```bash
curl -X POST http://localhost:8006/extended-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "finance_banque",
    "analysis_type": "market_analysis",
    "query": "Analyse du marché bancaire français 2024"
  }'
```

## 📊 Endpoints Disponibles

### Backend Service (Port 8006)

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | État du service |
| `/test-perplexity` | GET | Test de connexion Perplexity |
| `/diagnostics` | GET | Diagnostics complets |
| `/extended-analysis` | POST | Rapport long style cabinet conseil |
| `/business-analysis` | POST | Analyse métier |
| `/chat` | POST | Chat intelligent avec RAG |
| `/chat/stream` | POST | Chat en streaming |

### RAG Service (Port 8003)

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | État du service |
| `/synthesize` | POST | Synthèse exécutive |
| `/analyze_competition` | POST | Analyse concurrentielle |
| `/tech_watch` | POST | Veille technologique |
| `/risk_analysis` | POST | Analyse des risques |
| `/market_study` | POST | Étude de marché |

## 🎯 Exemples d'Utilisation

### Exemple 1 : Chat Simple

```python
import requests

response = requests.post(
    "http://localhost:8006/chat",
    json={
        "message": "Quelles sont les tendances du marché fintech en 2024 ?",
        "business_type": "finance_banque"
    }
)

result = response.json()
print(result["response"])  # Réponse avec citations
print(result["sources"])    # Sources utilisées
```

### Exemple 2 : Analyse Approfondie

```python
import requests

response = requests.post(
    "http://localhost:8006/extended-analysis",
    json={
        "business_type": "tech_digital",
        "analysis_type": "digital_transformation",
        "query": "Transformation digitale du secteur bancaire",
        "title": "Digital Banking 2024"
    }
)

report = response.json()
print(report["content"])     # Rapport complet (6000+ mots)
print(report["sources"])     # Sources citées avec APA
print(report["metadata"])    # Métadonnées (modèle, provider, etc.)
```

### Exemple 3 : Veille Technologique

```python
import requests

response = requests.post(
    "http://localhost:8003/tech_watch",
    json={
        "query": "Intelligence artificielle dans le trading",
        "title": "AI Trading Watch 2024",
        "top_k": 10
    }
)

analysis = response.json()
print(analysis["content"])   # Analyse tech détaillée
```

## 🔧 Dépannage

### Erreur : "PERPLEXITY_API_KEY not configured"

**Solution** : Vérifiez que votre fichier `.env` contient bien :
```bash
PERPLEXITY_API_KEY=pplx-xxxxx...
```

Redémarrez les services :
```bash
docker-compose down
docker-compose up -d
```

### Erreur : "Perplexity API error"

**Causes possibles** :
1. Clé API invalide ou expirée
2. Quota dépassé
3. Problème de connectivité

**Solution** :
1. Vérifiez votre clé sur [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)
2. Consultez votre quota et factures
3. Testez avec `curl https://api.perplexity.ai` (doit répondre)

### Les sources internes ne sont pas utilisées

**Solution** :
1. Vérifiez que vos documents sont bien indexés :
   ```bash
   curl http://localhost:8001/documents
   ```

2. Testez la recherche vectorielle :
   ```bash
   curl -X POST http://localhost:8002/search \
     -H "Content-Type: application/json" \
     -d '{"query": "votre recherche", "top_k": 5}'
   ```

3. Vérifiez les logs du backend-service :
   ```bash
   docker-compose logs backend-service
   ```

## 💰 Coûts Perplexity

### Tarification (approximative, à vérifier sur leur site)

- **Requêtes API** : ~$0.001 - $0.005 par requête selon le modèle
- **Tokens** : Facturation par tokens (input + output)
- **Plans** : Gratuit avec limites, puis plans payants

### Optimisation des Coûts

1. **Utilisez le modèle small** pour des analyses simples :
   ```bash
   PERPLEXITY_MODEL=llama-3.1-sonar-small-128k-online
   ```

2. **Limitez les documents retournés** (top_k) :
   ```python
   {"query": "...", "top_k": 5}  # au lieu de 10
   ```

3. **Mettez en cache** les réponses fréquentes (à implémenter)

## 🚀 Prochaines Étapes

### Améliorations Futures

1. **Cache Redis** : Mettre en cache les réponses fréquentes
2. **Retry Logic** : Gérer automatiquement les erreurs temporaires
3. **Rate Limiting** : Éviter de dépasser les quotas
4. **Fallback** : Basculer sur OpenAI en cas d'échec Perplexity
5. **Analytics** : Suivre l'utilisation et les coûts

### Configuration Avancée

Pour des besoins spécifiques, vous pouvez ajuster :

- **Temperature** (0.0 - 1.0) : Créativité des réponses
- **Max Tokens** : Longueur maximale des réponses
- **Top K** : Nombre de documents RAG à utiliser

Modifiez ces paramètres dans :
- `backend-service/app/main.py` (fonction `call_perplexity_safe`)
- `rag-service/app/main.py` (fonction `call_perplexity`)

## 📞 Support

Pour toute question ou problème :
1. Consultez les logs : `docker-compose logs -f`
2. Testez les endpoints : `/health`, `/diagnostics`
3. Vérifiez la documentation Perplexity : [docs.perplexity.ai](https://docs.perplexity.ai)

---

**Version** : 2.0-perplexity-rag  
**Dernière mise à jour** : Novembre 2024

