# Migration vers Supabase Self-Hosted

Ce document décrit la procédure complète pour migrer Insight MVP vers Supabase self-hosted.

## Table des matières

1. [Prérequis](#prérequis)
2. [Configuration initiale](#configuration-initiale)
3. [Génération des clés JWT](#génération-des-clés-jwt)
4. [Lancement des services](#lancement-des-services)
5. [Migration des utilisateurs](#migration-des-utilisateurs)
6. [Migration des données](#migration-des-données)
7. [Test de la migration](#test-de-la-migration)
8. [Rollback](#rollback)

---

## Prérequis

- Docker et Docker Compose installés
- Python 3.9+ avec pip
- Node.js 18+ avec npm
- Accès à la base de données PostgreSQL existante

### Dépendances Python

```bash
pip install supabase psycopg2-binary python-jose
```

### Dépendances Node.js

```bash
cd frontend-openwebui
npm install @supabase/supabase-js
```

---

## Configuration initiale

### 1. Générer les clés JWT

```bash
chmod +x scripts/generate-jwt-keys.sh
./scripts/generate-jwt-keys.sh
```

Ce script génère :
- `JWT_SECRET` : Secret pour signer les tokens
- `ANON_KEY` : Clé publique pour les clients
- `SERVICE_ROLE_KEY` : Clé admin pour le backend

Les clés sont sauvegardées dans `supabase/.env`.

### 2. Configurer le fichier .env principal

Copiez les variables générées dans votre fichier `.env` :

```bash
# Supabase Configuration
SUPABASE_URL=http://localhost:8000
SUPABASE_ANON_KEY=<votre-anon-key>
SUPABASE_SERVICE_KEY=<votre-service-key>
SUPABASE_JWT_SECRET=<votre-jwt-secret>
SUPABASE_POSTGRES_PASSWORD=<mot-de-passe-généré>

# Frontend Supabase
NEXT_PUBLIC_SUPABASE_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_ANON_KEY=<votre-anon-key>
```

### 3. Structure des fichiers créés

```
insight-mvp/
├── docker-compose.yml          # Mis à jour avec services Supabase
├── supabase/
│   ├── .env                    # Variables Supabase
│   └── volumes/
│       ├── api/kong.yml        # Configuration Kong
│       └── db/realtime.sql     # Init script realtime
├── scripts/
│   ├── generate-jwt-keys.sh    # Générateur de clés
│   ├── migrate_users_to_supabase.py  # Migration utilisateurs
│   └── sql/
│       ├── 01_create_mapping_table.sql
│       ├── 02_migrate_data_to_uuid.sql
│       ├── 03_setup_rls_policies.sql
│       └── 04_enable_realtime.sql
├── gateway-api/app/
│   ├── supabase_client.py      # Client Supabase
│   └── supabase_auth.py        # Module auth Supabase
└── frontend-openwebui/app/
    ├── lib/supabase.ts         # Client Supabase JS
    ├── context/SupabaseAuthContext.tsx
    └── hooks/useRealtime.ts    # Hooks temps réel
```

---

## Lancement des services

### 1. Arrêter les services existants

```bash
docker compose down
```

### 2. Backup de la base de données

```bash
docker compose exec postgres pg_dump -U insight_user insight_db > backup_$(date +%Y%m%d).sql
```

### 3. Lancer les nouveaux services

```bash
# Tirer les nouvelles images
docker compose pull

# Démarrer les services
docker compose up -d

# Vérifier l'état
docker compose ps
```

### Services Supabase disponibles

| Service | Port | Description |
|---------|------|-------------|
| supabase-kong | 8000 | API Gateway principal |
| supabase-auth | 9999 | GoTrue (authentification) |
| supabase-rest | 3000 | PostgREST (API REST) |
| supabase-realtime | 4000 | WebSocket temps réel |
| supabase-studio | 3001 | Dashboard (optionnel) |
| supabase-db | 5432 | PostgreSQL |

### Vérifier que tout fonctionne

```bash
# Test de l'API Gateway
curl http://localhost:8000/auth/v1/health

# Test du dashboard (si activé)
open http://localhost:3001
```

---

## Migration des utilisateurs

### 1. Mode DRY RUN (simulation)

```bash
export OLD_DATABASE_URL="postgresql://insight_user:insight_password_2024@localhost:5432/insight_db"
export SUPABASE_URL="http://localhost:8000"
export SUPABASE_SERVICE_KEY="<votre-service-key>"
export DRY_RUN="true"

python scripts/migrate_users_to_supabase.py
```

Vérifiez le rapport de simulation avant de continuer.

### 2. Migration réelle

```bash
export DRY_RUN="false"
python scripts/migrate_users_to_supabase.py
```

Tapez `MIGRATE` pour confirmer.

### 3. Vérification

```bash
# Vérifier la table de mapping
docker compose exec supabase-db psql -U postgres -c "SELECT * FROM user_id_mapping;"

# Compter les utilisateurs dans Supabase
docker compose exec supabase-db psql -U postgres -c "SELECT COUNT(*) FROM auth.users;"
```

---

## Migration des données

### 1. Créer la table de mapping

```bash
docker compose exec supabase-db psql -U postgres -f /scripts/sql/01_create_mapping_table.sql
```

Ou via le dashboard Supabase Studio (port 3001).

### 2. Migrer les données vers UUID

```bash
docker compose exec supabase-db psql -U postgres -f /scripts/sql/02_migrate_data_to_uuid.sql
```

### 3. Configurer Row Level Security

```bash
docker compose exec supabase-db psql -U postgres -f /scripts/sql/03_setup_rls_policies.sql
```

### 4. Activer le temps réel

```bash
docker compose exec supabase-db psql -U postgres -f /scripts/sql/04_enable_realtime.sql
```

---

## Test de la migration

### 1. Test de connexion

```bash
# Test avec un utilisateur existant
curl -X POST http://localhost:8000/auth/v1/token?grant_type=password \
  -H "apikey: <ANON_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@axial.com",
    "password": "admin123"
  }'
```

### 2. Test via l'application

1. Accédez à http://localhost:3000
2. Connectez-vous avec un compte existant
3. Vérifiez que les historiques sont accessibles

### 3. Test du temps réel

```javascript
// Dans la console du navigateur
const { data, error } = await supabase
  .channel('test')
  .on('postgres_changes', { event: '*', schema: 'public', table: 'user_conversations' }, console.log)
  .subscribe()
```

### 4. Script de test automatisé

```bash
chmod +x scripts/test_migration.sh
./scripts/test_migration.sh
```

---

## Rollback

En cas de problème, vous pouvez revenir à l'ancienne configuration :

### 1. Restaurer l'ancien docker-compose

```bash
git checkout HEAD -- docker-compose.yml
```

### 2. Restaurer le provider frontend

```bash
# Modifier providers.tsx pour utiliser AuthProvider au lieu de SupabaseAuthProvider
```

### 3. Restaurer la base de données

```bash
docker compose up -d postgres
docker compose exec postgres psql -U insight_user insight_db < backup_YYYYMMDD.sql
```

### 4. Redémarrer les services

```bash
docker compose down
docker compose up -d
```

---

## Résolution des problèmes

### Erreur "JWT expired"

```bash
# Vérifier que JWT_SECRET est le même partout
echo $SUPABASE_JWT_SECRET
```

### Erreur "User not found"

```bash
# Vérifier le mapping
docker compose exec supabase-db psql -U postgres -c \
  "SELECT * FROM user_id_mapping WHERE email = 'user@example.com';"
```

### Realtime ne fonctionne pas

```bash
# Vérifier les publications
docker compose exec supabase-db psql -U postgres -c \
  "SELECT * FROM pg_publication_tables WHERE pubname = 'supabase_realtime';"
```

### Logs des services

```bash
# Logs Supabase Auth
docker compose logs -f supabase-auth

# Logs Realtime
docker compose logs -f supabase-realtime

# Logs Kong
docker compose logs -f supabase-kong
```

---

## Architecture finale

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js :3000)                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  SupabaseAuthProvider + useRealtime hooks               │   │
│  │  @supabase/supabase-js                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                Supabase Kong Gateway (:8000)                    │
│  ┌────────┬────────┬────────┬────────┬────────────────────┐     │
│  │/auth/* │/rest/* │/realtime│/storage│   API Routing     │     │
│  └────────┴────────┴────────┴────────┴────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
         ↓           ↓          ↓           ↓
┌────────────┬────────────┬────────────┬────────────┐
│ GoTrue     │ PostgREST  │ Realtime   │ Storage    │
│ (Auth)     │ (REST API) │ (WebSocket)│ (Files)    │
│ :9999      │ :3000      │ :4000      │ :5000      │
└────────────┴────────────┴────────────┴────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              Supabase PostgreSQL (:5432)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ auth.users (utilisateurs Supabase)                       │   │
│  │ public.user_conversations (avec RLS + realtime)          │   │
│  │ public.user_documents (avec RLS + realtime)              │   │
│  │ public.activity_logs (avec RLS + realtime)               │   │
│  │ public.user_id_mapping (correspondance IDs)              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Checklist de migration

- [ ] Générer les clés JWT
- [ ] Configurer le fichier .env
- [ ] Backup de la base existante
- [ ] Lancer les services Supabase
- [ ] Vérifier la santé des services
- [ ] Migration utilisateurs (DRY RUN)
- [ ] Migration utilisateurs (PRODUCTION)
- [ ] Vérifier la table de mapping
- [ ] Migrer les données vers UUID
- [ ] Configurer RLS
- [ ] Activer le temps réel
- [ ] Tester la connexion
- [ ] Tester les fonctionnalités temps réel
- [ ] Mettre à jour la documentation équipe

---

## Support

En cas de problème :
1. Consulter les logs : `docker compose logs -f`
2. Vérifier la documentation Supabase : https://supabase.com/docs/guides/self-hosting
3. Ouvrir une issue sur le dépôt du projet
