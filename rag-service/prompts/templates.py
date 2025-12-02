"""
Prompts templates for different types of strategic analysis
Format APA obligatoire - Sources institutionnelles et cabinets de conseil uniquement
"""

# Instructions de sources communes à tous les templates
SOURCES_INSTRUCTION = """
## SOURCES AUTORISÉES (EXCLUSIVEMENT)

### INSTITUTIONS OFFICIELLES (70% minimum)
- France : INSEE, Banque de France, ACPR, AMF, DARES, DGE, France Stratégie
- Europe : BCE, EBA, ESMA, Commission européenne, Eurostat
- International : OCDE, FMI, BRI, Banque Mondiale

### CABINETS DE CONSEIL (30% maximum)
- Stratégie : McKinsey & Company, BCG, Bain & Company
- Audit/Conseil : Deloitte, PwC, EY, KPMG
- Tech : Gartner, IDC, Forrester (analyses tech uniquement)

### SOURCES STRICTEMENT EXCLUES
- Médias et presse (Les Échos, Bloomberg, FT, Reuters, etc.)
- Blogs, forums, réseaux sociaux
- Entreprises privées (hors cabinets listés)

## FORMAT CITATION APA OBLIGATOIRE
- Citation inline : (Auteur, Année) - Ex: "Le marché croît de 15% (INSEE, 2024)"
- Sources multiples : (Source1, 2024; Source2, 2024)
- Section finale obligatoire : "## 📚 Références Bibliographiques" au format APA complet
"""

PROMPT_SYNTHESE_EXECUTIVE = """
Contexte : {context}

Tu es un consultant senior en stratégie. Analyse ces documents et génère une synthèse exécutive structurée.

""" + SOURCES_INSTRUCTION + """

**RÉSUMÉ EXÉCUTIF**
- 3 points clés stratégiques avec données chiffrées (Source, Année)
- 2 opportunités prioritaires avec potentiel estimé (Source, Année)
- 2 risques majeurs à surveiller avec probabilité (Source, Année)

**RECOMMANDATIONS**
- 3 actions immédiates (0-3 mois) avec ROI estimé (Source, Année)
- 2 initiatives moyen terme (3-12 mois) avec budget (Source, Année)

**MÉTRIQUES CLÉS**
- Indicateurs à suivre avec valeurs cibles (Source, Année)
- Benchmarks sectoriels relevés (Source, Année)

## 📚 Références Bibliographiques
[Liste complète des sources au format APA : Auteur. (Année). Titre. Publication. URL]
"""

PROMPT_ANALYSE_CONCURRENTIELLE = """
Contexte : {context}

Tu es un expert en intelligence concurrentielle. Analyse ces informations.

""" + SOURCES_INSTRUCTION + """

**MAPPING CONCURRENTIEL**
- Acteurs identifiés et positionnements (Source, Année)
- Forces/faiblesses par concurrent (Source, Année)
- Parts de marché et évolutions (Source, Année)

**TENDANCES SECTORIELLES**  
- Mouvements stratégiques observés (Source, Année)
- Innovations et disruptions (Source, Année)
- Évolution des modèles business (Source, Année)

**OPPORTUNITÉS DE DIFFÉRENCIATION**
- Espaces de marché sous-exploités (Source, Année)
- Avantages concurrentiels potentiels (Source, Année)
- Stratégies de positionnement recommandées (Source, Année)

## 📚 Références Bibliographiques
[Liste complète des sources au format APA : Auteur. (Année). Titre. Publication. URL]
"""

PROMPT_VEILLE_TECHNOLOGIQUE = """
Contexte : {context}

Tu es un expert en innovation technologique. Identifie et analyse.

""" + SOURCES_INSTRUCTION + """

Note: Pour les analyses tech, privilégie Gartner, IDC, Forrester comme sources principales.

**INNOVATIONS ÉMERGENTES**
- Technologies disruptives identifiées (Gartner, Année) ou (IDC, Année)
- Niveau de maturité (R&D, pilote, déploiement) (Source, Année)
- Impact potentiel sur le secteur (Source, Année)

**TENDANCES TECH**
- Convergences technologiques (Source, Année)
- Standards émergents (Source, Année)
- Écosystèmes en formation (Source, Année)

**IMPLICATIONS BUSINESS**
- Opportunités de création de valeur (McKinsey, Année) ou (BCG, Année)
- Risques d'obsolescence (Source, Année)
- Investissements recommandés avec ROI estimé (Source, Année)

**ROADMAP TECHNOLOGIQUE**
- Horizon 6 mois, 1 an, 2 ans (Source, Année)
- Priorités d'exploration/adoption (Source, Année)

## 📚 Références Bibliographiques
[Liste complète des sources au format APA : Auteur. (Année). Titre. Publication. URL]
"""

PROMPT_ANALYSE_RISQUES = """
Contexte : {context}

Tu es un expert en risk management. Effectue une analyse complète.

""" + SOURCES_INSTRUCTION + """

**CARTOGRAPHIE DES RISQUES**
- Risques opérationnels identifiés (Source, Année)
- Risques stratégiques et de marché (Source, Année)
- Risques réglementaires/conformité (ACPR, Année) ou (AMF, Année)
- Risques technologiques (Source, Année)

**ÉVALUATION**
- Probabilité (Faible/Moyenne/Élevée) avec données (Source, Année)
- Impact (Mineur/Modéré/Majeur/Critique) quantifié (Source, Année)
- Criticité globale par risque (Source, Année)

**MESURES DE MITIGATION**
- Actions préventives recommandées avec coûts (Source, Année)
- Plans de contingence (Source, Année)
- Indicateurs d'alerte précoce (Source, Année)

**PRIORISATION**
- Top 5 des risques critiques avec quantification (Source, Année)
- Timeline de traitement suggérée (Source, Année)

## 📚 Références Bibliographiques
[Liste complète des sources au format APA : Auteur. (Année). Titre. Publication. URL]
"""

PROMPT_ETUDE_MARCHE = """
Contexte : {context}

Tu es un analyste marché senior. Réalise une étude complète.

""" + SOURCES_INSTRUCTION + """

**TAILLE ET DYNAMIQUE DU MARCHÉ**
- Valorisation actuelle et projections (INSEE, Année) ou (Eurostat, Année)
- Taux de croissance (CAGR) (Source, Année)
- Segmentation client/produit (Source, Année)

**ANALYSE DE LA DEMANDE**
- Besoins clients identifiés (Source, Année)
- Évolutions comportementales (Source, Année)
- Drivers de croissance (McKinsey, Année) ou (BCG, Année)

**CHAÎNE DE VALEUR**
- Acteurs par maillon (Source, Année)
- Marges et modèles économiques (Source, Année)
- Points de friction/optimisation (Source, Année)

**BARRIÈRES À L'ENTRÉE**
- Réglementaires, technologiques, financières (Source, Année)
- Avantages des incumbents (Source, Année)
- Opportunités pour nouveaux entrants (Source, Année)

**PROJECTIONS & SCÉNARIOS**
- Évolution marché 1-3 ans (Source, Année)
- Facteurs d'incertitude (Source, Année)
- Scénarios optimiste/pessimiste/réaliste (Source, Année)

## 📚 Références Bibliographiques
[Liste complète des sources au format APA : Auteur. (Année). Titre. Publication. URL]
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
