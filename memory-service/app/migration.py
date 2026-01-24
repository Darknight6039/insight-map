"""
Legacy data migration from rag_memory.py to new memory service
Handles conversion of old JSON-based memory files to PostgreSQL tables
"""
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.models import UserConversation, MigrationStatus


def get_user_hash(user_id: int) -> str:
    """Generate hash for legacy file lookup"""
    return hashlib.md5(str(user_id).encode()).hexdigest()[:12]


def get_legacy_file_path(user_id: int) -> str:
    """Get path to legacy memory file"""
    user_hash = get_user_hash(user_id)
    return f"/app/data/memory/memory_{user_hash}.json"


def check_migration_status(user_id: int, db: Session) -> Optional[MigrationStatus]:
    """Check if user has already been migrated"""
    return db.query(MigrationStatus).filter_by(user_id=user_id).first()


def load_legacy_data(file_path: str) -> Optional[Dict]:
    """Load legacy JSON memory file"""
    if not os.path.exists(file_path):
        logger.warning(f"Legacy file not found: {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded legacy data from {file_path}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse legacy JSON file {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading legacy file {file_path}: {e}")
        return None


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse timestamp from legacy format"""
    try:
        # Try ISO format first
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except:
        try:
            # Try common formats
            return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except:
            # Fallback to current time
            logger.warning(f"Could not parse timestamp: {timestamp_str}, using current time")
            return datetime.utcnow()


def migrate_conversations(user_id: int, legacy_data: Dict, db: Session) -> int:
    """
    Migrate conversation history from legacy format to new table
    Returns count of migrated conversations
    """
    conversations = legacy_data.get("conversations", [])
    migrated_count = 0

    for conv in conversations:
        try:
            # Extract conversation data
            query = conv.get("query", "")
            response = conv.get("response", "") or conv.get("response_summary", "")

            # Skip empty conversations
            if not query or not response:
                logger.warning(f"Skipping empty conversation for user {user_id}")
                continue

            # Parse metadata
            conversation_type = conv.get("conversation_type", "chat")
            analysis_type = conv.get("analysis_type")
            business_type = conv.get("business_type")

            # Parse timestamp
            timestamp_str = conv.get("timestamp", conv.get("created_at"))
            if timestamp_str:
                created_at = parse_timestamp(timestamp_str)
            else:
                created_at = datetime.utcnow()

            # Create conversation record
            new_conv = UserConversation(
                user_id=user_id,
                query=query,
                response=response,
                conversation_type=conversation_type,
                analysis_type=analysis_type,
                business_type=business_type,
                created_at=created_at
            )
            db.add(new_conv)
            migrated_count += 1

        except Exception as e:
            logger.error(f"Error migrating conversation for user {user_id}: {e}")
            continue

    return migrated_count


def migrate_user_data(user_id: int, db: Session) -> Dict:
    """
    Main migration function for a user
    Returns migration result with status and count
    """
    try:
        # Check if already migrated
        migration_status = check_migration_status(user_id, db)
        if migration_status and migration_status.conversations_migrated:
            logger.info(f"User {user_id} already migrated")
            return {
                "status": "already_migrated",
                "migrated_count": migration_status.legacy_conversation_count,
                "migration_date": migration_status.migration_date
            }

        # Get legacy file path
        legacy_path = get_legacy_file_path(user_id)

        # Load legacy data
        legacy_data = load_legacy_data(legacy_path)
        if not legacy_data:
            logger.info(f"No legacy data found for user {user_id}")
            return {
                "status": "no_legacy_data",
                "message": f"No legacy file found at {legacy_path}"
            }

        # Migrate conversations
        migrated_count = migrate_conversations(user_id, legacy_data, db)

        # Create or update migration status
        if migration_status:
            migration_status.conversations_migrated = True
            migration_status.migration_date = datetime.utcnow()
            migration_status.legacy_conversation_count = migrated_count
        else:
            migration_status = MigrationStatus(
                user_id=user_id,
                conversations_migrated=True,
                migration_date=datetime.utcnow(),
                legacy_conversation_count=migrated_count
            )
            db.add(migration_status)

        # Commit transaction
        db.commit()

        # Rename legacy file to mark as migrated
        try:
            migrated_path = f"{legacy_path}.migrated"
            if os.path.exists(legacy_path):
                os.rename(legacy_path, migrated_path)
                logger.info(f"Renamed legacy file to {migrated_path}")
        except Exception as e:
            logger.warning(f"Could not rename legacy file: {e}")

        logger.info(f"Successfully migrated {migrated_count} conversations for user {user_id}")
        return {
            "status": "success",
            "migrated_count": migrated_count,
            "message": f"Successfully migrated {migrated_count} conversations"
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Migration failed for user {user_id}: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
