# 🚀 Instructions de Démarrage - Insight MVP avec Perplexity

## ✅ Étape 1 : Préparation

### Vérifiez que Docker est installé

```bash
docker --version
docker-compose --version
```

Si Docker n'est pas installé, téléchargez-le : https://www.docker.com/products/docker-desktop

### Vérifiez la configuration

```bash
# Vérifier que le fichier .env existe
ls -la .env

# Vérifier la clé Perplexity
cat .env | grep PERPLEXITY_API_KEY
```

Vous devriez voir :
```
PERPLEXITY_API_KEY=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
```

---

## 🚀 Étape 2 : Démarrage Automatique (RECOMMANDÉ)

### Option A : Script Automatique

```bash
# Exécuter le script de démarrage complet
./start_perplexity.sh
```

Ce script va :
1. ✅ Vérifier les prérequis
2. ✅ Arrêter les conteneurs existants
3. ✅ Reconstruire les images avec Perplexity
4. ✅ Démarrer tous les services
5. ✅ Exécuter les tests (optionnel)

**⏱️ Durée estimée : 3-5 minutes**

---

## 🔧 Étape 3 : Démarrage Manuel (Alternative)

Si vous préférez contrôler chaque étape :

### 1. Arrêter les conteneurs existants

```bash
docker-compose down
```

### 2. Reconstruire les images (IMPORTANT pour Perplexity)

```bash
# Reconstruire backend-service et rag-service
docker-compose build --no-cache backend-service rag-service

# Ou reconstruire tout
docker-compose build --no-cache
```

### 3. Démarrer les services

```bash
docker-compose up -d
```

### 4. Vérifier le status

```bash
docker-compose ps
```

Vous devriez voir tous les services "Up" :
```
NAME                          STATUS
insight_mvp-backend-service   Up
insight_mvp-rag-service       Up
insight_mvp-vector-service    Up
insight_mvp-document-service  Up
insight_mvp-postgres          Up
insight_mvp-qdrant            Up
...
```

---

## 🧪 Étape 4 : Tests de Validation

### Test 1 : Health Check

```bash
curl http://localhost:8006/health
```

**Résultat attendu :**
```json
{
  "status": "healthy",
  "service": "backend-intelligence-perplexity",
  "perplexity_configured": true,
  "perplexity_model": "llama-3.1-sonar-large-128k-online",
  "version": "2.0-perplexity-rag"
}
```

### Test 2 : Test Perplexity Direct

```bash
curl http://localhost:8006/test-perplexity
```

**Résultat attendu :**
```json
{
  "status": "success",
  "message": "Perplexity API functional",
  "model": "llama-3.1-sonar-large-128k-online",
  "response": "Hello..."
}
```

### Test 3 : Chat avec RAG

```bash
curl -X POST http://localhost:8006/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quelles sont les tendances du marché?",
    "business_type": "finance_banque"
  }'
```

### Test 4 : Suite de Tests Complète

```bash
./test_perplexity_integration.sh
```

---

## 📊 Étape 5 : Surveillance

### Voir les logs en temps réel

```bash
# Tous les services
docker-compose logs -f

# Backend uniquement
docker-compose logs -f backend-service

# RAG service uniquement
docker-compose logs -f rag-service
```

### Vérifier l'utilisation des ressources

```bash
docker stats
```

---

## 🐛 Dépannage

### Problème 1 : Port déjà utilisé

```bash
# Trouver le processus utilisant le port
lsof -i :8006

# Tuer le processus (remplacer PID)
kill -9 PID

# Ou changer le port dans docker-compose.yml
```

### Problème 2 : Erreur de build

```bash
# Nettoyer tout et reconstruire
docker-compose down -v
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

### Problème 3 : Service ne démarre pas

```bash
# Voir les logs d'erreur
docker-compose logs backend-service
docker-compose logs rag-service

# Redémarrer un service spécifique
docker-compose restart backend-service
```

### Problème 4 : Erreur "PERPLEXITY_API_KEY not configured"

```bash
# Vérifier le .env
cat .env | grep PERPLEXITY

# Si la clé est manquante, l'ajouter
echo "PERPLEXITY_API_KEY=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" >> .env

# Redémarrer
docker-compose restart backend-service rag-service
```

### Problème 5 : Conteneurs en statut "Restarting"

```bash
# Voir les logs pour comprendre pourquoi
docker-compose logs --tail=100 [service-name]

# Souvent lié à :
# - Base de données pas prête
# - Variable d'environnement manquante
# - Erreur dans le code
```

---

## 🔄 Commandes Utiles

### Redémarrer les services

```bash
# Tous les services
docker-compose restart

# Service spécifique
docker-compose restart backend-service rag-service
```

### Arrêter les services

```bash
# Arrêter sans supprimer
docker-compose stop

# Arrêter et supprimer les conteneurs
docker-compose down

# Arrêter et supprimer conteneurs + volumes
docker-compose down -v
```

### Reconstruire après modification de code

```bash
# Arrêter
docker-compose down

# Reconstruire
docker-compose build backend-service rag-service

# Redémarrer
docker-compose up -d
```

### Accéder à un conteneur

```bash
# Shell interactif
docker-compose exec backend-service bash

# Exécuter une commande
docker-compose exec backend-service python --version
```

---

## 📈 Vérification de Succès

Votre installation est réussie si :

✅ Tous les services sont "Up" : `docker-compose ps`  
✅ Health check répond : `curl http://localhost:8006/health`  
✅ Test Perplexity fonctionne : `curl http://localhost:8006/test-perplexity`  
✅ Pas d'erreurs dans les logs : `docker-compose logs --tail=50`  
✅ Tests d'intégration passent : `./test_perplexity_integration.sh`  

---

## 🎯 Services Disponibles

Une fois démarrés, vous pouvez accéder à :

| Service | URL | Description |
|---------|-----|-------------|
| Backend (Perplexity) | http://localhost:8006 | API principale avec Perplexity |
| Backend Health | http://localhost:8006/health | Status du service |
| Backend Test | http://localhost:8006/test-perplexity | Test API Perplexity |
| Backend Diagnostics | http://localhost:8006/diagnostics | Diagnostics complets |
| RAG Service | http://localhost:8003/health | Service d'analyse RAG |
| Vector Service | http://localhost:8002/health | Service de recherche vectorielle |
| Document Service | http://localhost:8001/health | Gestion des documents |
| Gateway API | http://localhost:8000/docs | API Gateway (Swagger) |

---

## 📚 Documentation Supplémentaire

- **Guide Rapide** : `QUICKSTART_PERPLEXITY.md`
- **Documentation Complète** : `PERPLEXITY_MIGRATION.md`
- **Résumé Technique** : `MIGRATION_SUMMARY.md`
- **Aperçu Général** : `README_PERPLEXITY.md`

---

## 💡 Conseils

1. **Première exécution** : Utilisez `./start_perplexity.sh` pour un démarrage guidé
2. **Développement** : Utilisez `docker-compose logs -f` pour suivre les logs
3. **Production** : Configurez des healthchecks et du monitoring
4. **Performance** : Ajustez les ressources dans `docker-compose.yml` si nécessaire

---

## ✨ Prêt !

Votre système Insight MVP avec Perplexity AI est maintenant opérationnel !

**Pour commencer :**
```bash
./start_perplexity.sh
```

Bon coding ! 🚀

