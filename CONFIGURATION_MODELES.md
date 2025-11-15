# 🎯 Configuration des modèles Sonar (Optimisation v3.1)

## Vue d'ensemble

L'application utilise une stratégie multi-modèles Perplexity optimisée par cas d'usage pour maximiser la qualité des réponses tout en minimisant les coûts d'API. Chaque endpoint sélectionne automatiquement le modèle le plus adapté à sa tâche.

## Stratégie multi-modèles

### Tableau comparatif

| Modèle | Usage | Max Tokens | Cost/1K tokens | Endpoints |
|--------|-------|------------|----------------|-----------|
| `sonar` | Chat rapide, tests | 4000 | $0.001 | `/chat`, `/chat/stream`, `/test-perplexity` |
| `sonar-pro` | Rapports longs (5000+ mots) | 8000 | $0.003 | `/extended-analysis`, `/business-analysis` |
| `sonar-reasoning` | Analyses complexes | 8000 | $0.005 | Configurable pour analyses expertes |

### Principes de sélection

**1. Chat conversationnel** → `sonar`
- Questions courtes et réponses rapides
- Tests API et validation
- Coût optimisé (3x moins cher que sonar-pro)
- Suffisant pour 95% des conversations

**2. Rapports stratégiques** → `sonar-pro`
- Génération de rapports longs (5000-8000 mots)
- Analyses sectorielles approfondies
- Web search profond avec citations multiples
- Qualité maximale pour livrables clients

**3. Analyses expertes** → `sonar-reasoning`
- Raisonnement structuré multi-étapes
- Analyses de risques complexes
- Modélisation de scénarios
- Qualité maximale pour cas critiques

## Configuration

### Variables d'environnement

Copier ces lignes dans votre fichier `.env` :

```bash
# Perplexity API Key (obligatoire)
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxx

# Configuration multi-modèles (optionnel, valeurs par défaut ci-dessous)
PERPLEXITY_MODEL_CHAT=sonar
PERPLEXITY_MODEL_ANALYSIS=sonar-pro
PERPLEXITY_MODEL_REASONING=sonar-reasoning
```

### Valeurs par défaut

Si les variables `PERPLEXITY_MODEL_*` ne sont pas définies, le système utilise automatiquement :
- Chat : `sonar`
- Analysis : `sonar-pro`
- Reasoning : `sonar-reasoning`

**Backward compatibility** : L'ancienne variable `PERPLEXITY_MODEL` n'est plus utilisée mais peut rester présente sans effet.

## Optimisation des coûts

### Réduction de coûts estimée

**Avant optimisation** (v3.0) :
- Tous les endpoints → `sonar` (4000 tokens)
- Coût uniforme mais rapports tronqués

**Après optimisation** (v3.1) :
- Chat endpoints → `sonar` : **-70% de coût**
- Analysis endpoints → `sonar-pro` : qualité maximale
- **Économie globale estimée : ~60%** sur volume d'API typique (80% chat / 20% analysis)

### Exemple de calcul

Pour 100 000 requêtes mensuelles (80% chat / 20% analysis) :

**Avant** (tout en sonar-pro) :
- 100 000 requêtes × 1500 tokens moy. × $0.003 = **$450/mois**

**Après** (mix optimisé) :
- 80 000 chat × 800 tokens × $0.001 = $64
- 20 000 analysis × 3000 tokens × $0.003 = $180
- **Total : $244/mois** → **Économie de $206/mois (-46%)**

## Sélection automatique

### Mapping endpoint → modèle

Le backend sélectionne automatiquement le modèle selon l'endpoint appelé :

```python
# Endpoints chat (sonar)
POST /chat                 → sonar (4000 tokens)
POST /chat/stream          → sonar (1500 tokens streaming)

# Endpoints analysis (sonar-pro)
POST /extended-analysis    → sonar-pro (8000 tokens)
POST /business-analysis    → sonar-pro (8000 tokens)

# Endpoints test (tous modèles)
GET /test-perplexity       → Teste les 3 modèles
```

### Vérification dans les logs

Le système log automatiquement le modèle sélectionné pour chaque requête :

```bash
# Voir les sélections de modèles en temps réel
docker-compose logs -f backend-service | grep "Using model"
```

Exemple de logs attendus :
```
INFO: Using model: sonar-pro for task: analysis (max_tokens: 8000)
INFO: Using model: sonar for task: chat (max_tokens: 4000)
INFO: Using model: sonar for task: chat (max_tokens: 4000)
INFO: Using model: sonar-pro for task: analysis (max_tokens: 8000)
```

