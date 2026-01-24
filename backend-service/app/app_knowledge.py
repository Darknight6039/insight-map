"""
Base de connaissance Prometheus - Documentation interne pour l'assistant intelligent

Ce fichier contient toutes les informations que l'assistant doit connaître
sur l'application Prometheus pour guider et aider les utilisateurs.
"""

# Description générale de l'application
APP_DESCRIPTION = """
Prometheus est une plateforme d'intelligence stratégique alimentée par l'IA.
Elle permet aux entreprises de :
- Générer des rapports d'analyse professionnels sur n'importe quel sujet
- Configurer des veilles automatisées pour suivre des sujets spécifiques
- Exporter des rapports au format PDF avec citations et sources
- Personnaliser les analyses selon le secteur d'activité
"""

# Types d'analyses disponibles
ANALYSIS_TYPES = {
    "synthese_executive": {
        "name": "Synthèse Exécutive",
        "description": "Analyse approfondie et complète avec recommandations stratégiques. Idéale pour les décideurs.",
        "use_case": "Quand vous avez besoin d'une vue d'ensemble complète avec des recommandations actionnables.",
        "duration": "2-3 minutes",
        "output": "Rapport détaillé avec sections structurées, graphiques et recommandations"
    },
    "analyse_concurrentielle": {
        "name": "Analyse Concurrentielle",
        "description": "Étude des acteurs du marché, positionnement et stratégies concurrentielles.",
        "use_case": "Pour comprendre votre environnement concurrentiel et identifier des opportunités.",
        "duration": "2-3 minutes",
        "output": "Mapping concurrentiel, forces/faiblesses, tendances du marché"
    },
    "veille_technologique": {
        "name": "Veille Technologique",
        "description": "Surveillance des innovations, brevets et évolutions technologiques.",
        "use_case": "Pour rester à jour sur les avancées technologiques de votre secteur.",
        "duration": "2-3 minutes",
        "output": "Innovations récentes, technologies émergentes, implications pour votre activité"
    },
    "analyse_risques": {
        "name": "Analyse des Risques",
        "description": "Identification et évaluation des risques stratégiques, opérationnels et de marché.",
        "use_case": "Pour anticiper les menaces et préparer des plans de mitigation.",
        "duration": "2-3 minutes",
        "output": "Cartographie des risques, probabilité/impact, recommandations de mitigation"
    },
    "analyse_reglementaire": {
        "name": "Analyse Réglementaire",
        "description": "Veille sur les évolutions légales et réglementaires impactant votre secteur.",
        "use_case": "Pour rester conforme et anticiper les changements réglementaires.",
        "duration": "2-3 minutes",
        "output": "Nouvelles réglementations, impacts, délais de mise en conformité"
    }
}

# Secteurs d'activité disponibles
SECTORS = {
    "general": {
        "name": "Général",
        "description": "Analyse transversale sans focus sectoriel spécifique"
    },
    "finance_banque": {
        "name": "Finance & Banque",
        "description": "Banques, assurances, fintech, marchés financiers"
    },
    "tech_digital": {
        "name": "Tech & Digital",
        "description": "Technologies, logiciels, startups, transformation digitale"
    },
    "retail_commerce": {
        "name": "Retail & Commerce",
        "description": "Distribution, e-commerce, grande consommation"
    },
    "industrie": {
        "name": "Industrie",
        "description": "Manufacturing, automobile, aéronautique, énergie industrielle"
    },
    "sante": {
        "name": "Santé",
        "description": "Pharmaceutique, biotech, dispositifs médicaux, e-santé"
    },
    "energie": {
        "name": "Énergie",
        "description": "Énergies renouvelables, pétrole, gaz, utilities"
    }
}

# Fréquences de veille disponibles
WATCH_FREQUENCIES = {
    "daily": {
        "name": "Quotidienne",
        "cron": "0 8 * * *",
        "description": "Tous les jours à 8h du matin"
    },
    "weekly_monday": {
        "name": "Hebdomadaire (Lundi)",
        "cron": "0 8 * * 1",
        "description": "Chaque lundi à 8h"
    },
    "weekly_friday": {
        "name": "Hebdomadaire (Vendredi)",
        "cron": "0 8 * * 5",
        "description": "Chaque vendredi à 8h"
    },
    "biweekly": {
        "name": "Bi-hebdomadaire",
        "cron": "0 8 * * 1,4",
        "description": "Lundi et jeudi à 8h"
    },
    "monthly": {
        "name": "Mensuelle",
        "cron": "0 8 1 * *",
        "description": "Le 1er de chaque mois à 8h"
    }
}

