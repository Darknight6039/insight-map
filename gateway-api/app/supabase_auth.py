"""
=============================================================================
Supabase Authentication Module
=============================================================================
Ce module gère l'authentification via Supabase Auth.
Remplace le module auth.py legacy tout en maintenant la compatibilité API.
"""

import os
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from .supabase_client import (
    get_supabase_client,
    get_supabase_admin_client,
    verify_supabase_token,
    get_supabase_config,
)

# Importer les modèles legacy pour la compatibilité
from .auth import (
    Base, engine, SessionLocal, get_db,
    Invitation, ActivityLog, log_activity,
    InvitationCreate, InvitationResponse,
    ActivityLogResponse, DashboardStats, DashboardCharts,
    generate_invitation_code,
)

# =============================================================================
# SECURITY
# =============================================================================

security = HTTPBearer()

# =============================================================================
# PYDANTIC SCHEMAS
# =============================================================================

class SupabaseUser(BaseModel):
    """Représentation d'un utilisateur Supabase"""
    id: str  # UUID
    email: str
    full_name: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_sign_in_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Schéma de connexion"""
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    """Schéma d'inscription"""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    invitation_code: str

class TokenResponse(BaseModel):
    """Réponse avec token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: SupabaseUser

class UserResponse(BaseModel):
    """Réponse utilisateur simplifiée"""
    id: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: Optional[datetime]

class PasswordResetRequest(BaseModel):
    """Demande de réinitialisation de mot de passe"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Confirmation de réinitialisation"""
    access_token: str
    new_password: str

class PasswordChange(BaseModel):
    """Changement de mot de passe"""
    current_password: str
    new_password: str

class ProfileUpdate(BaseModel):
    """Mise à jour du profil"""
    full_name: Optional[str] = None

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def extract_user_from_supabase(supabase_user) -> SupabaseUser:
    """Convertit un utilisateur Supabase en SupabaseUser"""
    user_metadata = supabase_user.user_metadata or {}
    app_metadata = supabase_user.app_metadata or {}

    return SupabaseUser(
        id=str(supabase_user.id),
        email=supabase_user.email,
        full_name=user_metadata.get("full_name"),
        role=app_metadata.get("role", "user"),
        is_active=app_metadata.get("is_active", True),
        created_at=supabase_user.created_at,
        last_sign_in_at=supabase_user.last_sign_in_at,
    )

def validate_invitation_code(db: Session, code: str, email: Optional[str] = None) -> Invitation:
    """Valide un code d'invitation (réutilise la logique legacy)"""
    invitation = db.query(Invitation).filter(Invitation.code == code).first()

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code d'invitation invalide"
        )

    if invitation.used_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette invitation a déjà été utilisée"
        )

    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette invitation a expiré"
        )

    if invitation.email and email and invitation.email.lower() != email.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette invitation n'est pas valide pour cet email"
        )

    return invitation

# =============================================================================
# AUTHENTICATION DEPENDENCIES
# =============================================================================

async def get_current_user_supabase(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> SupabaseUser:
    """
    Récupère l'utilisateur courant depuis le token JWT Supabase.
    Équivalent de get_current_user() pour Supabase.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    # Vérifier le token
    payload = verify_supabase_token(token)
    if not payload:
        raise credentials_exception

    # Extraire les informations utilisateur
    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    # Récupérer les métadonnées complètes depuis Supabase
    try:
        client = get_supabase_admin_client()
        supabase_user = client.auth.admin.get_user_by_id(user_id)

        if not supabase_user or not supabase_user.user:
            raise credentials_exception

        user = extract_user_from_supabase(supabase_user.user)

        # Vérifier si l'utilisateur est actif
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte désactivé"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting user from Supabase: {e}")
        raise credentials_exception

async def get_current_admin_supabase(
    current_user: SupabaseUser = Depends(get_current_user_supabase)
) -> SupabaseUser:
    """Vérifie que l'utilisateur est admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès administrateur requis"
        )
    return current_user

# =============================================================================
# AUTH OPERATIONS
# =============================================================================

async def login_user(credentials: UserLogin, db: Session) -> TokenResponse:
    """
    Connecte un utilisateur via Supabase Auth.
    """
    try:
        client = get_supabase_client()

        response = client.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })

        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )

        user = extract_user_from_supabase(response.user)

        # Vérifier si l'utilisateur est actif
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte désactivé"
            )

        # Logger l'activité
        log_activity(db, "login", user_id=None, details=f"User {user.email} logged in via Supabase")

        return TokenResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            expires_in=response.session.expires_in or 3600,
            user=user
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

async def register_user(data: UserRegister, db: Session) -> TokenResponse:
    """
    Inscrit un nouvel utilisateur via Supabase Auth.
    Nécessite un code d'invitation valide.
    """
    # Valider l'invitation
    invitation = validate_invitation_code(db, data.invitation_code, data.email)

    try:
        client = get_supabase_admin_client()

        # Créer l'utilisateur avec métadonnées
        response = client.auth.admin.create_user({
            "email": data.email,
            "password": data.password,
            "email_confirm": True,  # Confirmer l'email automatiquement
            "user_metadata": {
                "full_name": data.full_name,
            },
            "app_metadata": {
                "role": "user",
                "is_active": True,
                "invitation_code": data.invitation_code,
            }
        })

        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erreur lors de la création du compte"
            )

        # Marquer l'invitation comme utilisée
        invitation.used_at = datetime.utcnow()
        # Note: used_by référence l'ancien système, on peut le laisser vide
        db.commit()

        # Connecter l'utilisateur pour obtenir les tokens
        public_client = get_supabase_client()
        login_response = public_client.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })

        user = extract_user_from_supabase(response.user)

        # Logger l'activité
        log_activity(db, "register", details=f"New user registered: {user.email}")

        return TokenResponse(
            access_token=login_response.session.access_token,
            refresh_token=login_response.session.refresh_token,
            expires_in=login_response.session.expires_in or 3600,
            user=user
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        if "already registered" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est déjà utilisé"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la création du compte: {str(e)}"
        )

