#!/bin/bash
# Complete Memory Service + Frontend Integration Deployment
# Deploys both backend memory-service and frontend updates

set -e  # Exit on error

echo "=========================================="
echo "Complete Memory Integration Deployment"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# =============================================================================
# PART 1: BACKEND - Deploy Memory Service
# =============================================================================

echo "=========================================="
echo "PART 1: Backend Deployment"
echo "=========================================="
echo ""

# Step 1: Check PostgreSQL
echo "Step 1: Checking PostgreSQL..."
if ! docker-compose ps postgres | grep -q "Up"; then
    echo -e "${YELLOW}Starting PostgreSQL...${NC}"
    docker-compose up -d postgres
    echo "Waiting for PostgreSQL to be ready..."
    sleep 10
fi
echo -e "${GREEN}✓ PostgreSQL is running${NC}"
echo ""

# Step 2: Run database migration
echo "Step 2: Running database migration..."
echo "Creating memory service tables..."

# Copy and execute migration
docker cp memory-service/migrations/001_create_memory_tables.sql insight-mvp-postgres-1:/tmp/ 2>/dev/null || \
docker cp memory-service/migrations/001_create_memory_tables.sql insight-mvp_postgres_1:/tmp/ 2>/dev/null || \
docker cp memory-service/migrations/001_create_memory_tables.sql postgres:/tmp/

docker exec -i insight-mvp-postgres-1 psql -U insight_user -d insight_db -f /tmp/001_create_memory_tables.sql 2>/dev/null || \
docker exec -i insight-mvp_postgres_1 psql -U insight_user -d insight_db -f /tmp/001_create_memory_tables.sql 2>/dev/null || \
docker exec -i postgres psql -U insight_user -d insight_db -f /tmp/001_create_memory_tables.sql

echo -e "${GREEN}✓ Database migration completed${NC}"
echo ""

# Step 3: Build memory-service
echo "Step 3: Building memory-service..."
docker-compose build memory-service
echo -e "${GREEN}✓ Memory service built${NC}"
echo ""

# Step 4: Start memory-service
echo "Step 4: Starting memory-service..."
docker-compose up -d memory-service
echo "Waiting for service to start..."
sleep 5
echo -e "${GREEN}✓ Memory service started${NC}"
echo ""

# Step 5: Verify memory service health
echo "Step 5: Verifying memory service health..."
max_retries=10
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if curl -s http://localhost:8008/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Memory service is healthy!${NC}"
        break
    fi
    retry_count=$((retry_count + 1))
    echo "Waiting for service... ($retry_count/$max_retries)"
    sleep 2
done

if [ $retry_count -eq $max_retries ]; then
    echo -e "${YELLOW}⚠️  Warning: Could not verify health, check logs${NC}"
fi
echo ""

# =============================================================================
# PART 2: FRONTEND - Deploy Updated Interface
# =============================================================================

echo "=========================================="
echo "PART 2: Frontend Deployment"
echo "=========================================="
echo ""

# Step 6: Check if gateway-api is running
echo "Step 6: Checking gateway-api..."
if ! docker-compose ps gateway-api | grep -q "Up"; then
    echo -e "${YELLOW}Starting gateway-api...${NC}"
    docker-compose up -d gateway-api
    sleep 5
fi
echo -e "${GREEN}✓ Gateway API is running${NC}"
echo ""

# Step 7: Build frontend with new pages
echo "Step 7: Building frontend with new integration..."
echo "This may take a few minutes..."
docker-compose build frontend-openwebui
echo -e "${GREEN}✓ Frontend built successfully${NC}"
echo ""

# Step 8: Restart frontend
echo "Step 8: Restarting frontend..."
docker-compose up -d frontend-openwebui
sleep 8
echo -e "${GREEN}✓ Frontend restarted${NC}"
echo ""

# Step 9: Verify frontend is accessible
echo "Step 9: Verifying frontend..."
max_retries=10
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is accessible!${NC}"
        break
    fi
    retry_count=$((retry_count + 1))
    echo "Waiting for frontend... ($retry_count/$max_retries)"
    sleep 2
done
echo ""

# =============================================================================
# VERIFICATION
# =============================================================================

echo "=========================================="
echo "Verification & Summary"
echo "=========================================="
echo ""

# Check all services
echo "Services Status:"
echo "----------------"
docker-compose ps gateway-api memory-service frontend-openwebui | tail -n +2
echo ""

# Verify database tables
echo "Database Tables:"
echo "----------------"
docker exec -i insight-mvp-postgres-1 psql -U insight_user -d insight_db -c "\dt user_conversations; \dt user_documents; \dt migration_status;" 2>/dev/null || \
docker exec -i insight-mvp_postgres_1 psql -U insight_user -d insight_db -c "\dt user_conversations; \dt user_documents; \dt migration_status;" 2>/dev/null || \
docker exec -i postgres psql -U insight_user -d insight_db -c "\dt user_conversations; \dt user_documents; \dt migration_status;"
echo ""

# =============================================================================
# SUCCESS MESSAGE
# =============================================================================

echo "=========================================="
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Backend Services:"
echo "  • Memory Service:  http://localhost:8008"
echo "  • Health Check:    http://localhost:8008/health"
echo "  • API Docs:        http://localhost:8008/docs"
echo "  • Gateway API:     http://localhost:8000"
echo ""
echo "Frontend Application:"
echo "  • Main App:        http://localhost:3000"
echo "  • New Pages:"
echo "    - Conversations: http://localhost:3000/history"
echo "    - Library:       http://localhost:3000/library"
echo ""
echo "Gateway Memory Endpoints:"
echo "  • GET  /api/memory/conversations"
echo "  • GET  /api/memory/documents"
echo "  • POST /api/memory/migrate"
echo ""
echo "Next Steps:"
echo "  1. Login to the app: http://localhost:3000"
echo "  2. Navigate to 'Historique' to see conversations"
echo "  3. Navigate to 'Bibliothèque' to see documents"
echo "  4. Run tests: ./test-memory-service.sh"
echo ""
echo "Troubleshooting:"
echo "  • View logs: docker-compose logs -f memory-service"
echo "  • View logs: docker-compose logs -f frontend-openwebui"
echo "  • View logs: docker-compose logs -f gateway-api"
echo ""
echo "Documentation:"
echo "  • Backend:  ./MEMORY_SERVICE_DEPLOYMENT.md"
echo "  • Frontend: ./FRONTEND_MEMORY_INTEGRATION.md"
echo ""