# Guides pas-à-pas
GUIDES = {
    "create_report": {
        "title": "Générer un rapport",
        "steps": [
            "1. Sur la page d'accueil, choisissez le type d'analyse souhaité",
            "2. Entrez votre question ou sujet dans le champ de recherche",
            "3. Optionnellement, sélectionnez un secteur spécifique",
            "4. Activez ou désactivez l'option 'Inclure les recommandations'",
            "5. Cliquez sur 'Générer l'analyse'",
            "6. Patientez pendant la génération (2-3 minutes)",
            "7. Une fois terminé, cliquez sur 'Exporter PDF' pour télécharger"
        ]
    },
    "create_watch": {
        "title": "Créer une veille automatisée",
        "steps": [
            "1. Accédez à la page 'Veilles' via le menu de navigation",
            "2. Cliquez sur 'Nouvelle veille'",
            "3. Donnez un nom à votre veille",
            "4. Définissez le sujet à surveiller",
            "5. Sélectionnez le secteur d'activité",
            "6. Choisissez le type de rapport souhaité",
            "7. Définissez la fréquence (quotidienne, hebdomadaire, etc.)",
            "8. Ajoutez les adresses email des destinataires",
            "9. Cliquez sur 'Créer la veille'"
        ]
    },
    "manage_watches": {
        "title": "Gérer vos veilles",
        "steps": [
            "1. Accédez à la page 'Veilles'",
            "2. Vous verrez la liste de toutes vos veilles",
            "3. Utilisez le toggle pour activer/désactiver une veille",
            "4. Cliquez sur l'icône crayon pour modifier",
            "5. Cliquez sur l'icône poubelle pour supprimer",
            "6. Consultez l'historique d'exécution de chaque veille"
        ]
    },
    "add_context": {
        "title": "Ajouter un contexte entreprise",
        "steps": [
            "1. Accédez à votre profil via l'icône en haut à droite",
            "2. Dans la section 'Contexte entreprise', vous pouvez :",
            "   - Saisir un texte décrivant votre entreprise",
            "   - Ou télécharger un document (PDF, DOCX, TXT)",
            "3. Ce contexte sera utilisé pour personnaliser vos analyses",
            "4. Les rapports seront plus pertinents pour votre activité"
        ]
    }
}

# FAQ - Questions fréquentes
FAQ = {
    "what_is_prometheus": {
        "question": "Qu'est-ce que Prometheus ?",
        "answer": "Prometheus est une plateforme d'intelligence stratégique IA qui génère des rapports d'analyse professionnels et permet de configurer des veilles automatisées sur n'importe quel sujet."
    },
    "how_long_report": {
        "question": "Combien de temps prend la génération d'un rapport ?",
        "answer": "La génération d'un rapport prend généralement 2 à 3 minutes. Vous pouvez suivre la progression en temps réel via la barre de progression."
    },
    "report_sources": {
        "question": "D'où viennent les informations des rapports ?",
        "answer": "Prometheus utilise l'API Perplexity pour rechercher des informations actualisées sur le web. Chaque rapport inclut des citations et sources vérifiables."
    },
    "watch_frequency": {
        "question": "À quelle fréquence puis-je recevoir mes veilles ?",
        "answer": "Vous pouvez configurer des veilles quotidiennes, hebdomadaires (lundi ou vendredi), bi-hebdomadaires ou mensuelles. Un système de fréquence personnalisée est également disponible."
    },
    "export_formats": {
        "question": "Quels formats d'export sont disponibles ?",
        "answer": "Actuellement, vous pouvez exporter vos rapports au format PDF professionnel avec mise en page, logo et citations formatées."
    },
    "recommendations_toggle": {
        "question": "Puis-je générer des rapports sans recommandations ?",
        "answer": "Oui, vous pouvez désactiver l'option 'Inclure les recommandations' avant de générer un rapport pour obtenir uniquement l'analyse factuelle."
    },
    "context_document": {
        "question": "À quoi sert le document de contexte ?",
        "answer": "Le document de contexte (pitch deck, business plan, etc.) permet à Prometheus de mieux comprendre votre entreprise et de produire des analyses plus pertinentes et personnalisées."
    }
}

# Fonctions utilitaires pour l'assistant
def get_analysis_type_info(analysis_type: str) -> dict:
    """Retourne les informations sur un type d'analyse"""
    return ANALYSIS_TYPES.get(analysis_type, {})

def get_sector_info(sector: str) -> dict:
    """Retourne les informations sur un secteur"""
    return SECTORS.get(sector, {})

def get_frequency_info(frequency_key: str) -> dict:
    """Retourne les informations sur une fréquence de veille"""
    return WATCH_FREQUENCIES.get(frequency_key, {})

def get_guide(guide_key: str) -> dict:
    """Retourne un guide pas-à-pas"""
    return GUIDES.get(guide_key, {})

def get_faq_answer(faq_key: str) -> dict:
    """Retourne une réponse FAQ"""
    return FAQ.get(faq_key, {})

def build_context_prompt() -> str:
    """Construit le prompt de contexte pour l'assistant avec toute la connaissance app"""
    context = f"""
Tu es l'assistant intelligent de Prometheus, une plateforme d'intelligence stratégique IA.

{APP_DESCRIPTION}

## Types d'analyses disponibles:
"""
    for key, info in ANALYSIS_TYPES.items():
        context += f"\n- **{info['name']}** ({key}): {info['description']}"
    
    context += "\n\n## Secteurs d'activité:"
    for key, info in SECTORS.items():
        context += f"\n- **{info['name']}** ({key}): {info['description']}"
    
    context += "\n\n## Fréquences de veille:"
    for key, info in WATCH_FREQUENCIES.items():
        context += f"\n- **{info['name']}**: {info['description']}"
    
    context += """

## Tes capacités:
1. Tu peux EXPLIQUER comment utiliser Prometheus
2. Tu peux CRÉER des veilles automatisées pour l'utilisateur
3. Tu peux MODIFIER ou SUPPRIMER des veilles existantes
4. Tu peux LANCER la génération de rapports
5. Tu peux LISTER les veilles actives de l'utilisateur

## Instructions:
- Sois concis et professionnel
- Propose toujours des actions concrètes quand c'est pertinent
- Si l'utilisateur demande une action, propose les paramètres et demande confirmation
- Utilise le contexte RAG de l'entreprise pour personnaliser tes réponses
"""
    return context

def get_all_analysis_types() -> list:
    """Retourne la liste de tous les types d'analyses"""
    return list(ANALYSIS_TYPES.keys())

def get_all_sectors() -> list:
    """Retourne la liste de tous les secteurs"""
    return list(SECTORS.keys())

def get_all_frequencies() -> list:
    """Retourne la liste de toutes les fréquences"""
    return list(WATCH_FREQUENCIES.keys())
