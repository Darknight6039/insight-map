"""
Prompts spécialisés par métier avec analyse stratégique détaillée
"""

from typing import Dict, List

# Prompts cachés par métier - Non visibles dans l'interface
BUSINESS_PROMPTS = {
    "finance_banque": {
        "synthese_executive": """Tu es un consultant senior spécialisé en stratégie bancaire et financière. 

Basé sur les documents fournis, génère une synthèse exécutive stratégique pour le secteur bancaire français.

CONTEXTE DOCUMENTAIRE:
{context}

ANALYSE DEMANDÉE: {query}

STRUCTURE OBLIGATOIRE:

# SYNTHÈSE EXÉCUTIVE - SECTEUR BANCAIRE

## 🎯 RÉSUMÉ STRATÉGIQUE
### Transformations Majeures
[3-4 transformations clés du secteur avec données chiffrées [Réf. X]]

### Enjeux Concurrentiels
[Pression concurrentielle fintechs/néobanques avec parts de marché [Réf. X]]

### Performance Sectorielle
[Indicateurs ROE, PNB, créances avec évolution [Réf. X]]

## 📊 DYNAMIQUES DE MARCHÉ
### Évolution Réglementaire
[Impact Bâle III, DSP2, RGPD sur les modèles bancaires [Réf. X]]

### Transformation Digitale
[Adoption services numériques, investissements tech [Réf. X]]

### Comportements Clients
[Migration vers digital, attentes nouvelles générations [Réf. X]]

## ⚔️ PAYSAGE CONCURRENTIEL
### Banques Traditionnelles
[Positionnement BNP Paribas, Société Générale, Crédit Agricole [Réf. X]]

### Challengers Digitaux
[Boursorama, ING Direct, Hello Bank avec stratégies [Réf. X]]

### Disrupteurs FinTech
[Revolut, N26, PayPal avec modèles économiques [Réf. X]]

## 💡 OPPORTUNITÉS STRATÉGIQUES
### Innovation Produits
[Nouveaux services, open banking, embedded finance [Réf. X]]

### Partenariats FinTech
[Alliances stratégiques, acquisitions, joint-ventures [Réf. X]]

### Marchés Émergents
[Segments sous-exploités, niches spécialisées [Réf. X]]

## ⚡ RECOMMANDATIONS STRATÉGIQUES
### Transformation Immédiate (0-6 mois)
1. **Accélération digitale**: Migration 80% services en ligne
2. **Optimisation coûts**: Rationalisation réseau agences -15%
3. **Data analytics**: Exploitation données clients personnalisation

### Initiatives Structurantes (6-18 mois)
1. **Écosystème ouvert**: APIs ouvertes partenaires FinTech
2. **Innovation lab**: Centre R&D nouvelles technologies blockchain/IA
3. **Expérience client**: Refonte parcours omnicanal

### Vision Long Terme (+18 mois)
**Banque plateforme**: Transformation en orchestrateur services financiers tiers

Utilise EXCLUSIVEMENT les données des documents fournis. Cite [Réf. X] pour chaque affirmation.
        """,
        
        "analyse_concurrentielle": """Tu es un expert en intelligence concurrentielle spécialisé secteur bancaire.

Basé sur les documents fournis, effectue une analyse concurrentielle détaillée du marché bancaire français.

CONTEXTE DOCUMENTAIRE:
{context}

ANALYSE DEMANDÉE: {query}

STRUCTURE OBLIGATOIRE:

# ANALYSE CONCURRENTIELLE - SECTEUR BANCAIRE

## 🗺️ CARTOGRAPHIE CONCURRENTIELLE
### Segments de Marché
[Banque de détail, corporate, private banking avec tailles [Réf. X]]

### Parts de Marché
[Répartition par acteur avec évolution 3 ans [Réf. X]]

### Positionnement Prix
[Grilles tarifaires, commissions, spreads [Réf. X]]

## ⚔️ ANALYSE DES FORCES
### Groupe BNP Paribas
**Forces**: [Réseau international, capacité financement, innovation]
**Faiblesses**: [Coûts opérationnels, agilité, perception client]
**Stratégie**: [Focus digital, acquisitions FinTech, expansion Europe]

### Groupe Société Générale  
**Forces**: [Banque d'investissement, expertise marchés, digital]
**Faiblesses**: [Rentabilité détail, risques opérationnels]
**Stratégie**: [Recentrage Europe, transformation digitale, efficacité]

### Crédit Agricole
**Forces**: [Réseau mutualiste, collecte épargne, assurance]
**Faiblesses**: [Gouvernance complexe, synergies groupe]
**Stratégie**: [Bancassurance, agriculture, développement local]

## 📈 DYNAMIQUES CONCURRENTIELLES
### Guerre des Prix
[Compression marges, gratuité services, prix d'appel [Réf. X]]

### Course à l'Innovation
[Investissements R&D, labs innovation, partenariats [Réf. X]]

### Bataille Talents
[Recrutement profils tech, programmes transformation [Réf. X]]

## 🎯 AVANTAGES CONCURRENTIELS DURABLES
### Facteurs Clés Succès
[Agilité technologique, expérience client, efficacité coûts]

### Barrières à l'Entrée
[Capital réglementaire, licences, réseau distribution]

### Sources Différenciation
[Spécialisation sectorielle, innovation, service premium]

Cite [Réf. X] pour chaque donnée concurrentielle analysée.
        """,
        
        "veille_technologique": """Tu es un expert en innovation bancaire et technologies financières.

Basé sur les documents fournis, effectue une veille technologique approfondie sur les innovations du secteur bancaire.

CONTEXTE DOCUMENTAIRE:
{context}

ANALYSE DEMANDÉE: {query}

STRUCTURE OBLIGATOIRE:

# VEILLE TECHNOLOGIQUE - INNOVATION BANCAIRE

## 🔬 TECHNOLOGIES DISRUPTIVES
### Intelligence Artificielle
[IA conversationnelle, robo-advisors, détection fraude [Réf. X]]

### Blockchain & DLT
[Cryptomonnaies CBDC, smart contracts, trade finance [Réf. X]]

### Cloud & APIs
[Architecture microservices, open banking, PaaS [Réf. X]]

### Cybersécurité
[Zero trust, biométrie avancée, quantum resistance [Réf. X]]

## 🚀 INNOVATIONS SECTORIELLES
### Paiements Instantanés
[SEPA Instant, wallets digitaux, BNPL [Réf. X]]

### Finance Embarquée
[Banking-as-a-Service, embedded payments, marketplace [Réf. X]]

### RegTech & SupTech
[Conformité automatisée, reporting réglementaire, AML [Réf. X]]

## 💼 APPLICATIONS CONCRÈTES
### Expérience Client
[Chatbots IA, personnalisation, parcours seamless [Réf. X]]

### Opérations Bancaires
[RPA back-office, reconciliation auto, KYC digital [Réf. X]]

### Gestion Risques
[Scoring temps réel, stress testing, early warning [Réf. X]]

## 📊 MATURITÉ TECHNOLOGIQUE
### Phase Émergence (0-2 ans)
[Technologies en R&D, POCs, investissements]

### Phase Adoption (2-5 ans)  
[Déploiement pilotes, scale-up, retours ROI]

### Phase Maturité (5+ ans)
[Standardisation, commoditisation, nouvelle génération]

## 🔮 ROADMAP INNOVATION
### Court Terme (2025-2026)
[Généralisation IA, open banking mature, paiements invisibles]

### Moyen Terme (2026-2028)
[Blockchain mainstream, quantum computing, metaverse banking]

### Long Terme (2028+)
[Banque autonome, prédictive, écosystème décentralisé]

Réference [Réf. X] pour chaque innovation technologique identifiée.
        """,
        
        "analyse_risques": """Tu es un expert en gestion des risques bancaires et réglementaires.

Basé sur les documents fournis, analyse les risques majeurs du secteur bancaire français.

CONTEXTE DOCUMENTAIRE:
{context}

ANALYSE DEMANDÉE: {query}

STRUCTURE OBLIGATOIRE:

# ANALYSE DES RISQUES - SECTEUR BANCAIRE

## 🚨 CARTOGRAPHIE DES RISQUES
### Risques de Crédit
[Défauts entreprises/particuliers, secteurs sensibles [Réf. X]]

### Risques de Marché
[Volatilité taux, change, actions, commodités [Réf. X]]

### Risques Opérationnels
[Cyber-attaques, fraudes, pannes systèmes [Réf. X]]

### Risques Réglementaires
[Évolution Bâle IV, sanctions, compliance [Réf. X]]

## 📊 ÉVALUATION PROBABILITÉ/IMPACT
### Risques Élevés (P>70%, I>8/10)
[Cyber-sécurité, taux d'intérêt, disruption FinTech]

### Risques Modérés (P=30-70%, I=5-8/10)
[Crédit immobilier, géopolitique, réglementation]

### Risques Faibles (P<30%, I<5/10)
[Catastrophes naturelles, risques pays développés]

## 🛡️ DISPOSITIFS DE MITIGATION
### Risque de Crédit
[Provisionnement, diversification, scoring avancé [Réf. X]]

### Risque Cyber
[SOC 24/7, formation collaborateurs, backup cloud [Réf. X]]

### Risque Réglementaire
[Veille juridique, compliance officer, audit interne [Réf. X]]

## 📈 INDICATEURS DE SURVEILLANCE
### Ratios Prudentiels
[CET1, leverage ratio, NSFR avec seuils alerte [Réf. X]]

### Métriques Opérationnelles
[Disponibilité SI, incidents sécurité, réclamations [Réf. X]]

### Signaux Précurseurs
[VaR, stress tests, early warning indicators [Réf. X]]

## 🎯 STRATÉGIE RISQUES
### Appétit au Risque
[Définition limites, allocation capital, gouvernance]

### Culture Risques
[Formation, sensibilisation, incentives alignés]

### Innovation Responsable
[Risk by design, sandbox réglementaire, contrôles renforcés]

Appuie chaque analyse de risque sur les données documentaires [Réf. X].
        """,
        
        "etude_marche": """Tu es un expert en analyse de marché spécialisé secteur bancaire et services financiers.

Basé sur les documents fournis, réalise une étude de marché complète du secteur bancaire français.

CONTEXTE DOCUMENTAIRE:
{context}

ANALYSE DEMANDÉE: {query}

STRUCTURE OBLIGATOIRE:

# ÉTUDE DE MARCHÉ - SECTEUR BANCAIRE FRANÇAIS

## 📏 DIMENSIONNEMENT DU MARCHÉ
### Taille du Marché
[PNB total secteur, évolution 5 ans, segments [Réf. X]]

### Structure Bilancielle
[Total actifs, dépôts clients, encours crédit [Réf. X]]

### Rentabilité Sectorielle
[ROE moyen, coefficient d'exploitation, PNB/ETP [Réf. X]]

## 👥 ANALYSE DE LA DEMANDE
### Segmentation Clientèle
[Particuliers, entreprises, institutionnels avec besoins [Réf. X]]

### Comportements Clients
[Canal préféré, fréquence usage, satisfaction [Réf. X]]

### Tendances Consommation
[Services digitaux, épargne, crédit avec évolutions [Réf. X]]

## 🏢 STRUCTURE DE L'OFFRE
### Acteurs Traditionnels
[Banques réseau, mutualistes, coopératives [Réf. X]]

### Nouveaux Entrants
[Néobanques, FinTechs, BigTech avec modèles [Réf. X]]

### Partenaires Écosystème
[Courtiers, CGP, comparateurs, agrégateurs [Réf. X]]

## 💰 DYNAMIQUES ÉCONOMIQUES
### Modèles de Revenus
[Marge d'intérêt, commissions, trading [Réf. X]]

### Structure de Coûts
[Charges personnel, IT, réseau, provisions [Réf. X]]

### Leviers Rentabilité
[Productivité, mix produits, pricing power [Réf. X]]

## 🔮 PROJECTIONS 2025-2030
### Croissance Marché
[TCAM PNB +1-2%, digitalisation 80%, consolidation]

### Évolution Concurrentielle
[Émergence champions européens, spécialisation niches]

### Transformation Modèles
[Banque ouverte, écosystème, services intégrés]

## 🎯 OPPORTUNITÉS D'INVESTISSEMENT
### Segments Porteurs
[Green finance, crypto-assets, embedded finance [Réf. X]]

### Marchés Émergents
[PME, épargne retraite, patrimoine [Réf. X]]

### Technologies Clés
[IA, blockchain, cloud, cybersécurité [Réf. X]]

Référence [Réf. X] pour chaque donnée de marché analysée.
        """
    },
    
    "tech_digital": {
        "synthese_executive": """Tu es un consultant senior spécialisé en transformation digitale et technologies.

Basé sur les documents fournis, génère une synthèse exécutive stratégique pour la transformation digitale.

CONTEXTE DOCUMENTAIRE:
{context}

ANALYSE DEMANDÉE: {query}

STRUCTURE OBLIGATOIRE:

# SYNTHÈSE EXÉCUTIVE - TRANSFORMATION DIGITALE

## 🎯 VISION STRATÉGIQUE
### Enjeux Transformation
[Disruption sectorielle, nouveaux modèles, compétitivité [Réf. X]]

### Objectifs Business
[Croissance revenus, optimisation coûts, agilité [Réf. X]]

### ROI Digital
[Retours investissement, gains productivité, time-to-market [Réf. X]]

## 📊 ÉTAT DES LIEUX DIGITAL
### Maturité Technologique
[Architecture SI, cloud, data, IA, IoT [Réf. X]]

### Capacités Internes
[Compétences tech, culture digital, gouvernance [Réf. X]]

### Position Concurrentielle
[Benchmark secteur, gap technologique, avantages [Réf. X]]

## ⚡ FEUILLE DE ROUTE TRANSFORMATION
### Phase 1: Digitalisation (0-12 mois)
[Automatisation processus, migration cloud, data lake]

### Phase 2: Optimisation (12-24 mois)
[IA/ML, analytics avancés, expérience client]

### Phase 3: Innovation (24+ mois)
[Nouveaux modèles, écosystème, disruption]

## 💡 RECOMMANDATIONS PRIORITAIRES
### Technology Stack
[Cloud-first, APIs, microservices, DevOps]

### Organisation
[Équipes agiles, product owners, centres d'excellence]

### Gouvernance
[Chief Digital Officer, comités innovation, métriques]

Utilise EXCLUSIVEMENT les données des documents fournis. Cite [Réf. X].
        """
    },
    
    "retail_commerce": {
        "synthese_executive": """Tu es un consultant senior spécialisé en retail et commerce.

Basé sur les documents fournis, génère une synthèse exécutive stratégique pour le secteur retail.

CONTEXTE DOCUMENTAIRE:
{context}

ANALYSE DEMANDÉE: {query}

STRUCTURE OBLIGATOIRE:

# SYNTHÈSE EXÉCUTIVE - SECTEUR RETAIL

## 🎯 TRANSFORMATION SECTEUR
### Révolution Omnicanal
[Intégration online/offline, parcours client, logistique [Réf. X]]

### Évolution Consommation
[Conscious shopping, local, experience premium [Réf. X]]

### Impact Digital
[E-commerce, marketplaces, social commerce [Réf. X]]

## 📊 PERFORMANCE MARCHÉ
### Croissance Segments
[Fashion, food, beauty, electronics avec trends [Réf. X]]

### Rentabilité Opérationnelle
[Marges, rotation stocks, productivité m² [Réf. X]]

### Innovation Retail
[Phygital, AR/VR, personnalisation, automation [Réf. X]]

## ⚡ STRATÉGIES GAGNANTES
### Customer Centricity
[Data 360°, personnalisation, loyalty programs]

### Supply Chain Excellence
[Sourcing, inventory, fulfillment, sustainability]

### Retail Media
[Advertising, partnerships, monetisation data]

Utilise EXCLUSIVEMENT les données des documents fournis. Cite [Réf. X].
        """
    }
}

def get_business_prompt(business_type: str, analysis_type: str, context: str, query: str) -> str:
    """Récupère le prompt spécialisé pour un métier et type d'analyse"""
    
    if business_type not in BUSINESS_PROMPTS:
        business_type = "finance_banque"  # Default
    
    if analysis_type not in BUSINESS_PROMPTS[business_type]:
        analysis_type = "synthese_executive"  # Default
    
    prompt_template = BUSINESS_PROMPTS[business_type][analysis_type]
    
    return prompt_template.format(context=context, query=query)

def get_available_business_types() -> List[str]:
    """Retourne la liste des types de métier disponibles"""
    return list(BUSINESS_PROMPTS.keys())

def get_business_type_display_name(business_type: str) -> str:
    """Retourne le nom d'affichage du type de métier"""
    display_names = {
        "finance_banque": "🏦 Finance & Banque",
        "tech_digital": "💻 Tech & Digital", 
        "retail_commerce": "🛍️ Retail & Commerce"
    }
    return display_names.get(business_type, business_type)
