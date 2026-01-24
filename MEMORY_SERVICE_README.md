# 🧠 Memory Service - Guide Complet

## 📋 Vue d'Ensemble

Le Memory Service est un nouveau microservice qui permet aux utilisateurs de:
- **Consulter l'historique** de toutes leurs conversations
- **Gérer leur bibliothèque** de rapports et veilles
- **Rechercher et filtrer** leurs contenus
- **Migrer** les anciennes données du système legacy

## 🎯 Fonctionnalités

### Backend (Memory Service - Port 8008)

✅ **API REST complète**
- CRUD conversations (Create, Read, Delete)
- CRUD documents (Create, Read, Delete)
- Migration des données legacy
- Authentication JWT
- Filtrage et pagination

✅ **Base de données PostgreSQL**
- 3 nouvelles tables:
  - `user_conversations` - Historique des conversations
  - `user_documents` - Bibliothèque de documents
  - `migration_status` - Suivi de migration

✅ **Intégrations**
- backend-service (sauvegarde conversations)
- report-service (sauvegarde rapports)
- scheduler-service (sauvegarde veilles)
- gateway-api (endpoints proxy)

### Frontend (Pages React - Port 3000)

✅ **Page Historique (/history)**
- Liste toutes les conversations
- Recherche en temps réel
- Filtres par type (chat/analyse)
- Expansion/réduction des contenus
- Suppression avec confirmation

✅ **Page Bibliothèque (/library)**
- Liste tous les documents (rapports + veilles)
- Statistiques (total, rapports, veilles)
- Recherche dans titres et contenus
- Filtres multiples (type, analyse, secteur)
- Téléchargement PDF
- Suppression avec confirmation
- Organisation par date

✅ **Navigation**
- Nouveaux liens dans la navbar
- Icônes visuelles
- État actif/inactif

## 🚀 Déploiement Rapide

### Option 1: Déploiement Automatique (Recommandé)

```bash
# 1. Démarrer Docker Desktop
# 2. Lancer le script de déploiement complet
./deploy-complete-memory-integration.sh
```

Ce script va:
1. ✓ Vérifier Docker
2. ✓ Démarrer PostgreSQL
3. ✓ Créer les tables
4. ✓ Build memory-service
5. ✓ Démarrer memory-service
6. ✓ Build frontend
7. ✓ Démarrer frontend
8. ✓ Vérifier la santé des services

### Option 2: Déploiement Manuel

#### Backend Only

```bash
./deploy-memory-service.sh
```

#### Frontend Only

```bash
cd frontend-openwebui
npm run dev
# OU
docker-compose build frontend-openwebui
docker-compose up -d frontend-openwebui
```

## 🧪 Tests

### Test Automatique

```bash
# Tester tous les endpoints du memory service
./test-memory-service.sh
```

### Test Manuel - Backend

