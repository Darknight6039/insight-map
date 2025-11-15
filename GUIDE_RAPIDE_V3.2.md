# 🚀 Guide Rapide - Rapports Améliorés V3.2

## ⚡ Démarrage en 3 Étapes

### 1️⃣ Rebuild (30 secondes)
```bash
cd /Users/isaiaebongue/insight-mvp
./rebuild_and_test.sh
```

### 2️⃣ Test Rapide
```bash
# Health check
curl http://localhost:8006/health | jq '.perplexity_models'

# Résultat attendu :
# {
#   "chat": "sonar",
#   "analysis": "sonar-pro",
#   "reasoning": "sonar-reasoning"
# }
```

### 3️⃣ Générer un Rapport Test
```bash
curl -X POST http://localhost:8006/extended-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "finance_banque",
    "analysis_type": "synthese_executive",
    "query": "Évolution du secteur bancaire français 2024"
  }' > test_rapport.json

# Vérifier la qualité
cat test_rapport.json | jq '.content' | wc -w  # Devrait être 6000-8000 mots
cat test_rapport.json | jq '.sources | length'  # Devrait être 15-25
```

---

## 🎯 Ce Qui a Changé

### Augmentations Principales
| Paramètre | Avant | Après | Gain |
|-----------|-------|-------|------|
| **Sources minimum** | 5 | 15-25 | +200-400% |
| **Tokens max** | 4K/8K | 6K/12K | +50% |
| **Données chiffrées** | Variable | 30+ | Standardisé |
| **Tableaux** | 0+ | 3+ | Obligatoire |
| **Contexte RAG** | 3K | 5K | +67% |
| **Docs RAG** | 8 | 12 | +50% |
| **Chat sources** | 3 | 5-8 | +67-167% |

### Qualité Renforcée
✅ **Croisement systématique** des sources  
✅ **Précision temporelle** (dates obligatoires)  
✅ **Tableaux comparatifs** structurés  
✅ **Scénarios financiers** obligatoires  
✅ **KPIs détaillés** par recommandation  
✅ **Température 0.1** (précision maximale)  

---

## 📊 Exemple de Rapport Généré

### Structure Attendue

