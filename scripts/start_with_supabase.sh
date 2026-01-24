#!/bin/bash
# =============================================================================
# Script de Démarrage Complet avec Supabase
# =============================================================================

set -e

echo "=========================================="
echo "DÉMARRAGE INSIGHT MVP + SUPABASE"
echo "=========================================="

# Vérifier que Docker est lancé
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker n'est pas lancé. Veuillez démarrer Docker Desktop."
    exit 1
fi

# 1. Installer les dépendances Python
echo ""
echo "[1/6] Installation des dépendances Python..."
pip install -q supabase gotrue psycopg2-binary python-jose[cryptography]

# 2. Installer les dépendances frontend
echo ""
echo "[2/6] Installation des dépendances frontend..."
cd frontend-openwebui
npm install --silent
cd ..

# 3. Arrêter les services existants
echo ""
echo "[3/6] Arrêt des services existants..."
docker compose down

# 4. Tirer les nouvelles images
echo ""
echo "[4/6] Téléchargement des images Docker..."
docker compose pull

# 5. Démarrer les services
echo ""
echo "[5/6] Démarrage des services..."
docker compose up -d

# 6. Attendre que les services soient prêts
echo ""
echo "[6/6] Attente du démarrage des services..."
echo "Cela peut prendre 30-60 secondes..."

# Attendre que supabase-db soit prêt
max_wait=60
counter=0
while ! docker compose exec -T supabase-db pg_isready -U postgres > /dev/null 2>&1; do
    if [ $counter -ge $max_wait ]; then
        echo "❌ Timeout: PostgreSQL n'a pas démarré dans les temps"
        exit 1
    fi
    echo -n "."
    sleep 2
    counter=$((counter + 2))
done

echo ""
echo "✅ PostgreSQL est prêt!"

# Attendre que supabase-auth soit prêt
counter=0
while ! curl -s http://localhost:8000/auth/v1/health > /dev/null 2>&1; do
    if [ $counter -ge $max_wait ]; then
        echo "❌ Timeout: Supabase Auth n'a pas démarré dans les temps"
        exit 1
    fi
    echo -n "."
    sleep 2
    counter=$((counter + 2))
done

echo ""
echo "✅ Supabase Auth est prêt!"

# Afficher l'état
echo ""
echo "=========================================="
echo "SERVICES DÉMARRÉS"
echo "=========================================="
docker compose ps

echo ""
echo "=========================================="
echo "PROCHAINES ÉTAPES"
echo "=========================================="
echo ""
echo "1. Migrer les utilisateurs :"
echo "   ./scripts/migrate_users_to_supabase.py"
echo ""
echo "2. Exécuter les scripts SQL (via Supabase Studio) :"
echo "   - http://localhost:3001"
echo "   - Username: supabase"
echo "   - Password: axial2024"
echo ""
echo "3. Tester l'application :"
echo "   - Frontend: http://localhost:3000"
echo "   - API: http://localhost:8080"
echo ""
echo "4. Exécuter les tests :"
echo "   ./scripts/test_migration.sh"
echo ""
echo "=========================================="
