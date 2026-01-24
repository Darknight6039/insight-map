#!/bin/bash
# =============================================================================
# Script de génération des clés JWT pour Supabase Self-Hosted
# =============================================================================

set -e

echo "=============================================="
echo "Génération des clés JWT pour Supabase"
echo "=============================================="

# Générer un secret JWT de 64 caractères
JWT_SECRET=$(openssl rand -base64 48 | tr -d '\n' | cut -c1-64)
echo "JWT_SECRET généré: $JWT_SECRET"

# Fonction pour générer un JWT
generate_jwt() {
    local role=$1
    local secret=$2

    # Header
    local header='{"alg":"HS256","typ":"JWT"}'
    local header_base64=$(echo -n "$header" | base64 | tr -d '=' | tr '/+' '_-' | tr -d '\n')

    # Payload avec expiration dans 10 ans
    local exp=$(($(date +%s) + 315360000))
    local payload="{\"role\":\"$role\",\"iss\":\"supabase\",\"iat\":$(date +%s),\"exp\":$exp}"
    local payload_base64=$(echo -n "$payload" | base64 | tr -d '=' | tr '/+' '_-' | tr -d '\n')

    # Signature
    local signature=$(echo -n "${header_base64}.${payload_base64}" | openssl dgst -sha256 -hmac "$secret" -binary | base64 | tr -d '=' | tr '/+' '_-' | tr -d '\n')

    echo "${header_base64}.${payload_base64}.${signature}"
}

# Générer ANON_KEY (role: anon)
ANON_KEY=$(generate_jwt "anon" "$JWT_SECRET")
echo ""
echo "ANON_KEY généré (role: anon)"

# Générer SERVICE_ROLE_KEY (role: service_role)
SERVICE_ROLE_KEY=$(generate_jwt "service_role" "$JWT_SECRET")
echo "SERVICE_ROLE_KEY généré (role: service_role)"

# Générer un mot de passe PostgreSQL sécurisé
POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -d '\n' | cut -c1-32)
echo ""
echo "POSTGRES_PASSWORD généré"

# Créer le fichier .env pour Supabase
ENV_FILE="/Users/isaiaebongue/insight-mvp/supabase/.env"

cat > "$ENV_FILE" << EOF
# =============================================================================
# SUPABASE SELF-HOSTED - CONFIGURATION
# =============================================================================
# Généré automatiquement le $(date)
# NE PAS COMMITER CE FICHIER EN PRODUCTION
# =============================================================================

# =============================================================================
# JWT SECRETS (CRITIQUE - NE PAS PARTAGER)
# =============================================================================
JWT_SECRET=$JWT_SECRET
ANON_KEY=$ANON_KEY
SERVICE_ROLE_KEY=$SERVICE_ROLE_KEY

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_HOST=supabase-db
POSTGRES_PORT=5432
POSTGRES_DB=postgres

# =============================================================================
# API CONFIGURATION
# =============================================================================
# URL externe accessible par les clients
SITE_URL=http://localhost:3000
API_EXTERNAL_URL=http://localhost:8000

# Configuration interne
SUPABASE_PUBLIC_URL=http://localhost:8000
KONG_HTTP_PORT=8000
KONG_HTTPS_PORT=8443

# =============================================================================
# STUDIO (Dashboard) - Optionnel en production
# =============================================================================
STUDIO_DEFAULT_ORGANIZATION=Insight MVP
STUDIO_DEFAULT_PROJECT=insight-mvp
STUDIO_PORT=3001

# =============================================================================
# AUTH CONFIGURATION
# =============================================================================
# Désactiver l'inscription publique (on garde le système d'invitation)
GOTRUE_DISABLE_SIGNUP=false
GOTRUE_SITE_URL=http://localhost:3000
GOTRUE_URI_ALLOW_LIST=http://localhost:3000,http://localhost:3000/**

# Configuration email
GOTRUE_SMTP_HOST=\${SMTP_HOST:-smtp.gmail.com}
GOTRUE_SMTP_PORT=\${SMTP_PORT:-587}
GOTRUE_SMTP_USER=\${SMTP_USER}
GOTRUE_SMTP_PASS=\${SMTP_PASSWORD}
GOTRUE_SMTP_ADMIN_EMAIL=\${SMTP_FROM:-noreply@insight.com}
GOTRUE_SMTP_SENDER_NAME=Insight MVP

# Durée des tokens
GOTRUE_JWT_EXP=3600
GOTRUE_JWT_DEFAULT_GROUP_NAME=authenticated

# =============================================================================
# REALTIME CONFIGURATION
# =============================================================================
REALTIME_IP_ADDR=0.0.0.0
REALTIME_PORT=4000

# =============================================================================
# STORAGE CONFIGURATION
# =============================================================================
STORAGE_BACKEND=file
FILE_SIZE_LIMIT=52428800

# =============================================================================
# POOLER CONFIGURATION (Supavisor)
# =============================================================================
POOLER_ENABLED=true
POOLER_DEFAULT_POOL_SIZE=20
POOLER_MAX_CLIENT_CONN=100

# =============================================================================
# LOGS
# =============================================================================
LOGFLARE_ENABLED=false
EOF

echo ""
echo "=============================================="
echo "Fichier $ENV_FILE créé avec succès!"
echo "=============================================="
echo ""
echo "Résumé des clés générées:"
echo "  - JWT_SECRET: ${JWT_SECRET:0:20}..."
echo "  - ANON_KEY: ${ANON_KEY:0:50}..."
echo "  - SERVICE_ROLE_KEY: ${SERVICE_ROLE_KEY:0:50}..."
echo "  - POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:0:10}..."
echo ""
echo "IMPORTANT: Sauvegardez ces clés dans un endroit sécurisé!"
echo ""

# Afficher les variables à ajouter au .env principal
echo "=============================================="
echo "Variables à ajouter à votre .env principal:"
echo "=============================================="
echo ""
echo "# Supabase Configuration"
echo "SUPABASE_URL=http://localhost:8000"
echo "SUPABASE_ANON_KEY=$ANON_KEY"
echo "SUPABASE_SERVICE_KEY=$SERVICE_ROLE_KEY"
echo "SUPABASE_JWT_SECRET=$JWT_SECRET"
echo ""
echo "# Frontend Supabase"
echo "NEXT_PUBLIC_SUPABASE_URL=http://localhost:8000"
echo "NEXT_PUBLIC_SUPABASE_ANON_KEY=$ANON_KEY"