```markdown
# Analyse du Marché Bancaire Français 2024

## 1. Executive Summary (600-800 mots)

Le secteur bancaire français représente 85 milliards € de revenus en 2024 [1][2],
avec une croissance de 3,2% selon l'ACPR [1] et 3,5% selon la FBF [2]...

### KPIs Clés
- Taille marché : 85 Md€ [1][2]
- Croissance : +3,2% [1]
- Nombre d'établissements : 298 [3]
- ...

## 2. Analyse Sectorielle (1500-2000 mots)

### Dimensionnement Marché

Le marché bancaire français atteint 85 milliards € en 2024 selon l'ACPR [1],
confirmé par la FBF à 84,7 milliards [2]...

| Segment | Taille (M€) | Part (%) | CAGR 3 ans | Source |
|---------|-------------|----------|------------|--------|
| Banque de détail | 45 000 | 53% | +2,8% | [1][2] |
| Banque privée | 12 500 | 15% | +5,2% | [3][4] |
| ... | ... | ... | ... | ... |

### Parts de Marché

| Banque | Part 2024 | Évolution vs 2023 | Source |
|--------|-----------|-------------------|--------|
| BNP Paribas | 18,5% | +0,3pp | [5] |
| Crédit Agricole | 16,2% | -0,1pp | [5] |
| ... | ... | ... | ... |

## 3. Analyse Concurrentielle (1200-1500 mots)

[Tableau comparatif 8 critères × 5 concurrents avec sources]

## 4. Recommandations Stratégiques (1500-2000 mots)

### Recommandation 1 : Digitalisation Parcours Client

**Investissement requis :** 15-25 M€ sur 24 mois [benchmarks BCG] [6]
**ROI estimé :** 8,5% après 18 mois [méthodologie McKinsey] [7]
**Timeline :** 
- Phase 1 (mois 1-6) : Audit et design (3 M€)
- Phase 2 (mois 7-12) : Développement (8 M€)
- Phase 3 (mois 13-24) : Déploiement (9 M€)

**KPIs de suivi :**
- Taux d'adoption digital : objectif 65% à 12 mois
- NPS : +15 points à 18 mois
- Coût d'acquisition : -25% à 24 mois

**Risques quantifiés :**
- Retard technique (30% probabilité, impact -5M€)
- Résistance utilisateurs (20% probabilité, impact -3M€)

[... autres recommandations similaires]

## 5. Projections et Scénarios (1000-1200 mots)

| Métrique | Optimiste | Central | Pessimiste |
|----------|-----------|---------|------------|
| Croissance marché | +5,2% | +3,5% | +1,8% |
| Part de marché | 19,5% | 18,2% | 16,8% |
| Revenus 2026 | 95 M€ | 88 M€ | 82 M€ |
| ROI projet | 12% | 8,5% | 5% |

### Hypothèses Scénario Central
- Croissance PIB France : +1,8% [INSEE] [8]
- Inflation : +2,2% [BCE] [9]
- Taux directeurs : 3,5% [BCE] [9]
...

## 📚 Sources

### Sources Institutionnelles et Statistiques
[1] ACPR. (2024). Panorama bancaire français T3 2024. Rapport trimestriel. 
    https://acpr.banque-france.fr/panorama-t3-2024
[2] FBF. (2024). Rapport annuel du secteur bancaire français. Rapport annuel.
    https://fbf.fr/rapport-annuel-2024
[3] INSEE. (2024). Statistiques secteur financier Q3 2024. Données économiques.
    https://insee.fr/finance-q3-2024
...

### Études et Rapports Sectoriels
[6] BCG. (2024). Transformation digitale bancaire - Benchmarks coûts. Étude sectorielle.
    https://bcg.com/digital-banking-costs-2024
[7] McKinsey & Company. (2024). ROI transformation bancaire. Méthodologie.
    https://mckinsey.com/banking-roi-methodology
...

### Presse Économique Spécialisée
[12] Les Échos. (12 nov 2024). "Le secteur bancaire face au digital". Article.
     https://lesechos.fr/finance/banques/secteur-bancaire-digital-2024
...

### Sources Réglementaires
[18] Directive UE 2024/123. (2024). Consolidation bancaire européenne. Texte officiel.
     https://eur-lex.europa.eu/directive-2024-123

**Total : 22 sources**
```

---

## 🔍 Vérification Qualité

### Checklist Automatique

Après génération d'un rapport, vérifier :

```bash
# 1. Compter les mots
cat rapport.json | jq -r '.content' | wc -w
# Attendu : 6000-8000 mots

# 2. Compter les sources
cat rapport.json | jq -r '.content' | grep -o '\[1\]' | wc -l
# Attendu : 30+ citations

# 3. Compter sources uniques
cat rapport.json | jq -r '.content' | grep -A 50 "## 📚 Sources" | grep "^\[" | wc -l
# Attendu : 15-25 sources

# 4. Vérifier tableaux
cat rapport.json | jq -r '.content' | grep -c "^|"
# Attendu : 15+ lignes de tableau (3 tableaux × 5 lignes min)

# 5. Vérifier données chiffrées
cat rapport.json | jq -r '.content' | grep -oE '[0-9]+(\.[0-9]+)?\s?(M€|%|milliards|millions)' | wc -l
# Attendu : 30+ données chiffrées
```

### Checklist Manuelle

- [ ] **Croisement sources visible** : Rechercher `[1][2]` dans le texte
- [ ] **Dates précises** : Rechercher "2024", "Q3 2024", "2022-2024"
- [ ] **Périmètres** : Rechercher "en France", "Europe", "au niveau mondial"
- [ ] **Scénarios** : 3 scénarios (optimiste/central/pessimiste) présents
- [ ] **KPIs recommandations** : Chaque recommandation a 3+ KPIs
- [ ] **Bibliographie organisée** : Sources groupées par catégories
- [ ] **Divergences mentionnées** : Rechercher "varie entre", "selon"

---

## 📈 Monitoring Performance

### Logs à Surveiller

```bash
# En temps réel
docker compose logs -f backend-service | grep -E "Using model|API error|sources"

# Patterns attendus
✅ "Using model: sonar-pro for task: analysis (max_tokens: 12000)"
✅ "Using model: sonar for task: chat (max_tokens: 6000)"
✅ Génération rapport en 40-60 secondes
❌ PAS d'erreurs "401 Unauthorized"
❌ PAS d'erreurs "Rate limit exceeded"
```

