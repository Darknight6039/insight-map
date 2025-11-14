#!/bin/bash

# Script d'ingestion de tous les PDFs du dossier data/pdfs/

echo "🚀 INDEXATION AUTOMATIQUE DES PDFs"
echo "===================================="

# Configuration
DATA_DIR="../data/pdfs"
API_URL="http://localhost:8001/ingest"
COUNT=0
SUCCESS=0
FAILED=0

# Vérifier que le service est accessible
if ! curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "❌ Document-service non accessible"
    exit 1
fi

echo "✅ Document-service accessible"
echo ""

# Parcourir tous les PDFs
for pdf_file in "$DATA_DIR"/*.pdf; do
    if [ ! -f "$pdf_file" ]; then
        continue
    fi
    
    filename=$(basename "$pdf_file")
    title="${filename%.pdf}"
    title="${title//_/ }"
    title="${title//-/ }"
    
    COUNT=$((COUNT + 1))
    echo "[$COUNT] 📄 $filename"
    
    # Envoyer le PDF (avec timeout de 60s)
    response=$(curl -s -X POST "$API_URL" \
        -F "file=@$pdf_file" \
        -F "title=$title" \
        --max-time 60 \
        -w "\n%{http_code}" 2>&1)
    
    http_code=$(echo "$response" | tail -1)
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo "    ✅ Indexé avec succès"
        SUCCESS=$((SUCCESS + 1))
    else
        echo "    ❌ Échec (code: $http_code)"
        FAILED=$((FAILED + 1))
    fi
    
    # Petite pause entre chaque upload
    sleep 2
    
    echo ""
done

# Résumé
echo "===================================="
echo "📊 RÉSUMÉ"
echo "===================================="
echo "Total traité : $COUNT"
echo "✅ Réussis   : $SUCCESS"
echo "❌ Échoués   : $FAILED"
echo ""

# Vérifier l'indexation dans Qdrant
echo "🔍 Vérification Qdrant..."
vectors_info=$(curl -s http://localhost:6333/collections/documents | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"Vecteurs: {d['result']['vectors_count']}, Points: {d['result']['points_count']}\")" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ $vectors_info"
else
    echo "⚠️  Impossible de vérifier Qdrant"
fi

echo ""
echo "✨ Indexation terminée !"

