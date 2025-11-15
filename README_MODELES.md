# Configuration Modèles Perplexity

**Date**: 15 novembre 2025  
**Version**: v4.0-sonar-pro-exclusive  
**Status**: ✅ Configuration Active

---

## Vue d'Ensemble

L'application utilise une stratégie multi-modèles Perplexity optimisée selon le type de requête, permettant d'optimiser les coûts tout en maximisant la qualité des rapports.

---

## Configuration Actuelle

### Rapports (Tous Types)

**Modèle**: `sonar-pro`  
**Max tokens**: 12 000  
**Timeout**: 7.5 minutes (450s)  
**Température**: 0.1  

**Utilisation**:
- ✅ Rapports standards (15-25 sources)
- ✅ Rapports approfondis (60 sources, 8000-10000 mots)
- ✅ Analyses sectorielles
- ✅ Études concurrentielles
- ✅ Veilles technologiques
- ✅ Analyses de risques
- ✅ Études de marché

**Configuration**:
```python
# backend-service/app/main.py (ligne 47)
"analysis": os.getenv("PERPLEXITY_MODEL_ANALYSIS", "sonar-pro")

# Endpoint impacté
task_type="analysis"  # Tous les rapports
```

**Caractéristiques**:
- Recherche web extensive (native Perplexity)
- Citations multiples et croisement de sources
- Génération longue (8000-10000 mots pour rapports approfondis)
- Hiérarchie stricte des sources (60% institutionnelles, 20% académiques, 15% média, 5% autres)

---

### Chat

**Modèle**: `sonar`  
**Max tokens**: 6 000  
**Timeout**: 5 minutes (300s)  
**Température**: 0.1  

**Utilisation**:
- ✅ Conversations courtes
- ✅ Réponses rapides (2-4 paragraphes)
- ✅ 5-8 sources minimum

**Configuration**:
```python
# backend-service/app/main.py (ligne 46)
"chat": os.getenv("PERPLEXITY_MODEL_CHAT", "sonar")

# Endpoints impactés
task_type="chat"  # Conversations
```

**Caractéristiques**:
- Coût optimisé (~70% moins cher que sonar-pro)
- Réponses concises et sourcées
- Recherche web Perplexity pour informations actuelles

---

### Reasoning (Non Utilisé)

**Modèle**: `sonar-reasoning`  
**Max tokens**: 16 000 (configuré mais non utilisé)  
**Statut**: Réservé pour usage futur  

**Configuration**:
```python
# backend-service/app/main.py (ligne 48)
"reasoning": os.getenv("PERPLEXITY_MODEL_REASONING", "sonar-reasoning")

# Aucun endpoint ne l'utilise actuellement
```

**Note**: Ce modèle est configuré pour des analyses complexes multi-étapes futures mais n'est pas actuellement utilisé dans l'application.

---

## Détails Techniques

### Sélection Dynamique

Le modèle est sélectionné automatiquement selon le `task_type` passé à la fonction `call_perplexity_safe()`:

```python
def get_model_for_task(task_type: str) -> str:
    """Sélectionne le modèle Sonar approprié selon la tâche"""
    return PERPLEXITY_MODELS.get(task_type, PERPLEXITY_MODELS["chat"])
```

### Configuration Max Tokens

```python
max_tokens_config = {
    "sonar": 6000,
    "sonar-pro": 12000,  # Rapports standards ET approfondis
    "sonar-reasoning": 16000  # Non utilisé actuellement
}
```

### Endpoints par Type

| Endpoint | Task Type | Modèle | Max Tokens | Usage |
|----------|-----------|--------|------------|-------|
| `/extended-analysis` | `analysis` | `sonar-pro` | 12000 | Rapports détaillés |
| `/business-analysis` | `analysis` | `sonar-pro` | 12000 | Analyses métier |
| `/chat` | `chat` | `sonar` | 6000 | Conversations |
| `/chat/stream` | `chat` | `sonar` | 6000 | Chat streaming |
| `/test-perplexity` | `chat` | Tous | Varie | Tests config |

---

## Rapports Approfondis (60 Sources)

### Détection Automatique

Les rapports approfondis sont détectés par la présence du mot "approfondi" dans `analysis_type`:

```python
if "approfondi" in analysis_type.lower():
    # Template spécial 60 sources
```

### Configuration Spécifique

**Modèle**: `sonar-pro` (identique aux rapports standards)  
**Max tokens**: 12 000 (identique, suffisant pour 60 sources)  
**Timeout**: 7.5 minutes (permettant génération longue)  

**Exigences**:
- Minimum 60 sources organisées par catégorie
- 36 sources institutionnelles (60%)
- 12 sources académiques (20%)
- 9 sources média réputé (15%)
- 3 sources complémentaires (5%)
- 50+ données chiffrées avec sources croisées
- 5+ tableaux comparatifs détaillés
- 8000-10000 mots

**Template Prompt**:
```python
prompt_templates_deep = {
    "finance_banque": """
    **FORMAT** : Rapport ultra-détaillé (8000-10000 mots) avec 60 sources MINIMUM
    
    ## HIÉRARCHIE SOURCES STRICTE (60 sources) :
    - 36 sources institutionnelles (60%)
    - 12 sources académiques (20%)
    - 9 sources média réputé (15%)
    - 3 sources complémentaires (5%)
    """
}
```

---

## Variables d'Environnement

### Fichier `.env`

```bash
# Perplexity API
PERPLEXITY_API_KEY=pplx-xxxxx

# Configuration multi-modèles
PERPLEXITY_MODEL_CHAT=sonar
PERPLEXITY_MODEL_ANALYSIS=sonar-pro
PERPLEXITY_MODEL_REASONING=sonar-reasoning
```

