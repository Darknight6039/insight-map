#!/bin/bash
# Memory Service Test Script
# Tests all memory service endpoints with authentication

set -e

echo "=========================================="
echo "Memory Service API Tests"
echo "=========================================="
echo ""

# Configuration
GATEWAY_URL="http://localhost:8000"
MEMORY_URL="http://localhost:8008"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@axial.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123}"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print test result
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

echo "Test 1: Health Check (No Auth)"
echo "--------------------------------------"
RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8008/health)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Health check endpoint"
    echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
else
    print_result 1 "Health check endpoint (HTTP $HTTP_CODE)"
fi
echo ""

echo "Test 2: Authentication"
echo "--------------------------------------"
echo "Logging in as $ADMIN_EMAIL..."
LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$GATEWAY_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}")

HTTP_CODE=$(echo "$LOGIN_RESPONSE" | tail -n1)
BODY=$(echo "$LOGIN_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    TOKEN=$(echo "$BODY" | jq -r '.access_token')
    if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
        print_result 0 "User authentication"
        echo "Token: ${TOKEN:0:20}..."
    else
        print_result 1 "User authentication (no token in response)"
        TOKEN=""
    fi
else
    print_result 1 "User authentication (HTTP $HTTP_CODE)"
    echo "$BODY"
    TOKEN=""
fi
echo ""

if [ -z "$TOKEN" ]; then
    echo -e "${RED}Cannot proceed without authentication token${NC}"
    echo "Please check your credentials and try again"
    exit 1
fi

echo "Test 3: List Conversations (Direct)"
echo "--------------------------------------"
RESPONSE=$(curl -s -w "\n%{http_code}" "$MEMORY_URL/api/v1/conversations" \
    -H "Authorization: Bearer $TOKEN")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "List conversations (direct)"
    TOTAL=$(echo "$BODY" | jq -r '.total' 2>/dev/null || echo "0")
    echo "Total conversations: $TOTAL"
else
    print_result 1 "List conversations (HTTP $HTTP_CODE)"
fi
echo ""

echo "Test 4: List Conversations (Gateway Proxy)"
echo "--------------------------------------"
RESPONSE=$(curl -s -w "\n%{http_code}" "$GATEWAY_URL/api/memory/conversations" \
    -H "Authorization: Bearer $TOKEN")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "List conversations (gateway)"
    TOTAL=$(echo "$BODY" | jq -r '.total' 2>/dev/null || echo "0")
    echo "Total conversations: $TOTAL"
else
    print_result 1 "List conversations via gateway (HTTP $HTTP_CODE)"
fi
echo ""

echo "Test 5: List Documents (Direct)"
echo "--------------------------------------"
RESPONSE=$(curl -s -w "\n%{http_code}" "$MEMORY_URL/api/v1/documents" \
    -H "Authorization: Bearer $TOKEN")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "List documents (direct)"
    TOTAL=$(echo "$BODY" | jq -r '.total' 2>/dev/null || echo "0")
    echo "Total documents: $TOTAL"
else
    print_result 1 "List documents (HTTP $HTTP_CODE)"
fi
echo ""

echo "Test 6: List Documents (Gateway Proxy)"
echo "--------------------------------------"
RESPONSE=$(curl -s -w "\n%{http_code}" "$GATEWAY_URL/api/memory/documents" \
    -H "Authorization: Bearer $TOKEN")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "List documents (gateway)"
    TOTAL=$(echo "$BODY" | jq -r '.total' 2>/dev/null || echo "0")
    echo "Total documents: $TOTAL"
else
    print_result 1 "List documents via gateway (HTTP $HTTP_CODE)"
fi
echo ""

echo "Test 7: Filter Documents by Type"
echo "--------------------------------------"
RESPONSE=$(curl -s -w "\n%{http_code}" "$GATEWAY_URL/api/memory/documents?type=report" \
    -H "Authorization: Bearer $TOKEN")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Filter documents by type=report"
    TOTAL=$(echo "$BODY" | jq -r '.total' 2>/dev/null || echo "0")
    echo "Total reports: $TOTAL"
else
    print_result 1 "Filter documents by type (HTTP $HTTP_CODE)"
fi
echo ""

echo "Test 8: Migration Status"
echo "--------------------------------------"
RESPONSE=$(curl -s -w "\n%{http_code}" "$GATEWAY_URL/api/memory/migrate/status" \
    -H "Authorization: Bearer $TOKEN")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Check migration status"
    echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
else
    print_result 1 "Check migration status (HTTP $HTTP_CODE)"
fi
echo ""

echo "Test 9: Create Test Conversation"
echo "--------------------------------------"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$MEMORY_URL/api/v1/conversations" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "Test query for memory service",
        "response": "Test response from memory service",
        "conversation_type": "chat",
        "analysis_type": "test"
    }')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "201" ]; then
    print_result 0 "Create test conversation"
    CONV_ID=$(echo "$BODY" | jq -r '.id' 2>/dev/null)
    echo "Created conversation ID: $CONV_ID"
else
    print_result 1 "Create test conversation (HTTP $HTTP_CODE)"
    CONV_ID=""
fi
echo ""

if [ -n "$CONV_ID" ] && [ "$CONV_ID" != "null" ]; then
    echo "Test 10: Delete Test Conversation"
    echo "--------------------------------------"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$MEMORY_URL/api/v1/conversations/$CONV_ID" \
        -H "Authorization: Bearer $TOKEN")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

    if [ "$HTTP_CODE" = "204" ]; then
        print_result 0 "Delete test conversation"
    else
        print_result 1 "Delete test conversation (HTTP $HTTP_CODE)"
    fi
    echo ""
fi

echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
echo -e "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Check the output above.${NC}"
    exit 1
fi
