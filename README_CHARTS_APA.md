# 📊 Documentation - Citations APA + Graphiques Automatiques

## 🎯 Vue d'ensemble

Cette mise à jour majeure introduit deux améliorations fondamentales pour la qualité des rapports :

1. **Citations en format APA** : Remplacement complet des citations numériques `[1], [2], [3]` par le format académique standard `(Auteur, Année)`
2. **Graphiques automatiques** : Génération et intégration automatique de 2-4 graphiques professionnels dans chaque rapport

---

## 📝 1. CITATIONS AU FORMAT APA

### Avant (format numérique)
```
Le marché bancaire français représente 450 milliards d'euros [1] avec une croissance 
de 3,2% en 2024 [2]. La digitalisation s'accélère [3][4].

## 📚 Sources
[1] INSEE. (2024). Panorama économique français...
[2] Banque de France. (2024). Situation économique...
```

### Après (format APA)
```
Le marché bancaire français représente 450 milliards d'euros (INSEE, 2024) avec une 
croissance de 3,2% en 2024 (Banque de France, 2024). La digitalisation s'accélère 
(McKinsey, 2024; BCG, 2024).

## 📚 Références Bibliographiques
INSEE. (2024). Panorama économique français Q3 2024. Rapport trimestriel. https://...
Banque de France. (2024). Situation économique France. Bulletin mensuel. https://...
```

### Avantages
- ✅ **Lisibilité accrue** : Les citations sont intégrées naturellement dans le texte
- ✅ **Standard académique** : Conforme aux normes APA 7ème édition
- ✅ **Croisement visible** : `(Source1, 2024; Source2, 2024)` pour données croisées
- ✅ **Export PDF optimisé** : Les citations APA sont automatiquement converties dans le PDF

---

## 📊 2. GRAPHIQUES AUTOMATIQUES

### Format Markdown pour les Graphiques

Les rapports peuvent maintenant inclure des graphiques via un format markdown spécial :

```markdown
```chart
type: bar
title: Évolution du marché bancaire français 2020-2024
data: {labels: ["2020", "2021", "2022", "2023", "2024"], values: [420, 430, 440, 445, 450]}
source: (INSEE, 2024)
```
```

### Types de Graphiques Supportés

| Type | Usage | Exemple |
|------|-------|---------|
| `bar` | Comparaisons entre catégories, parts de marché | Parts de marché par acteur |
| `line` | Évolutions temporelles, tendances | Croissance sur 5 ans |
| `pie` | Répartitions, pourcentages | Distribution géographique |

### Exemple Complet

```markdown
## 📈 Analyse Sectorielle

Le marché bancaire français connaît une croissance soutenue (Banque de France, 2024).

```chart
type: line
title: Croissance du secteur bancaire 2020-2024 (en Mds€)
data: {labels: ["2020", "2021", "2022", "2023", "2024"], values: [420, 430, 440, 445, 450]}
source: (Banque de France, 2024)
```

La digitalisation s'accélère avec 78% des transactions en ligne (ACPR, 2024).

```chart
type: pie
title: Répartition des canaux bancaires 2024
data: {labels: ["Mobile", "Web", "Agence", "Téléphone"], values: [45, 33, 18, 4]}
source: (ACPR, 2024)
```
```

### Génération Automatique

Le `report-service` :
1. **Parse** automatiquement les blocs ````chart```
2. **Génère** des images PNG haute résolution (150 DPI)
3. **Intègre** les graphiques dans le PDF après chaque section
4. **Style** professionnel avec couleurs corporate (#0052A5)

### Style des Graphiques

- **Dimensions** : 10x6 inches (25x15 cm dans le PDF)
- **Couleur principale** : Bleu corporate (#0052A5)
- **Police** : Helvetica, tailles adaptées (14pt titre, 10pt axes)
- **Source** : Citation APA en bas à droite (8pt, italique)
- **Résolution** : 150 DPI pour qualité print

---

## 🔧 3. IMPLÉMENTATION TECHNIQUE

### Backend Service (`backend-service/app/main.py`)

#### Modifications des Prompts

Tous les prompts ont été modifiés pour :
- Demander des citations APA au lieu de numériques
- Exiger 2-4 graphiques pertinents
- Fournir le format markdown exact pour les graphiques

```python
# Exemple de prompt modifié
✓ CITE SYSTÉMATIQUEMENT en format APA: (Auteur, Année) ou (Organisation, Année)
✓ Pour données chiffrées : citer 2 sources si possible (Source1, 2024; Source2, 2024)
✓ Exemple: "Le secteur croît de 12% selon l'INSEE (INSEE, 2024) et 11,5% selon 
  la Banque de France (Banque de France, 2024)"
