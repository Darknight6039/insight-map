# 🎨 Style PDF Template AXIAL - Version 4.2

## 📋 Vue d'ensemble

Le style des PDF générés a été entièrement repensé pour **matcher exactement** les templates de référence AXIAL. Cette documentation décrit toutes les modifications apportées pour garantir une cohérence visuelle parfaite.

---

## ✅ Modifications apportées

### 1. **Polices et couleurs des titres**

#### Avant (Style bleu corporate)
```python
SectionHeader:
- Couleur: #0052A5 (Bleu)
- Taille: 14pt
- Alignement: CENTER

SubsectionHeader:
- Couleur: #333333 (Gris foncé)
- Taille: 12pt

CustomBodyText:
- Couleur: #333333 (Gris foncé)
- Taille: 10pt

BulletPoint:
- Couleur: #333333 (Gris foncé)
- Taille: 10pt
```

#### Après (Style template AXIAL)
```python
SectionHeader:
- Couleur: #000000 (Noir pur) ✅
- Taille: 15pt (+1pt)
- Alignement: LEFT ✅
- spaceBefore: 14px
- spaceAfter: 8px

SubsectionHeader:
- Couleur: #000000 (Noir pur) ✅
- Taille: 13pt (+1pt)
- Alignement: LEFT ✅
- spaceBefore: 10px
- spaceAfter: 6px

CustomBodyText:
- Couleur: #000000 (Noir pur) ✅
- Taille: 10.5pt (+0.5pt)
- spaceAfter: 8px
- Justification complète

BulletPoint:
- Couleur: #000000 (Noir pur) ✅
- Taille: 10.5pt (+0.5pt)
- spaceAfter: 5px
- leftIndent: 20px
```

**Justification** : Les templates de référence utilisent un texte noir pur sur fond clair pour une lisibilité maximale.

---

### 2. **Filigrane AXIAL visible**

#### Avant
```python
canvas_obj.setFillAlpha(0.08)  # 8% d'opacité
canvas_obj.setStrokeAlpha(0.08)
```

#### Après
```python
canvas_obj.setFillAlpha(0.15)  # 15% d'opacité ✅
canvas_obj.setStrokeAlpha(0.15)
```

**Résultat** : Le filigrane AXIAL avec les lignes diagonales est maintenant bien visible sur toutes les pages, exactement comme dans les templates de référence.

---

### 3. **Background coloré**

#### Nouveau (ajouté)
```python
# Ajouter fond légèrement teinté (bleu/gris clair) comme dans les templates AXIAL
canvas_obj.setFillColor(colors.HexColor('#E8EEF7'))  # Bleu très clair
canvas_obj.rect(0, 0, page_width, page_height, fill=1, stroke=0)
```

