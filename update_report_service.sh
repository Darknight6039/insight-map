#!/bin/bash

# Script de mise à jour report-service avec améliorations PDF v2.0

echo "🎨 Mise à Jour Report Service - Style PDF Professionnel v2.0"
echo ""
echo "📋 Améliorations appliquées :"
echo "   ✅ Filigrane pleine page (100% au lieu de 95%)"
echo "   ✅ Citations APA réelles (Auteur, année) au lieu de [1], [2]"
echo "   ✅ Titres centrés pour toutes les sections"
echo "   ✅ Suppression des traits/lignes (style plus épuré)"
echo "   ✅ Pied de page discret et professionnel"
echo "   ✅ Bibliographie organisée sans emojis"
echo ""

# 1. Arrêt du service actuel
echo "⏹️  Arrêt du service report..."
docker compose stop report-service

# 2. Rebuild avec nouvelles modifications
echo ""
echo "🔨 Rebuild du service report..."
docker compose build report-service

# 3. Redémarrage
echo ""
echo "🔄 Redémarrage du service..."
docker compose up -d report-service

# 4. Attente démarrage
echo ""
echo "⏳ Attente du démarrage (10 secondes)..."
sleep 10

# 5. Test de santé
echo ""
echo "🏥 Test de santé du service..."
health_response=$(curl -s http://localhost:8004/health)
echo "$health_response" | jq '.' || echo "$health_response"

# 6. Affichage logs récents
echo ""
echo "📋 Logs récents (5 dernières lignes):"
docker compose logs --tail=5 report-service

echo ""
echo "✅ Mise à jour terminée !"
echo ""
echo "🧪 Test de génération PDF :"
echo ""
echo "1. Générer un rapport depuis le frontend"
echo "   → Aller sur http://localhost:7860"
echo "   → Générer un rapport détaillé"
echo "   → Cliquer sur 'Exporter en PDF'"
echo ""
echo "2. Vérifier les améliorations :"
echo "   ✓ Citations format (Auteur, 2024) au lieu de [1]"
echo "   ✓ Filigrane couvre toute la page"
echo "   ✓ Titres bien centrés"
echo "   ✓ Pas de lignes/traits artificiels"
echo "   ✓ Style épuré et professionnel"
echo ""

