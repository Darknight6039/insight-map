#!/bin/bash
# Script pour exporter le cahier des charges en PDF sur macOS

echo "📄 Export Cahier des Charges en PDF"
echo "===================================="
echo ""

# Méthode 1: Via TextEdit + Print to PDF (GUI)
echo "MÉTHODE MANUELLE (Recommandée pour meilleur rendu):"
echo "1. Ouvrir le fichier:"
echo "   open CAHIER_DES_CHARGES.txt"
echo ""
echo "2. Dans TextEdit: Fichier > Exporter au format PDF..."
echo "   Ou: Fichier > Imprimer > PDF > Enregistrer comme PDF"
echo ""
echo "3. Nom suggéré: CDC_Axial_Intelligence_v2.1.pdf"
echo ""

# Méthode 2: Via cupsfilter (ligne de commande - basique)
echo "MÉTHODE AUTOMATIQUE (Rendu simple):"
if command -v cupsfilter &> /dev/null; then
    echo "Génération PDF automatique..."
    cupsfilter CAHIER_DES_CHARGES.txt > CDC_Axial_Intelligence_v2.1.pdf 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ PDF créé: CDC_Axial_Intelligence_v2.1.pdf"
        echo "📍 Emplacement: $(pwd)/CDC_Axial_Intelligence_v2.1.pdf"
        open -R CDC_Axial_Intelligence_v2.1.pdf
    else
        echo "⚠️  Échec génération automatique. Utilisez la méthode manuelle."
    fi
else
    echo "⚠️  cupsfilter non disponible. Utilisez la méthode manuelle."
fi

echo ""
echo "=================================================="
echo "Pour partage prestataires, utilisez le PDF avec:"
echo "  - Page de garde professionnelle"
echo "  - Table des matières cliquable"
echo "  - Numérotation pages"
echo "=================================================="