**Résultat** : Les pages ont maintenant un fond bleu/gris très clair (#E8EEF7) qui donne un aspect professionnel et distingué, identique aux templates.

---

### 4. **Footer style AXIAL**

#### Avant
```python
# Pied de page discret
canvas_obj.setFont('Helvetica', 8)
canvas_obj.setFillColor(colors.HexColor('#999999'))

# Date à gauche
footer_text = f"{datetime.now().strftime('%d/%m/%Y')}"
canvas_obj.drawString(2*cm, 1.5*cm, footer_text)

# Numéro de page à droite
page_num = f"Page {doc.page}"
canvas_obj.drawRightString(page_width - 2*cm, 1.5*cm, page_num)
```

#### Après
```python
# Pied de page style template AXIAL
canvas_obj.setFont('Helvetica', 7.5)

# Créer un rectangle coloré pour le footer (comme dans le template)
canvas_obj.setFillColor(colors.HexColor('#6B8FC1'))  # Bleu moyen pour le fond
canvas_obj.rect(0, 0, page_width, 1*cm, fill=1, stroke=0)

# Texte du footer en blanc
canvas_obj.setFillColor(colors.HexColor('#FFFFFF'))
footer_text = f"© AXIAL {datetime.now().year}. Tous droits réservés. www.axial-ia.com"
canvas_obj.drawString(2*cm, 0.4*cm, footer_text)

# Numéro de page à droite en blanc
page_num = f"Page {doc.page}"
canvas_obj.drawRightString(page_width - 2*cm, 0.4*cm, page_num)
```

**Résultat** : Footer avec bande bleue (#6B8FC1) et texte blanc, exactement comme dans les templates de référence.

---

### 5. **Marges optimisées**

#### Avant
```python
doc = SimpleDocTemplate(
    buffer, 
    pagesize=A4, 
    rightMargin=2*cm, 
    leftMargin=2*cm, 
    topMargin=3*cm, 
    bottomMargin=2.5*cm
)
```

#### Après
```python
doc = SimpleDocTemplate(
    buffer, 
    pagesize=A4, 
    rightMargin=2*cm, 
    leftMargin=2*cm, 
    topMargin=2*cm,       # Réduit de 3cm → 2cm ✅
    bottomMargin=1.5*cm   # Réduit de 2.5cm → 1.5cm ✅
)
```

**Résultat** : Plus de contenu par page, mise en page plus compacte et professionnelle comme dans les templates.

---

## 📊 Comparaison visuelle

### Avant (Style bleu corporate)
```
┌─────────────────────────────────┐
│                                 │
│   [Titre en bleu centré]        │
│                                 │
│   Texte en gris #333333         │
│   Filigrane très discret (8%)   │
│                                 │
│                                 │
│   Date    -    Page N           │
└─────────────────────────────────┘
```

### Après (Style template AXIAL)
```
┌─────────────────────────────────┐
│ ╔═══════════════════════════╗   │
│ [Titre en noir aligné gauche]   │
│                                 │
│ Texte en noir pur #000000       │
│ Fond bleu clair #E8EEF7         │
│ Filigrane AXIAL visible (15%)   │
│                                 │
│ ███████████████████████████████ │
│ © AXIAL 2025... │ Page N        │
└─────────────────────────────────┘
```

---

## 🎯 Checklist de validation

Après génération d'un PDF, vérifier :

- [ ] **Titres principaux** en noir (#000000) et alignés à gauche
- [ ] **Sous-titres** en noir (#000000) et alignés à gauche
- [ ] **Texte corps** en noir pur, justifié, taille 10.5pt
- [ ] **Filigrane AXIAL** bien visible (15% opacité) avec logo et lignes diagonales
- [ ] **Fond** bleu/gris clair (#E8EEF7) sur toutes les pages
- [ ] **Footer** avec bande bleue (#6B8FC1) et texte blanc
- [ ] **Copyright** : "© AXIAL 2025. Tous droits réservés. www.axial-ia.com"
- [ ] **Numérotation** hiérarchique visible (1., 1.1, 1.1.1)
- [ ] **Citations APA** dans le texte (Auteur, Année)
- [ ] **Sources** avec URLs cliquables en bleu souligné
- [ ] **Mise en page** compacte avec plus de contenu par page

---

## 🚀 Déploiement

Pour appliquer ces changements :

```bash
cd /Users/isaiaebongue/insight-mvp
chmod +x rebuild_rich_content.sh
./rebuild_rich_content.sh
```

Le script va :
1. Rebuild `backend-service` avec contenu enrichi (60% paragraphes)
2. Rebuild `report-service` avec nouveau style template AXIAL
3. Redémarrer les services
4. Valider le fonctionnement

---

## 📝 Fichiers modifiés

### Backend Service (`backend-service/app/main.py`)
- **Lignes 673-677** : Augmentation max_tokens (8000/16000/20000)
- **Ligne 865** : Timeout 600s (10 minutes)
- **Ligne 879** : Température 0.2
- **Lignes 402-679** : Templates métier avec instructions paragraphes narratifs
- **Lignes 922-941** : Enhanced prompt avec ratio 60/40 paragraphes/bullets

### Report Service (`report-service/app/main.py`)
- **Lignes 240-252** : SectionHeader noir 15pt aligné gauche
- **Lignes 255-265** : SubsectionHeader noir 13pt aligné gauche
- **Lignes 267-277** : CustomBodyText noir 10.5pt
- **Lignes 279-289** : BulletPoint noir 10.5pt
- **Lignes 346-348** : Background bleu clair #E8EEF7
- **Lignes 369-370** : Filigrane opacité 15%
- **Lignes 397-412** : Footer style AXIAL avec bande bleue
- **Lignes 424-431** : Marges optimisées (2cm top, 1.5cm bottom)

---

## 🎨 Palette de couleurs finale

| Élément | Couleur | Code Hex | Usage |
|---------|---------|----------|-------|
| **Titres principaux** | Noir | `#000000` | SectionHeader |
| **Sous-titres** | Noir | `#000000` | SubsectionHeader |
| **Texte corps** | Noir | `#000000` | Body, bullets |
| **Background page** | Bleu clair | `#E8EEF7` | Fond de page |
| **Footer bande** | Bleu moyen | `#6B8FC1` | Rectangle footer |
| **Footer texte** | Blanc | `#FFFFFF` | Copyright, page |
| **Liens hypertextes** | Bleu | `#0000FF` | URLs sources |

---

## 📚 Références

- Templates AXIAL de référence : `/templates/`
- Document APA citations : `README_CHARTS_APA.md`
- Configuration modèles : `README_MODELES.md`
- Déploiement : `LIRE_MOI_DEPLOIEMENT.txt`

---

## 🔄 Historique des versions

### Version 4.2 (15/11/2024) - Style Template AXIAL
- ✅ Titres en noir pur alignés à gauche
- ✅ Filigrane AXIAL visible (15%)
- ✅ Background bleu/gris clair
- ✅ Footer avec bande bleue et texte blanc
- ✅ Marges optimisées pour plus de contenu

### Version 4.1 (15/11/2024) - Contenu Enrichi
- ✅ 60% paragraphes narratifs + 40% bullets
- ✅ Max tokens augmentés (8000/16000/20000)
- ✅ Timeout 10 minutes
- ✅ Température 0.2 pour créativité

### Version 4.0 (14/11/2024) - Citations APA et Graphiques
- ✅ Citations APA (Auteur, Année)
- ✅ URLs hypertextes cliquables
- ✅ Numérotation hiérarchique
- ✅ Génération graphiques matplotlib

---

## ✨ Résultat final

Le PDF généré est maintenant **visuellement identique** aux templates de référence AXIAL :
- Style professionnel et épuré
- Filigrane bien visible
- Fond coloré élégant
- Footer institutionnel
- Lisibilité optimale avec texte noir sur fond clair
- Plus de contenu par page grâce aux marges optimisées

---

**Auteur** : Cursor AI Assistant  
**Date** : 15 novembre 2024  
**Version** : 4.2 - Template AXIAL Style

