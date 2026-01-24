"""
Système d'actions pour l'assistant intelligent Prometheus

Ce module gère les actions que l'assistant peut proposer et exécuter:
- Création/modification/suppression de veilles
- Génération de rapports
- Consultation des données utilisateur
"""

import httpx
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from loguru import logger
from enum import Enum
import os

# URLs des services
SCHEDULER_URL = os.getenv("SCHEDULER_URL", "http://scheduler-service:8007")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-service:8006")


class ActionType(str, Enum):
    """Types d'actions disponibles"""
    CREATE_WATCH = "create_watch"
    UPDATE_WATCH = "update_watch"
    DELETE_WATCH = "delete_watch"
    LIST_WATCHES = "list_watches"
    GENERATE_REPORT = "generate_report"
    EXPLAIN_FEATURE = "explain_feature"
    VIEW_WATCH_DETAILS = "view_watch_details"


class ActionStatus(str, Enum):
    """Statuts d'exécution d'action"""
    PROPOSED = "proposed"  # Action proposée, en attente de confirmation
    CONFIRMED = "confirmed"  # Action confirmée par l'utilisateur
    EXECUTED = "executed"  # Action exécutée avec succès
    FAILED = "failed"  # Échec de l'exécution
    CANCELLED = "cancelled"  # Action annulée par l'utilisateur


class ProposedAction(BaseModel):
    """Modèle pour une action proposée par l'assistant"""
    action_type: ActionType
    label: str  # Texte du bouton
    description: str  # Description de l'action
    parameters: Dict[str, Any]  # Paramètres de l'action
    requires_confirmation: bool = True  # Nécessite confirmation utilisateur


