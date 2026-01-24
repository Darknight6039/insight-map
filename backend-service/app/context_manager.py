"""
Context Manager - Gestion du contexte utilisateur pour RAG
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger
import hashlib

# Directory for storing user contexts
CONTEXT_DIR = os.getenv("CONTEXT_DIR", "/data/contexts")


def ensure_context_dir():
    """Cree le repertoire de contextes si necessaire"""
    os.makedirs(CONTEXT_DIR, exist_ok=True)


def get_user_context_path(user_id: str) -> str:
    """Retourne le chemin du fichier de contexte pour un utilisateur"""
    ensure_context_dir()
    # Hash user_id for privacy in filenames
    user_hash = hashlib.md5(user_id.encode()).hexdigest()[:12]
    return os.path.join(CONTEXT_DIR, f"context_{user_hash}.json")


def save_text_context(user_id: str, content: str) -> Dict[str, Any]:
    """
    Sauvegarde un contexte texte pour un utilisateur
    
    Args:
        user_id: Identifiant de l'utilisateur
        content: Contenu texte du contexte
    
    Returns:
        Informations sur le contexte sauvegarde
    """
    context_path = get_user_context_path(user_id)
    
    context_data = {
        "type": "text",
        "content": content,
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "preview": content[:100] if content else ""
    }
    
    with open(context_path, 'w', encoding='utf-8') as f:
        json.dump(context_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Context saved for user {user_id[:8]}... (text, {len(content)} chars)")
    
    return {
        "type": "text",
        "preview": context_data["preview"],
        "length": len(content)
    }


def save_document_context(user_id: str, filename: str, content: str, file_type: str) -> Dict[str, Any]:
    """
    Sauvegarde un contexte document pour un utilisateur
    
    Args:
        user_id: Identifiant de l'utilisateur
        filename: Nom du fichier original
        content: Contenu extrait du document
        file_type: Type de fichier (pdf, docx, txt)
    
    Returns:
        Informations sur le contexte sauvegarde
    """
    context_path = get_user_context_path(user_id)
    
    context_data = {
        "type": "document",
        "content": content,
        "filename": filename,
        "file_type": file_type,
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "preview": content[:100] if content else ""
    }
    
    with open(context_path, 'w', encoding='utf-8') as f:
        json.dump(context_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Context saved for user {user_id[:8]}... (document: {filename})")
    
    return {
        "type": "document",
        "name": filename,
        "length": len(content)
    }


def get_user_context(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Recupere le contexte d'un utilisateur
    
    Args:
        user_id: Identifiant de l'utilisateur
    
    Returns:
        Donnees du contexte ou None si inexistant
    """
    context_path = get_user_context_path(user_id)
    
    if not os.path.exists(context_path):
        return None
    
    try:
        with open(context_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading context for user {user_id[:8]}...: {e}")
        return None


def get_user_context_info(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Recupere les infos du contexte (sans le contenu complet)
    
    Args:
        user_id: Identifiant de l'utilisateur
    
    Returns:
        Infos du contexte (type, preview, etc.) ou None
    """
    context = get_user_context(user_id)
    if not context:
        return None
    
    return {
        "type": context.get("type"),
        "name": context.get("filename"),
        "preview": context.get("preview"),
        "created_at": context.get("created_at"),
        "updated_at": context.get("updated_at")
    }


def delete_user_context(user_id: str) -> bool:
    """
    Supprime le contexte d'un utilisateur
    
    Args:
        user_id: Identifiant de l'utilisateur
    
    Returns:
        True si supprime, False sinon
    """
    context_path = get_user_context_path(user_id)
    
    if os.path.exists(context_path):
        try:
            os.remove(context_path)
            logger.info(f"Context deleted for user {user_id[:8]}...")
            return True
        except Exception as e:
            logger.error(f"Error deleting context: {e}")
            return False
    
    return False


def get_context_for_prompt(user_id: str, max_length: int = 2000) -> str:
    """
    Recupere le contexte formate pour inclusion dans un prompt
    
    Args:
        user_id: Identifiant de l'utilisateur
        max_length: Longueur maximale du contexte
    
    Returns:
        Contexte formate ou chaine vide
    """
    context = get_user_context(user_id)
    if not context:
        return ""
    
    content = context.get("content", "")
    if len(content) > max_length:
        content = content[:max_length] + "..."
    
    context_type = context.get("type", "text")
    if context_type == "document":
        filename = context.get("filename", "document")
        return f"""
## CONTEXTE ENTREPRISE (extrait de: {filename})
{content}
"""
    else:
        return f"""
## CONTEXTE ENTREPRISE
{content}
"""


def extract_text_from_pdf(file_path: str) -> str:
    """Extrait le texte d'un fichier PDF"""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return ""


def extract_text_from_docx(file_path: str) -> str:
    """Extrait le texte d'un fichier DOCX"""
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting DOCX text: {e}")
        return ""


def extract_text_from_file(file_path: str, file_type: str) -> str:
    """
    Extrait le texte d'un fichier selon son type
    
    Args:
        file_path: Chemin du fichier
        file_type: Type de fichier (pdf, docx, txt)
    
    Returns:
        Texte extrait
    """
    if file_type == "pdf":
        return extract_text_from_pdf(file_path)
    elif file_type == "docx":
        return extract_text_from_docx(file_path)
    elif file_type == "txt":
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading TXT file: {e}")
            return ""
    else:
        logger.warning(f"Unsupported file type: {file_type}")
        return ""
