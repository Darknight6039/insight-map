# 🚀 Configuration et Démarrage - Insight MVP

## ⚡ Configuration Rapide

### 1. Configurer la clé API OpenAI

```bash
cd /Users/isaiaebongue/insight-mvp

# Méthode A : Utiliser le script automatique
chmod +x setup-env.sh
./setup-env.sh

# Méthode B : Créer manuellement le .env
cat > .env << 'EOF'
OPENAI_API_KEY=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
QDRANT_URL=http://qdrant:6333
VECTOR_SERVICE_URL=http://vector-service:8002
POSTGRES_DB=insight_db
POSTGRES_USER=user
POSTGRES_PASSWORD=password
DATABASE_URL=postgresql://user:password@postgres:5432/insight_db
NEXT_PUBLIC_BACKEND_URL=http://localhost:8006
EOF
```

### 2. Rebuild et Démarrer les Services

```bash
# Rebuild le backend avec les nouveaux timeouts (300s = 5 min)
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
docker compose build backend-service

# Démarrer tous les services
docker compose up -d

# Vérifier que tout tourne
docker compose ps

# Logs en temps réel (si besoin)
docker compose logs -f backend-service
```

### 3. Tester l'Application

```bash
# Test backend health
curl http://localhost:8006/health

# Test OpenAI
curl http://localhost:8006/test-openai

# Ouvrir l'application
open http://localhost:3000
```

---

## 🔧 Corrections Appliquées

### ✅ Timeouts augmentés
- **Avant** : 30 secondes → ⏱️ Timeout pour rapports longs
- **Après** : 300 secondes (5 min) → ✅ Rapports détaillés OK

### ✅ Clé API OpenAI configurée
- Clé valide ajoutée au .env
- Quota vérifié et opérationnel

---

## 🎯 Scénario de Démo

### 1. Page d'accueil
- Sélectionner **"Finance & Banque"**

### 2. Onglet "Analyses"
- **Query** : "Tendances IA et transformation digitale bancaire"
- **Type** : "Veille Technologique"
- Cliquer "Lancer l'analyse" ⏳ (1-2 min)
- ✅ Rapport de 6000+ mots généré
- 📄 Export PDF avec logo Axial

### 3. Chat avec Citations
- **Question** : "Quels sont les principaux risques de l'IA en finance ?"
- Voir citations cliquables [¹][²][³]
- Cliquer sur badge → Modal avec document

---

## 📊 Services et Ports

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend | 8006 | http://localhost:8006 |
| RAG Service | 8003 | http://localhost:8003 |
| Report Service | 8004 | http://localhost:8004 |
| Qdrant | 6333 | http://localhost:6333 |
| PostgreSQL | 5432 | localhost:5432 |

---

## 🐛 Troubleshooting

### Erreur "Request timed out"
✅ **RÉSOLU** : Timeouts augmentés à 300s

### Erreur "Invalid API Key"
```bash
# Vérifier .env
cat .env | grep OPENAI_API_KEY

# Recréer si besoin
./setup-env.sh
docker compose restart backend-service
```

### Services ne démarrent pas
```bash
# Nettoyer et recréer
docker compose down
docker compose up -d --force-recreate
```

---

## ✨ Fonctionnalités

- ✅ Chat avec citations APA cliquables
- ✅ 5 types de rapports professionnels (6000+ mots)
- ✅ Export PDF avec logo Axial Intelligence
- ✅ 3 spécialisations métier (Finance, Tech, Retail)
- ✅ Recherche vectorielle RAG (Qdrant)
- ✅ Prompts ultra-structurés format cabinet conseil
- ✅ Timeouts optimisés (5 min max)

---

**🎉 Application prête pour démo !**