async def logout_user(token: str) -> dict:
    """Déconnecte l'utilisateur"""
    try:
        client = get_supabase_client()
        client.auth.sign_out()
        return {"message": "Déconnexion réussie"}
    except Exception as e:
        print(f"Logout error: {e}")
        return {"message": "Déconnexion réussie"}

async def refresh_session(refresh_token: str) -> TokenResponse:
    """Rafraîchit la session avec le refresh token"""
    try:
        client = get_supabase_client()

        response = client.auth.refresh_session(refresh_token)

        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expirée"
            )

        user = extract_user_from_supabase(response.user)

        return TokenResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            expires_in=response.session.expires_in or 3600,
            user=user
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expirée"
        )

async def request_password_reset(email: str) -> dict:
    """Envoie un email de réinitialisation de mot de passe"""
    try:
        client = get_supabase_client()
        config = get_supabase_config()

        # Utiliser l'URL du site configurée
        redirect_url = os.environ.get("SITE_URL", "http://localhost:3000")

        client.auth.reset_password_email(
            email,
            options={"redirect_to": f"{redirect_url}/reset-password"}
        )

        return {"message": "Si cet email existe, un lien de réinitialisation a été envoyé"}

    except Exception as e:
        print(f"Password reset request error: {e}")
        # Ne pas révéler si l'email existe ou non
        return {"message": "Si cet email existe, un lien de réinitialisation a été envoyé"}

async def reset_password(access_token: str, new_password: str) -> dict:
    """Réinitialise le mot de passe avec le token de réinitialisation"""
    try:
        client = get_supabase_client()

        # Le token de réinitialisation est passé comme access_token
        client.auth.update_user({
            "password": new_password
        })

        return {"message": "Mot de passe mis à jour avec succès"}

    except Exception as e:
        print(f"Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur lors de la réinitialisation du mot de passe"
        )

async def change_password(
    current_user: SupabaseUser,
    current_password: str,
    new_password: str
) -> dict:
    """Change le mot de passe de l'utilisateur connecté"""
    try:
        client = get_supabase_client()

        # Vérifier le mot de passe actuel en tentant une connexion
        try:
            client.auth.sign_in_with_password({
                "email": current_user.email,
                "password": current_password
            })
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mot de passe actuel incorrect"
            )

        # Mettre à jour le mot de passe
        client.auth.update_user({
            "password": new_password
        })

        return {"message": "Mot de passe mis à jour avec succès"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur lors du changement de mot de passe"
        )

async def update_profile(
    current_user: SupabaseUser,
    profile_data: ProfileUpdate
) -> SupabaseUser:
    """Met à jour le profil de l'utilisateur"""
    try:
        client = get_supabase_admin_client()

        update_data = {}
        if profile_data.full_name is not None:
            update_data["user_metadata"] = {"full_name": profile_data.full_name}

        if update_data:
            response = client.auth.admin.update_user_by_id(
                current_user.id,
                update_data
            )

            if response and response.user:
                return extract_user_from_supabase(response.user)

        return current_user

    except Exception as e:
        print(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur lors de la mise à jour du profil"
        )

# =============================================================================
# ADMIN OPERATIONS
# =============================================================================

async def list_users() -> List[UserResponse]:
    """Liste tous les utilisateurs (admin seulement)"""
    try:
        client = get_supabase_admin_client()
        users = client.auth.admin.list_users()

        return [
            UserResponse(
                id=str(u.id),
                email=u.email,
                full_name=(u.user_metadata or {}).get("full_name"),
                role=(u.app_metadata or {}).get("role", "user"),
                is_active=(u.app_metadata or {}).get("is_active", True),
                created_at=u.created_at
            )
            for u in users
        ]

    except Exception as e:
        print(f"List users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des utilisateurs"
        )

async def toggle_user_active(user_id: str, is_active: bool) -> UserResponse:
    """Active/désactive un utilisateur (admin seulement)"""
    try:
        client = get_supabase_admin_client()

        # Récupérer l'utilisateur actuel
        user_response = client.auth.admin.get_user_by_id(user_id)
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )

        # Mettre à jour le statut
        current_app_metadata = user_response.user.app_metadata or {}
        current_app_metadata["is_active"] = is_active

        response = client.auth.admin.update_user_by_id(
            user_id,
            {"app_metadata": current_app_metadata}
        )

        if response and response.user:
            return UserResponse(
                id=str(response.user.id),
                email=response.user.email,
                full_name=(response.user.user_metadata or {}).get("full_name"),
                role=(response.user.app_metadata or {}).get("role", "user"),
                is_active=is_active,
                created_at=response.user.created_at
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Toggle user active error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour du statut"
        )

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'SupabaseUser',
    'UserLogin',
    'UserRegister',
    'TokenResponse',
    'UserResponse',
    'PasswordResetRequest',
    'PasswordResetConfirm',
    'PasswordChange',
    'ProfileUpdate',
    'get_current_user_supabase',
    'get_current_admin_supabase',
    'login_user',
    'register_user',
    'logout_user',
    'refresh_session',
    'request_password_reset',
    'reset_password',
    'change_password',
    'update_profile',
    'list_users',
    'toggle_user_active',
]
