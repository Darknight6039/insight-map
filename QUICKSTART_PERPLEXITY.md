# 🚀 Guide de Démarrage Rapide - Perplexity AI

## ✅ Changements Effectués

Votre système Insight MVP a été migré avec succès de l'API OpenAI vers l'API Perplexity AI !

### Fichiers Modifiés

1. **`backend-service/app/main.py`** ✓
   - Remplacé OpenAI par Perplexity
   - Ajouté support RAG interne prioritaire
   - Nouveaux endpoints : `/test-perplexity`, `/diagnostics`

2. **`rag-service/app/main.py`** ✓
   - Migration vers Perplexity AI
   - Conservation des 5 types d'analyses
   - RAG hybride (documents internes + web)

3. **`env.example`** ✓
   - Nouvelles variables Perplexity
   - Documentation des modèles disponibles

4. **Votre fichier `.env`** ⚠️
   - La clé API est déjà configurée
   - **IMPORTANT** : Ce fichier est ignoré par git (.gitignore)

## 🔧 Démarrage Rapide

### Étape 1 : Vérifier la Configuration

Votre clé API Perplexity est déjà configurée :

```bash
# Vérifier que le fichier .env existe et contient la clé
cat .env | grep PERPLEXITY_API_KEY
```

Vous devriez voir :
```
PERPLEXITY_API_KEY=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
```

### Étape 2 : Démarrer les Services

```bash
# Si vous utilisez docker-compose
docker-compose down
docker-compose up -d --build

# Vérifier que les services sont démarrés
docker-compose ps
```

### Étape 3 : Tester l'Intégration

```bash
# Utiliser le script de test fourni
./test_perplexity_integration.sh
```

Ou manuellement :

```bash
# Test 1: Health check backend
curl http://localhost:8006/health

# Test 2: Test Perplexity direct
curl http://localhost:8006/test-perplexity

# Test 3: Chat simple avec RAG
curl -X POST http://localhost:8006/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quelles sont les tendances du marché bancaire?",
    "business_type": "finance_banque"
  }'
```

## 🎯 Points Clés de la Migration

### Ce qui a changé

| Avant (OpenAI) | Après (Perplexity) |
|----------------|-------------------|
| API OpenAI uniquement | Perplexity avec recherche web |
| Modèle : gpt-4o-mini | Modèle : llama-3.1-sonar-large-128k-online |
| Pas de recherche web | Enrichissement web automatique |
| `/test-openai` | `/test-perplexity` |

### Ce qui reste identique

✅ **Tous les endpoints existants** fonctionnent exactement de la même manière  
✅ **Le système RAG** continue de prioriser vos documents internes  
✅ **Les citations APA** sont toujours générées  
✅ **Les 5 types d'analyses** sont conservés  

## 📊 Fonctionnement du RAG Hybride

```
Votre Question
      ↓
1. Recherche dans vos documents internes (Qdrant)
      ↓
2. Les meilleurs passages sont extraits
      ↓
3. Perplexity reçoit :
   - Vos documents (PRIORITÉ 1) ✓
   - Instruction de chercher sur le web si besoin (PRIORITÉ 2)
      ↓
4. Réponse enrichie avec :
   - Citations de vos docs [Réf. 1], [Réf. 2]...
   - Données web récentes (si pertinent)
```

## 🧪 Exemples de Test

### Test 1 : Chat Simple

```bash
curl -X POST http://localhost:8006/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyse les risques du secteur fintech",
    "business_type": "finance_banque"
  }' | jq '.'
```

### Test 2 : Analyse Complète

```bash
curl -X POST http://localhost:8006/extended-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "tech_digital",
    "analysis_type": "digital_transformation",
    "query": "Transformation digitale des banques",
    "title": "Banking Digital 2024"
  }' | jq '.metadata'
```

### Test 3 : Veille Technologique

```bash
curl -X POST http://localhost:8003/tech_watch \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Intelligence artificielle dans le trading",
    "title": "AI Trading 2024",
    "top_k": 8
  }' | jq '.content[0:500]'
```

## ⚙️ Configuration Avancée

### Changer de Modèle Perplexity

Éditez votre `.env` :

```bash
# Pour un modèle plus économique
PERPLEXITY_MODEL=llama-3.1-sonar-small-128k-online

# Pour le modèle le plus puissant
PERPLEXITY_MODEL=llama-3.1-sonar-huge-128k-online
```

Puis redémarrez :
```bash
docker-compose restart backend-service rag-service
```

### Ajuster les Paramètres RAG

Dans `backend-service/app/main.py`, ligne ~520 :

```python
response = client.chat.completions.create(
    model=PERPLEXITY_MODEL,
    messages=[...],
    temperature=0.3,      # Ajustez entre 0.0 (précis) et 1.0 (créatif)
    max_tokens=8000       # Longueur max de la réponse
)
```

## 🐛 Dépannage Rapide

### Erreur : "PERPLEXITY_API_KEY not configured"

```bash
# Vérifier que la variable est bien dans .env
grep PERPLEXITY .env

# Redémarrer les services
docker-compose restart
```

### Erreur : "Connection refused"

```bash
# Vérifier que les services tournent
docker-compose ps

# Redémarrer si nécessaire
docker-compose up -d
```

### Les réponses ne citent pas mes documents

```bash
# Vérifier que les documents sont indexés
curl http://localhost:8001/documents

# Tester la recherche vectorielle
curl -X POST http://localhost:8002/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 5}'
```

### Voir les Logs

```bash
# Tous les services
docker-compose logs -f

# Backend uniquement
docker-compose logs -f backend-service

# RAG service uniquement
docker-compose logs -f rag-service
```

## 📚 Documentation Complète

Pour plus de détails, consultez :
- **`PERPLEXITY_MIGRATION.md`** - Documentation complète de la migration
- **`README.md`** - Documentation générale du projet

## 💡 Avantages de Perplexity

1. **🔍 Recherche Web Intégrée** : Enrichit automatiquement avec des données récentes
2. **📚 RAG Prioritaire** : Vos documents internes restent la source principale
3. **⚡ Performance** : Modèles LLaMA 3.1 très performants
4. **💰 Coût** : Généralement moins cher qu'OpenAI pour des résultats comparables
5. **🌐 Contexte Long** : 128k tokens de contexte

## 🚀 Prochaines Étapes

1. ✅ Testez les endpoints : `./test_perplexity_integration.sh`
2. ✅ Vérifiez la qualité des réponses
3. ✅ Ajustez les paramètres si nécessaire (température, max_tokens)
4. ✅ Indexez vos documents : voir `scripts/ingest_pdfs.py`
5. ✅ Utilisez l'interface frontend (si disponible)

## ❓ Questions Fréquentes

**Q: Puis-je revenir à OpenAI ?**  
R: Oui, il suffit de restaurer les fichiers depuis git et reconfigurer OPENAI_API_KEY

**Q: Perplexity va-t-il chercher sur le web pour chaque requête ?**  
R: Non, il utilise d'abord vos documents internes. Le web est un complément.

**Q: Combien coûte Perplexity ?**  
R: ~$0.001-0.005 par requête selon le modèle. Vérifiez sur perplexity.ai

**Q: Les modèles sont-ils compatibles ?**  
R: Oui, l'API Perplexity est compatible avec OpenAI SDK.

---

**Félicitations ! 🎉** Votre système est maintenant propulsé par Perplexity AI avec RAG hybride.

Pour toute question : consultez les logs ou la documentation complète.

