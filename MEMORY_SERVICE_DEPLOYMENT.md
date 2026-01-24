# Memory Service Deployment Guide

## Overview

The memory service provides conversation history and document storage for the Insight MVP platform. This guide will help you deploy and verify the service.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose installed
- PostgreSQL container running (insight_db)
- Gateway API running on port 8000

## Quick Start

### 1. Start Docker Desktop

Make sure Docker Desktop is running before proceeding.

### 2. Deploy Memory Service

Run the automated deployment script:

```bash
./deploy-memory-service.sh
```

This script will:
1. ✓ Check Docker is running
2. ✓ Start PostgreSQL if needed
3. ✓ Create database tables (3 new tables)
4. ✓ Build memory-service Docker image
5. ✓ Start memory-service container
6. ✓ Verify service health
7. ✓ Display service status

### 3. Test Memory Service

Run the automated test suite:

```bash
./test-memory-service.sh
```

This will test:
- Health check endpoint
- Authentication
- Conversation CRUD operations
- Document CRUD operations
- Gateway proxy endpoints
- Migration status

## Manual Deployment Steps

If you prefer to deploy manually:

### Step 1: Update Environment Variables

The `.env` file has already been updated with:
```bash
MEMORY_SERVICE_URL=http://memory-service:8008
```

### Step 2: Run Database Migration

```bash
# Copy migration script to PostgreSQL container
docker cp memory-service/migrations/001_create_memory_tables.sql insight-mvp-postgres-1:/tmp/

# Execute migration
docker exec -i insight-mvp-postgres-1 psql -U insight_user -d insight_db -f /tmp/001_create_memory_tables.sql
```

Expected output:
```
CREATE TABLE
CREATE INDEX
CREATE INDEX
...
GRANT
```

### Step 3: Build Memory Service

```bash
docker-compose build memory-service
```

### Step 4: Start Memory Service

```bash
docker-compose up -d memory-service
```

### Step 5: Verify Service

```bash
# Check health
curl http://localhost:8008/health

# View logs
docker-compose logs -f memory-service

# Check container status
docker-compose ps memory-service
```

## Database Schema

The migration creates 3 new tables:

### 1. user_conversations
Stores chat discussion history with full context.

**Columns:**
- `id` - Primary key
- `user_id` - Foreign key to users table
- `query` - User's question
- `response` - AI response
- `conversation_type` - 'chat' or 'analysis'
- `analysis_type` - Type of analysis performed
- `business_type` - Business sector
- `created_at` - Timestamp

**Indexes:**
- `idx_conversations_user` on user_id
- `idx_conversations_created` on created_at DESC
- `idx_conversations_type` on conversation_type

### 2. user_documents
Stores references to generated reports and watch results.

**Columns:**
- `id` - Primary key
- `user_id` - Foreign key to users table
- `document_type` - 'report' or 'watch'
- `title` - Document title
- `content` - Full text content (truncated for storage)
- `file_path` - Path to PDF if exists
- `analysis_type` - Type of analysis
- `business_type` - Sector classification
- `report_id` - Reference to reports table
- `watch_id` - Reference to watch_configs table
- `metadata` - JSONB field for additional data
- `created_at` - Timestamp

**Indexes:**
- `idx_documents_user` on user_id
- `idx_documents_type` on (document_type, analysis_type)
- `idx_documents_created` on created_at DESC

### 3. migration_status
Tracks which users have been migrated from legacy system.

**Columns:**
- `user_id` - Primary key, foreign key to users table
- `conversations_migrated` - Boolean flag
- `migration_date` - When migration completed
- `legacy_conversation_count` - Number of conversations migrated

## API Endpoints

### Direct Memory Service (Port 8008)

**Conversations:**
- `GET /api/v1/conversations` - List conversations (paginated)
- `POST /api/v1/conversations` - Create new conversation
- `GET /api/v1/conversations/{id}` - Get specific conversation
- `DELETE /api/v1/conversations/{id}` - Delete conversation

**Documents:**
- `GET /api/v1/documents` - List documents (paginated)
- `POST /api/v1/documents` - Register new document
- `GET /api/v1/documents/{id}` - Get specific document
- `DELETE /api/v1/documents/{id}` - Delete document

**Migration:**
- `GET /api/v1/migrate/status` - Check migration status
- `POST /api/v1/migrate` - Trigger migration from legacy system

**Health:**
- `GET /health` - Service health check

### Gateway Proxy (Port 8000)

All endpoints are prefixed with `/api/memory/` and require authentication:

- `GET /api/memory/conversations`
- `GET /api/memory/conversations/{id}`
- `DELETE /api/memory/conversations/{id}`
- `GET /api/memory/documents`
- `GET /api/memory/documents/{id}`
- `DELETE /api/memory/documents/{id}`
- `GET /api/memory/migrate/status`
- `POST /api/memory/migrate`

## Query Parameters

### Conversations List

```bash
GET /api/v1/conversations?skip=0&limit=20&conversation_type=chat&analysis_type=synthese_executive&search=market
```

Parameters:
- `skip` - Offset for pagination (default: 0)
- `limit` - Max results per page (default: 20, max: 100)
- `conversation_type` - Filter by type: 'chat' or 'analysis'
- `analysis_type` - Filter by analysis type
- `business_type` - Filter by business sector
- `search` - Text search in query/response

