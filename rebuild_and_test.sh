#!/bin/bash
# Script de rebuild et tests après amélioration prompts

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "🚀 REBUILD ET TESTS - Amélioration Prompts Multi-Sources"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# 1. Rebuild backend-service
echo "📦 1/5 - Rebuild backend-service..."
docker compose build backend-service
echo "✅ Backend-service rebuilt"
echo ""

# 2. Redémarrer le service
echo "🔄 2/5 - Redémarrage backend-service..."
docker compose up -d backend-service
echo "✅ Service redémarré"
echo ""

# 3. Attendre démarrage
echo "⏳ 3/5 - Attente démarrage (10 secondes)..."
sleep 10
echo ""

# 4. Health check
echo "🔍 4/5 - Health check..."
curl -s http://localhost:8006/health | jq '.'
echo ""

# 5. Test Perplexity models
echo "🧪 5/5 - Test des 3 modèles Sonar..."
curl -s http://localhost:8006/test-perplexity | jq '.'
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "✅ REBUILD TERMINÉ - Prêt à générer rapports améliorés"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📋 AMÉLIORATIONS APPLIQUÉES:"
echo "  ✓ Tokens max: sonar 6000, sonar-pro 12000"
echo "  ✓ Sources min: 15-25 (au lieu de 5)"
echo "  ✓ Contexte RAG: 5000 chars, 12 documents"
echo "  ✓ Chat: 5-8 sources (au lieu de 3)"
echo "  ✓ Température: 0.1 (précision max)"
echo "  ✓ Templates: 6000-8000 mots, 30+ chiffres, 3+ tableaux"
echo ""
echo "🧪 POUR TESTER UN RAPPORT:"
echo "  curl -X POST http://localhost:8006/extended-analysis \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{"
echo "      \"business_type\": \"finance_banque\","
echo "      \"analysis_type\": \"analyse_sectorielle\","
echo "      \"query\": \"Analyse du marché bancaire français 2024-2025\""
echo "    }' | jq '.metadata'"
echo ""

