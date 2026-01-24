#!/bin/bash
# Memory Service Deployment Script
# Run this after starting Docker Desktop

set -e  # Exit on error

echo "=========================================="
echo "Memory Service Deployment"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Step 1: Check if postgres is running
echo "Step 1: Checking PostgreSQL container..."
if ! docker-compose ps postgres | grep -q "Up"; then
    echo "Starting PostgreSQL container..."
    docker-compose up -d postgres
    echo "Waiting for PostgreSQL to be ready..."
    sleep 10
fi
echo "✓ PostgreSQL is running"
echo ""

# Step 2: Run database migration
echo "Step 2: Running database migration..."
echo "Creating memory service tables..."

# Copy migration script to container
docker cp memory-service/migrations/001_create_memory_tables.sql insight-mvp-postgres-1:/tmp/ 2>/dev/null || \
docker cp memory-service/migrations/001_create_memory_tables.sql insight-mvp_postgres_1:/tmp/ 2>/dev/null || \
docker cp memory-service/migrations/001_create_memory_tables.sql postgres:/tmp/

# Execute migration
docker exec -i insight-mvp-postgres-1 psql -U insight_user -d insight_db -f /tmp/001_create_memory_tables.sql 2>/dev/null || \
docker exec -i insight-mvp_postgres_1 psql -U insight_user -d insight_db -f /tmp/001_create_memory_tables.sql 2>/dev/null || \
docker exec -i postgres psql -U insight_user -d insight_db -f /tmp/001_create_memory_tables.sql

echo "✓ Database migration completed"
echo ""

# Step 3: Build memory-service
echo "Step 3: Building memory-service Docker image..."
docker-compose build memory-service
echo "✓ Memory service built successfully"
echo ""

# Step 4: Start memory-service
echo "Step 4: Starting memory-service..."
docker-compose up -d memory-service
echo "Waiting for service to start..."
sleep 5
echo "✓ Memory service started"
echo ""

# Step 5: Verify service health
echo "Step 5: Verifying service health..."
max_retries=10
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if curl -s http://localhost:8008/health > /dev/null 2>&1; then
        echo "✓ Memory service is healthy!"
        curl -s http://localhost:8008/health | jq . 2>/dev/null || curl -s http://localhost:8008/health
        break
    fi
    retry_count=$((retry_count + 1))
    echo "Waiting for service to be ready... ($retry_count/$max_retries)"
    sleep 2
done

if [ $retry_count -eq $max_retries ]; then
    echo "⚠️  Warning: Could not verify service health, but container is running"
    echo "Check logs with: docker-compose logs memory-service"
fi
echo ""

# Step 6: Show service status
echo "Step 6: Service Status"
echo "=========================================="
docker-compose ps memory-service
echo ""

# Step 7: Verify database tables
echo "Step 7: Verifying database tables..."
docker exec -i insight-mvp-postgres-1 psql -U insight_user -d insight_db -c "\dt user_*; \dt migration_status;" 2>/dev/null || \
docker exec -i insight-mvp_postgres_1 psql -U insight_user -d insight_db -c "\dt user_*; \dt migration_status;" 2>/dev/null || \
docker exec -i postgres psql -U insight_user -d insight_db -c "\dt user_*; \dt migration_status;"
echo ""

echo "=========================================="
echo "✅ Memory Service Deployment Complete!"
echo "=========================================="
echo ""
echo "Service Details:"
echo "  - URL: http://localhost:8008"
echo "  - Health: http://localhost:8008/health"
echo "  - API Docs: http://localhost:8008/docs"
echo ""
echo "Gateway Proxy Endpoints (authenticated):"
echo "  - GET  /api/memory/conversations"
echo "  - GET  /api/memory/documents"
echo "  - POST /api/memory/migrate"
echo ""
echo "Next Steps:"
echo "  1. View logs: docker-compose logs -f memory-service"
echo "  2. Test API: curl http://localhost:8008/health"
echo "  3. Access docs: open http://localhost:8008/docs"
echo ""
