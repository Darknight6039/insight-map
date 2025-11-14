#!/bin/bash
# Script de démarrage Insight MVP avec Perplexity AI

set -e  # Arrêter en cas d'erreur

echo "🚀 Démarrage de Insight MVP avec Perplexity AI"
echo "================================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les étapes
step() {
    echo -e "${BLUE}==>${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# Vérification des prérequis
step "Vérification des prérequis..."

if ! command -v docker &> /dev/null; then
    error "Docker n'est pas installé. Installez Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi
success "Docker trouvé: $(docker --version)"

if ! command -v docker-compose &> /dev/null; then
    error "docker-compose n'est pas installé"
    exit 1
fi
success "docker-compose trouvé: $(docker-compose --version)"

# Vérification du fichier .env
step "Vérification de la configuration..."

if [ ! -f ".env" ]; then
    error "Fichier .env manquant!"
    echo "   Copiez env.example vers .env et configurez votre clé API Perplexity"
    exit 1
fi

if ! grep -q "PERPLEXITY_API_KEY=pplx-" .env; then
    warning "La clé API Perplexity semble manquante dans .env"
    echo "   Assurez-vous que PERPLEXITY_API_KEY est configurée"
    read -p "   Voulez-vous continuer quand même? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    success "Configuration .env validée"
fi

# Arrêt des conteneurs existants
step "Arrêt des conteneurs existants..."
docker-compose down 2>/dev/null || true
success "Conteneurs arrêtés"

# Nettoyage optionnel
read -p "Voulez-vous nettoyer les volumes (⚠️ supprime les données)? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    step "Nettoyage des volumes..."
    docker-compose down -v
    success "Volumes nettoyés"
fi

# Construction des images
step "Construction des images Docker (cela peut prendre quelques minutes)..."
docker-compose build --no-cache backend-service rag-service

if [ $? -eq 0 ]; then
    success "Images construites avec succès"
else
    error "Échec de la construction des images"
    exit 1
fi

# Démarrage des services
step "Démarrage de tous les services..."
docker-compose up -d

if [ $? -eq 0 ]; then
    success "Services démarrés"
else
    error "Échec du démarrage des services"
    exit 1
fi

# Attente du démarrage complet
echo ""
step "Attente du démarrage complet des services (30 secondes)..."
for i in {30..1}; do
    echo -ne "\r   ⏳ Attente: $i secondes restantes...   "
    sleep 1
done
echo -e "\r   ${GREEN}✓${NC} Services prêts                          "

# Affichage du status
echo ""
step "Status des conteneurs:"
docker-compose ps

echo ""
echo "================================================"
echo -e "${GREEN}✨ Application démarrée avec succès!${NC}"
echo "================================================"
echo ""
echo "📊 Services disponibles:"
echo ""
echo "   🔹 Backend (Perplexity):  http://localhost:8006"
echo "   🔹 RAG Service:           http://localhost:8003"
echo "   🔹 Vector Service:        http://localhost:8002"
echo "   🔹 Document Service:      http://localhost:8001"
echo "   🔹 Report Service:        http://localhost:8004"
echo "   🔹 Gateway API:           http://localhost:8000"
echo ""
echo "🧪 Tests rapides:"
echo ""
echo "   # Health check"
echo "   curl http://localhost:8006/health"
echo ""
echo "   # Test Perplexity"
echo "   curl http://localhost:8006/test-perplexity"
echo ""
echo "   # Diagnostics"
echo "   curl http://localhost:8006/diagnostics"
echo ""
echo "📚 Pour des tests complets:"
echo "   ./test_perplexity_integration.sh"
echo ""
echo "📋 Voir les logs:"
echo "   docker-compose logs -f backend-service"
echo "   docker-compose logs -f rag-service"
echo ""
echo "🛑 Arrêter les services:"
echo "   docker-compose down"
echo ""
echo "================================================"

# Proposer d'exécuter les tests
echo ""
read -p "Voulez-vous exécuter les tests d'intégration maintenant? (Y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    step "Exécution des tests d'intégration..."
    echo ""
    if [ -f "./test_perplexity_integration.sh" ]; then
        chmod +x ./test_perplexity_integration.sh
        ./test_perplexity_integration.sh
    else
        warning "Script de test non trouvé"
    fi
fi

echo ""
echo -e "${GREEN}🎉 Prêt à utiliser!${NC}"
echo ""

