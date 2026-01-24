"""
Memory Service - FastAPI Application
Handles conversation history and document storage for Insight MVP
"""
import os
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from loguru import logger

from app.database import get_db, engine, Base
from app.models import UserConversation, UserDocument, MigrationStatus, UserIdMapping, UserContext, UserStorageQuota
from app.schemas import (
    ConversationCreate, ConversationResponse, ConversationList,
    InternalConversationCreate,
    DocumentCreate, DocumentResponse, DocumentList,
    InternalDocumentCreate,
    MigrationStatusResponse, MigrationResult,
    HealthResponse, ErrorResponse,
    # Context schemas
    ContextCreate, ContextUpdate, ContextResponse, ContextDetailResponse,
    ContextListResponse, StorageQuotaResponse, InternalContextCreate
)
from app.migration import migrate_user_data, check_migration_status

# Configuration
# Prioritize Supabase JWT secret for token validation
SECRET_KEY = os.environ.get("SUPABASE_JWT_SECRET") or os.environ.get("JWT_SECRET_KEY", "your-super-secret-key-change-in-production-2024")
ALGORITHM = "HS256"

# Security
security = HTTPBearer()

# Initialize FastAPI app
app = FastAPI(
    title="Memory Service",
    description="Conversation and Document Storage Service",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
Base.metadata.create_all(bind=engine)


# ============================================================================
# Authentication
# ============================================================================

def resolve_supabase_user_id(supabase_uuid: str, db: Session) -> int:
    """Resolve Supabase UUID to legacy integer user_id via mapping table"""
    mapping = db.query(UserIdMapping).filter(
        UserIdMapping.supabase_user_id == supabase_uuid
    ).first()
    if mapping:
        return mapping.old_user_id
    # Return 0 if no mapping found (should not happen for valid users)
    logger.warning(f"No user_id mapping found for Supabase UUID: {supabase_uuid}")
    return 0


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> int:
    """Extract user_id from JWT token (supports both legacy and Supabase tokens)"""
    try:
        token = credentials.credentials
        # Try decoding with audience validation (Supabase tokens)
        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
                options={"verify_aud": False}  # Supabase uses 'authenticated' audience
            )
        except JWTError:
            # Fallback: try without any options
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing user_id")

        # Check if sub is a UUID (Supabase) or integer (legacy)
        try:
            # Try parsing as integer (legacy token)
            return int(user_id)
        except ValueError:
            # It's a UUID (Supabase token) - resolve via mapping
            resolved_id = resolve_supabase_user_id(str(user_id), db)
            if resolved_id == 0:
                raise HTTPException(status_code=401, detail="User mapping not found")
            return resolved_id

    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        service="memory-service",
        timestamp=datetime.utcnow()
    )


# ============================================================================
# INTERNAL ENDPOINTS (Service-to-Service - No JWT Required)
# Used by backend-service, report-service, scheduler-service
# ============================================================================

INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", "internal-service-key-2024")

# Cache for UUID to integer user_id mapping
_user_id_cache: dict = {}


def resolve_user_id(user_id_input: str, db: Session) -> int:
    """
    Resolve a user_id input (UUID string or integer) to an integer user_id.

    Args:
        user_id_input: Either a UUID string from Supabase or an integer user_id
        db: Database session

    Returns:
        Integer user_id for database operations
    """
    # If it's already an integer, return it
    try:
        return int(user_id_input)
    except (ValueError, TypeError):
        pass

    # Check cache first
    if user_id_input in _user_id_cache:
        return _user_id_cache[user_id_input]

    # It's likely a UUID - look it up in the mapping table
    try:
        mapping = db.query(UserIdMapping).filter(
            UserIdMapping.supabase_user_id == user_id_input
        ).first()

        if mapping:
            # Cache the result
            _user_id_cache[user_id_input] = mapping.old_user_id
            logger.info(f"Resolved UUID {user_id_input[:8]}... to user_id {mapping.old_user_id}")
            return mapping.old_user_id
        else:
            logger.warning(f"No mapping found for UUID {user_id_input}, defaulting to user_id=1")
            return 1

    except Exception as e:
        logger.error(f"Error resolving user_id {user_id_input}: {e}")
        return 1


def verify_internal_key(x_internal_key: str = Query(None, alias="x-internal-key")):
    """Verify internal API key for service-to-service calls"""
    # For simplicity, accept calls without key in dev mode
    # In production, require proper key
    return True  # Allow all internal calls for now


