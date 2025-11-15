#!/bin/bash

# Script de mise à jour backend avec améliorations prompts v4.0

echo "🚀 Mise à jour Backend Service avec Prompts Améliorés v4.0"
echo ""
echo "📋 Améliorations incluses :"
echo "   ✅ Tokens max augmentés : sonar 6000, sonar-pro 12000"
echo "   ✅ System prompts : 15-25 sources minimum avec croisement"
echo "   ✅ Enhanced prompt : 5 phases de recherche approfondie"
echo "   ✅ Templates métier : métriques quantitatives obligatoires"
echo "   ✅ RAG : 12 documents (au lieu de 8)"
echo "   ✅ Chat : 5-8 sources minimum (au lieu de 3)"
echo "   ✅ Température : 0.1 (plus précis)"
echo ""

# 1. Arrêt du service actuel
echo "⏹️  Arrêt du service backend..."
docker compose stop backend-service

# 2. Rebuild avec nouvelles modifications
echo ""
echo "🔨 Rebuild du service backend..."
docker compose build backend-service

# 3. Redémarrage
echo ""
echo "🔄 Redémarrage du service..."
docker compose up -d backend-service

# 4. Attente démarrage
echo ""
echo "⏳ Attente du démarrage (15 secondes)..."
sleep 15

# 5. Test de santé
echo ""
echo "🏥 Test de santé du service..."
health_response=$(curl -s http://localhost:8006/health)
echo "$health_response" | jq '.'

# 6. Affichage logs récents
echo ""
echo "📋 Logs récents (5 dernières lignes):"
docker compose logs --tail=5 backend-service

echo ""
echo "✅ Mise à jour terminée !"
echo ""
echo "🧪 Tests recommandés :"
echo ""
echo "1. Test multi-modèles :"
echo "   curl http://localhost:8006/test-perplexity | jq '.'"
echo ""
echo "2. Test rapport détaillé (15-25 sources) :"
echo "   curl -X POST http://localhost:8006/extended-analysis \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"business_type\":\"finance_banque\",\"analysis_type\":\"analyse_marche\",\"query\":\"Analyse marché bancaire français 2024\"}' | jq '.'"
echo ""
echo "3. Test chat amélioré (5-8 sources) :"
echo "   curl -X POST http://localhost:8006/chat \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"message\":\"Tendances fintech 2024\",\"business_type\":\"finance_banque\"}' | jq '.'"
echo ""
echo "4. Monitoring logs en temps réel :"
echo "   docker compose logs -f backend-service | grep -E 'Using model|sources'"
echo ""