✓ En fin : "## 📚 Références Bibliographiques" avec format APA complet + URLs

✅ GRAPHIQUES ET VISUALISATIONS :
- Inclure 2-4 graphiques pertinents pour illustrer les données clés
- Format markdown pour graphiques:
```chart
type: bar|line|pie
title: Titre du graphique
data: {{labels: ["Label1", "Label2"], values: [valeur1, valeur2]}}
source: (Auteur, Année)
```
```

#### System Prompts Enrichis

Les system prompts pour `finance_banque`, `tech_digital` et `retail_commerce` incluent maintenant :
- Instructions explicites pour citations APA
- Exemples de croisement de sources avec format APA
- Hiérarchie des sources maintenue (60/20/15/5%)

### Report Service (`report-service/app/main.py`)

#### Nouvelles Fonctions

```python
def parse_chart_blocks(content: str) -> List[Dict]:
    """Parse les blocs ```chart``` dans le contenu markdown"""
    # Utilise regex pour extraire type, title, data, source
    # Retourne liste de dictionnaires avec données des graphiques
    
def generate_chart_image(chart_data: Dict) -> Optional[BytesIO]:
    """Génère une image PNG à partir des données de graphique"""
    # Utilise matplotlib pour créer bar/line/pie chart
    # Style professionnel avec couleurs corporate
    # Retourne BytesIO contenant l'image PNG
    
def remove_chart_blocks(content: str) -> str:
    """Retire les blocs ```chart``` du contenu après parsing"""
    # Nettoie le markdown pour éviter les blocs vides dans le PDF
```

#### Intégration dans `create_professional_pdf`

```python
# 1. Parser et générer les graphiques
charts = parse_chart_blocks(content)
chart_images = {}
for chart_data in charts:
    chart_img = generate_chart_image(chart_data)
    if chart_img:
        chart_images[chart_data['index']] = chart_img

# 2. Retirer les blocs chart du contenu
content_without_charts = remove_chart_blocks(content)

# 3. Passer les images à la fonction de rendu
sources_from_content = self._add_content_sections(
    story, content_without_charts, citations_map, chart_images
)
```

#### Insertion dans PDF

Les graphiques sont insérés automatiquement après chaque section de niveau 2 (`##`) :

```python
# Dans _add_content_sections
if chart_counter in chart_images:
    img = Image(chart_images[chart_counter], width=15*cm, height=9*cm)
    story.append(Spacer(1, 0.3*cm))
    story.append(img)
    story.append(Spacer(1, 0.3*cm))
    chart_counter += 1
```

### Dépendances

#### `report-service/requirements.txt`
```txt
matplotlib==3.9.2  # Nouvelle dépendance pour génération graphiques
```

---

## 🚀 4. DÉPLOIEMENT

### Script de Déploiement Automatique

```bash
chmod +x rebuild_charts_apa.sh
./rebuild_charts_apa.sh
```

Le script effectue :
1. ✅ Arrêt des services `backend-service` et `report-service`
2. ✅ Rebuild complet avec `--no-cache`
3. ✅ Redémarrage des services
4. ✅ Tests de validation (health checks, matplotlib)
5. ✅ Affichage des commandes de test

### Déploiement Manuel

```bash
# 1. Rebuild backend (citations APA)
docker compose build --no-cache backend-service
docker compose up -d backend-service

# 2. Rebuild report-service (graphiques)
docker compose build --no-cache report-service
docker compose up -d report-service

# 3. Vérifier les logs
docker compose logs -f backend-service report-service
```

---

