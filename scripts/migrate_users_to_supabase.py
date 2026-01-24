#!/usr/bin/env python3
"""
=============================================================================
Script de Migration des Utilisateurs vers Supabase Auth
=============================================================================
Ce script migre les utilisateurs existants de l'ancien système PostgreSQL
vers Supabase Auth, en conservant les hashes bcrypt des mots de passe.

Usage:
    # Mode DRY RUN (simulation)
    python migrate_users_to_supabase.py

    # Mode PRODUCTION (migration réelle)
    DRY_RUN=false python migrate_users_to_supabase.py

Environment Variables:
    OLD_DATABASE_URL: URL de l'ancienne base PostgreSQL
    SUPABASE_URL: URL de l'API Supabase
    SUPABASE_SERVICE_KEY: Clé service_role pour l'API Admin
    DRY_RUN: "true" pour simulation, "false" pour migration réelle
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

# =============================================================================
# CONFIGURATION
# =============================================================================

class MigrationMode(Enum):
    DRY_RUN = "dry_run"
    PRODUCTION = "production"

@dataclass
class MigrationConfig:
    """Configuration de la migration"""
    old_database_url: str
    supabase_url: str
    supabase_service_key: str
    mode: MigrationMode

    @classmethod
    def from_env(cls) -> 'MigrationConfig':
        dry_run = os.environ.get("DRY_RUN", "true").lower() == "true"
        return cls(
            old_database_url=os.environ.get(
                "OLD_DATABASE_URL",
                "postgresql://insight_user:insight_password_2024@localhost:5432/insight_db"
            ),
            supabase_url=os.environ.get("SUPABASE_URL", "http://localhost:8000"),
            supabase_service_key=os.environ.get("SUPABASE_SERVICE_KEY", ""),
            mode=MigrationMode.DRY_RUN if dry_run else MigrationMode.PRODUCTION
        )

@dataclass
class User:
    """Représentation d'un utilisateur à migrer"""
    id: int
    email: str
    password_hash: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

@dataclass
class MigrationResult:
    """Résultat de la migration d'un utilisateur"""
    user: User
    success: bool
    supabase_uuid: Optional[str] = None
    error_message: Optional[str] = None

# =============================================================================
# DATABASE OPERATIONS
# =============================================================================