class ActionResult(BaseModel):
    """Résultat d'exécution d'une action"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Définitions des actions avec leurs schémas
ACTION_DEFINITIONS = {
    ActionType.CREATE_WATCH: {
        "name": "Créer une veille",
        "description": "Crée une nouvelle veille automatisée",
        "parameters": {
            "name": {"type": "string", "required": True, "description": "Nom de la veille"},
            "topic": {"type": "string", "required": True, "description": "Sujet à surveiller"},
            "sector": {"type": "string", "required": False, "default": "general", "description": "Secteur d'activité"},
            "report_type": {"type": "string", "required": False, "default": "synthese_executive", "description": "Type de rapport"},
            "frequency": {"type": "string", "required": False, "default": "weekly_monday", "description": "Fréquence de la veille"},
            "cron_expression": {"type": "string", "required": False, "description": "Expression cron personnalisée"},
            "email_recipients": {"type": "list", "required": True, "description": "Liste des emails destinataires"}
        }
    },
    ActionType.UPDATE_WATCH: {
        "name": "Modifier une veille",
        "description": "Modifie une veille existante",
        "parameters": {
            "watch_id": {"type": "integer", "required": True, "description": "ID de la veille à modifier"},
            "name": {"type": "string", "required": False},
            "topic": {"type": "string", "required": False},
            "sector": {"type": "string", "required": False},
            "report_type": {"type": "string", "required": False},
            "cron_expression": {"type": "string", "required": False},
            "email_recipients": {"type": "list", "required": False},
            "is_active": {"type": "boolean", "required": False}
        }
    },
    ActionType.DELETE_WATCH: {
        "name": "Supprimer une veille",
        "description": "Supprime définitivement une veille",
        "parameters": {
            "watch_id": {"type": "integer", "required": True, "description": "ID de la veille à supprimer"}
        }
    },
    ActionType.LIST_WATCHES: {
        "name": "Lister les veilles",
        "description": "Affiche toutes les veilles de l'utilisateur",
        "parameters": {}
    },
    ActionType.GENERATE_REPORT: {
        "name": "Générer un rapport",
        "description": "Lance la génération d'un rapport d'analyse",
        "parameters": {
            "query": {"type": "string", "required": True, "description": "Sujet du rapport"},
            "analysis_type": {"type": "string", "required": True, "description": "Type d'analyse"},
            "sector": {"type": "string", "required": False, "default": "general"},
            "include_recommendations": {"type": "boolean", "required": False, "default": True}
        }
    },
    ActionType.VIEW_WATCH_DETAILS: {
        "name": "Voir les détails",
        "description": "Affiche les détails d'une veille",
        "parameters": {
            "watch_id": {"type": "integer", "required": True}
        }
    }
}

# Mapping fréquence vers cron
FREQUENCY_TO_CRON = {
    "daily": "0 8 * * *",
    "weekly_monday": "0 8 * * 1",
    "weekly_friday": "0 8 * * 5",
    "biweekly": "0 8 * * 1,4",
    "monthly": "0 8 1 * *"
}


async def execute_action(action: ProposedAction, user_id: str = "default_user") -> ActionResult:
    """
    Exécute une action confirmée par l'utilisateur
    """
    try:
        if action.action_type == ActionType.CREATE_WATCH:
            return await _create_watch(action.parameters, user_id)
        elif action.action_type == ActionType.UPDATE_WATCH:
            return await _update_watch(action.parameters)
        elif action.action_type == ActionType.DELETE_WATCH:
            return await _delete_watch(action.parameters)
        elif action.action_type == ActionType.LIST_WATCHES:
            return await _list_watches()
        elif action.action_type == ActionType.GENERATE_REPORT:
            return await _generate_report(action.parameters)
        elif action.action_type == ActionType.VIEW_WATCH_DETAILS:
            return await _view_watch_details(action.parameters)
        else:
            return ActionResult(
                success=False,
                message="Action non reconnue",
                error=f"Type d'action inconnu: {action.action_type}"
            )
    except Exception as e:
        logger.error(f"Error executing action {action.action_type}: {e}")
        return ActionResult(
            success=False,
            message="Une erreur s'est produite",
            error=str(e)
        )


async def _create_watch(params: Dict[str, Any], user_id: str) -> ActionResult:
    """Crée une nouvelle veille via le scheduler-service"""
    try:
        # #region agent log H3-H4
        logger.info(f"[DEBUG-H4] Create watch entry: params={params}")
        # #endregion
        # Convertir la fréquence en cron si nécessaire
        cron = params.get("cron_expression")
        if not cron and params.get("frequency"):
            cron = FREQUENCY_TO_CRON.get(params["frequency"], "0 8 * * 1")
        elif not cron:
            cron = "0 8 * * 1"  # Default: hebdomadaire lundi
        
        # Préparer les données
        watch_data = {
            "name": params["name"],
            "topic": params["topic"],
            "sector": params.get("sector", "general"),
            "report_type": params.get("report_type", "synthese_executive"),
            "keywords": params.get("keywords", []),
            "sources_preference": "all",
            "cron_expression": cron,
            "email_recipients": params["email_recipients"],
            "is_active": True
        }
        # #region agent log H4
        logger.info(f"[DEBUG-H4] Watch data to send to scheduler: {watch_data}")
        # #endregion
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{SCHEDULER_URL}/watches",
                json=watch_data
            )
            # #region agent log H4
            logger.info(f"[DEBUG-H4] Scheduler response: status={response.status_code}, body={response.text[:500]}")
            # #endregion
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                return ActionResult(
                    success=True,
                    message=f"Veille '{params['name']}' créée avec succès !",
                    data=data
                )
            else:
                return ActionResult(
                    success=False,
                    message="Échec de la création de la veille",
                    error=response.text
                )
    except Exception as e:
        logger.error(f"Error creating watch: {e}")
        return ActionResult(
            success=False,
            message="Erreur lors de la création de la veille",
            error=str(e)
        )


async def _update_watch(params: Dict[str, Any]) -> ActionResult:
    """Modifie une veille existante"""
    try:
        watch_id = params.pop("watch_id")
        
        # Convertir la fréquence en cron si présente
        if params.get("frequency"):
            params["cron_expression"] = FREQUENCY_TO_CRON.get(params.pop("frequency"), params.get("cron_expression"))
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.put(
                f"{SCHEDULER_URL}/watches/{watch_id}",
                json=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return ActionResult(
                    success=True,
                    message=f"Veille mise à jour avec succès !",
                    data=data
                )
            else:
                return ActionResult(
                    success=False,
                    message="Échec de la mise à jour",
                    error=response.text
                )
    except Exception as e:
        logger.error(f"Error updating watch: {e}")
        return ActionResult(
            success=False,
            message="Erreur lors de la mise à jour",
            error=str(e)
        )


async def _delete_watch(params: Dict[str, Any]) -> ActionResult:
    """Supprime une veille"""
    try:
        watch_id = params["watch_id"]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(f"{SCHEDULER_URL}/watches/{watch_id}")
            
            if response.status_code == 200 or response.status_code == 204:
                return ActionResult(
                    success=True,
                    message="Veille supprimée avec succès !",
                    data={"deleted_id": watch_id}
                )
            else:
                return ActionResult(
                    success=False,
                    message="Échec de la suppression",
                    error=response.text
                )
    except Exception as e:
        logger.error(f"Error deleting watch: {e}")
        return ActionResult(
            success=False,
            message="Erreur lors de la suppression",
            error=str(e)
        )


async def _list_watches() -> ActionResult:
    """Liste toutes les veilles"""
    try:
        logger.info(f"Fetching watches from {SCHEDULER_URL}/watches")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{SCHEDULER_URL}/watches")
            logger.info(f"Watches list response status: {response.status_code}")

            if response.status_code == 200:
                watches = response.json()
                logger.info(f"Successfully retrieved {len(watches) if watches else 0} watches")

                if not watches:
                    return ActionResult(
                        success=True,
                        message="Vous n'avez pas encore de veilles configurées.",
                        data={"watches": [], "count": 0}
                    )

                # Formatter la liste
                watch_list = []
                for w in watches:
                    status = "Active" if w.get("is_active") else "Inactive"
                    watch_list.append({
                        "id": w["id"],
                        "name": w["name"],
                        "topic": w["topic"],
                        "status": status,
                        "next_run": w.get("next_run", "Non planifiée")
                    })

                return ActionResult(
                    success=True,
                    message=f"Vous avez {len(watches)} veille(s) configurée(s).",
                    data={"watches": watch_list, "count": len(watches)}
                )
            else:
                logger.error(f"Failed to fetch watches: {response.status_code} - {response.text}")
                return ActionResult(
                    success=False,
                    message=f"Impossible de récupérer les veilles (erreur {response.status_code})",
                    error=response.text
                )
    except httpx.ConnectError as e:
        logger.error(f"Connection error when listing watches: {e}")
        return ActionResult(
            success=False,
            message="Impossible de se connecter au service de veilles. Veuillez réessayer.",
            error=f"Connection error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error listing watches: {e}", exc_info=True)
        return ActionResult(
            success=False,
            message="Erreur lors de la récupération des veilles. Veuillez réessayer.",
            error=str(e)
        )


async def _generate_report(params: Dict[str, Any]) -> ActionResult:
    """Lance la génération d'un rapport (retourne les infos pour le frontend)"""
    # Note: La génération réelle est gérée côté frontend via SSE
    # Cette action prépare juste les paramètres
    return ActionResult(
        success=True,
        message="Prêt à générer le rapport. Cliquez pour lancer l'analyse.",
        data={
            "ready_to_generate": True,
            "query": params["query"],
            "analysis_type": params["analysis_type"],
            "sector": params.get("sector", "general"),
            "include_recommendations": params.get("include_recommendations", True)
        }
    )


