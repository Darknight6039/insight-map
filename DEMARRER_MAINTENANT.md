# 🚀 DÉMARRER L'APPLICATION MAINTENANT

## ⚡ Commandes à Exécuter (Copier-Coller)

Ouvrez votre terminal et exécutez ces commandes une par une :

### 📍 Étape 1 : Aller dans le dossier du projet

```bash
cd /Users/isaiaebongue/insight-mvp
```

### 🛑 Étape 2 : Arrêter les anciens conteneurs

```bash
docker-compose down
```

### 🔨 Étape 3 : Reconstruire avec Perplexity (IMPORTANT)

```bash
docker-compose build --no-cache backend-service rag-service
```

⏱️ **Cela prendra 2-3 minutes...**

### ▶️ Étape 4 : Démarrer tous les services

```bash
docker-compose up -d
```

### ⏳ Étape 5 : Attendre 30 secondes

```bash
sleep 30
```

### ✅ Étape 6 : Vérifier que tout fonctionne

```bash
curl http://localhost:8006/health
```

**Vous devriez voir :**
```json
{
  "status": "healthy",
  "service": "backend-intelligence-perplexity",
  "perplexity_configured": true,
  "perplexity_model": "llama-3.1-sonar-large-128k-online"
}
```

### 🧪 Étape 7 : Tester Perplexity

```bash
curl http://localhost:8006/test-perplexity
```

---

## 🚀 DÉMARRAGE AUTOMATIQUE (RECOMMANDÉ)

Ou utilisez simplement le script automatique :

```bash
cd /Users/isaiaebongue/insight-mvp
./start_perplexity.sh
```

Ce script fait tout automatiquement ! ✨

---

## 📊 Vérifier le Status

```bash
docker-compose ps
```

Tous les services doivent être "Up" (en cours d'exécution).

---

## 📋 Voir les Logs

```bash
# Tous les services
docker-compose logs -f

# Ou juste le backend
docker-compose logs -f backend-service
```

Appuyez sur `Ctrl+C` pour arrêter de voir les logs.

---

## 🎯 Tester l'API Complète

```bash
./test_perplexity_integration.sh
```

---

## 🛑 Arrêter l'Application

```bash
docker-compose down
```

---

## ❓ Problèmes ?

### "Permission denied"

```bash
chmod +x start_perplexity.sh
chmod +x test_perplexity_integration.sh
```

### "Port already in use"

```bash
docker-compose down
lsof -i :8006
kill -9 [PID]
docker-compose up -d
```

### "Cannot connect to Docker"

Démarrez Docker Desktop, puis réessayez.

---

## ✨ C'est Tout !

Une fois démarré, votre application sera accessible sur :

- **Backend API** : http://localhost:8006
- **Tests** : http://localhost:8006/test-perplexity
- **Diagnostics** : http://localhost:8006/diagnostics

**Bonne utilisation ! 🎉**

