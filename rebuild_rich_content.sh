#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════
# 🚀 SCRIPT DE DÉPLOIEMENT - CONTENU ENRICHI AVEC PARAGRAPHES NARRATIFS
# ═══════════════════════════════════════════════════════════════════════════
# Version: 4.1 - Rich Narrative Content
# Date: 2024-11-15
# Auteur: Cursor AI Assistant
#
# OBJECTIFS:
# - Implémenter contenu 60% paragraphes narratifs + 40% bullet points
# - Augmenter max_tokens: sonar 8000, sonar-pro 16000, sonar-reasoning 20000
# - Augmenter timeout API à 600s (10 minutes)
# - Augmenter température à 0.2 pour créativité
# - Aligner tous les titres PDF à gauche (plus centrés)
# ═══════════════════════════════════════════════════════════════════════════

set -e  # Arrêt en cas d'erreur

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'affichage
print_step() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}▶ $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Vérifications préliminaires
print_step "1. VÉRIFICATIONS PRÉLIMINAIRES"

if ! command -v docker &> /dev/null; then
    print_error "Docker n'est pas installé ou non accessible"
    exit 1
fi
print_success "Docker disponible"

if ! docker compose version &> /dev/null; then
    print_error "Docker Compose n'est pas disponible"
    exit 1
fi
print_success "Docker Compose disponible"

# Vérifier que les fichiers modifiés existent
if [ ! -f "backend-service/app/main.py" ]; then
    print_error "backend-service/app/main.py introuvable"
    exit 1
fi
print_success "backend-service/app/main.py présent"

if [ ! -f "report-service/app/main.py" ]; then
    print_error "report-service/app/main.py introuvable"
    exit 1
fi
print_success "report-service/app/main.py présent"

# ═══════════════════════════════════════════════════════════════════════════
# ÉTAPE 1: ARRÊT DES SERVICES ACTUELS
# ═══════════════════════════════════════════════════════════════════════════

print_step "2. ARRÊT DES SERVICES ACTUELS"

docker compose stop backend-service report-service 2>/dev/null || true
print_success "Services arrêtés"

# ═══════════════════════════════════════════════════════════════════════════
# ÉTAPE 2: REBUILD DES IMAGES
# ═══════════════════════════════════════════════════════════════════════════

print_step "3. REBUILD DES IMAGES DOCKER"

echo "🔨 Build backend-service..."
if docker compose build --no-cache backend-service; then
    print_success "Backend service rebuild réussi"
else
    print_error "Échec du build backend-service"
    exit 1
fi

echo "🔨 Build report-service..."
if docker compose build --no-cache report-service; then
    print_success "Report service rebuild réussi"
else
    print_error "Échec du build report-service"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════════════
# ÉTAPE 3: REDÉMARRAGE DES SERVICES
# ═══════════════════════════════════════════════════════════════════════════

print_step "4. REDÉMARRAGE DES SERVICES"

if docker compose up -d backend-service report-service; then
    print_success "Services redémarrés"
else
    print_error "Échec du redémarrage"
    exit 1
fi

# Attendre que les services soient prêts
print_warning "Attente du démarrage des services (30s)..."
sleep 30

# ═══════════════════════════════════════════════════════════════════════════
# ÉTAPE 4: TESTS DE VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

print_step "5. TESTS DE VALIDATION"

