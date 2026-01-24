"""
SQLAlchemy models for Memory Service
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.database import Base


class UserConversation(Base):
    """
    Stores chat discussion history with full context
    """
    __tablename__ = "user_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)

    # Conversation content
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)

    # Metadata
    conversation_type = Column(String(50), default='chat', index=True)  # 'chat', 'analysis'
    analysis_type = Column(String(100), nullable=True)  # 'synthese_executive', 'analyse_concurrentielle', etc.
    business_type = Column(String(100), nullable=True)  # 'finance_banque', 'retail', etc.

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Additional indexes
    __table_args__ = (
        Index('idx_conversations_user', 'user_id'),
        Index('idx_conversations_created', 'created_at'),
        Index('idx_conversations_type', 'conversation_type'),
    )


class UserDocument(Base):
    """
    Stores references to generated reports and watch results
    """
    __tablename__ = "user_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)

    # Document classification
    document_type = Column(String(50), nullable=False, index=True)  # 'report' or 'watch'
    analysis_type = Column(String(100), nullable=True)  # Type of analysis/report
    business_type = Column(String(100), nullable=True)  # Sector classification

    # Content
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)  # Full text content for search
    file_path = Column(String(1000), nullable=True)  # Path to PDF if exists

    # Source references
    report_id = Column(Integer, nullable=True)
    watch_id = Column(Integer, nullable=True)

    # Extra data (renamed from 'metadata' - reserved in SQLAlchemy)
    extra_data = Column(JSONB, default={})

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Additional indexes
    __table_args__ = (
        Index('idx_documents_user', 'user_id'),
        Index('idx_documents_type', 'document_type', 'analysis_type'),
        Index('idx_documents_created', 'created_at'),
    )


class MigrationStatus(Base):
    """
    Track which users have been migrated from legacy system
    """
    __tablename__ = "migration_status"

    user_id = Column(Integer, primary_key=True)
    conversations_migrated = Column(Boolean, default=False)
    migration_date = Column(DateTime, nullable=True)
    legacy_conversation_count = Column(Integer, default=0)


class UserIdMapping(Base):
    """
    Maps Supabase UUID user_ids to legacy integer user_ids
    Created during user migration from legacy auth to Supabase
    """
    __tablename__ = "user_id_mapping"

    old_user_id = Column(Integer, primary_key=True)
    supabase_user_id = Column(String(36), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    migrated_at = Column(DateTime, default=datetime.utcnow)