### Valeurs par Défaut

Si les variables ne sont pas définies, l'application utilise les valeurs par défaut:
- Chat: `sonar`
- Analysis: `sonar-pro`
- Reasoning: `sonar-reasoning`

---

## Optimisation Coûts

### Répartition Actuelle

| Type Requête | Volume Estimé | Modèle | Coût/1K tokens | Impact |
|--------------|---------------|--------|----------------|--------|
| Chat | 70% | sonar | $0.001 | Optimisé ✅ |
| Rapports standards | 25% | sonar-pro | $0.003 | Qualité max ✅ |
| Rapports approfondis | 5% | sonar-pro | $0.003 | Qualité max ✅ |

### Économies

- **Chat**: ~70% moins cher que si on utilisait sonar-pro
- **Rapports**: Qualité maximale justifiant le coût
- **Économie globale estimée**: ~50-60% sur coûts API totaux

---

## Monitoring

### Vérifier Configuration

```bash
# Health check avec configuration modèles
curl http://localhost:8006/health | jq '.perplexity_models'
```

**Sortie attendue**:
```json
{
  "chat": "sonar",
  "analysis": "sonar-pro",
  "reasoning": "sonar-reasoning"
}
```

### Logs Backend

```bash
# Voir modèle utilisé par requête
docker compose logs -f backend-service | grep "Using model"
```

**Exemples**:
```
INFO: Using model: sonar-pro for task: analysis (max_tokens: 12000)
INFO: Using model: sonar for task: chat (max_tokens: 6000)
```

### Logs Progression Rapports

```bash
# Suivre progression génération rapport
docker compose logs -f backend-service | grep -E '\[.*\]'
```

**Sortie typique**:
```
📊 [1/5] Recherche documents RAG...
✓ [1/5] Trouvé 12 documents RAG
📝 [2/5] Formatage contexte documentaire...
✓ [2/5] Contexte formaté (4823 caractères)
🎯 [3/5] Création prompt optimisé...
✓ [3/5] Prompt créé (type: 60 sources)
🌐 [4/5] Appel Perplexity API (60 sources, estimation: 90-120s)...
INFO: Using model: sonar-pro for task: analysis (max_tokens: 12000)
✓ [4/5] Contenu généré par Perplexity
✅ [5/5] Finalisation du rapport...
✓ [5/5] Rapport finalisé avec 12 sources RAG
```

---

## Tests

### Test Configuration Modèles

```bash
curl http://localhost:8006/test-perplexity | jq
```

**Résultat attendu**:
```json
{
  "status": "success",
  "models_tested": {
    "chat": {
      "model": "sonar",
      "status": "✅ OK"
    },
    "analysis": {
      "model": "sonar-pro",
      "status": "✅ OK"
    },
    "reasoning": {
      "model": "sonar-reasoning",
      "status": "✅ OK"
    }
  }
}
```

### Test Rapport Standard

```bash
curl -X POST http://localhost:8006/extended-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "finance_banque",
    "analysis_type": "synthese_executive",
    "query": "Analyse marché bancaire français 2025"
  }' | jq '.metadata.model'
```

**Résultat attendu**: `"sonar-pro"`

### Test Rapport Approfondi

```bash
curl -X POST http://localhost:8006/extended-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "finance_banque",
    "analysis_type": "analyse_approfondie",
    "query": "Analyse exhaustive marché bancaire français"
  }' | jq '.metadata.model'
```

**Résultat attendu**: `"sonar-pro"` (identique, mais avec 60 sources)

---

## FAQ

### Pourquoi sonar-pro pour tous les rapports?

**Réponse**: sonar-pro offre la meilleure qualité pour la génération longue (8000-10000 mots) avec recherche web extensive. Avec 12000 tokens, il peut générer aussi bien des rapports standards (15-25 sources) que des rapports approfondis (60 sources) sans limitation.

### Pourquoi ne pas utiliser sonar-reasoning?

**Réponse**: sonar-reasoning (16000 tokens) est conçu pour des analyses complexes multi-étapes avec raisonnement structuré. Actuellement, nos rapports n'utilisent pas ce niveau de complexité. sonar-pro (12000 tokens) est suffisant et plus économique.

### Peut-on changer le modèle dynamiquement?

**Réponse**: Oui, via les variables d'environnement. Modifier `.env` puis redémarrer:
```bash
PERPLEXITY_MODEL_ANALYSIS=sonar-reasoning  # Exemple: tester reasoning
docker compose restart backend-service
```

### Les 60 sources fonctionnent avec 12000 tokens?

**Réponse**: Oui. Le nombre de sources ne dépend pas des tokens mais de la recherche web Perplexity. Les 12000 tokens concernent la longueur du rapport généré (8000-10000 mots + bibliographie), ce qui est largement suffisant.

### Comment forcer un rapport standard à utiliser 60 sources?

**Réponse**: Inclure "approfondi" dans `analysis_type`:
```json
{
  "analysis_type": "synthese_executive_approfondie"
}
```

---

## Références

- **Documentation Perplexity**: https://docs.perplexity.ai/
- **Modèles Sonar**: https://docs.perplexity.ai/docs/model-cards
- **Pricing**: https://www.perplexity.ai/pricing
- **Configuration Backend**: `backend-service/app/main.py` (lignes 43-52, 543-550)
- **Configuration Env**: `env.example` (lignes 17-22)

---

**Dernière mise à jour**: 15 novembre 2025  
**Maintenu par**: Équipe Insight MVP

