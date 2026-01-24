"""
Module de détection automatique de la langue des requêtes utilisateur.
Utilise langdetect pour identifier si la query est en français ou anglais.
"""

from langdetect import detect, LangDetectException
from loguru import logger


def detect_query_language(query: str) -> str:
    """
    Détecte automatiquement la langue de la query utilisateur.
    
    Args:
        query: La requête texte de l'utilisateur
        
    Returns:
        'fr' pour français, 'en' pour anglais.
        Retourne 'fr' par défaut si la langue n'est pas détectable ou autre.
    """
    if not query or len(query.strip()) < 10:
        # Query trop courte pour une détection fiable
        logger.debug(f"Query trop courte pour détection de langue, utilisation du français par défaut")
        return 'fr'
    
    try:
        detected_lang = detect(query)
        logger.info(f"Langue détectée: {detected_lang} pour query: '{query[:50]}...'")
        
        # On supporte français et anglais
        if detected_lang == 'en':
            return 'en'
        elif detected_lang == 'fr':
            return 'fr'
        else:
            # Pour toute autre langue, on utilise le français par défaut
            logger.info(f"Langue '{detected_lang}' non supportée, utilisation du français")
            return 'fr'
            
    except LangDetectException as e:
        logger.warning(f"Erreur de détection de langue: {e}, utilisation du français par défaut")
        return 'fr'
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la détection de langue: {e}")
        return 'fr'

