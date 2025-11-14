#!/bin/bash
# Script pour lancer l'application Insight MVP avec Perplexity

echo "🚀 Lancement de Insight MVP avec Perplexity AI"
echo "==============================================="
echo ""

# Aller dans le bon dossier
cd /Users/isaiaebongue/insight-mvp

# Arrêter les conteneurs existants
echo "📍 Étape 1/5: Arrêt des conteneurs existants..."
docker compose down
echo "✅ Conteneurs arrêtés"
echo ""

# Reconstruire les images
echo "🔨 Étape 2/5: Reconstruction des images avec Perplexity..."
echo "(Cela peut prendre 2-3 minutes...)"
docker compose build --no-cache backend-service rag-service
echo "✅ Images reconstruites"
echo ""

# Démarrer tous les services
echo "▶️  Étape 3/5: Démarrage de tous les services..."
docker compose up -d
echo "✅ Services démarrés"
echo ""

# Attendre que tout démarre
echo "⏳ Étape 4/5: Attente du démarrage complet (30 secondes)..."
sleep 30
echo "✅ Services prêts"
echo ""

# Tests
echo "🧪 Étape 5/5: Tests de validation..."
echo ""

echo "Test 1 - Health Check:"
curl -s http://localhost:8006/health | jq '.'
echo ""

echo "Test 2 - Perplexity API:"
curl -s http://localhost:8006/test-perplexity | jq '.'
echo ""

echo "Test 3 - Status des conteneurs:"
docker compose ps
echo ""

echo "==============================================="
echo "✅ Application démarrée avec succès!"
echo "==============================================="
echo ""
echo "📊 Services disponibles:"
echo "   - Backend (Perplexity): http://localhost:8006"
echo "   - RAG Service:          http://localhost:8003"
echo "   - Vector Service:       http://localhost:8002"
echo "   - Document Service:     http://localhost:8001"
echo ""
echo "🧪 Pour tester complètement:"
echo "   ./test_perplexity_integration.sh"
echo ""
echo "📋 Pour voir les logs:"
echo "   docker compose logs -f backend-service"
echo ""
echo "🛑 Pour arrêter:"
echo "   docker compose down"
echo ""