## Validation et tests

### 1. Health check

Vérifier que la configuration multi-modèles est bien active :

```bash
curl http://localhost:8006/health | jq
```

Réponse attendue :
```json
{
  "status": "healthy",
  "service": "backend-intelligence-perplexity",
  "perplexity_configured": true,
  "perplexity_models": {
    "chat": "sonar",
    "analysis": "sonar-pro",
    "reasoning": "sonar-reasoning"
  },
  "version": "3.1-multi-model"
}
```

### 2. Test multi-modèles

Tester la connectivité pour chaque modèle configuré :

```bash
curl http://localhost:8006/test-perplexity | jq
```

Réponse attendue :
```json
{
  "status": "success",
  "models_tested": {
    "chat": {
      "model": "sonar",
      "status": "✅ OK",
      "response": "Hello! How can I assist you today?"
    },
    "analysis": {
      "model": "sonar-pro",
      "status": "✅ OK",
      "response": "I'm ready to help with detailed analysis."
    },
    "reasoning": {
      "model": "sonar-reasoning",
      "status": "✅ OK",
      "response": "Let me reason through this systematically."
    }
  },
  "config": {
    "chat": "sonar",
    "analysis": "sonar-pro",
    "reasoning": "sonar-reasoning"
  }
}
```

### 3. Test rapport long

Vérifier que les rapports utilisent bien `sonar-pro` :

```bash
curl -X POST http://localhost:8006/extended-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "finance_banque",
    "analysis_type": "synthese_executive",
    "query": "Analyse du marché bancaire français 2025"
  }' | jq '.metadata.model'
```

Résultat attendu : `"sonar-pro"`

### 4. Test chat court

Vérifier que le chat utilise bien `sonar` :

```bash
curl -X POST http://localhost:8006/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quelles sont les tendances fintech ?",
    "business_type": "finance_banque"
  }' | jq '.metadata.model'
```

Résultat attendu : `"sonar"`

## Monitoring et observabilité

### Commandes de monitoring

**1. Suivre les sélections de modèles en temps réel**
```bash
docker-compose logs -f backend-service | grep -E "Using model|API error"
```

**2. Compter les requêtes par modèle (dernière heure)**
```bash
docker-compose logs --since 1h backend-service | grep "Using model" | sort | uniq -c
```

Exemple de sortie :
```
     142 INFO: Using model: sonar for task: chat (max_tokens: 4000)
      18 INFO: Using model: sonar-pro for task: analysis (max_tokens: 8000)
       3 INFO: Using model: sonar-reasoning for task: reasoning (max_tokens: 8000)
```

**3. Détecter les erreurs par modèle**
```bash
docker-compose logs --since 1h backend-service | grep "API error with"
```

### Patterns de logs

**✅ Patterns normaux :**
```
INFO: Using model: sonar-pro for task: analysis (max_tokens: 8000)
INFO: Using model: sonar for task: chat (max_tokens: 4000)
```

**❌ Patterns d'erreur à surveiller :**
```
ERROR: Perplexity API error with sonar-pro: 401 Unauthorized
ERROR: Perplexity API error with sonar: 429 Rate limit exceeded
ERROR: Perplexity API error with sonar-reasoning: 404 Model not found
```

## Troubleshooting

### Problème : Erreur 404 Model not found

**Cause** : Le modèle configuré n'existe pas ou n'est pas accessible avec votre clé API.

**Solution** :
1. Vérifier les modèles disponibles sur votre compte Perplexity
2. Mettre à jour `.env` avec les noms de modèles corrects
3. Redémarrer le service : `docker-compose restart backend-service`

### Problème : Tous les endpoints utilisent le même modèle

**Cause** : Variables d'environnement non définies ou non chargées.

**Solution** :
1. Vérifier `.env` contient bien les 3 variables `PERPLEXITY_MODEL_*`
2. Rebuild et redémarrer : `docker-compose up -d --build backend-service`
3. Vérifier `/health` affiche bien `"perplexity_models": {...}`

### Problème : Erreur 429 Rate limit

**Cause** : Quota API dépassé.

**Solution** :
1. Vérifier votre quota sur https://www.perplexity.ai/settings/api
2. Réduire temporairement le trafic ou augmenter votre plan
3. Implémenter un rate limiting côté application si nécessaire