### Métriques Business

Créer un fichier `metrics.sh` :

```bash
#!/bin/bash
# Métriques qualité rapports générés aujourd'hui

echo "📊 Métriques Rapports - $(date +%Y-%m-%d)"
echo "=========================================="

# Nombre de rapports générés
echo "Rapports générés : $(docker compose logs backend-service | grep -c 'extended-analysis')"

# Modèles utilisés
echo ""
echo "Utilisation modèles :"
docker compose logs backend-service | grep "Using model" | sort | uniq -c

# Temps moyen génération (approximatif)
echo ""
echo "Temps moyen génération : ~45-60s pour rapports longs"

# Erreurs API
echo ""
echo "Erreurs API : $(docker compose logs backend-service | grep -c 'API error')"
```

---

## 🐛 Troubleshooting

### Problème : Rapport trop court (<6000 mots)

**Causes possibles :**
1. Modèle `sonar` au lieu de `sonar-pro` utilisé
2. Timeout trop court
3. Prompt tronqué

**Solutions :**
```bash
# Vérifier modèle utilisé
docker compose logs backend-service | grep "Using model" | tail -1

# Vérifier timeout (doit être 300s)
grep timeout backend-service/app/main.py

# Relancer avec query plus détaillée
curl -X POST http://localhost:8006/extended-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "finance_banque",
    "analysis_type": "analyse_sectorielle",
    "query": "Analyse complète et détaillée du marché bancaire français 2024 : dimensionnement, acteurs, tendances, réglementation, perspectives 2025-2027"
  }'
```

---

### Problème : Pas assez de sources (<15)

**Causes possibles :**
1. Query trop vague ou trop générique
2. API Perplexity rate limited
3. Prompt pas correctement transmis

**Solutions :**
```bash
# Vérifier quota API Perplexity
# → Se connecter sur https://www.perplexity.ai/settings/api

# Query plus spécifique avec contexte
curl -X POST http://localhost:8006/extended-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "finance_banque",
    "analysis_type": "analyse_sectorielle",
    "query": "Analyse détaillée secteur bancaire français 2024 : parts de marché BNP/SG/CA, évolution revenus 2022-2024, impact réglementation ACPR, comparaison Europe"
  }'

# Vérifier system prompt dans logs
docker compose logs backend-service | grep -A 5 "MINIMUM 15-25 sources"
```

---

### Problème : Erreur "Rate limit exceeded"

**Solution :**
```bash
# Attendre 60 secondes entre requêtes
sleep 60

# OU upgrader plan Perplexity API
# → https://www.perplexity.ai/settings/api
```

---

### Problème : PDF export échoue

**Solution :**
```bash
# Vérifier report-service
docker compose logs report-service | tail -50

# Redémarrer report-service si nécessaire
docker compose restart report-service

# Attendre 10s
sleep 10

# Réessayer export
curl -X POST http://localhost:8004/generate-report \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Rapport",
    "content": "...",
    "business_type": "finance_banque"
  }'
```

---

## 📚 Documentation Complète

- **`AMELIORATIONS_RAPPORTS_V3.2.md`** : Documentation exhaustive des améliorations
- **`multi-model-so.plan.md`** : Plan d'implémentation détaillé
- **`CONFIGURATION_MODELES.md`** : Stratégie multi-modèles Sonar
- **`rebuild_and_test.sh`** : Script automatique de déploiement

---

## 🎯 Prochaines Étapes

### Immédiat
1. ✅ Exécuter `./rebuild_and_test.sh`
2. ✅ Tester génération 2-3 rapports
3. ✅ Vérifier qualité (sources, mots, tableaux)
4. ✅ Tester export PDF

### Court terme (1 semaine)
- Monitorer temps de génération
- Surveiller coûts API Perplexity
- Collecter feedback utilisateurs
- Ajuster si nécessaire

### Moyen terme (1 mois)
- Analyser métriques qualité sur 50+ rapports
- Optimiser prompts si patterns identifiés
- Considérer `sonar-reasoning` pour analyses complexes
- Envisager cache pour requêtes similaires

---

**Version :** 3.2  
**Date :** 15 novembre 2024  
**Prêt à déployer :** ✅ OUI

🚀 **Lancer maintenant :** `./rebuild_and_test.sh`