def get_old_db_connection(config: MigrationConfig):
    """Connexion à l'ancienne base de données"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        return psycopg2.connect(config.old_database_url, cursor_factory=RealDictCursor)
    except ImportError:
        print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
        sys.exit(1)

def fetch_users_from_old_db(config: MigrationConfig) -> List[User]:
    """Récupère tous les utilisateurs de l'ancienne base"""
    conn = get_old_db_connection(config)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id,
                    email,
                    password_hash,
                    full_name,
                    role,
                    is_active,
                    created_at,
                    last_login
                FROM users
                ORDER BY created_at ASC
            """)
            rows = cur.fetchall()
            return [
                User(
                    id=row['id'],
                    email=row['email'],
                    password_hash=row['password_hash'],
                    full_name=row['full_name'],
                    role=row['role'],
                    is_active=row['is_active'],
                    created_at=row['created_at'],
                    last_login=row['last_login']
                )
                for row in rows
            ]
    finally:
        conn.close()

# =============================================================================
# SUPABASE OPERATIONS
# =============================================================================

def get_supabase_client(config: MigrationConfig):
    """Crée un client Supabase Admin"""
    try:
        from supabase import create_client, Client
        return create_client(config.supabase_url, config.supabase_service_key)
    except ImportError:
        print("ERROR: supabase not installed. Run: pip install supabase")
        sys.exit(1)

def migrate_user_to_supabase(
    client,
    user: User,
    config: MigrationConfig
) -> MigrationResult:
    """Migre un utilisateur vers Supabase Auth"""

    if config.mode == MigrationMode.DRY_RUN:
        print(f"  [DRY RUN] Would create user: {user.email}")
        print(f"            Role: {user.role}")
        print(f"            Hash: {user.password_hash[:30]}...")
        return MigrationResult(
            user=user,
            success=True,
            supabase_uuid="dry-run-uuid"
        )

    try:
        # Préparer les métadonnées utilisateur
        user_metadata = {
            "full_name": user.full_name,
            "old_user_id": user.id,
            "migrated_at": datetime.utcnow().isoformat(),
        }
        if user.last_login:
            user_metadata["last_login_legacy"] = user.last_login.isoformat()

        app_metadata = {
            "role": user.role,
            "is_active": user.is_active,
            "legacy_system": "insight_mvp_v1",
            "provider": "email",
            "providers": ["email"]
        }

        # Créer l'utilisateur via l'API Admin
        response = client.auth.admin.create_user({
            "email": user.email,
            "password_hash": user.password_hash,
            "email_confirm": True,
            "user_metadata": user_metadata,
            "app_metadata": app_metadata
        })

        if response and response.user:
            return MigrationResult(
                user=user,
                success=True,
                supabase_uuid=response.user.id
            )
        else:
            return MigrationResult(
                user=user,
                success=False,
                error_message="No user returned from Supabase"
            )

    except Exception as e:
        return MigrationResult(
            user=user,
            success=False,
            error_message=str(e)
        )

def check_user_exists_in_supabase(client, email: str) -> bool:
    """Vérifie si un utilisateur existe déjà dans Supabase"""
    try:
        # Utiliser l'API admin pour lister les utilisateurs
        response = client.auth.admin.list_users()
        for supabase_user in response:
            if supabase_user.email == email:
                return True
        return False
    except Exception:
        return False

# =============================================================================
# MAPPING TABLE OPERATIONS
# =============================================================================

def create_mapping_table(config: MigrationConfig) -> None:
    """Crée la table de mapping si elle n'existe pas"""
    if config.mode == MigrationMode.DRY_RUN:
        print("  [DRY RUN] Would create mapping table: user_id_mapping")
        return

    conn = get_old_db_connection(config)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_id_mapping (
                    old_user_id INTEGER PRIMARY KEY,
                    supabase_user_id UUID NOT NULL UNIQUE,
                    email VARCHAR(255) NOT NULL,
                    migrated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            conn.commit()
            print("  Table user_id_mapping créée/vérifiée")
    finally:
        conn.close()

def save_mapping(
    config: MigrationConfig,
    old_id: int,
    supabase_uuid: str,
    email: str
) -> None:
    """Sauvegarde le mapping old_id -> supabase_uuid"""
    if config.mode == MigrationMode.DRY_RUN:
        return

    conn = get_old_db_connection(config)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_id_mapping (old_user_id, supabase_user_id, email)
                VALUES (%s, %s, %s)
                ON CONFLICT (old_user_id) DO UPDATE
                SET supabase_user_id = EXCLUDED.supabase_user_id,
                    email = EXCLUDED.email,
                    migrated_at = NOW()
            """, (old_id, supabase_uuid, email))
            conn.commit()
    finally:
        conn.close()

# =============================================================================
# MIGRATION REPORT
# =============================================================================

def generate_report(results: List[MigrationResult], config: MigrationConfig) -> str:
    """Génère un rapport de migration"""
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    report = []
    report.append("=" * 80)
    report.append("RAPPORT DE MIGRATION SUPABASE")
    report.append("=" * 80)
    report.append(f"Date: {datetime.utcnow().isoformat()}")
    report.append(f"Mode: {config.mode.value.upper()}")
    report.append("")
    report.append("-" * 80)
    report.append("RÉSUMÉ")
    report.append("-" * 80)
    report.append(f"Total utilisateurs: {len(results)}")
    report.append(f"Succès: {len(successful)}")
    report.append(f"Échecs: {len(failed)}")
    report.append("")

    if successful:
        report.append("-" * 80)
        report.append("UTILISATEURS MIGRÉS")
        report.append("-" * 80)
        for r in successful:
            uuid_display = r.supabase_uuid[:8] if r.supabase_uuid else "N/A"
            report.append(f"  ✓ {r.user.email} (old_id={r.user.id}) -> {uuid_display}...")

    if failed:
        report.append("")
        report.append("-" * 80)
        report.append("ÉCHECS DE MIGRATION")
        report.append("-" * 80)
        for r in failed:
            report.append(f"  ✗ {r.user.email}: {r.error_message}")

    report.append("")
    report.append("=" * 80)

    return "\n".join(report)

# =============================================================================
# MAIN
# =============================================================================

def main():
    """Point d'entrée principal"""
    print("=" * 80)
    print("MIGRATION DES UTILISATEURS VERS SUPABASE AUTH")
    print("=" * 80)

    # Charger la configuration
    config = MigrationConfig.from_env()
    print(f"\nMode: {config.mode.value.upper()}")
    print(f"Old Database: {config.old_database_url.split('@')[1] if '@' in config.old_database_url else 'N/A'}")
    print(f"Supabase URL: {config.supabase_url}")

    if not config.supabase_service_key:
        print("\nERROR: SUPABASE_SERVICE_KEY non définie")
        print("Définissez la variable d'environnement SUPABASE_SERVICE_KEY")
        sys.exit(1)

    # Créer le client Supabase
    print("\n" + "-" * 80)
    print("[1/5] Connexion à Supabase...")
    client = get_supabase_client(config)
    print("  ✓ Client Supabase initialisé")

    # Récupérer les utilisateurs existants
    print("\n" + "-" * 80)
    print("[2/5] Récupération des utilisateurs de l'ancienne base...")
    try:
        users = fetch_users_from_old_db(config)
        print(f"  ✓ {len(users)} utilisateurs trouvés")
    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        sys.exit(1)

    if not users:
        print("\nAucun utilisateur à migrer.")
        return

    # Afficher les utilisateurs
    print("\n  Utilisateurs à migrer:")
    for user in users:
        status = "actif" if user.is_active else "inactif"
        print(f"    - {user.email} (role: {user.role}, {status})")

    # Confirmation en mode production
    if config.mode == MigrationMode.PRODUCTION:
        print("\n" + "!" * 80)
        print("ATTENTION: Mode PRODUCTION - Les utilisateurs seront réellement migrés!")
        print("!" * 80)
        confirm = input("\nTapez 'MIGRATE' pour confirmer: ")
        if confirm != "MIGRATE":
            print("Migration annulée.")
            return

    # Créer la table de mapping
    print("\n" + "-" * 80)
    print("[3/5] Création de la table de mapping...")
    create_mapping_table(config)

    # Migrer les utilisateurs
    print("\n" + "-" * 80)
    print("[4/5] Migration des utilisateurs...")
    results: List[MigrationResult] = []

    for user in users:
        print(f"\n  Traitement de {user.email}...")

        # Vérifier si l'utilisateur existe déjà
        if config.mode == MigrationMode.PRODUCTION:
            if check_user_exists_in_supabase(client, user.email):
                print(f"    ⚠ Utilisateur déjà existant dans Supabase, ignoré")
                results.append(MigrationResult(
                    user=user,
                    success=True,
                    error_message="Already exists in Supabase"
                ))
                continue

        # Migrer l'utilisateur
        result = migrate_user_to_supabase(client, user, config)
        results.append(result)

        if result.success:
            print(f"    ✓ Migré avec succès")
            if result.supabase_uuid and config.mode == MigrationMode.PRODUCTION:
                save_mapping(config, user.id, result.supabase_uuid, user.email)
                print(f"    ✓ Mapping sauvegardé: {user.id} -> {result.supabase_uuid[:8]}...")
        else:
            print(f"    ✗ Échec: {result.error_message}")

    # Générer le rapport
    print("\n" + "-" * 80)
    print("[5/5] Génération du rapport...")
    report = generate_report(results, config)

    # Sauvegarder le rapport
    report_path = f"/Users/isaiaebongue/insight-mvp/scripts/migration_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
    if config.mode == MigrationMode.PRODUCTION:
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"  ✓ Rapport sauvegardé: {report_path}")

    # Afficher le rapport
    print("\n" + report)

    # Instructions finales
    if config.mode == MigrationMode.DRY_RUN:
        print("\n" + "=" * 80)
        print("MODE DRY RUN TERMINÉ - Aucune modification effectuée")
        print("=" * 80)
        print("\nPour lancer la migration réelle:")
        print("  DRY_RUN=false python migrate_users_to_supabase.py")
    else:
        print("\n" + "=" * 80)
        print("MIGRATION TERMINÉE")
        print("=" * 80)
        print("\nProchaines étapes:")
        print("  1. Vérifier la table user_id_mapping")
        print("  2. Tester le login avec un utilisateur migré")
        print("  3. Exécuter la migration des données (conversations, documents, etc.)")

if __name__ == "__main__":
    main()
