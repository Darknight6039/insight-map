# 🚀 Quick Start - Memory Service

## Démarrage en 3 Étapes

### 1️⃣ Démarrer Docker Desktop

Assurez-vous que Docker Desktop est en cours d'exécution sur votre Mac.

### 2️⃣ Lancer le Déploiement

```bash
cd /Users/isaiaebongue/insight-mvp
./deploy-complete-memory-integration.sh
```

Ce script va automatiquement:
- ✓ Créer les tables de base de données
- ✓ Démarrer le memory-service
- ✓ Rebuild le frontend
- ✓ Vérifier que tout fonctionne

**Durée:** ~3-5 minutes

### 3️⃣ Tester l'Application

Ouvrez votre navigateur:

```
http://localhost:3000
```

**Connexion:**
- Email: `admin@axial.com`
- Password: `admin123`

**Nouvelles fonctionnalités:**
- 📝 **Historique** - Cliquez sur "Historique" dans la navbar
- 📚 **Bibliothèque** - Cliquez sur "Bibliothèque" dans la navbar

---

## ✅ Vérification Rapide

Après le déploiement, vérifiez:

```bash
# 1. Memory service fonctionne
curl http://localhost:8008/health

# 2. Frontend accessible
curl http://localhost:3000

# 3. Lancer les tests automatiques
./test-memory-service.sh
```

---

## 🎯 Que Tester?

### Page Historique (`/history`)
1. Voir toutes vos conversations passées
2. Rechercher dans les conversations
3. Filtrer par type (chat/analyse)
4. Supprimer des conversations

### Page Bibliothèque (`/library`)
1. Voir tous vos rapports et veilles
2. Filtrer par type (rapport/veille)
3. Rechercher dans les documents
4. Télécharger les PDF
5. Supprimer des documents

---

## 📚 Documentation Complète

- **Vue d'ensemble:** `MEMORY_SERVICE_README.md`
- **Backend:** `MEMORY_SERVICE_DEPLOYMENT.md`
- **Frontend:** `FRONTEND_MEMORY_INTEGRATION.md`
- **Changements:** `CHANGES_SUMMARY.md`

---

## 🐛 Problème?

```bash
# Voir les logs
docker-compose logs -f memory-service
docker-compose logs -f frontend-openwebui

# Redémarrer tout
docker-compose restart

# Ou relancer le déploiement
./deploy-complete-memory-integration.sh
```

---

## 🎉 C'est Tout!

Vous êtes prêt à utiliser le nouveau système de mémoire avec historique et bibliothèque intégrés.

**Bon test! 🚀**
