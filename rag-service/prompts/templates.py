"""
Prompts templates for different types of strategic analysis
"""

PROMPT_SYNTHESE_EXECUTIVE = """
Contexte : {context}

Tu es un consultant senior en stratégie. Analyse ces documents et génère une synthèse exécutive structurée :

**RÉSUMÉ EXÉCUTIF**
- 3 points clés stratégiques
- 2 opportunités prioritaires  
- 2 risques majeurs à surveiller

**RECOMMANDATIONS**
- 3 actions immédiates (0-3 mois)
- 2 initiatives moyen terme (3-12 mois)

**MÉTRIQUES CLÉS**
- Indicateurs à suivre
- Benchmarks sectoriels relevés

Sources citées : [liste des documents analysés]
"""

PROMPT_ANALYSE_CONCURRENTIELLE = """
Contexte : {context}

Tu es un expert en intelligence concurrentielle. Analyse ces informations :

**MAPPING CONCURRENTIEL**
- Acteurs identifiés et positionnements
- Forces/faiblesses par concurrent
- Parts de marché et évolutions

**TENDANCES SECTORIELLES**  
- Mouvements stratégiques observés
- Innovations et disruptions
- Évolution des modèles business

**OPPORTUNITÉS DE DIFFÉRENCIATION**
- Espaces de marché sous-exploités
- Avantages concurrentiels potentiels
- Stratégies de positionnement recommandées

Sources : {sources}
"""

PROMPT_VEILLE_TECHNOLOGIQUE = """
Contexte : {context}

Tu es un expert en innovation technologique. Identifie et analyse :

**INNOVATIONS ÉMERGENTES**
- Technologies disruptives identifiées
- Niveau de maturité (R&D, pilote, déploiement)
- Impact potentiel sur le secteur

**TENDANCES TECH**
- Convergences technologiques
- Standards émergents
- Écosystèmes en formation

**IMPLICATIONS BUSINESS**
- Opportunités de création de valeur
- Risques d'obsolescence
- Investissements recommandés

**ROADMAP TECHNOLOGIQUE**
- Horizon 6 mois, 1 an, 2 ans
- Priorités d'exploration/adoption

Sources consultées : {sources}
"""

PROMPT_ANALYSE_RISQUES = """
Contexte : {context}

Tu es un expert en risk management. Effectue une analyse complète :

**CARTOGRAPHIE DES RISQUES**
- Risques opérationnels identifiés
- Risques stratégiques et de marché
- Risques réglementaires/conformité
- Risques technologiques

**ÉVALUATION**
- Probabilité (Faible/Moyenne/Élevée)
- Impact (Mineur/Modéré/Majeur/Critique)
- Criticité globale par risque

**MESURES DE MITIGATION**
- Actions préventives recommandées
- Plans de contingence
- Indicateurs d'alerte précoce

**PRIORISATION**
- Top 5 des risques critiques
- Timeline de traitement suggérée

Données sources : {sources}
"""

PROMPT_ETUDE_MARCHE = """
Contexte : {context}

Tu es un analyste marché senior. Réalise une étude complète :

**TAILLE ET DYNAMIQUE DU MARCHÉ**
- Valorisation actuelle et projections
- Taux de croissance (CAGR)
- Segmentation client/produit

**ANALYSE DE LA DEMANDE**
- Besoins clients identifiés
- Évolutions comportementales
- Drivers de croissance

**CHAÎNE DE VALEUR**
- Acteurs par maillon
- Marges et modèles économiques
- Points de friction/optimisation

**BARRIÈRES À L'ENTRÉE**
- Réglementaires, technologiques, financières
- Avantages des incumbents
- Opportunités pour nouveaux entrants

**PROJECTIONS & SCÉNARIOS**
- Évolution marché 1-3 ans
- Facteurs d'incertitude
- Scénarios optimiste/pessimiste/réaliste

Sources : {sources}
"""

# Dictionary mapping analysis types to prompts
ANALYSIS_PROMPTS = {
    "synthese_executive": PROMPT_SYNTHESE_EXECUTIVE,
    "analyse_concurrentielle": PROMPT_ANALYSE_CONCURRENTIELLE,
    "veille_technologique": PROMPT_VEILLE_TECHNOLOGIQUE,
    "analyse_risques": PROMPT_ANALYSE_RISQUES,
    "etude_marche": PROMPT_ETUDE_MARCHE
}

def get_prompt_template(analysis_type: str) -> str:
    """Get the prompt template for a specific analysis type"""
    return ANALYSIS_PROMPTS.get(analysis_type, PROMPT_SYNTHESE_EXECUTIVE)

def format_context(passages: list) -> str:
    """Format retrieved passages into context string"""
    if not passages:
        return "Aucun contexte disponible."
    
    context_parts = []
    for i, passage in enumerate(passages, 1):
        text = passage.get("text", "")
        doc_id = passage.get("doc_id", "inconnu")
        score = passage.get("score", 0.0)
        context_parts.append(f"[Passage {i} - Doc {doc_id} - Score: {score:.2f}]\n{text}")
    
    return "\n\n".join(context_parts)

def format_sources(passages: list) -> str:
    """Format sources list from passages"""
    if not passages:
        return "Aucune source disponible."
    
    sources = set()
    for passage in passages:
        doc_id = passage.get("doc_id", "inconnu")
        sources.add(f"Document {doc_id}")
    
    return ", ".join(sorted(sources))