@app.post("/internal/conversations", status_code=201)
async def internal_create_conversation(
    conversation: InternalConversationCreate,
    user_id: str = Query(..., description="User ID (integer or UUID)"),
    db: Session = Depends(get_db)
):
    """
    Internal endpoint: Create conversation without JWT auth
    Called by backend-service after chat/analysis

    user_id can be either:
    - An integer (legacy user_id)
    - A UUID string (Supabase user_id) - will be resolved via user_id_mapping

    Accepts JSON body with: query, response, conversation_type, analysis_type, business_type
    """
    try:
        # Resolve UUID to integer if needed
        resolved_user_id = resolve_user_id(user_id, db)

        new_conversation = UserConversation(
            user_id=resolved_user_id,
            query=conversation.query,
            response=conversation.response,
            conversation_type=conversation.conversation_type,
            analysis_type=conversation.analysis_type,
            business_type=conversation.business_type,
            created_at=datetime.utcnow()
        )

        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)

        logger.info(f"[INTERNAL] Created conversation {new_conversation.id} for user {resolved_user_id} (input: {user_id[:16]}...)")
        return {"status": "ok", "id": new_conversation.id}

    except Exception as e:
        db.rollback()
        logger.error(f"[INTERNAL] Error creating conversation for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/internal/documents")
async def internal_create_document(
    document: InternalDocumentCreate,
    db: Session = Depends(get_db)
):
    """
    Internal endpoint: Create document without JWT auth
    Called by report-service and scheduler-service

    user_id can be either:
    - An integer (legacy user_id)
    - A UUID string (Supabase user_id) - will be resolved via user_id_mapping
    """
    try:
        # Resolve UUID to integer if needed
        resolved_user_id = resolve_user_id(str(document.user_id), db)

        new_document = UserDocument(
            user_id=resolved_user_id,
            document_type=document.document_type,
            title=document.title,
            content=document.content,
            file_path=document.file_path,
            analysis_type=document.analysis_type,
            business_type=document.business_type,
            report_id=document.report_id,
            watch_id=document.watch_id,
            extra_data=document.extra_data,
            created_at=datetime.utcnow()
        )

        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        logger.info(f"[INTERNAL] Created document {new_document.id} for user {resolved_user_id} (input: {str(document.user_id)[:16]}...)")
        return {"status": "ok", "id": new_document.id}

    except Exception as e:
        db.rollback()
        logger.error(f"[INTERNAL] Error creating document for user {document.user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/internal/conversations")
