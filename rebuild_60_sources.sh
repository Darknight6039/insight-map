#!/bin/bash

echo "🚀 Rebuild & Redémarrage - 60 Sources + Barre Progression"
echo "=========================================================="
echo ""

# Vérifier Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker non lancé. Démarrez Docker Desktop."
    exit 1
fi

cd /Users/isaiaebongue/insight-mvp

# 1. Rebuild backend
echo "📦 [1/3] Rebuild backend-service (60 sources, logs progression)..."
docker compose build backend-service
if [ $? -ne 0 ]; then
    echo "❌ Erreur build backend"
    exit 1
fi
echo "✅ Backend rebuilt"
echo ""

# 2. Rebuild frontend
echo "📦 [2/3] Rebuild frontend-openwebui (barre progression)..."
docker compose build frontend-openwebui
if [ $? -ne 0 ]; then
    echo "❌ Erreur build frontend"
    exit 1
fi
echo "✅ Frontend rebuilt"
echo ""

# 3. Redémarrer services
echo "🔄 [3/3] Redémarrage services..."
docker compose up -d backend-service frontend-openwebui
echo "✅ Services redémarrés"
echo ""

# Attendre démarrage
echo "⏳ Démarrage en cours (15s)..."
sleep 15
echo ""

# Tests
echo "🧪 Tests de validation"
echo "======================"
echo ""

echo "Test 1: Backend health..."
curl -s http://localhost:8006/health | python3 -m json.tool | grep -E "status|version|perplexity_models" | head -10
echo ""

echo "Test 2: Frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_STATUS" -eq 200 ]; then
    echo "✅ Frontend OK (http://localhost:3000)"
else
    echo "⚠️  Frontend status: $FRONTEND_STATUS"
fi
echo ""

# Résumé
echo "✅ Déploiement terminé!"
echo "======================="
echo ""
echo "🎯 Nouvelles fonctionnalités:"
echo "  • Rapports approfondis 60 sources (8000-10000 mots)"
echo "  • Hiérarchie stricte: 60% instit, 20% acad, 15% média"
echo "  • Barre progression en bas à droite"
echo "  • Logs backend détaillés (5 phases)"
echo "  • Timeout 7.5 min, max_tokens 16000"
echo ""
echo "🧪 Tester rapport approfondi:"
echo "  1. http://localhost:3000"
echo "  2. Onglet 'Analyses'"
echo "  3. Lancer 'Analyse Approfondie'"
echo "  4. Observer barre progression"
echo ""
echo "📋 Voir logs backend:"
echo "  docker compose logs -f backend-service | grep -E '\\[.*\\]'"
echo ""