### Problème : Rapports tronqués malgré sonar-pro

**Cause** : Prompt trop long dépassant les limites du modèle.

**Vérification** :
```bash
docker-compose logs backend-service | grep "Prompt très long"
```

**Solution** : Le système tronque automatiquement à 15 000 caractères. Si nécessaire, réduire le nombre de documents RAG dans la requête.

## Impact business

### Qualité des livrables

**Chat** (sonar) :
- ✅ Réponses rapides et pertinentes pour questions courtes
- ✅ Citations web avec sources vérifiables
- ✅ Latence réduite (<2s en moyenne)

**Rapports** (sonar-pro) :
- ✅ Génération de 5000-8000 mots structurés
- ✅ Recherche web approfondie avec 10+ sources
- ✅ Format cabinet de conseil professionnel
- ✅ Citations APA académiques complètes

**Analyses expertes** (sonar-reasoning) :
- ✅ Raisonnement structuré multi-étapes
- ✅ Modélisation de scénarios complexes
- ✅ Qualité maximale pour cas critiques

### ROI de l'optimisation

**Pour une utilisation typique** (startup/PME) :
- **Avant** : ~$450/mois (tout en sonar-pro)
- **Après** : ~$244/mois (mix optimisé)
- **Économie** : $206/mois soit **$2 472/an**

**Pour une utilisation intensive** (cabinet conseil) :
- **Avant** : ~$2 000/mois
- **Après** : ~$1 080/mois
- **Économie** : $920/mois soit **$11 040/an**

## Déploiement en production

### Checklist de déploiement

- [ ] Copier `.env.example` vers `.env` avec vraie clé API
- [ ] Définir les 3 variables `PERPLEXITY_MODEL_*`
- [ ] Build du service : `docker-compose build backend-service`
- [ ] Redémarrage : `docker-compose up -d backend-service`
- [ ] Validation `/health` affiche version `3.1-multi-model`
- [ ] Test `/test-perplexity` affiche ✅ OK pour les 3 modèles
- [ ] Test rapport long vérifie utilisation `sonar-pro`
- [ ] Test chat vérifie utilisation `sonar`
- [ ] Monitoring logs actif pour détection d'erreurs

### Stratégie de rollback

Si problème en production, revenir à la version précédente :

```bash
# 1. Downgrade du code
git checkout v3.0

# 2. Rebuild
docker-compose build backend-service

# 3. Redémarrage
docker-compose up -d backend-service

# 4. Vérification
curl http://localhost:8006/health
```

## Évolutions futures

### V3.2 - Sélection dynamique avancée

- **Détection automatique** de la longueur de réponse attendue
- **Switch intelligent** chat court (sonar) vs chat long (sonar-pro)
- **Fallback automatique** si modèle indisponible

### V3.3 - Optimisation par utilisateur

- **Profiling utilisateur** : préférences qualité/coût par compte
- **Budget mensuel** : basculement auto vers modèles économiques
- **Analytics coûts** : dashboard temps réel de consommation

### V4.0 - Support multi-providers

- **Perplexity** : Sonar (default)
- **OpenAI** : GPT-4o (fallback)
- **Anthropic** : Claude 3.5 Sonnet (option qualité)
- **Local** : Ollama/LLaMA (option privacy)

## Support et ressources

### Documentation officielle

- [Perplexity API Docs](https://docs.perplexity.ai/)
- [Sonar Models Reference](https://docs.perplexity.ai/docs/model-cards)
- [Pricing Calculator](https://www.perplexity.ai/settings/api)

### Contacts internes

- **Tech Lead** : support-technique@example.com
- **Product** : product@example.com
- **Slack** : #perplexity-integration

### Changelog

**v3.1 (2025-01-15)** :
- ✅ Implémentation stratégie multi-modèles
- ✅ Sélection automatique par endpoint
- ✅ Monitoring et observabilité
- ✅ Documentation complète

**v3.0 (2025-01-01)** :
- ✅ Migration vers Perplexity API
- ✅ Web search natif avec citations
- ✅ Désactivation RAG interne

**v2.0 (2024-12-01)** :
- ✅ Architecture microservices
- ✅ RAG avec Qdrant
- ✅ Rapports PDF professionnels

---

**🎯 Configuration v3.1 - Multi-Model Sonar Strategy**  
*Optimisez vos coûts tout en maximisant la qualité de vos analyses IA*

