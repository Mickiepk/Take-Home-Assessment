"""
Pydantic schemas for API request/response models.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer


class SessionStatus(str, Enum):
    """Session status enumeration."""
    ACTIVE = "active"
    PROCESSING = "processing"
    IDLE = "idle"
    TERMINATED = "terminated"


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class UpdateType(str, Enum):
    """Agent update type enumeration."""
    THINKING = "thinking"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"
    SCREENSHOT = "screenshot"
    ERROR = "error"
    COMPLETE = "complete"


# Request schemas
class SessionCreate(BaseModel):
    """Schema for creating a new session."""
    session_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MessageCreate(BaseModel):
    """Schema for creating a new message."""
    content: str = Field(..., max_length=1024*1024)  # 1MB limit
    role: MessageRole = MessageRole.USER
    message_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


# Response schemas
class SessionResponse(BaseModel):
    """Schema for session response."""
    session_id: UUID
    created_at: datetime
    updated_at: datetime
    status: SessionStatus
    worker_id: Optional[str] = None
    vnc_port: Optional[int] = None
    session_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_serializer('session_id')
    def serialize_session_id(self, value: UUID) -> str:
        return str(value)
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Schema for message response."""
    message_id: UUID
    session_id: UUID
    role: MessageRole
    content: str
    timestamp: datetime
    message_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_serializer('message_id', 'session_id')
    def serialize_uuid(self, value: UUID) -> str:
        return str(value)
    
    class Config:
        from_attributes = True


class AgentUpdate(BaseModel):
    """Schema for agent execution updates."""
    update_type: UpdateType
    content: str
    timestamp: datetime
    update_metadata: Dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    service: str
    components: Optional[Dict[str, Any]] = None