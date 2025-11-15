#!/bin/bash
# Script de mise à jour du backend-service avec stratégie multi-modèles v3.1

set -e  # Arrêter en cas d'erreur

echo "🔄 Mise à jour du backend-service avec stratégie multi-modèles..."
echo ""

# Se placer dans le répertoire du projet
cd /Users/isaiaebongue/insight-mvp

# 1. Rebuild du service backend
echo "📦 Rebuild du backend-service..."
docker compose build backend-service

# 2. Redémarrer le service
echo "🚀 Redémarrage du backend-service..."
docker compose up -d backend-service

# 3. Attendre que le service démarre
echo "⏳ Attente du démarrage du service (10 secondes)..."
sleep 10

# 4. Vérifier le health check
echo ""
echo "✅ Vérification de la santé du service..."
curl -s http://localhost:8006/health | jq '.'

echo ""
echo "🎯 Mise à jour terminée !"
echo ""
echo "Pour vérifier les logs en temps réel :"
echo "  docker compose logs -f backend-service | grep 'Using model'"
echo ""
echo "Pour tester les 3 modèles configurés :"
echo "  curl -s http://localhost:8006/test-perplexity | jq '.'"