## 🧪 5. TESTS ET VALIDATION

### Test 1 : Génération Rapport avec Graphiques

```bash
curl -X POST http://localhost:8006/extended-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "finance_banque",
    "analysis_type": "synthese_executive",
    "query": "Analyse complète du secteur bancaire français avec évolution 2020-2024"
  }' | jq
```

**Vérifications** :
- ✅ Contenu contient `(INSEE, 2024)` et PAS `[1]`
- ✅ Section `## 📚 Références Bibliographiques` présente
- ✅ Blocs ````chart` présents dans le markdown
- ✅ Au moins 2-4 graphiques générés

### Test 2 : Export PDF avec Graphiques

1. Ouvrir OpenWebUI : `http://localhost:3000`
2. Générer un rapport détaillé (Finance/Tech/Retail)
3. Cliquer sur "Exporter en PDF"
4. Ouvrir le PDF téléchargé

**Vérifications PDF** :
- ✅ Citations dans le texte : `(Auteur, 2024)`
- ✅ Graphiques intégrés (2-4 par rapport)
- ✅ Graphiques haute résolution et professionnels
- ✅ Sources APA sur chaque graphique
- ✅ Section "Références Bibliographiques" complète

### Test 3 : Monitoring Logs

```bash
# Logs backend (génération graphiques)
docker compose logs -f backend-service | grep -E "chart|graphique|APA"

# Logs report-service (intégration PDF)
docker compose logs -f report-service | grep -E "Chart|matplotlib|Inserted"
```

**Logs attendus** :
```
backend-service  | INFO: Using model: sonar-pro for task: analysis (max_tokens: 12000)
report-service   | INFO: Parsing chart blocks...
report-service   | INFO: Chart parsed: Évolution du marché bancaire
report-service   | INFO: Chart generated: Évolution du marché bancaire
report-service   | INFO: Generated 3 charts
report-service   | INFO: Inserted chart 1 after section: Analyse Sectorielle
report-service   | INFO: Inserted chart 2 after section: Analyse Concurrentielle
```

---

## 📈 6. EXEMPLES DE RAPPORTS

### Finance Banque

**Graphiques Typiques** :
1. **Line Chart** : Évolution du CA bancaire 2020-2024
2. **Bar Chart** : Parts de marché top 5 banques françaises
3. **Pie Chart** : Répartition activités (retail/corporate/investment)

### Tech Digital

**Graphiques Typiques** :
1. **Line Chart** : Adoption cloud computing 2020-2024
2. **Bar Chart** : Investissements IA par secteur
3. **Bar Chart** : Comparaison coûts cloud providers

### Retail Commerce

**Graphiques Typiques** :
1. **Line Chart** : Croissance e-commerce 2020-2024
2. **Pie Chart** : Répartition canaux vente (online/offline)
3. **Bar Chart** : CA par catégorie produit

---

## 🔍 7. TROUBLESHOOTING

### Problème : Graphiques non générés

**Symptôme** : Rapport sans graphiques dans le PDF

**Solutions** :
```bash
# 1. Vérifier matplotlib installé
docker compose exec report-service pip show matplotlib

# 2. Vérifier logs report-service
docker compose logs report-service | grep -i "error.*chart"

# 3. Rebuild avec --no-cache
docker compose build --no-cache report-service
docker compose up -d report-service
```

### Problème : Format chart non parsé

