#!/bin/bash

# Example API Calls Script
# Demonstrates all the key endpoints of the Insight MVP

echo "🚀 Insight MVP - Example API Calls"
echo "=================================="

BASE_URL="http://localhost:8000"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo_section() {
    echo -e "\n${YELLOW}$1${NC}"
    echo "$(printf '=%.0s' $(seq 1 ${#1}))"
}

echo_example() {
    echo -e "\n${BLUE}📝 $1${NC}"
    echo "Command:"
    echo "  $2"
    echo ""
    echo "Response:"
}

# Health Checks
echo_section "🏥 HEALTH CHECKS"

echo_example "Gateway Health" "curl -s $BASE_URL/health | jq"
curl -s "$BASE_URL/health" | jq

echo_example "All Services Health" "curl -s $BASE_URL/health/services | jq"
curl -s "$BASE_URL/health/services" | jq

echo_example "System Status" "curl -s $BASE_URL/status | jq"
curl -s "$BASE_URL/status" | jq 2>/dev/null || echo "Status service not available"

# Document Management
echo_section "📄 DOCUMENT MANAGEMENT"

echo_example "List Documents" "curl -s '$BASE_URL/documents?limit=5' | jq"
curl -s "$BASE_URL/documents?limit=5" | jq

echo_example "Document Statistics" "curl -s $BASE_URL/documents/stats | jq"
curl -s "$BASE_URL/documents/stats" | jq

# Get first document if available
DOC_ID=$(curl -s "$BASE_URL/documents" | jq -r '.[0].id // empty' 2>/dev/null)
if [ ! -z "$DOC_ID" ] && [ "$DOC_ID" != "null" ]; then
    echo_example "Get Document Details" "curl -s $BASE_URL/documents/$DOC_ID | jq"
    curl -s "$BASE_URL/documents/$DOC_ID" | jq
fi

# Vector Search
echo_section "🔍 VECTOR SEARCH"

echo_example "Vector Collections" "curl -s $BASE_URL/search/collections | jq"
curl -s "$BASE_URL/search/collections" | jq

echo_example "Semantic Search" "curl -s -X POST $BASE_URL/search -H 'Content-Type: application/json' -d '{\"query\": \"strategic opportunities\", \"top_k\": 3}' | jq"
curl -s -X POST "$BASE_URL/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "strategic opportunities and market trends", "top_k": 3}' | jq

# Strategic Analysis - The 5 Main Types
echo_section "📊 STRATEGIC ANALYSIS - 5 TYPES"

# Analysis Types
echo_example "Available Analysis Types" "curl -s $BASE_URL/analysis/types | jq"
curl -s "$BASE_URL/analysis/types" | jq

# 1. Synthèse Exécutive
echo_example "1. Synthèse Exécutive" "curl -s -X POST $BASE_URL/analysis/synthesize -H 'Content-Type: application/json' -d '{...}' | jq"
curl -s -X POST "$BASE_URL/analysis/synthesize" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Quelles sont les principales opportunités stratégiques pour notre entreprise?",
    "title": "Synthèse Stratégique Q4 2024",
    "top_k": 5
  }' | jq

# 2. Analyse Concurrentielle  
echo_example "2. Analyse Concurrentielle" "curl -s -X POST $BASE_URL/analysis/competition -H 'Content-Type: application/json' -d '{...}' | jq"
curl -s -X POST "$BASE_URL/analysis/competition" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Qui sont nos principaux concurrents et comment se positionnent-ils?",
    "title": "Analyse Concurrentielle 2024",
    "top_k": 6
  }' | jq

# 3. Veille Technologique
echo_example "3. Veille Technologique" "curl -s -X POST $BASE_URL/analysis/tech-watch -H 'Content-Type: application/json' -d '{...}' | jq"
curl -s -X POST "$BASE_URL/analysis/tech-watch" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Quelles technologies émergentes impactent notre secteur?",
    "title": "Veille Technologique IA & Innovation",
    "top_k": 7
  }' | jq

# 4. Analyse de Risques
echo_example "4. Analyse de Risques" "curl -s -X POST $BASE_URL/analysis/risk-analysis -H 'Content-Type: application/json' -d '{...}' | jq"
curl -s -X POST "$BASE_URL/analysis/risk-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Quels sont les principaux risques stratégiques identifiés?",
    "title": "Analyse de Risques Globale",
    "top_k": 8
  }' | jq

