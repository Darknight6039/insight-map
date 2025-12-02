"""
SQLAlchemy models for watch configurations and history
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class WatchConfig(Base):
    """Configuration d'une veille automatisée"""
    __tablename__ = "watch_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    topic = Column(String(500), nullable=False)  # Sujet de la veille
    sector = Column(String(100), default="general")  # Secteur d'activité
    report_type = Column(String(100), default="synthese_executive")  # Type de rapport
    keywords = Column(JSON, default=list)  # Mots-clés à surveiller
    sources_preference = Column(String(100), default="all")  # Préférence de sources
    cron_expression = Column(String(100), nullable=False)  # Expression cron (ex: "0 8 * * 1" = lundi 8h)
    email_recipients = Column(JSON, nullable=False)  # Liste des emails destinataires
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relation avec l'historique
    history = relationship("WatchHistory", back_populates="watch", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "topic": self.topic,
            "sector": self.sector,
            "report_type": self.report_type,
            "keywords": self.keywords or [],
            "sources_preference": self.sources_preference,
            "cron_expression": self.cron_expression,
            "email_recipients": self.email_recipients or [],
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class WatchHistory(Base):
    """Historique des exécutions de veilles"""
    __tablename__ = "watch_history"

    id = Column(Integer, primary_key=True, index=True)
    watch_id = Column(Integer, ForeignKey("watch_configs.id", ondelete="CASCADE"), nullable=False)
    executed_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="pending")  # pending, running, success, failed
    report_id = Column(Integer, nullable=True)  # ID du rapport généré
    error_message = Column(Text, nullable=True)
    execution_time_seconds = Column(Integer, nullable=True)

    # Relation avec la config
    watch = relationship("WatchConfig", back_populates="history")

    def to_dict(self):
        return {
            "id": self.id,
            "watch_id": self.watch_id,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "status": self.status,
            "report_id": self.report_id,
            "error_message": self.error_message,
            "execution_time_seconds": self.execution_time_seconds,
        }
