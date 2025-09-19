#!/bin/bash

# Test All Services Script
# Tests health and basic functionality of all microservices

set -e

echo "🧪 Testing All Microservices..."
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Service URLs
GATEWAY_URL="http://localhost:8000"
DOCUMENT_URL="http://localhost:8001"
VECTOR_URL="http://localhost:8002"
RAG_URL="http://localhost:8003"
REPORT_URL="http://localhost:8004"
STATUS_URL="http://localhost:8005"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
test_endpoint() {
    local url=$1
    local expected_status=${2:-200}
    local description=$3
    
    echo -n "Testing: $description... "
    
    if response=$(curl -s -w "%{http_code}" "$url" -o /tmp/test_response 2>/dev/null); then
        status_code="${response: -3}"
        if [ "$status_code" = "$expected_status" ]; then
            echo -e "${GREEN}✓ PASS${NC} (HTTP $status_code)"
            ((TESTS_PASSED++))
            return 0
        else
            echo -e "${RED}✗ FAIL${NC} (Expected $expected_status, got $status_code)"
            ((TESTS_FAILED++))
            return 1
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (Connection failed)"
        ((TESTS_FAILED++))
        return 1
    fi
}

test_post_endpoint() {
    local url=$1
    local data=$2
    local expected_status=${3:-200}
    local description=$4
    
    echo -n "Testing: $description... "
    
    if response=$(curl -s -w "%{http_code}" -X POST "$url" \
        -H "Content-Type: application/json" \
        -d "$data" \
        -o /tmp/test_response 2>/dev/null); then
        status_code="${response: -3}"
        if [ "$status_code" = "$expected_status" ]; then
            echo -e "${GREEN}✓ PASS${NC} (HTTP $status_code)"
            ((TESTS_PASSED++))
            return 0
        else
            echo -e "${RED}✗ FAIL${NC} (Expected $expected_status, got $status_code)"
            echo "Response: $(cat /tmp/test_response)"
            ((TESTS_FAILED++))
            return 1
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (Connection failed)"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo -e "\n${YELLOW}🔧 Testing Gateway API (Port 8000)${NC}"
echo "-----------------------------------"
test_endpoint "$GATEWAY_URL/health" 200 "Gateway health check"
test_endpoint "$GATEWAY_URL/health/services" 200 "All services health check"
test_endpoint "$GATEWAY_URL/analysis/types" 200 "Available analysis types"
test_endpoint "$GATEWAY_URL/docs" 200 "Swagger documentation"

echo -e "\n${YELLOW}📄 Testing Document Service (Port 8001)${NC}"
echo "----------------------------------------"
test_endpoint "$DOCUMENT_URL/health" 200 "Document service health"
test_endpoint "$DOCUMENT_URL/documents" 200 "List documents"
test_endpoint "$DOCUMENT_URL/stats" 200 "Document statistics"

echo -e "\n${YELLOW}🔍 Testing Vector Service (Port 8002)${NC}"
echo "--------------------------------------"
test_endpoint "$VECTOR_URL/health" 200 "Vector service health"
test_endpoint "$VECTOR_URL/collections" 200 "Vector collections"

echo -e "\n${YELLOW}🤖 Testing RAG Service (Port 8003)${NC}"
echo "----------------------------------"
test_endpoint "$RAG_URL/health" 200 "RAG service health"
test_endpoint "$RAG_URL/analysis_types" 200 "RAG analysis types"

# Test each of the 5 analysis endpoints
echo -e "\n${YELLOW}📊 Testing Analysis Endpoints${NC}"
echo "-------------------------------"

analysis_payload='{"query": "Test strategic analysis", "title": "Test Analysis"}'

test_post_endpoint "$RAG_URL/synthesize" "$analysis_payload" 200 "Synthèse Exécutive analysis"
test_post_endpoint "$RAG_URL/analyze_competition" "$analysis_payload" 200 "Analyse Concurrentielle"
test_post_endpoint "$RAG_URL/tech_watch" "$analysis_payload" 200 "Veille Technologique"
test_post_endpoint "$RAG_URL/risk_analysis" "$analysis_payload" 200 "Analyse de Risques"
test_post_endpoint "$RAG_URL/market_study" "$analysis_payload" 200 "Étude de Marché"

echo -e "\n${YELLOW}📑 Testing Report Service (Port 8004)${NC}"
echo "-------------------------------------"
test_endpoint "$REPORT_URL/health" 200 "Report service health"
test_endpoint "$REPORT_URL/reports" 200 "List reports"
test_endpoint "$REPORT_URL/stats" 200 "Report statistics"

echo -e "\n${YELLOW}⚡ Testing Status Service (Port 8005)${NC}"
echo "------------------------------------"
test_endpoint "$STATUS_URL/health" 200 "Status service health"
test_endpoint "$STATUS_URL/status" 200 "System status"

echo -e "\n${YELLOW}🔄 Testing Gateway Integration${NC}"
echo "-------------------------------"

# Test search functionality
search_payload='{"query": "test search", "top_k": 3}'
test_post_endpoint "$GATEWAY_URL/search" "$search_payload" 200 "Gateway search"

# Test analysis through gateway
test_post_endpoint "$GATEWAY_URL/analysis/synthesize" "$analysis_payload" 200 "Gateway analysis - Synthesize"
test_post_endpoint "$GATEWAY_URL/analysis/competition" "$analysis_payload" 200 "Gateway analysis - Competition"

echo -e "\n${YELLOW}🧪 Testing Vector Search${NC}"
echo "-------------------------"
if [ "$TESTS_FAILED" -eq 0 ]; then
    # Only test vector operations if services are healthy
    vector_payload='{"doc_id": 999, "segments": ["Test segment for vector search"]}'
    test_post_endpoint "$VECTOR_URL/index" "$vector_payload" 200 "Vector indexing"
    
    search_vector_payload='{"query": "test vector search", "top_k": 1}'
    test_post_endpoint "$VECTOR_URL/search" "$search_vector_payload" 200 "Vector search"
fi

echo -e "\n${YELLOW}📋 Testing Report Generation${NC}"
echo "-----------------------------"
if [ "$TESTS_FAILED" -eq 0 ]; then
    report_payload='{"title": "Test Report", "content": "**TEST SECTION**\nThis is test content for report generation.", "analysis_type": "synthese_executive"}'
    test_post_endpoint "$REPORT_URL/generate" "$report_payload" 200 "Report generation"
fi

# Final results
echo -e "\n🎯 TEST RESULTS"
echo "================"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo -e "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED! System is healthy.${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Check service logs for details.${NC}"
    echo -e "\n${YELLOW}💡 Troubleshooting tips:${NC}"
    echo "1. Ensure all services are running: docker-compose ps"
    echo "2. Check service logs: docker-compose logs [service-name]"
    echo "3. Verify environment variables in .env file"
    echo "4. Make sure OpenAI API key is configured if using AI features"
    exit 1
fi

# Clean up
rm -f /tmp/test_response