**Symptôme** : Blocs ```chart visibles dans le PDF

**Cause** : Format markdown incorrect

**Solution** : Vérifier le format exact :
```markdown
```chart
type: bar
title: Mon titre
data: {labels: ["A", "B"], values: [10, 20]}
source: (Auteur, 2024)
```
```

⚠️ **Attention** :
- Pas d'espace après `type:`, `title:`, etc.
- `data:` doit être un dict Python valide
- Guillemets doubles pour les strings

### Problème : Citations APA non converties

**Symptôme** : Citations `[1]` encore présentes

**Causes possibles** :
1. Backend service pas rebuildé
2. Cache Docker

**Solution** :
```bash
docker compose down
docker compose build --no-cache backend-service
docker compose up -d
```

---

## 📊 8. MÉTRIQUES ET QUALITÉ

### Sources par Rapport

| Type de Rapport | Sources Minimum | Sources avec Graphiques |
|----------------|-----------------|------------------------|
| Court (synthèse) | 40-60 | 40-60 + 2-4 graphiques |
| Approfondi | 40-60 | 40-60 + 2-4 graphiques |

### Répartition Sources (Inchangée)

- 60% Institutionnelles (INSEE, Banque de France, etc.)
- 20% Académiques (McKinsey, BCG, etc.)
- 15% Média spécialisé (Les Échos, Bloomberg, etc.)
- 5% Autres vérifiées

### Qualité Graphiques

- **Résolution** : 150 DPI (qualité print)
- **Format** : PNG avec transparence
- **Dimensions PDF** : 15 cm × 9 cm
- **Style** : Corporate (#0052A5)
- **Sources** : Citation APA sur chaque graphique

---

## 🎯 9. RECOMMANDATIONS

### Pour les Utilisateurs

1. **Spécifiez les données** : Plus la requête inclut de données chiffrées précises, meilleurs seront les graphiques
2. **Types de graphiques** : Le modèle choisit automatiquement, mais vous pouvez guider via la requête
   - "avec évolution temporelle" → line chart
   - "avec comparaison entre acteurs" → bar chart
   - "avec répartition" → pie chart

### Pour les Développeurs

1. **Personnaliser les styles** : Modifier `generate_chart_image()` dans `report-service/app/main.py`
2. **Ajouter types graphiques** : Matplotlib supporte scatter, histogram, etc.
3. **Graphiques multi-séries** : Étendre le format `data` pour supporter multiple datasets

---

## 📝 10. CHANGELOG

### Version 4.0 (Actuelle)

**Citations APA** :
- ✅ Remplacement complet `[1]` → `(Auteur, Année)`
- ✅ Section "Références Bibliographiques" au lieu de "Sources"
- ✅ Croisement sources visible : `(Source1, 2024; Source2, 2024)`
- ✅ Conversion automatique dans PDF

**Graphiques** :
- ✅ Format markdown ```chart
- ✅ 3 types supportés : bar, line, pie
- ✅ Génération automatique avec matplotlib
- ✅ Intégration dans PDF après chaque section
- ✅ Style professionnel + sources APA

**Prompts** :
- ✅ Tous les prompts enrichis (finance, tech, retail)
- ✅ Instructions APA explicites
- ✅ Demande 2-4 graphiques par rapport
- ✅ Exemples de format chart inclus

**Infrastructure** :
- ✅ `matplotlib==3.9.2` ajouté à report-service
- ✅ Fonctions parsing et génération graphiques
- ✅ Script de déploiement `rebuild_charts_apa.sh`

### Version 3.2 (Précédente)

- 40-60 sources pour tous les rapports
- Barre de progression OpenWebUI
- Sonar-pro exclusif pour tous les rapports
- Timeout API 7.5 minutes

---

## 📚 11. RESSOURCES

### Documentation Connexe

- `README_MODELES.md` : Configuration multi-modèles Sonar
- `AMELIORATIONS_PDF_V2.md` : Améliorations style PDF
- `DEPLOIEMENT_COMPLET.md` : Guide déploiement complet

### Références Externes

- [APA Style 7th Edition](https://apastyle.apa.org/)
- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)
- [ReportLab User Guide](https://www.reportlab.com/docs/reportlab-userguide.pdf)

---

## ✅ STATUT ACTUEL

- ✅ **Backend Service** : Citations APA + prompts graphiques
- ✅ **Report Service** : Génération graphiques + intégration PDF
- ✅ **OpenWebUI** : Support complet PDF avec graphiques
- ✅ **Documentation** : README_CHARTS_APA.md complet
- ✅ **Script Déploiement** : `rebuild_charts_apa.sh` fonctionnel
- ✅ **Tests** : Validés sur les 3 types (finance, tech, retail)

---

**📧 Support** : Pour toute question, consulter les logs Docker ou relancer le script de déploiement.

**🚀 Prêt pour production** : Tous les services sont opérationnels et testés.

