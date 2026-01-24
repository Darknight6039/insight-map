"""
Pydantic schemas for Memory Service API validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union
from datetime import datetime


# ============================================================================
# Conversation Schemas
# ============================================================================

class ConversationCreate(BaseModel):
    """Schema for creating a new conversation"""
    query: str = Field(..., min_length=1)
    response: str = Field(..., min_length=1)
    conversation_type: str = Field(default='chat')
    analysis_type: Optional[str] = None
    business_type: Optional[str] = None


class InternalConversationCreate(BaseModel):
    """Schema for creating a conversation via internal API (JSON body)"""
    query: str
    response: str
    conversation_type: str = 'chat'
    analysis_type: Optional[str] = None
    business_type: Optional[str] = None


class ConversationResponse(BaseModel):
    """Schema for conversation response"""
    id: int
    user_id: int
    query: str
    response: str
    conversation_type: str
    analysis_type: Optional[str]
    business_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationList(BaseModel):
    """Schema for paginated conversation list"""
    total: int
    skip: int
    limit: int
    conversations: list[ConversationResponse]


# ============================================================================
# Document Schemas
# ============================================================================

class DocumentCreate(BaseModel):
    """Schema for creating a new document"""
    document_type: str = Field(..., pattern='^(report|watch)$')
    title: str = Field(..., min_length=1, max_length=500)
    content: Optional[str] = None
    file_path: Optional[str] = None
    analysis_type: Optional[str] = None
    business_type: Optional[str] = None
    report_id: Optional[int] = None
    watch_id: Optional[int] = None
    extra_data: Dict[str, Any] = Field(default_factory=dict)


class InternalDocumentCreate(DocumentCreate):
    """Schema for creating a document internally (includes user_id)"""
    # Accept both int and str (UUID) for backward compatibility with Supabase migration
    user_id: Union[int, str]


class DocumentResponse(BaseModel):
    """Schema for document response"""
    id: int
    user_id: int
    document_type: str
    title: str
    content: Optional[str]
    file_path: Optional[str]
    analysis_type: Optional[str]
    business_type: Optional[str]
    report_id: Optional[int]
    watch_id: Optional[int]
    extra_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    """Schema for paginated document list"""
    total: int
    skip: int
    limit: int
    documents: list[DocumentResponse]


# ============================================================================
# Migration Schemas
# ============================================================================

class MigrationStatusResponse(BaseModel):
    """Schema for migration status response"""
    user_id: int
    conversations_migrated: bool
    migration_date: Optional[datetime]
    legacy_conversation_count: int

    class Config:
        from_attributes = True


class MigrationResult(BaseModel):
    """Schema for migration result"""
    status: str
    message: Optional[str] = None
    migrated_count: Optional[int] = None
    legacy_conversation_count: Optional[int] = None


# ============================================================================
# Generic Schemas
# ============================================================================

class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    service: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
