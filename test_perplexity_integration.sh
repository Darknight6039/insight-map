#!/bin/bash
# Script de test pour l'intégration Perplexity AI

echo "🧪 Test de l'intégration Perplexity AI"
echo "======================================="
echo ""

# Couleurs pour les outputs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour tester un endpoint
test_endpoint() {
    local url=$1
    local description=$2
    
    echo -e "${YELLOW}Testing:${NC} $description"
    echo "URL: $url"
    
    response=$(curl -s -w "\n%{http_code}" "$url" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ SUCCESS${NC} (HTTP $http_code)"
        echo "Response: $body" | jq '.' 2>/dev/null || echo "$body"
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $http_code)"
        echo "Response: $body"
    fi
    echo ""
}

# Fonction pour tester un POST endpoint
test_post_endpoint() {
    local url=$1
    local data=$2
    local description=$3
    
    echo -e "${YELLOW}Testing:${NC} $description"
    echo "URL: $url"
    echo "Data: $data"
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
        -H "Content-Type: application/json" \
        -d "$data" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ SUCCESS${NC} (HTTP $http_code)"
        echo "Response preview:" 
        echo "$body" | jq '.metadata // .response[0:200] // .' 2>/dev/null || echo "${body:0:200}..."
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $http_code)"
        echo "Response: $body"
    fi
    echo ""
}

echo "📌 STEP 1: Test Backend Service Health"
echo "---------------------------------------"
test_endpoint "http://localhost:8006/health" "Backend Service Health Check"

echo "📌 STEP 2: Test RAG Service Health"
echo "-----------------------------------"
test_endpoint "http://localhost:8003/health" "RAG Service Health Check"

echo "📌 STEP 3: Test Perplexity Connection"
echo "--------------------------------------"
test_endpoint "http://localhost:8006/test-perplexity" "Direct Perplexity API Test"

echo "📌 STEP 4: Test Diagnostics"
echo "---------------------------"
test_endpoint "http://localhost:8006/diagnostics" "Full System Diagnostics"

echo "📌 STEP 5: Test Vector Service"
echo "-------------------------------"
test_endpoint "http://localhost:8002/health" "Vector Service Health"

echo "📌 STEP 6: Test Simple Chat (with RAG)"
echo "---------------------------------------"
test_post_endpoint "http://localhost:8006/chat" \
    '{"message": "Quelles sont les principales tendances en finance?", "business_type": "finance_banque"}' \
    "Chat with RAG Integration"

echo "📌 STEP 7: Test RAG Service - Synthèse Executive"
echo "------------------------------------------------"
test_post_endpoint "http://localhost:8003/synthesize" \
    '{"query": "Analyse du marché bancaire", "title": "Test Synthèse", "top_k": 5}' \
    "Executive Synthesis with Perplexity"

echo "📌 STEP 8: Test Extended Analysis"
echo "----------------------------------"
test_post_endpoint "http://localhost:8006/extended-analysis" \
    '{"business_type": "finance_banque", "analysis_type": "market_analysis", "query": "Tendances fintech 2024"}' \
    "Extended Analysis Report"

echo ""
echo "======================================="
echo "🎉 Tests terminés!"
echo "======================================="
echo ""
echo "📊 Résumé:"
echo "- Vérifiez que tous les tests sont ${GREEN}✓ SUCCESS${NC}"
echo "- Si des tests échouent, vérifiez:"
echo "  1. Les services Docker sont démarrés: docker-compose ps"
echo "  2. La clé API Perplexity est configurée dans .env"
echo "  3. Les logs des services: docker-compose logs backend-service"
echo ""
echo "📚 Documentation complète: voir PERPLEXITY_MIGRATION.md"

