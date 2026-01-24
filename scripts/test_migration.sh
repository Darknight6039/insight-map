#!/bin/bash
# =============================================================================
# Script de Test de la Migration Supabase
# =============================================================================

set -e

echo "=========================================="
echo "TEST DE LA MIGRATION SUPABASE"
echo "=========================================="

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
ANON_KEY="${SUPABASE_ANON_KEY}"
SERVICE_KEY="${SUPABASE_SERVICE_KEY}"
API_URL="${API_EXTERNAL_URL:-http://localhost:8000}"

# =============================================================================
# Fonction de test
# =============================================================================
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_code="$3"

    echo -n "Testing $name... "

    response_code=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [ "$response_code" -eq "$expected_code" ]; then
        echo -e "${GREEN}✓ OK${NC} (HTTP $response_code)"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $response_code, expected $expected_code)"
        return 1
    fi
}

# =============================================================================
# 1. Test des services Docker
# =============================================================================
echo ""
echo "----------------------------------------"
echo "[1/5] Vérification des services Docker"
echo "----------------------------------------"

services=(
    "supabase-db"
    "supabase-auth"
    "supabase-kong"
    "supabase-realtime"
    "gateway-api"
    "frontend-openwebui"
)

for service in "${services[@]}"; do
    if docker compose ps | grep -q "$service.*running"; then
        echo -e "${GREEN}✓${NC} $service est en cours d'exécution"
    else
        echo -e "${RED}✗${NC} $service n'est PAS en cours d'exécution"
    fi
done

# =============================================================================
# 2. Test de l'API Supabase
# =============================================================================
echo ""
echo "----------------------------------------"
echo "[2/5] Test de l'API Supabase"
echo "----------------------------------------"

# Test Kong Gateway
test_endpoint "Kong Gateway" "$API_URL" "404"

# Test Auth Health (ne doit pas être accessible directement)
# Auth est accessible via Kong sur /auth/v1/*

# =============================================================================
# 3. Test de connexion avec utilisateur existant
# =============================================================================
echo ""
echo "----------------------------------------"
echo "[3/5] Test de connexion utilisateur"
echo "----------------------------------------"

# Vérifier qu'il y a des utilisateurs dans la base
echo -n "Vérification des utilisateurs migrés... "
user_count=$(docker compose exec -T supabase-db psql -U postgres -t -c "SELECT COUNT(*) FROM auth.users;" 2>/dev/null | tr -d ' ')

if [ "$user_count" -gt 0 ]; then
    echo -e "${GREEN}✓ $user_count utilisateurs trouvés${NC}"
else
    echo -e "${YELLOW}⚠ Aucun utilisateur trouvé (migration non effectuée)${NC}"
fi

# Test de connexion (nécessite un utilisateur existant)
echo ""
echo "Pour tester la connexion, utilisez :"
echo "  curl -X POST '$API_URL/auth/v1/token?grant_type=password' \\"
echo "    -H 'apikey: $ANON_KEY' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"email\":\"admin@axial.com\",\"password\":\"admin123\"}'"

# =============================================================================
# 4. Test de la table de mapping
# =============================================================================
echo ""
echo "----------------------------------------"
echo "[4/5] Vérification de la table de mapping"
echo "----------------------------------------"

echo -n "Vérification de user_id_mapping... "
mapping_count=$(docker compose exec -T supabase-db psql -U postgres -t -c "SELECT COUNT(*) FROM public.user_id_mapping;" 2>/dev/null | tr -d ' ')

if [ "$mapping_count" -gt 0 ]; then
    echo -e "${GREEN}✓ $mapping_count mappings trouvés${NC}"
else
    echo -e "${YELLOW}⚠ Table de mapping vide (migration non effectuée)${NC}"
fi

# =============================================================================
# 5. Test des publications realtime
# =============================================================================
echo ""
echo "----------------------------------------"
echo "[5/5] Vérification du realtime"
echo "----------------------------------------"

echo -n "Vérification des publications... "
pub_tables=$(docker compose exec -T supabase-db psql -U postgres -t -c "SELECT COUNT(*) FROM pg_publication_tables WHERE pubname = 'supabase_realtime';" 2>/dev/null | tr -d ' ')

if [ "$pub_tables" -gt 0 ]; then
    echo -e "${GREEN}✓ $pub_tables tables dans la publication${NC}"
    docker compose exec -T supabase-db psql -U postgres -c "SELECT schemaname, tablename FROM pg_publication_tables WHERE pubname = 'supabase_realtime';" 2>/dev/null | grep -E "user_conversations|user_documents|activity_logs"
else
    echo -e "${YELLOW}⚠ Aucune table dans la publication (scripts SQL non exécutés)${NC}"
fi

# =============================================================================
# Résumé
# =============================================================================
echo ""
echo "=========================================="
echo "RÉSUMÉ"
echo "=========================================="
echo ""
echo "Services Docker:        $(docker compose ps | grep -c "running" || echo 0) services actifs"
echo "Utilisateurs migrés:    $user_count"
echo "Mappings créés:         $mapping_count"
echo "Tables realtime:        $pub_tables"
echo ""
echo "Pour accéder au dashboard Supabase Studio:"
echo "  http://localhost:3001"
echo "  Username: supabase"
echo "  Password: axial2024"
echo ""
echo "Pour accéder à l'application:"
echo "  http://localhost:3000"
echo ""
echo "=========================================="