async def _view_watch_details(params: Dict[str, Any]) -> ActionResult:
    """Récupère les détails d'une veille spécifique"""
    try:
        watch_id = params["watch_id"]
        logger.info(f"Fetching details for watch ID: {watch_id}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{SCHEDULER_URL}/watches/{watch_id}")
            logger.info(f"Watch details response status: {response.status_code}")

            if response.status_code == 200:
                watch = response.json()
                logger.info(f"Successfully retrieved details for watch: {watch.get('name')}")
                return ActionResult(
                    success=True,
                    message=f"Détails de la veille '{watch['name']}'",
                    data=watch
                )
            elif response.status_code == 404:
                logger.warning(f"Watch not found: {watch_id}")
                return ActionResult(
                    success=False,
                    message=f"Veille avec l'ID {watch_id} non trouvée",
                    error="Watch not found"
                )
            else:
                logger.error(f"Failed to fetch watch details: {response.status_code} - {response.text}")
                return ActionResult(
                    success=False,
                    message=f"Impossible de récupérer les détails (erreur {response.status_code})",
                    error=response.text
                )
    except httpx.ConnectError as e:
        logger.error(f"Connection error when fetching watch details: {e}")
        return ActionResult(
            success=False,
            message="Impossible de se connecter au service de veilles. Veuillez réessayer.",
            error=f"Connection error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error getting watch details: {e}", exc_info=True)
        return ActionResult(
            success=False,
            message="Erreur lors de la récupération des détails. Veuillez réessayer.",
            error=str(e)
        )


