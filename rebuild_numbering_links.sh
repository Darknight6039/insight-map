#!/bin/bash

# ========================================================================
# 🚀 SCRIPT DE DÉPLOIEMENT - NUMÉROTATION + LIENS HYPERTEXTES + STYLE
# ========================================================================
# Ce script rebuild et redémarre les services avec :
# - Numérotation hiérarchique automatique (1, 1.1, 1.2, etc.)
# - Liens hypertextes cliquables dans les sources PDF
# - Instructions de style rédactionnel fluide et clair
# - Filigrane légèrement plus visible (opacité 8%)
# ========================================================================

set -e  # Arrêter en cas d'erreur

echo ""
echo "========================================================================="
echo "🚀 DÉPLOIEMENT - NUMÉROTATION + LIENS + STYLE"
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
# ÉTAPE 2: REBUILD BACKEND-SERVICE
# ========================================================================
echo "🔨 ÉTAPE 2/5 - Rebuild backend-service..."
echo "---------------------------------------------------------------"
echo "   - Numérotation hiérarchique dans tous les prompts"
echo "   - Instructions de style rédactionnel fluide"
echo "   - Format: ## 1. Titre, ### 1.1 Sous-titre, #### 1.1.1"
/Applications/Docker.app/Contents/Resources/bin/docker compose build --no-cache backend-service
echo "✅ Backend-service rebuilt"
echo ""

# ========================================================================
# ÉTAPE 3: REBUILD REPORT-SERVICE
# ========================================================================
echo "🔨 ÉTAPE 3/5 - Rebuild report-service..."
echo "---------------------------------------------------------------"
echo "   - Extraction URLs des sources APA"
echo "   - Liens hypertextes cliquables (bleus, soulignés)"
echo "   - Préservation numérotation dans PDF"
echo "   - Filigrane légèrement plus visible (8% opacité)"
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
if curl -s http://localhost:8004/health | grep -q "ok"; then
    echo "   ✅ Report-service opérationnel"
else
    echo "   ❌ Report-service non disponible"
fi

echo ""
echo "========================================================================="
echo "✅ DÉPLOIEMENT TERMINÉ"
echo "========================================================================="
echo ""
echo "📊 NOUVELLES FONCTIONNALITÉS ACTIVÉES:"
echo ""
echo "1️⃣  NUMÉROTATION HIÉRARCHIQUE:"
echo "   - Tous les titres numérotés automatiquement"
echo "   - Format: 1, 1.1, 1.2, 2, 2.1, 2.1.1, etc."
echo "   - Facilite navigation et références croisées"
echo ""
echo "2️⃣  LIENS HYPERTEXTES:"
echo "   - URLs cliquables dans 'Références Bibliographiques'"
echo "   - Format: texte source + URL en bleu souligné"
echo "   - Clic ouvre le lien dans le navigateur"
echo ""
echo "3️⃣  STYLE RÉDACTIONNEL:"
echo "   - Phrases courtes et claires (15-20 mots max)"
echo "   - Transitions naturelles, vocabulaire accessible"
echo "   - Style fluide et agréable à lire"
echo ""
echo "4️⃣  FILIGRANE:"
echo "   - Opacité réduite à 8% (plus visible)"
echo "   - Couvre toute la page sans gêner la lecture"
echo ""
echo "========================================================================="
echo "🧪 TESTER LES FONCTIONNALITÉS:"
echo "========================================================================="
echo ""
echo "1️⃣  TEST GÉNÉRATION RAPPORT AVEC NUMÉROTATION:"
echo "   curl -X POST http://localhost:8006/extended-analysis \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"business_type\": \"finance_banque\","
echo "          \"analysis_type\": \"synthese_executive\","
echo "          \"query\": \"Analyse marché bancaire français\"}' | jq '.content' | head -80"
echo ""
echo "   Vérifier: ## 1. Executive Summary, ### 1.1 Synthèse, ## 2. Analyse..."
echo ""
echo "2️⃣  TEST EXPORT PDF AVEC LIENS:"
echo "   - Ouvrir OpenWebUI: http://localhost:3000"
echo "   - Générer un rapport détaillé"
echo "   - Cliquer sur 'Exporter en PDF'"
echo "   - Vérifier dans le PDF:"
echo "     • Titres numérotés: 1. Titre, 1.1 Sous-titre"
echo "     • URLs cliquables dans Références Bibliographiques"
echo "     • Style fluide et phrases claires"
echo "     • Filigrane visible mais discret"
echo ""
echo "3️⃣  MONITORING LOGS:"
echo "   # Backend (numérotation prompts)"
echo "   docker-compose logs -f backend-service | grep -E 'Processing header|numérot'"
echo ""
echo "   # Report (liens + numérotation PDF)"
echo "   docker-compose logs -f report-service | grep -E 'Processing header|extract.*url'"
echo ""
echo "========================================================================="
echo "📖 DOCUMENTATION:"
echo "   - README_CHARTS_APA.md (mis à jour)"
echo "   - PLAN: multi-model-so.plan.md"
echo "========================================================================="
echo ""