# 5. Étude de Marché
echo_example "5. Étude de Marché" "curl -s -X POST $BASE_URL/analysis/market-study -H 'Content-Type: application/json' -d '{...}' | jq"
curl -s -X POST "$BASE_URL/analysis/market-study" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Quelle est la taille du marché et les perspectives de croissance?",
    "title": "Étude de Marché Complète 2024",
    "top_k": 6
  }' | jq

# Report Management
echo_section "📑 REPORT MANAGEMENT"

echo_example "List Reports" "curl -s '$BASE_URL/reports?limit=5' | jq"
curl -s "$BASE_URL/reports?limit=5" | jq

echo_example "Report Statistics" "curl -s $BASE_URL/reports/stats | jq"
curl -s "$BASE_URL/reports/stats" | jq

# Get first report if available
REPORT_ID=$(curl -s "$BASE_URL/reports" | jq -r '.[0].id // empty' 2>/dev/null)
if [ ! -z "$REPORT_ID" ] && [ "$REPORT_ID" != "null" ]; then
    echo_example "Get Report Details" "curl -s $BASE_URL/reports/$REPORT_ID | jq"
    curl -s "$BASE_URL/reports/$REPORT_ID" | jq
    
    echo_example "Export Report as PDF" "curl -s $BASE_URL/reports/$REPORT_ID/export --output report_$REPORT_ID.pdf"
    echo "Downloading PDF to report_$REPORT_ID.pdf..."
    curl -s "$BASE_URL/reports/$REPORT_ID/export" --output "report_$REPORT_ID.pdf"
    if [ -f "report_$REPORT_ID.pdf" ]; then
        echo -e "${GREEN}✓ PDF downloaded successfully ($(stat -f%z report_$REPORT_ID.pdf 2>/dev/null || stat -c%s report_$REPORT_ID.pdf) bytes)${NC}"
    fi
fi

# Workflow - Complete Analysis + Report
echo_section "🔄 COMPLETE WORKFLOW"

echo_example "Analyze and Generate Report" "curl -s -X POST '$BASE_URL/workflows/analyze-and-report?analysis_type=synthesize&query=...&title=...&auto_export=true' | jq"
curl -s -X POST "$BASE_URL/workflows/analyze-and-report" \
  -H "Content-Type: application/json" \
  -G \
  --data-urlencode "analysis_type=synthesize" \
  --data-urlencode "query=Effectuer une synthèse stratégique complète de nos opportunités" \
  --data-urlencode "title=Synthèse Automatisée via Workflow" \
  --data-urlencode "auto_export=true" | jq

# Generate a New Report
echo_section "📝 GENERATE NEW REPORT"

echo_example "Generate Report from Analysis" "curl -s -X POST '$BASE_URL/reports/generate?title=...&content=...&analysis_type=...' | jq"
curl -s -X POST "$BASE_URL/reports/generate" \
  -H "Content-Type: application/json" \
  -G \
  --data-urlencode "title=Rapport Test via API" \
  --data-urlencode "content=**SECTION TEST**\nCeci est un rapport de test généré via API.\n\n**RECOMMANDATIONS**\n- Action 1\n- Action 2\n- Action 3" \
  --data-urlencode "analysis_type=synthese_executive" | jq

# Legacy Endpoints
echo_section "🔄 LEGACY ENDPOINTS (Backward Compatibility)"

echo_example "Legacy Search" "curl -s -X POST $BASE_URL/search -H 'Content-Type: application/json' -d '{...}' | jq"
curl -s -X POST "$BASE_URL/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "legacy search test", "top_k": 2}' | jq

echo_example "Legacy Report Generation" "curl -s -X POST $BASE_URL/report -H 'Content-Type: application/json' -d '{...}' | jq"
curl -s -X POST "$BASE_URL/report" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Legacy Report Test",
    "query": "test legacy report generation"
  }' | jq

# Documentation
echo_section "📚 API DOCUMENTATION"

echo_example "OpenAPI/Swagger Documentation" "curl -s $BASE_URL/docs"
echo "Visit: $BASE_URL/docs for interactive API documentation"

echo_example "OpenAPI JSON Schema" "curl -s $BASE_URL/openapi.json | jq '.info'"
curl -s "$BASE_URL/openapi.json" | jq '.info'

echo -e "\n${GREEN}🎉 Example API calls completed!${NC}"
echo -e "\n${YELLOW}💡 Next steps:${NC}"
echo "1. Visit $BASE_URL/docs for interactive Swagger documentation"
echo "2. Upload some PDFs using: curl -X POST $BASE_URL/documents/upload -F 'file=@document.pdf'"
echo "3. Run the full workflow test: python3 scripts/test_workflow.py"
echo "4. Test all services: ./scripts/test_all_services.sh"