def build_action_from_intent(
    intent: str,
    entities: Dict[str, Any],
    user_email: Optional[str] = None
) -> Optional[ProposedAction]:
    """
    Construit une action proposée à partir de l'intention détectée
    """
    # #region agent log H2
    logger.info(f"[DEBUG-H2] Building action: intent={intent}, entities={entities}, user_email={user_email}")
    # #endregion
    if intent == "create_watch":
        # Extraire les paramètres de l'intention
        params = {
            "name": entities.get("watch_name", entities.get("topic", "Nouvelle veille")),
            "topic": entities.get("topic", ""),
            "sector": entities.get("sector", "general"),
            "report_type": entities.get("report_type", "synthese_executive"),
            "frequency": entities.get("frequency", "weekly_monday"),
            "email_recipients": entities.get("emails", [user_email] if user_email else [])
        }
        # #region agent log H2
        logger.info(f"[DEBUG-H2] Create watch params built: {params}")
        # #endregion
        
        return ProposedAction(
            action_type=ActionType.CREATE_WATCH,
            label="Créer cette veille",
            description=f"Créer une veille sur '{params['topic']}'",
            parameters=params,
            requires_confirmation=True
        )
    
    elif intent == "list_watches":
        return ProposedAction(
            action_type=ActionType.LIST_WATCHES,
            label="Voir mes veilles",
            description="Afficher toutes vos veilles configurées",
            parameters={},
            requires_confirmation=False
        )
    
    elif intent == "generate_report":
        params = {
            "query": entities.get("query", entities.get("topic", "")),
            "analysis_type": entities.get("analysis_type", "synthese_executive"),
            "sector": entities.get("sector", "general"),
            "include_recommendations": entities.get("include_recommendations", True)
        }
        
        return ProposedAction(
            action_type=ActionType.GENERATE_REPORT,
            label="Générer le rapport",
            description=f"Générer un rapport sur '{params['query']}'",
            parameters=params,
            requires_confirmation=True
        )
    
    elif intent == "delete_watch":
        if "watch_id" in entities:
            return ProposedAction(
                action_type=ActionType.DELETE_WATCH,
                label="Supprimer la veille",
                description="Supprimer définitivement cette veille",
                parameters={"watch_id": entities["watch_id"]},
                requires_confirmation=True
            )
    
    elif intent == "update_watch":
        if "watch_id" in entities:
            params = {"watch_id": entities["watch_id"]}
            # Ajouter les champs à modifier
            for field in ["name", "topic", "sector", "report_type", "frequency", "is_active"]:
                if field in entities:
                    params[field] = entities[field]
            
            return ProposedAction(
                action_type=ActionType.UPDATE_WATCH,
                label="Modifier la veille",
                description="Appliquer les modifications",
                parameters=params,
                requires_confirmation=True
            )
    
    return None


def get_action_definition(action_type: ActionType) -> Dict:
    """Retourne la définition d'une action"""
    return ACTION_DEFINITIONS.get(action_type, {})