```bash
# 1. Récupérer un token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@axial.com","password":"admin123"}' \
  | jq -r '.access_token')

# 2. Lister les conversations
curl http://localhost:8000/api/memory/conversations \
  -H "Authorization: Bearer $TOKEN" | jq .

# 3. Lister les documents
curl http://localhost:8000/api/memory/documents \
  -H "Authorization: Bearer $TOKEN" | jq .

# 4. Vérifier la migration
curl http://localhost:8000/api/memory/migrate/status \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### Test Manuel - Frontend

1. **Ouvrir l'application**
   ```
   http://localhost:3000
   ```

2. **Se connecter**
   - Email: admin@axial.com
   - Password: admin123

3. **Tester la page Historique**
   - Cliquer sur "Historique" dans la navbar
   - Vérifier que les conversations s'affichent
   - Tester la recherche
   - Tester les filtres
   - Tester "Voir plus/moins"
   - Tester la suppression

4. **Tester la page Bibliothèque**
   - Cliquer sur "Bibliothèque" dans la navbar
   - Vérifier les statistiques en haut
   - Tester la recherche
   - Tester les filtres par type
   - Tester le téléchargement PDF
   - Tester la suppression

## 📊 Architecture

```
┌─────────────────────────────────────────────┐
│           Frontend (React/Next.js)          │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ /history │  │ /library │  │  Navbar  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼─────────────┼─────────────┼─────────┘
        │             │             │
        └─────────────┴─────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │   Gateway API (8000)    │
        │  /api/memory/*          │
        └──────────┬──────────────┘
                   │
        ┌──────────┴──────────────────────┐
        │                                 │
        ▼                                 ▼
┌─────────────────┐            ┌──────────────────┐
│ Memory Service  │            │  Other Services  │
│    (8008)       │            │                  │
│                 │            │ • Backend (8006) │
│ • Conversations │◄───────────┤ • Report (8004)  │
│ • Documents     │            │ • Scheduler(8007)│
│ • Migration     │            │                  │
└────────┬────────┘            └──────────────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│   insight_db    │
│                 │
│ • conversations │
│ • documents     │
│ • migration     │
└─────────────────┘
```

## 📁 Structure des Fichiers

```
insight-mvp/
├── memory-service/                     # Nouveau service
│   ├── app/
│   │   ├── main.py                    # API FastAPI
│   │   ├── models.py                  # Modèles DB
│   │   ├── schemas.py                 # Validation
│   │   ├── database.py                # Config DB
│   │   └── migration.py               # Migration legacy
│   ├── migrations/
│   │   └── 001_create_memory_tables.sql
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend-openwebui/                 # Frontend mis à jour
│   └── app/
│       ├── history/                   # Nouvelle page
│       │   └── page.tsx
│       ├── library/                   # Nouvelle page
│       │   └── page.tsx
│       └── components/
│           └── Navbar.tsx             # Modifié
│
├── gateway-api/app/main.py            # Modifié (proxy endpoints)
├── backend-service/app/main.py        # Modifié (save conversations)
├── report-service/app/main.py         # Modifié (save reports)
├── scheduler-service/app/scheduler.py # Modifié (save watches)
├── docker-compose.yml                 # Modifié (memory-service)
├── .env                               # Modifié (MEMORY_SERVICE_URL)
│
├── deploy-memory-service.sh           # Script backend
├── deploy-complete-memory-integration.sh # Script complet ⭐
├── test-memory-service.sh             # Script de test
├── MEMORY_SERVICE_DEPLOYMENT.md       # Doc backend
├── FRONTEND_MEMORY_INTEGRATION.md     # Doc frontend
└── MEMORY_SERVICE_README.md           # Ce fichier
```

## 🔌 Endpoints API

### Via Gateway (Authentifié)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/memory/conversations` | Liste conversations |
| GET | `/api/memory/conversations/{id}` | Détail conversation |
| DELETE | `/api/memory/conversations/{id}` | Supprimer conversation |
| GET | `/api/memory/documents` | Liste documents |
| GET | `/api/memory/documents/{id}` | Détail document |
| DELETE | `/api/memory/documents/{id}` | Supprimer document |
| GET | `/api/memory/migrate/status` | Statut migration |
| POST | `/api/memory/migrate` | Lancer migration |

### Query Parameters

**Conversations:**
```
?skip=0&limit=20&conversation_type=chat&analysis_type=synthese_executive&search=market
```

**Documents:**
```
?skip=0&limit=20&type=report&analysis_type=synthese_executive&business_type=finance&search=technology
```

## 🗄️ Base de Données

### Tables Créées

1. **user_conversations** (Conversations)
   - Stocke toutes les interactions utilisateur
   - Champs: id, user_id, query, response, type, analysis_type, business_type, created_at

2. **user_documents** (Documents)
   - Stocke les rapports et veilles
   - Champs: id, user_id, document_type, title, content, file_path, analysis_type, business_type, report_id, watch_id, extra_data, created_at

3. **migration_status** (Migration)
   - Suivi de migration legacy
   - Champs: user_id, conversations_migrated, migration_date, legacy_conversation_count

### Vérifier les Tables

```bash
docker exec -i insight-mvp-postgres-1 psql -U insight_user -d insight_db -c "
SELECT
  table_name,
  (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columns
FROM information_schema.tables t
WHERE table_schema = 'public'
  AND (table_name LIKE 'user_%' OR table_name = 'migration_status')
ORDER BY table_name;
"
```

## 🔒 Sécurité

### Authentication

- **JWT Tokens** pour toutes les requêtes
- **User Isolation** - Chaque user ne voit que ses données
- **Expiration** - Tokens expirés après 24h

### Autorisations

```python
# Filtrage automatique par user_id
query = db.query(UserConversation).filter(
    UserConversation.user_id == current_user.id
)
```

## 📈 Performance

### Métriques Attendues

| Opération | Temps Attendu |
|-----------|--------------|
| Liste conversations (100) | < 2s |
| Liste documents (100) | < 2s |
| Recherche (client-side) | < 100ms |
| Suppression | < 500ms |
| Téléchargement PDF | 2-5s |

### Limites Actuelles

- **Pagination:** Limite de 100 items par requête
- **Cache:** Pas de cache (rechargement à chaque visite)
- **Real-time:** Pas de mise à jour automatique

### Optimisations Futures

1. Pagination côté serveur avec infinite scroll
2. Cache avec React Query ou SWR
3. Virtual scrolling pour grandes listes
4. WebSocket pour real-time updates

## 🐛 Dépannage

### Problème: Services ne démarrent pas

```bash
# Vérifier Docker
docker info

# Vérifier les services
docker-compose ps

# Relancer tout
docker-compose down
docker-compose up -d
```

### Problème: "Cannot connect to database"

```bash
# Vérifier PostgreSQL
docker-compose ps postgres

# Voir les logs
docker-compose logs postgres

# Redémarrer
docker-compose restart postgres
```

### Problème: "Authentication failed"

```bash
# Vérifier JWT_SECRET_KEY est le même partout
grep JWT_SECRET_KEY .env

# Obtenir un nouveau token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@axial.com","password":"admin123"}'
```

### Problème: Frontend ne charge pas

```bash
# Vérifier les logs
docker-compose logs frontend-openwebui

# Rebuild
docker-compose build frontend-openwebui
docker-compose up -d frontend-openwebui

# En dev mode
cd frontend-openwebui
npm install
npm run dev
```

### Problème: "No data" mais base a des données

```bash
# Compter les entrées
docker exec -i insight-mvp-postgres-1 psql -U insight_user -d insight_db -c "
SELECT
  'Conversations' as type, COUNT(*) as count FROM user_conversations
UNION ALL
SELECT
  'Documents', COUNT(*) FROM user_documents;
"

# Vérifier l'isolation des users
docker exec -i insight-mvp-postgres-1 psql -U insight_user -d insight_db -c "
SELECT user_id, COUNT(*)
FROM user_conversations
GROUP BY user_id;
"
```

## 📚 Documentation

### Documents Disponibles

1. **MEMORY_SERVICE_DEPLOYMENT.md** - Guide backend complet
2. **FRONTEND_MEMORY_INTEGRATION.md** - Guide frontend complet
3. **MEMORY_SERVICE_README.md** - Ce fichier (vue d'ensemble)

### API Documentation

Une fois déployé:
- Swagger UI: http://localhost:8008/docs
- ReDoc: http://localhost:8008/redoc

## ✅ Checklist de Validation

Avant de considérer l'intégration terminée:

**Backend:**
- [ ] Memory-service déployé (port 8008)
- [ ] 3 tables créées dans PostgreSQL
- [ ] Health check répond: `curl http://localhost:8008/health`
- [ ] Endpoints accessibles avec auth
- [ ] Gateway proxy fonctionne

**Frontend:**
- [ ] Build sans erreurs
- [ ] Page /history accessible
- [ ] Page /library accessible
- [ ] Navbar mise à jour avec nouveaux liens
- [ ] Recherche fonctionne
- [ ] Filtres fonctionnent
- [ ] Suppression fonctionne
- [ ] Téléchargement PDF fonctionne

**Intégration:**
- [ ] Nouvelles conversations sauvegardées
- [ ] Nouveaux rapports sauvegardés
- [ ] Veilles sauvegardées
- [ ] User isolation validée
- [ ] Pas d'erreurs console
- [ ] Tests automatiques passent

## 🎯 Prochaines Étapes

### Court Terme

1. **Migration des données existantes**
   ```bash
   # Déclencher migration pour un user
   curl -X POST http://localhost:8000/api/memory/migrate \
     -H "Authorization: Bearer $TOKEN"
   ```

2. **Tests avec utilisateurs réels**
   - Créer plusieurs users
   - Tester l'isolation des données
   - Vérifier les performances

3. **Monitoring**
   - Surveiller les logs
   - Vérifier les temps de réponse
   - Analyser l'utilisation

### Moyen Terme

1. **Optimisations**
   - Implémenter pagination serveur
   - Ajouter cache (Redis ou React Query)
   - Virtual scrolling

2. **Fonctionnalités**
   - Export CSV/JSON
   - Tags personnalisés
   - Favoris/épinglés
   - Partage de documents

3. **Service-to-Service Auth**
   - Tokens internes pour report-service
   - Tokens internes pour scheduler-service

### Long Terme

1. **Analytics**
   - Métriques d'utilisation
   - Rapports les plus consultés
   - Tendances de recherche

2. **Améliorations UX**
   - Real-time updates (WebSocket)
   - Notifications
   - Suggestions de recherche

3. **Scalabilité**
   - Clustering PostgreSQL
   - Load balancing
   - CDN pour assets

## 📞 Support

### Logs à Consulter

```bash
# Memory Service
docker-compose logs -f memory-service

# Frontend
docker-compose logs -f frontend-openwebui

# Gateway
docker-compose logs -f gateway-api

# Tous ensemble
docker-compose logs -f memory-service frontend-openwebui gateway-api
```

### Tests Rapides

```bash
# Health checks
curl http://localhost:8008/health
curl http://localhost:8000/health
curl http://localhost:3000

# Test complet
./test-memory-service.sh
```

### Debug Base de Données

```bash
# Se connecter à PostgreSQL
docker exec -it insight-mvp-postgres-1 psql -U insight_user -d insight_db

# Requêtes utiles
\dt                                    # Liste tables
SELECT COUNT(*) FROM user_conversations;
SELECT COUNT(*) FROM user_documents;
SELECT * FROM user_conversations LIMIT 5;
```

---

## 🎉 Conclusion

Le Memory Service est maintenant intégré au système Insight MVP, offrant:

✅ **Persistance** - Toutes les conversations et documents sont sauvegardés
✅ **Historique** - Interface claire pour consulter le passé
✅ **Recherche** - Retrouver facilement l'information
✅ **Organisation** - Filtres et tri par date/type
✅ **User Experience** - Design moderne et intuitif

**Pour démarrer immédiatement:**

```bash
./deploy-complete-memory-integration.sh
```

Puis ouvrez http://localhost:3000 et explorez les nouvelles fonctionnalités!

---

**Version:** 1.0.0
**Date:** 2026-01-18
**Auteur:** Claude Code (Anthropic)
