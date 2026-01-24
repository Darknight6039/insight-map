"""
RAG Memory - Memoire conversationnelle pour Prometheus
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
import hashlib

# Directory for storing conversation history
MEMORY_DIR = os.getenv("MEMORY_DIR", "/data/memory")
MAX_HISTORY_ITEMS = 50  # Maximum number of conversations to keep per user


def ensure_memory_dir():
    """Cree le repertoire de memoire si necessaire"""
    os.makedirs(MEMORY_DIR, exist_ok=True)


def get_user_memory_path(user_id: str) -> str:
    """Retourne le chemin du fichier de memoire pour un utilisateur"""
    ensure_memory_dir()
    user_hash = hashlib.md5(user_id.encode()).hexdigest()[:12]
    return os.path.join(MEMORY_DIR, f"memory_{user_hash}.json")


def load_user_memory(user_id: str) -> List[Dict[str, Any]]:
    """
    Charge l'historique de memoire d'un utilisateur
    
    Args:
        user_id: Identifiant de l'utilisateur
    
    Returns:
        Liste des conversations passees
    """
    memory_path = get_user_memory_path(user_id)
    
    if not os.path.exists(memory_path):
        return []
    
    try:
        with open(memory_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("conversations", [])
    except Exception as e:
        logger.error(f"Error loading memory for user {user_id[:8]}...: {e}")
        return []


def save_user_memory(user_id: str, conversations: List[Dict[str, Any]]) -> bool:
    """
    Sauvegarde l'historique de memoire d'un utilisateur
    
    Args:
        user_id: Identifiant de l'utilisateur
        conversations: Liste des conversations
    
    Returns:
        True si sauvegarde reussie
    """
    memory_path = get_user_memory_path(user_id)
    
    # Limiter le nombre de conversations
    if len(conversations) > MAX_HISTORY_ITEMS:
        conversations = conversations[-MAX_HISTORY_ITEMS:]
    
    try:
        data = {
            "user_id": user_id,
            "updated_at": datetime.now().isoformat(),
            "conversations": conversations
        }
        with open(memory_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving memory for user {user_id[:8]}...: {e}")
        return False


def add_conversation(
    user_id: str,
    query: str,
    response: str,
    analysis_type: str,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Ajoute une conversation a l'historique de l'utilisateur
    
    Args:
        user_id: Identifiant de l'utilisateur
        query: Requete de l'utilisateur
        response: Reponse generee
        analysis_type: Type d'analyse
        metadata: Metadonnees optionnelles
    
    Returns:
        True si ajout reussi
    """
    conversations = load_user_memory(user_id)
    
    new_conversation = {
        "id": hashlib.md5(f"{user_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16],
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "response_summary": response[:500] if len(response) > 500 else response,
        "analysis_type": analysis_type,
        "metadata": metadata or {}
    }
    
    conversations.append(new_conversation)
    return save_user_memory(user_id, conversations)


def get_relevant_history(
    user_id: str,
    query: str,
    max_items: int = 5
) -> List[Dict[str, Any]]:
    """
    Recupere l'historique pertinent pour une requete
    
    Args:
        user_id: Identifiant de l'utilisateur
        query: Requete actuelle
        max_items: Nombre maximum d'elements a retourner
    
    Returns:
        Liste des conversations pertinentes
    """
    conversations = load_user_memory(user_id)
    
    if not conversations:
        return []
    
    # Simple keyword matching for now
    # In production, use vector similarity search
    query_words = set(query.lower().split())
    
    scored_conversations = []
    for conv in conversations:
        conv_words = set(conv.get("query", "").lower().split())
        # Score = intersection of words
        score = len(query_words & conv_words)
        if score > 0:
            scored_conversations.append((score, conv))
    
    # Sort by score descending
    scored_conversations.sort(key=lambda x: x[0], reverse=True)
    
    # Return top items
    return [conv for _, conv in scored_conversations[:max_items]]


def get_history_for_prompt(user_id: str, query: str, max_length: int = 1000) -> str:
    """
    Recupere l'historique formate pour inclusion dans un prompt
    
    Args:
        user_id: Identifiant de l'utilisateur
        query: Requete actuelle
        max_length: Longueur maximale du texte
    
    Returns:
        Historique formate ou chaine vide
    """
    relevant = get_relevant_history(user_id, query, max_items=3)
    
    if not relevant:
        return ""
    
    history_parts = []
    total_length = 0
    
    for conv in relevant:
        entry = f"- {conv.get('analysis_type', 'analyse')}: {conv.get('query', '')[:100]}"
        if total_length + len(entry) > max_length:
            break
        history_parts.append(entry)
        total_length += len(entry)
    
    if not history_parts:
        return ""
    
    return f"""
## HISTORIQUE DES ANALYSES PRECEDENTES
{chr(10).join(history_parts)}
"""


def get_full_history(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Recupere l'historique complet d'un utilisateur
    
    Args:
        user_id: Identifiant de l'utilisateur
        limit: Nombre maximum d'elements
    
    Returns:
        Liste des conversations
    """
    conversations = load_user_memory(user_id)
    # Sort by timestamp descending (most recent first)
    conversations.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return conversations[:limit]


def clear_user_memory(user_id: str) -> bool:
    """
    Supprime l'historique d'un utilisateur
    
    Args:
        user_id: Identifiant de l'utilisateur
    
    Returns:
        True si suppression reussie
    """
    memory_path = get_user_memory_path(user_id)
    
    if os.path.exists(memory_path):
        try:
            os.remove(memory_path)
            logger.info(f"Memory cleared for user {user_id[:8]}...")
            return True
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")
            return False
    
    return False


def search_history(
    user_id: str,
    search_query: str,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Recherche dans l'historique d'un utilisateur
    
    Args:
        user_id: Identifiant de l'utilisateur
        search_query: Terme de recherche
        max_results: Nombre maximum de resultats
    
    Returns:
        Liste des conversations correspondantes
    """
    conversations = load_user_memory(user_id)
    search_terms = search_query.lower().split()
    
    results = []
    for conv in conversations:
        text = f"{conv.get('query', '')} {conv.get('response_summary', '')}".lower()
        if any(term in text for term in search_terms):
            results.append(conv)
    
    # Sort by relevance (number of matching terms)
    results.sort(
        key=lambda c: sum(
            1 for term in search_terms 
            if term in f"{c.get('query', '')} {c.get('response_summary', '')}".lower()
        ),
        reverse=True
    )
    
    return results[:max_results]
