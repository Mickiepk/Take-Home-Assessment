"""
SQLAlchemy database models for Computer Use Backend.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Session(Base):
    """Session model for storing session information."""
    
    __tablename__ = "sessions"
    
    session_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    status = Column(
        String(20),
        default="active",
        nullable=False,
        index=True
    )
    worker_id = Column(String(255), nullable=True)
    vnc_port = Column(Integer, nullable=True)
    session_metadata = Column(JSON, default=dict, nullable=False)
    
    # Relationship to messages
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Session(session_id={self.session_id}, status={self.status})>"

class Message(Base):
    """Message model for storing conversation messages."""
    
    __tablename__ = "messages"
    
    message_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role = Column(
        String(20),
        nullable=False,
        index=True
    )
    content = Column(Text, nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    message_metadata = Column(JSON, default=dict, nullable=False)
    
    # Relationship to session
    session = relationship("Session", back_populates="messages")
    
    def __repr__(self) -> str:
        return f"<Message(message_id={self.message_id}, session_id={self.session_id}, role={self.role})>"