### Documents List

```bash
GET /api/v1/documents?skip=0&limit=20&type=report&analysis_type=synthese_executive
```

Parameters:
- `skip` - Offset for pagination (default: 0)
- `limit` - Max results per page (default: 20, max: 100)
- `type` - Filter by document_type: 'report' or 'watch'
- `analysis_type` - Filter by analysis type
- `business_type` - Filter by business sector
- `search` - Text search in title/content

## Authentication

All memory service endpoints require a valid JWT token:

```bash
# Get token from gateway
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@axial.com","password":"admin123"}' \
  | jq -r '.access_token')

# Use token in requests
curl http://localhost:8008/api/v1/conversations \
  -H "Authorization: Bearer $TOKEN"
```

## Testing Examples

### 1. List All Conversations

```bash
curl http://localhost:8000/api/memory/conversations \
  -H "Authorization: Bearer $TOKEN"
```

### 2. List Reports Only

```bash
curl "http://localhost:8000/api/memory/documents?type=report" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. List Watches Only

```bash
curl "http://localhost:8000/api/memory/documents?type=watch" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Filter by Analysis Type

```bash
curl "http://localhost:8000/api/memory/documents?analysis_type=synthese_executive" \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Search Documents

```bash
curl "http://localhost:8000/api/memory/documents?search=market+analysis" \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Check Migration Status

```bash
curl http://localhost:8000/api/memory/migrate/status \
  -H "Authorization: Bearer $TOKEN"
```

### 7. Trigger Migration

```bash
curl -X POST http://localhost:8000/api/memory/migrate \
  -H "Authorization: Bearer $TOKEN"
```

## Service Integration Status

### ✅ Completed Integrations

1. **backend-service** - Function added to save conversations (requires user token)
2. **report-service** - Integrated to save reports as documents
3. **scheduler-service** - Prepared for watch document storage
4. **gateway-api** - Full proxy endpoints with authentication

### ⚠️ Known Limitations

1. **Service-to-Service Authentication**: Report-service and scheduler-service don't have user JWT tokens when calling memory-service. This is noted in code with TODO comments.

2. **Recommended Enhancement**: Implement internal service tokens for backend services to communicate with memory-service without user context.

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs memory-service

# Common issues:
# 1. Port 8008 already in use
# 2. Database migration not run
# 3. Environment variables missing
```

### Database Migration Fails

```bash
# Check if tables already exist
docker exec -i insight-mvp-postgres-1 psql -U insight_user -d insight_db -c "\dt user_*;"

# Drop tables if needed (WARNING: deletes data)
docker exec -i insight-mvp-postgres-1 psql -U insight_user -d insight_db -c "DROP TABLE IF EXISTS user_conversations CASCADE; DROP TABLE IF EXISTS user_documents CASCADE; DROP TABLE IF EXISTS migration_status CASCADE;"

# Re-run migration
./deploy-memory-service.sh
```

### Authentication Errors

```bash
# Verify JWT_SECRET_KEY is the same across all services
grep JWT_SECRET_KEY .env

# Check token is valid
echo $TOKEN | cut -d'.' -f2 | base64 -d 2>/dev/null | jq .
```

### Service Unreachable

```bash
# Check service is running
docker-compose ps memory-service

# Check network connectivity
docker exec -it insight-mvp-gateway-api-1 ping memory-service

# Check port mapping
docker port insight-mvp-memory-service-1
```

## Monitoring

### View Real-time Logs

```bash
docker-compose logs -f memory-service
```

### Check Service Health

```bash
# Simple health check
curl http://localhost:8008/health | jq .

# Detailed service info
docker-compose ps memory-service
docker stats insight-mvp-memory-service-1 --no-stream
```

### Database Statistics

```bash
# Count records
docker exec -i insight-mvp-postgres-1 psql -U insight_user -d insight_db -c "
SELECT
  'Conversations' as table_name, COUNT(*) as count FROM user_conversations
UNION ALL
SELECT
  'Documents', COUNT(*) FROM user_documents
UNION ALL
SELECT
  'Migrations', COUNT(*) FROM migration_status;
"
```

## API Documentation

Once the service is running, view interactive API documentation:

- Swagger UI: http://localhost:8008/docs
- ReDoc: http://localhost:8008/redoc

## Next Steps

1. **Frontend Integration**: Update frontend to use `/api/memory/*` endpoints
2. **Service Authentication**: Implement service-to-service auth tokens
3. **Legacy Migration**: Trigger migration for existing users
4. **Monitoring**: Add metrics and alerting
5. **Backup**: Set up automated backups for memory data

## Support

For issues or questions:
- Check logs: `docker-compose logs memory-service`
- Review deployment output
- Run test suite: `./test-memory-service.sh`
- Check database: Verify tables were created

## Files Created

```
memory-service/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── database.py       # Database config
│   └── migration.py      # Legacy migration logic
├── migrations/
│   └── 001_create_memory_tables.sql
├── Dockerfile
└── requirements.txt

Root directory:
├── deploy-memory-service.sh      # Automated deployment
├── test-memory-service.sh        # Automated testing
└── MEMORY_SERVICE_DEPLOYMENT.md  # This file
```