async def internal_list_conversations(
    user_id: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Internal endpoint: List conversations without JWT auth

    user_id can be either an integer or a UUID string
    """
    try:
        # Resolve UUID to integer if needed
        resolved_user_id = resolve_user_id(user_id, db)

        conversations = db.query(UserConversation).filter(
            UserConversation.user_id == resolved_user_id
        ).order_by(UserConversation.created_at.desc()).limit(limit).all()

        return {
            "total": len(conversations),
            "conversations": [
                {
                    "id": c.id,
                    "query": c.query[:200],
                    "response": c.response[:500],
                    "conversation_type": c.conversation_type,
                    "analysis_type": c.analysis_type,
                    "business_type": c.business_type,
                    "created_at": c.created_at.isoformat() if c.created_at else None
                }
                for c in conversations
            ]
        }
    except Exception as e:
        logger.error(f"[INTERNAL] Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/internal/documents")
async def internal_list_documents(
    user_id: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Internal endpoint: List documents without JWT auth

    user_id can be either an integer or a UUID string
    """
    try:
        # Resolve UUID to integer if needed
        resolved_user_id = resolve_user_id(user_id, db)

        documents = db.query(UserDocument).filter(
            UserDocument.user_id == resolved_user_id
        ).order_by(UserDocument.created_at.desc()).limit(limit).all()

        return {
            "total": len(documents),
            "documents": [
                {
                    "id": d.id,
                    "document_type": d.document_type,
                    "title": d.title,
                    "analysis_type": d.analysis_type,
                    "business_type": d.business_type,
                    "report_id": d.report_id,
                    "watch_id": d.watch_id,
                    "created_at": d.created_at.isoformat() if d.created_at else None
                }
                for d in documents
            ]
        }
    except Exception as e:
        logger.error(f"[INTERNAL] Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Conversation Endpoints
# ============================================================================

@app.get("/api/v1/conversations", response_model=ConversationList)
async def list_conversations(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    conversation_type: Optional[str] = Query(None),
    analysis_type: Optional[str] = Query(None),
    business_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    List user's conversations with optional filters and pagination
    """
    try:
        # Build base query
        query = db.query(UserConversation).filter(UserConversation.user_id == user_id)

        # Apply filters
        if conversation_type:
            query = query.filter(UserConversation.conversation_type == conversation_type)

        if analysis_type:
            query = query.filter(UserConversation.analysis_type == analysis_type)

        if business_type:
            query = query.filter(UserConversation.business_type == business_type)

        # Text search in query or response
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    UserConversation.query.ilike(search_pattern),
                    UserConversation.response.ilike(search_pattern)
                )
            )

        # Get total count
        total = query.count()

        # Get paginated results
        conversations = query.order_by(
            UserConversation.created_at.desc()
        ).offset(skip).limit(limit).all()

        return ConversationList(
            total=total,
            skip=skip,
            limit=limit,
            conversations=conversations
        )

    except Exception as e:
        logger.error(f"Error listing conversations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to list conversations")


@app.post("/api/v1/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    conversation: ConversationCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new conversation entry
    """
    try:
        new_conversation = UserConversation(
            user_id=user_id,
            query=conversation.query,
            response=conversation.response,
            conversation_type=conversation.conversation_type,
            analysis_type=conversation.analysis_type,
            business_type=conversation.business_type,
            created_at=datetime.utcnow()
        )

        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)

        logger.info(f"Created conversation {new_conversation.id} for user {user_id}")
        return new_conversation

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating conversation for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create conversation")


@app.get("/api/v1/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific conversation by ID
    """
    conversation = db.query(UserConversation).filter(
        UserConversation.id == conversation_id,
        UserConversation.user_id == user_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation


@app.delete("/api/v1/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a conversation
    """
    conversation = db.query(UserConversation).filter(
        UserConversation.id == conversation_id,
        UserConversation.user_id == user_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    try:
        db.delete(conversation)
        db.commit()
        logger.info(f"Deleted conversation {conversation_id} for user {user_id}")
        return None

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete conversation")


# ============================================================================
# Document Endpoints
# ============================================================================

@app.get("/api/v1/documents", response_model=DocumentList)
async def list_documents(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    document_type: Optional[str] = Query(None, alias="type"),
    analysis_type: Optional[str] = Query(None),
    business_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    List user's documents with optional filters and pagination
    """
    try:
        # Build base query
        query = db.query(UserDocument).filter(UserDocument.user_id == user_id)

        # Apply filters
        if document_type:
            query = query.filter(UserDocument.document_type == document_type)

        if analysis_type:
            query = query.filter(UserDocument.analysis_type == analysis_type)

        if business_type:
            query = query.filter(UserDocument.business_type == business_type)

        # Text search in title or content
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    UserDocument.title.ilike(search_pattern),
                    UserDocument.content.ilike(search_pattern)
                )
            )

        # Get total count
        total = query.count()

        # Get paginated results
        documents = query.order_by(
            UserDocument.created_at.desc()
        ).offset(skip).limit(limit).all()

        return DocumentList(
            total=total,
            skip=skip,
            limit=limit,
            documents=documents
        )

    except Exception as e:
        logger.error(f"Error listing documents for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to list documents")


@app.post("/api/v1/documents", response_model=DocumentResponse, status_code=201)
async def create_document(
    document: DocumentCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new document entry
    """
    try:
        new_document = UserDocument(
            user_id=user_id,
            document_type=document.document_type,
            title=document.title,
            content=document.content,
            file_path=document.file_path,
            analysis_type=document.analysis_type,
            business_type=document.business_type,
            report_id=document.report_id,
            watch_id=document.watch_id,
            extra_data=document.extra_data,
            created_at=datetime.utcnow()
        )

        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        logger.info(f"Created document {new_document.id} for user {user_id}")
        return new_document

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating document for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create document")


@app.get("/api/v1/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific document by ID
    """
    document = db.query(UserDocument).filter(
        UserDocument.id == document_id,
        UserDocument.user_id == user_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@app.delete("/api/v1/documents/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a document
    """
    document = db.query(UserDocument).filter(
        UserDocument.id == document_id,
        UserDocument.user_id == user_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        db.delete(document)
        db.commit()
        logger.info(f"Deleted document {document_id} for user {user_id}")
        return None

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")


# ============================================================================
# Internal Endpoints (for service-to-service communication)
# ============================================================================

@app.post("/api/internal/documents", response_model=DocumentResponse, status_code=201)
async def create_document_internal(
    document: DocumentCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Internal endpoint for service-to-service document creation.
    This endpoint does not require JWT authentication and should only be
    accessible from within the Docker network.

    Used by:
    - report-service: To register generated reports
    - scheduler-service: To register watch executions
    """
    try:
        new_document = UserDocument(
            user_id=user_id,
            document_type=document.document_type,
            title=document.title,
            content=document.content,
            file_path=document.file_path,
            analysis_type=document.analysis_type,
            business_type=document.business_type,
            report_id=document.report_id,
            watch_id=document.watch_id,
            extra_data=document.extra_data,
            created_at=datetime.utcnow()
        )

        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        logger.info(f"Created document {new_document.id} for user {user_id} via internal API")
        return new_document

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating document for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create document")


@app.post("/api/internal/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation_internal(
    conversation: ConversationCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Internal endpoint for service-to-service conversation creation.
    This endpoint does not require JWT authentication.

    Used by:
    - backend-service: To save analysis conversations
    """
    try:
        new_conversation = UserConversation(
            user_id=user_id,
            query=conversation.query,
            response=conversation.response,
            conversation_type=conversation.conversation_type,
            analysis_type=conversation.analysis_type,
            business_type=conversation.business_type,
            created_at=datetime.utcnow()
        )

        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)

        logger.info(f"Created conversation {new_conversation.id} for user {user_id} via internal API")
        return new_conversation

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating conversation for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create conversation")


# ============================================================================
# Migration Endpoints
# ============================================================================

@app.get("/api/v1/migrate/status", response_model=MigrationStatusResponse)
async def get_migration_status(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Check migration status for current user
    """
    status = check_migration_status(user_id, db)

    if not status:
        # Return default status if not found
        return MigrationStatusResponse(
            user_id=user_id,
            conversations_migrated=False,
            migration_date=None,
            legacy_conversation_count=0
        )

    return status


@app.post("/api/v1/migrate", response_model=MigrationResult)
async def trigger_migration(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Trigger migration for current user from legacy system
    """
    try:
        result = migrate_user_data(user_id, db)
        logger.info(f"Migration result for user {user_id}: {result}")
        return MigrationResult(**result)

    except Exception as e:
        logger.error(f"Migration error for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


# ============================================================================
# Context Management Endpoints (Multi-context with 2GB quota)
# ============================================================================

MAX_STORAGE_BYTES = 2 * 1024 * 1024 * 1024  # 2GB


def get_or_create_quota(user_id: int, db: Session) -> UserStorageQuota:
    """Get or create storage quota for user"""
    quota = db.query(UserStorageQuota).filter(UserStorageQuota.user_id == user_id).first()
    if not quota:
        quota = UserStorageQuota(
            user_id=user_id,
            total_used_bytes=0,
            max_bytes=MAX_STORAGE_BYTES
        )
        db.add(quota)
        db.commit()
        db.refresh(quota)
    return quota


@app.get("/api/v1/contexts", response_model=ContextListResponse)
async def list_contexts(
    active_only: bool = Query(False, description="Filter to active contexts only"),
    context_type: Optional[str] = Query(None, description="Filter by context type"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """List all contexts for current user"""
    query = db.query(UserContext).filter(UserContext.user_id == user_id)

    if active_only:
        query = query.filter(UserContext.is_active == True)
    if context_type:
        query = query.filter(UserContext.context_type == context_type)

    contexts = query.order_by(UserContext.created_at.desc()).all()

    return ContextListResponse(total=len(contexts), contexts=contexts)


@app.post("/api/v1/contexts", response_model=ContextResponse, status_code=201)
async def create_context(
    context: ContextCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new context (enforces quota)"""
    # Calculate content size
    content_size = len(context.content.encode('utf-8'))

    # Check quota
    quota = get_or_create_quota(user_id, db)

    if quota.total_used_bytes + content_size > quota.max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Quota de stockage depassé. Utilisé: {quota.total_used_bytes} bytes, Limite: {quota.max_bytes} bytes"
        )

    # Create context
    new_context = UserContext(
        user_id=user_id,
        name=context.name,
        context_type=context.context_type,
        content=context.content,
        preview=context.content[:200] if context.content else None,
        filename=context.filename,
        file_type=context.file_type,
        content_size=content_size,
        is_active=context.is_active
    )
    db.add(new_context)

    # Update quota
    quota.total_used_bytes += content_size

    db.commit()
    db.refresh(new_context)

    logger.info(f"Context created for user {user_id}: {context.name} ({content_size} bytes)")

    return new_context


@app.get("/api/v1/contexts/quota", response_model=StorageQuotaResponse)
async def get_storage_quota(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get user's storage quota info"""
    quota = get_or_create_quota(user_id, db)

    return StorageQuotaResponse(
        user_id=user_id,
        total_used_bytes=quota.total_used_bytes,
        max_bytes=quota.max_bytes,
        used_percentage=(quota.total_used_bytes / quota.max_bytes) * 100 if quota.max_bytes > 0 else 0,
        remaining_bytes=max(0, quota.max_bytes - quota.total_used_bytes)
    )


@app.get("/api/v1/contexts/{context_id}", response_model=ContextDetailResponse)
async def get_context(
    context_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get full context by ID"""
    context = db.query(UserContext).filter(
        UserContext.id == context_id,
        UserContext.user_id == user_id
    ).first()

    if not context:
        raise HTTPException(status_code=404, detail="Contexte non trouvé")

    return context


@app.patch("/api/v1/contexts/{context_id}", response_model=ContextResponse)
async def update_context(
    context_id: int,
    update: ContextUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update a context"""
    context = db.query(UserContext).filter(
        UserContext.id == context_id,
        UserContext.user_id == user_id
    ).first()

    if not context:
        raise HTTPException(status_code=404, detail="Contexte non trouvé")

    # Handle content update with quota adjustment
    if update.content is not None:
        new_size = len(update.content.encode('utf-8'))
        size_diff = new_size - context.content_size
        quota = get_or_create_quota(user_id, db)

        if quota.total_used_bytes + size_diff > quota.max_bytes:
            raise HTTPException(
                status_code=413,
                detail="Quota de stockage depassé"
            )

        context.content = update.content
        context.preview = update.content[:200]
        context.content_size = new_size
        quota.total_used_bytes += size_diff

    if update.name is not None:
        context.name = update.name

    if update.is_active is not None:
        context.is_active = update.is_active

    db.commit()
    db.refresh(context)

    logger.info(f"Context updated for user {user_id}: {context.name}")

    return context


@app.delete("/api/v1/contexts/{context_id}", status_code=204)
async def delete_context(
    context_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a context and free quota"""
    context = db.query(UserContext).filter(
        UserContext.id == context_id,
        UserContext.user_id == user_id
    ).first()

    if not context:
        raise HTTPException(status_code=404, detail="Contexte non trouvé")

    # Free quota
    quota = get_or_create_quota(user_id, db)
    quota.total_used_bytes = max(0, quota.total_used_bytes - context.content_size)

    db.delete(context)
    db.commit()

    logger.info(f"Context deleted for user {user_id}: {context.name}")


@app.get("/internal/contexts/active")
async def get_active_contexts_internal(
    user_id: str = Query(..., description="User ID (integer or UUID)"),
    db: Session = Depends(get_db)
):
    """
    Internal endpoint: Get all active contexts for prompt building.
    Used by backend-service to inject contexts into prompts.
    """
    # Resolve user ID (handles both integer and UUID)
    try:
        resolved_id = int(user_id)
    except ValueError:
        # It's a UUID, need to resolve
        resolved_id = resolve_supabase_user_id(user_id, db)

    contexts = db.query(UserContext).filter(
        UserContext.user_id == resolved_id,
        UserContext.is_active == True
    ).order_by(UserContext.created_at.desc()).all()

    return {
        "contexts": [
            {
                "id": c.id,
                "name": c.name,
                "content": c.content,
                "type": c.context_type,
                "preview": c.preview
            }
            for c in contexts
        ],
        "total": len(contexts)
    }


@app.post("/internal/contexts", response_model=ContextResponse, status_code=201)
async def create_context_internal(
    context: InternalContextCreate,
    db: Session = Depends(get_db)
):
    """
    Internal endpoint: Create context with explicit user_id.
    Used by gateway-api proxy.
    """
    # Resolve user ID
    try:
        resolved_id = int(context.user_id)
    except ValueError:
        resolved_id = resolve_supabase_user_id(str(context.user_id), db)

    content_size = len(context.content.encode('utf-8'))
    quota = get_or_create_quota(resolved_id, db)

    if quota.total_used_bytes + content_size > quota.max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Quota de stockage depassé"
        )

    new_context = UserContext(
        user_id=resolved_id,
        name=context.name,
        context_type=context.context_type,
        content=context.content,
        preview=context.content[:200] if context.content else None,
        filename=context.filename,
        file_type=context.file_type,
        content_size=content_size,
        is_active=context.is_active
    )
    db.add(new_context)
    quota.total_used_bytes += content_size
    db.commit()
    db.refresh(new_context)

    logger.info(f"Context created internally for user {resolved_id}: {context.name}")

    return new_context


# ============================================================================
# Startup Event
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("Memory Service started successfully")
    logger.info(f"Database URL: {os.environ.get('DATABASE_URL', 'Not set')}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