# Test 1: Health check backend
echo "🔍 Test health backend-service..."
if curl -s http://localhost:8006/health | grep -q "healthy"; then
    print_success "Backend service opérationnel"
    
    # Vérifier version
    VERSION=$(curl -s http://localhost:8006/health | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    echo "   Version: $VERSION"
    
    # Vérifier configuration multi-modèles
    if curl -s http://localhost:8006/health | grep -q "perplexity_models"; then
        print_success "Configuration multi-modèles détectée"
    fi
else
    print_error "Backend service non opérationnel"
    echo "Logs backend:"
    docker compose logs --tail=50 backend-service
    exit 1
fi

# Test 2: Health check report service
echo "🔍 Test health report-service..."
if curl -s http://localhost:8007/health | grep -q "healthy"; then
    print_success "Report service opérationnel"
else
    print_error "Report service non opérationnel"
    echo "Logs report:"
    docker compose logs --tail=50 report-service
    exit 1
fi

# Test 3: Test modèles Perplexity
echo "🔍 Test configuration modèles Perplexity..."
if curl -s http://localhost:8006/test-perplexity | grep -q "success"; then
    print_success "Configuration Perplexity validée"
    
    # Afficher les modèles configurés
    echo "   Modèles:"
    curl -s http://localhost:8006/test-perplexity | grep -o '"[^"]*":"[^"]*"' | head -6
else
    print_warning "Configuration Perplexity à vérifier (peut être normal si clé API non configurée)"
fi

# ═══════════════════════════════════════════════════════════════════════════
# ÉTAPE 5: VÉRIFICATION DES LOGS
# ═══════════════════════════════════════════════════════════════════════════

print_step "6. VÉRIFICATION DES LOGS"

echo "📋 Derniers logs backend (recherche 'max_tokens'):"
docker compose logs backend-service | grep -i "max_tokens" | tail -5 || echo "   (Aucun log max_tokens trouvé pour le moment)"

echo ""
echo "📋 Derniers logs backend (recherche 'temperature'):"
docker compose logs backend-service | grep -i "temperature" | tail -5 || echo "   (Aucun log temperature trouvé pour le moment)"

echo ""
echo "📋 Derniers logs backend (recherche 'timeout'):"
docker compose logs backend-service | grep -i "timeout" | tail -5 || echo "   (Aucun log timeout trouvé pour le moment)"

# ═══════════════════════════════════════════════════════════════════════════
# RÉSUMÉ DES MODIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════

print_step "7. RÉSUMÉ DES MODIFICATIONS V4.1"

cat << 'EOF'
┌────────────────────────────────────────────────────────────────────┐
│ ✅ BACKEND SERVICE - CONTENU ENRICHI                                │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ 1. MAX TOKENS AUGMENTÉS:                                            │
│    • sonar: 6000 → 8000 (+33%, chat enrichi)                        │
│    • sonar-pro: 12000 → 16000 (+33%, rapports détaillés)            │
│    • sonar-reasoning: 16000 → 20000 (+25%, analyses profondes)      │
│                                                                      │
│ 2. TIMEOUT API AUGMENTÉ:                                            │
│    • 450s → 600s (7.5 min → 10 min)                                 │
│    • Permet génération rapports longs avec paragraphes              │
│                                                                      │
│ 3. TEMPÉRATURE AUGMENTÉE:                                           │
│    • 0.1 → 0.2 (+100%)                                               │
│    • Plus de créativité pour paragraphes narratifs fluides          │
│                                                                      │
│ 4. INSTRUCTIONS PARAGRAPHES NARRATIFS:                              │
│    • 60% paragraphes narratifs + 40% bullet points                  │
│    • Structure: intro → développements → données → conclusion       │
│    • 3 templates métier enrichis avec exemples détaillés            │
│    • Enhanced prompt complété avec règles paragraphes               │
│                                                                      │
├────────────────────────────────────────────────────────────────────┤
│ ✅ REPORT SERVICE - STYLE TEMPLATE AXIAL                            │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ 1. POLICES ET COULEURS (COMME TEMPLATE):                            │
│    • SectionHeader: Bleu → Noir (#000000), taille 14 → 15pt        │
│    • SubsectionHeader: Gris → Noir, taille 12 → 13pt               │
│    • CustomBodyText: Gris → Noir, taille 10 → 10.5pt               │
│    • BulletPoint: Gris → Noir, taille 10 → 10.5pt                  │
│    • Tous alignés à gauche (sauf titre de couverture)               │
│                                                                      │
│ 2. FILIGRANE VISIBLE:                                               │
│    • Opacité: 8% → 15% (comme template AXIAL)                       │
│    • Couvre toute la page avec lignes diagonales                    │
│                                                                      │
│ 3. BACKGROUND COLORÉ:                                               │
│    • Fond bleu/gris clair (#E8EEF7)                                 │
│    • Comme dans les templates professionnels                        │
│                                                                      │
│ 4. FOOTER STYLE AXIAL:                                              │
│    • Bande bleue (#6B8FC1) en bas de page                           │
│    • Texte blanc: "© AXIAL 2025. Tous droits réservés..."          │
│    • Numéro de page à droite en blanc                               │
│                                                                      │
│ 5. MARGES OPTIMISÉES:                                               │
│    • topMargin: 3cm → 2cm (plus compact)                            │
│    • bottomMargin: 2.5cm → 1.5cm (pour footer)                      │
│    • Plus de contenu par page comme dans le template                │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘

📊 IMPACT ATTENDU:

   • Contenu plus riche et détaillé (60% narratif)
   • Style professionnel mais fluide et agréable à lire
   • Développements approfondis avec exemples concrets
   • Données chiffrées synthétisées en bullet points
   • Temps génération: +20-30% (acceptable pour qualité)
   • PDF plus lisible avec titres alignés à gauche

🔍 VALIDATION MANUELLE RECOMMANDÉE:

   1. Générer un rapport via OpenWebUI:
      → Vérifier présence paragraphes narratifs (60%)
      → Vérifier style fluide et transitions
      → Vérifier développements approfondis

   2. Exporter en PDF:
      → Vérifier titres en NOIR (pas bleu) et alignés à gauche
      → Vérifier mix paragraphes + bullets (60/40)
      → Vérifier filigrane AXIAL visible (15% opacité)
      → Vérifier fond bleu/gris clair
      → Vérifier footer avec bande bleue et texte blanc
      → Vérifier style correspond exactement aux templates

   3. Comparer avec templates de référence:
      → Couleurs identiques (noir sur fond clair) ?
      → Filigrane aussi visible ?
      → Footer identique avec bande bleue ?
      → Densité de contenu similaire ?
      → Style professionnel cohérent ?

EOF

print_success "Déploiement V4.1 terminé avec succès!"

# ═══════════════════════════════════════════════════════════════════════════
# COMMANDES UTILES
# ═══════════════════════════════════════════════════════════════════════════

print_step "8. COMMANDES UTILES"

cat << 'EOF'
📋 Surveillance des logs en temps réel:

# Tous les services
docker compose logs -f backend-service report-service

# Backend uniquement (rechercher max_tokens)
docker compose logs -f backend-service | grep "max_tokens"

# Voir les appels API avec modèles utilisés
docker compose logs -f backend-service | grep "Using model"

📊 Tests API manuels:

# Test génération rapport (vérifier temps de réponse)
curl -X POST http://localhost:8006/extended-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "finance_banque",
    "analysis_type": "synthese_executive",
    "query": "Analyse du marché bancaire français 2025"
  }' | jq '.content' | head -100

# Test chat (vérifier style narratif)
curl -X POST http://localhost:8006/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quelles sont les tendances fintech 2025?",
    "business_type": "finance_banque"
  }' | jq '.response' | head -50

🔄 Redémarrage rapide si besoin:

docker compose restart backend-service report-service

⚙️ Rebuild complet si problème:

docker compose down
docker compose build --no-cache backend-service report-service
docker compose up -d

EOF

print_success "Script terminé!"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Votre application est prête avec contenu enrichi ! 🎉${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""

