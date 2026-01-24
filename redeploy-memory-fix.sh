#!/bin/bash
# Quick redeploy for memory service fix
# Redeploys: memory-service, report-service, backend-service

set -e

echo "=========================================="
echo "Redeploying Memory Service Fix"
echo "=========================================="
echo ""

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Rebuild and restart memory-service
echo "1. Rebuilding memory-service..."
docker-compose build memory-service
echo "✓ Built memory-service"
echo ""

echo "2. Rebuilding report-service..."
docker-compose build report-service
echo "✓ Built report-service"
echo ""

echo "3. Rebuilding backend-service..."
docker-compose build backend-service
echo "✓ Built backend-service"
echo ""

# Restart services
echo "4. Restarting services..."
docker-compose up -d memory-service report-service backend-service
echo "✓ Services restarted"
echo ""

# Wait for services to be ready
echo "5. Waiting for services to be ready..."
sleep 5

# Check health
echo "6. Checking service health..."
if curl -s http://localhost:8008/health > /dev/null 2>&1; then
    echo "✓ memory-service: OK"
else
    echo "⚠️  memory-service: Not responding"
fi

if curl -s http://localhost:8004/health > /dev/null 2>&1; then
    echo "✓ report-service: OK"
else
    echo "⚠️  report-service: Not responding"
fi

if curl -s http://localhost:8006/health > /dev/null 2>&1; then
    echo "✓ backend-service: OK"
else
    echo "⚠️  backend-service: Not responding"
fi

echo ""
echo "=========================================="
echo "✅ Redeploy Complete!"
echo "=========================================="
echo ""
echo "Services updated:"
echo "  • memory-service (added internal endpoints)"
echo "  • report-service (uses internal API)"
echo "  • backend-service (uses internal API)"
echo ""
echo "Next steps:"
echo "  1. Generate a new report on the frontend"
echo "  2. Check /library page - report should appear!"
echo ""
echo "View logs:"
echo "  docker-compose logs -f memory-service"
echo "  docker-compose logs -f report-service"
echo ""
