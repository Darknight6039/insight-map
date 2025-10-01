#!/bin/bash

# Script de configuration .env pour Insight MVP

cat > .env << 'EOF'
OPENAI_API_KEY=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

# Configuration Vector Service
QDRANT_URL=http://qdrant:6333
VECTOR_SERVICE_URL=http://vector-service:8002

# Configuration PostgreSQL
POSTGRES_DB=insight_db
POSTGRES_USER=user
POSTGRES_PASSWORD=password
DATABASE_URL=postgresql://user:password@postgres:5432/insight_db

# Configuration Frontend
NEXT_PUBLIC_BACKEND_URL=http://localhost:8006
EOF

echo "✅ Fichier .env créé avec succès !"
echo ""
echo "🔑 Clé OpenAI configurée"
echo "📊 Services configurés (Qdrant, PostgreSQL, Backend)"
echo ""
echo "▶️  Prochaines étapes :"
echo "   1. docker compose build backend-service"
echo "   2. docker compose up -d"
echo ""

