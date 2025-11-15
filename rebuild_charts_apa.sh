#!/bin/bash

# ========================================================================
# 🚀 SCRIPT DE DÉPLOIEMENT - CITATIONS APA + GRAPHIQUES
# ========================================================================
# Ce script rebuild et redémarre les services avec :
# - Citations en format APA (Auteur, Année) au lieu de [1], [2], [3]
# - Génération automatique de graphiques dans les rapports
# - Intégration des graphiques dans les exports PDF
# ========================================================================

set -e  # Arrêter en cas d'erreur

echo ""
echo "========================================================================="
echo "🚀 DÉPLOIEMENT - CITATIONS APA + GRAPHIQUES"
echo "========================================================================="
echo ""

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Erreur: docker-compose.yml non trouvé"
    echo "   Veuillez exécuter ce script depuis le répertoire racine du projet"
    exit 1
fi

# ========================================================================
# ÉTAPE 1: ARRÊT DES SERVICES
# ========================================================================
echo "📦 ÉTAPE 1/5 - Arrêt des services existants..."
echo "---------------------------------------------------------------"
/Applications/Docker.app/Contents/Resources/bin/docker compose stop backend-service report-service
echo "✅ Services arrêtés"
echo ""

# ========================================================================
# ÉTAPE 2: REBUILD BACKEND-SERVICE (CITATIONS APA)
# ========================================================================
echo "🔨 ÉTAPE 2/5 - Rebuild backend-service (citations APA)..."
echo "---------------------------------------------------------------"
echo "   - Conversion [1][2][3] → (Auteur, Année)"
echo "   - Prompts enrichis pour 2-4 graphiques par rapport"
echo "   - Format chart markdown pour génération automatique"
/Applications/Docker.app/Contents/Resources/bin/docker compose build --no-cache backend-service
echo "✅ Backend-service rebuilt"
echo ""

# ========================================================================
# ÉTAPE 3: REBUILD REPORT-SERVICE (GÉNÉRATION GRAPHIQUES)
# ========================================================================
echo "🔨 ÉTAPE 3/5 - Rebuild report-service (graphiques + matplotlib)..."
echo "---------------------------------------------------------------"
echo "   - Installation matplotlib pour génération graphiques"
echo "   - Parser blocs ```chart``` dans markdown"
echo "   - Génération images PNG (bar, line, pie)"
echo "   - Intégration automatique dans PDF"
/Applications/Docker.app/Contents/Resources/bin/docker compose build --no-cache report-service
echo "✅ Report-service rebuilt"
echo ""

# ========================================================================
# ÉTAPE 4: REDÉMARRAGE DES SERVICES
# ========================================================================
echo "▶️  ÉTAPE 4/5 - Redémarrage des services..."
echo "---------------------------------------------------------------"
/Applications/Docker.app/Contents/Resources/bin/docker compose up -d backend-service report-service
echo "✅ Services redémarrés"
echo ""

# Attendre que les services soient prêts
echo "⏳ Attente de l'initialisation des services (30s)..."
sleep 30

# ========================================================================
# ÉTAPE 5: TESTS DE VALIDATION
# ========================================================================
echo "🧪 ÉTAPE 5/5 - Tests de validation..."
echo "---------------------------------------------------------------"

# Test 1: Health check backend
echo "📍 Test 1: Health check backend-service..."
if curl -s http://localhost:8006/health | grep -q "healthy"; then
    echo "   ✅ Backend-service opérationnel"
else
    echo "   ❌ Backend-service non disponible"
fi

# Test 2: Health check report-service
echo "📍 Test 2: Health check report-service..."
if curl -s http://localhost:8004/health | grep -q "healthy"; then
    echo "   ✅ Report-service opérationnel"
else
    echo "   ❌ Report-service non disponible"
fi

# Test 3: Vérifier matplotlib dans report-service
echo "📍 Test 3: Vérifier matplotlib installé..."
if /Applications/Docker.app/Contents/Resources/bin/docker compose exec -T report-service pip show matplotlib >/dev/null 2>&1; then
    echo "   ✅ Matplotlib installé"
else
    echo "   ⚠️  Matplotlib non détecté (rebuild peut-être nécessaire)"
fi

echo ""
echo "========================================================================="
echo "✅ DÉPLOIEMENT TERMINÉ"
echo "========================================================================="
echo ""
echo "📊 NOUVELLES FONCTIONNALITÉS ACTIVÉES:"
echo ""
echo "1️⃣  CITATIONS APA:"
echo "   - Format: (Auteur, Année) ou (Organisation, Année)"
echo "   - Exemple: 'Le marché croît de 15% (INSEE, 2024)'"
echo "   - Remplacement complet des [1], [2], [3]"
echo ""
echo "2️⃣  GRAPHIQUES AUTOMATIQUES:"
echo "   - 2-4 graphiques par rapport"
echo "   - Types: bar (barres), line (courbes), pie (camemberts)"
echo "   - Génération automatique dans les PDF"
echo "   - Sources APA sur chaque graphique"
echo ""
echo "📚 SECTION 'Références Bibliographiques' au lieu de 'Sources'"
echo ""
echo "========================================================================="
echo "🧪 TESTER LES FONCTIONNALITÉS:"
echo "========================================================================="
echo ""
echo "1️⃣  TEST GÉNÉRATION RAPPORT AVEC GRAPHIQUES:"
echo "   cd /Users/isaiaebongue/insight-mvp"
echo "   curl -X POST http://localhost:8006/extended-analysis \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"business_type\": \"finance_banque\","
echo "          \"analysis_type\": \"synthese_executive\","
echo "          \"query\": \"Analyse du marché bancaire français 2025\"}' | jq"
echo ""
echo "2️⃣  TEST EXPORT PDF AVEC GRAPHIQUES:"
echo "   - Ouvrir OpenWebUI: http://localhost:3000"
echo "   - Générer un rapport détaillé"
echo "   - Cliquer sur 'Exporter en PDF'"
echo "   - Vérifier: citations APA + graphiques intégrés"
echo ""
echo "3️⃣  MONITORING LOGS:"
echo "   # Voir les logs backend (génération graphiques)"
echo "   docker-compose logs -f backend-service | grep -E 'chart|graphique|APA'"
echo ""
echo "   # Voir les logs report-service (intégration PDF)"
echo "   docker-compose logs -f report-service | grep -E 'chart|matplotlib|Inserted'"
echo ""
echo "========================================================================="
echo "📖 DOCUMENTATION COMPLÈTE:"
echo "   - README_CHARTS_APA.md"
echo "   - AMELIORATIONS_V4_FINAL.md"
echo "========================================================================="
echo ""

