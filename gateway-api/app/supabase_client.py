"""
=============================================================================
Supabase Client Configuration
=============================================================================
Ce module initialise et configure le client Supabase pour le backend.
Utilisé pour l'authentification et l'accès aux données via Supabase.
"""

import os
from typing import Optional
from functools import lru_cache

# =============================================================================
# CONFIGURATION
# =============================================================================

class SupabaseConfig:
    """Configuration Supabase depuis les variables d'environnement"""

    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL", "http://supabase-kong:8000")
        # Direct GoTrue URL for admin operations (bypasses Kong)
        self.gotrue_url = os.environ.get("GOTRUE_URL", "http://supabase-auth:9999")
        self.anon_key = os.environ.get("SUPABASE_ANON_KEY", "")
        self.service_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        self.jwt_secret = os.environ.get("SUPABASE_JWT_SECRET", "")

        # Validation
        if not self.service_key:
            print("WARNING: SUPABASE_SERVICE_KEY not set")
        if not self.jwt_secret:
            print("WARNING: SUPABASE_JWT_SECRET not set")

    @property
    def is_configured(self) -> bool:
        """Vérifie si Supabase est correctement configuré"""
        return bool(self.url and self.service_key and self.jwt_secret)

@lru_cache()
def get_supabase_config() -> SupabaseConfig:
    """Singleton pour la configuration Supabase"""
    return SupabaseConfig()

# =============================================================================
# CLIENT INITIALIZATION
# =============================================================================

_supabase_client = None
_supabase_admin_client = None

def get_supabase_client():
    """
    Retourne le client Supabase public (avec anon key).
    Utilisé pour les opérations côté client proxifiées via Kong.
    """
    global _supabase_client

    if _supabase_client is None:
        try:
            from supabase import create_client, Client
            config = get_supabase_config()
            _supabase_client = create_client(config.url, config.anon_key)
        except ImportError:
            raise ImportError("supabase package not installed. Run: pip install supabase")
        except Exception as e:
            print(f"ERROR: Failed to initialize Supabase client: {e}")
            raise

    return _supabase_client

def get_supabase_admin_client():
    """
    Retourne le client Supabase admin (avec service_role key).
    Utilisé pour les opérations backend qui nécessitent un accès privilégié.
    IMPORTANT: Ne jamais exposer ce client côté frontend!
    """
    global _supabase_admin_client

    if _supabase_admin_client is None:
        try:
            from supabase import create_client, Client
            config = get_supabase_config()
            _supabase_admin_client = create_client(config.url, config.service_key)
        except ImportError:
            raise ImportError("supabase package not installed. Run: pip install supabase")
        except Exception as e:
            print(f"ERROR: Failed to initialize Supabase admin client: {e}")
            raise

    return _supabase_admin_client

# =============================================================================
# HEALTH CHECK
# =============================================================================

async def check_supabase_health() -> dict:
    """Vérifie la connexion à Supabase"""
    config = get_supabase_config()

    result = {
        "configured": config.is_configured,
        "url": config.url,
        "auth_available": False,
        "database_available": False,
        "error": None
    }

    if not config.is_configured:
        result["error"] = "Supabase not properly configured"
        return result

    try:
        client = get_supabase_admin_client()

        # Test auth
        try:
            # Tenter de lister les utilisateurs (nécessite service_role)
            users = client.auth.admin.list_users()
            result["auth_available"] = True
            result["user_count"] = len(users) if users else 0
        except Exception as e:
            result["auth_error"] = str(e)

        # Test database
        try:
            # Tenter une requête simple
            response = client.table("user_id_mapping").select("count", count="exact").limit(1).execute()
            result["database_available"] = True
        except Exception as e:
            # La table peut ne pas exister encore
            result["database_error"] = str(e)

    except Exception as e:
        result["error"] = str(e)

    return result

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def decode_jwt_token(token: str) -> Optional[dict]:
    """
    Décode un JWT Supabase sans vérification (pour inspection).
    Pour la vérification complète, utilisez verify_supabase_token().
    """
    try:
        import base64
        import json

        # Split le token
        parts = token.split('.')
        if len(parts) != 3:
            return None

        # Décoder le payload (partie 2)
        payload = parts[1]
        # Ajouter le padding si nécessaire
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding

        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)

    except Exception:
        return None

def verify_supabase_token(token: str) -> Optional[dict]:
    """
    Vérifie et décode un JWT Supabase avec validation de signature.
    Retourne le payload si valide, None sinon.
    """
    try:
        from jose import jwt, JWTError

        config = get_supabase_config()

        # First try with audience validation
        try:
            payload = jwt.decode(
                token,
                config.jwt_secret,
                algorithms=["HS256"],
                audience="authenticated"
            )
            return payload
        except JWTError as e:
            # If audience fails, try without audience validation for debugging
            print(f"JWT verification with audience failed: {e}")

            # Try to decode without audience check to see if it's an audience issue
            try:
                payload_no_aud = jwt.decode(
                    token,
                    config.jwt_secret,
                    algorithms=["HS256"],
                    options={"verify_aud": False}
                )
                print(f"Token decoded WITHOUT audience check. Payload aud: {payload_no_aud.get('aud')}")
                # If it works without audience check, the token is valid but has wrong/missing audience
                if payload_no_aud.get('aud') == 'authenticated':
                    return payload_no_aud
                print(f"Token has unexpected audience: {payload_no_aud.get('aud')}")
                return None
            except JWTError as e2:
                print(f"JWT verification without audience also failed: {e2}")
                return None

    except Exception as e:
        print(f"Token verification error: {e}")
        return None

# =============================================================================
# DATABASE HELPERS
# =============================================================================

def get_user_by_id(user_id: str) -> Optional[dict]:
    """Récupère un utilisateur Supabase par son UUID"""
    try:
        client = get_supabase_admin_client()
        user = client.auth.admin.get_user_by_id(user_id)
        return user.user if user else None
    except Exception as e:
        print(f"Error fetching user {user_id}: {e}")
        return None

def get_user_by_email(email: str) -> Optional[dict]:
    """Récupère un utilisateur Supabase par son email"""
    try:
        client = get_supabase_admin_client()
        # Lister tous les utilisateurs et filtrer par email
        users = client.auth.admin.list_users()
        for user in users:
            if user.email == email:
                return user
        return None
    except Exception as e:
        print(f"Error fetching user by email {email}: {e}")
        return None

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'SupabaseConfig',
    'get_supabase_config',
    'get_supabase_client',
    'get_supabase_admin_client',
    'check_supabase_health',
    'decode_jwt_token',
    'verify_supabase_token',
    'get_user_by_id',
    'get_user_by_email',
]
