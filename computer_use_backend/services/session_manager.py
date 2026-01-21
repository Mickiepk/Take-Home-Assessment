"""
Session management service.
"""

import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from ..models.database import Session, Message
from ..models.schemas import SessionCreate, MessageCreate
from ..logging_config import get_logger
from .worker import WorkerPool

logger = get_logger(__name__)

class SessionManager:
    """Manages session lifecycle and operations with worker integration."""
    
    def __init__(self, worker_pool: Optional[WorkerPool] = None):
        self.worker_pool = worker_pool or WorkerPool()
    
    async def create_session(
        self,
        db: AsyncSession,
        session_data: SessionCreate
    ) -> Session:
        """Create a new session."""
        try:
            session = Session(
                session_metadata=session_data.session_metadata or {}
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
            
            logger.info("Session created", session_id=str(session.session_id))
            return session
        except Exception as e:
            await db.rollback()
            logger.error("Failed to create session", error=str(e))
            raise
    
    async def get_session(
        self,
        db: AsyncSession,
        session_id: str
    ) -> Optional[Session]:
        """Get a session by ID."""
        try:
            session_uuid = uuid.UUID(session_id)
            result = await db.execute(
                select(Session).where(Session.session_id == session_uuid)
            )
            session = result.scalar_one_or_none()
            
            if session:
                logger.info("Session retrieved", session_id=session_id)
            else:
                logger.warning("Session not found", session_id=session_id)
            
            return session
        except ValueError:
            logger.warning("Invalid session ID format", session_id=session_id)
            return None
        except Exception as e:
            logger.error("Failed to get session", session_id=session_id, error=str(e))
            raise
    
    async def list_sessions(self, db: AsyncSession) -> List[Session]:
        """List all active sessions."""
        try:
            result = await db.execute(
                select(Session)
                .where(Session.status != "terminated")
                .order_by(desc(Session.created_at))
            )
            sessions = result.scalars().all()
            
            logger.info("Sessions listed", count=len(sessions))
            return list(sessions)
        except Exception as e:
            logger.error("Failed to list sessions", error=str(e))
            raise
    
    async def get_session_messages(
        self,
        db: AsyncSession,
        session_id: str
    ) -> List[Message]:
        """Get messages for a session."""
        try:
            session_uuid = uuid.UUID(session_id)
            result = await db.execute(
                select(Message)
                .where(Message.session_id == session_uuid)
                .order_by(Message.timestamp)
            )
            messages = result.scalars().all()
            
            logger.info("Messages retrieved", session_id=session_id, count=len(messages))
            return list(messages)
        except ValueError:
            logger.warning("Invalid session ID format", session_id=session_id)
            return []
        except Exception as e:
            logger.error("Failed to get session messages", session_id=session_id, error=str(e))
            raise
    
    async def create_message(
        self,
        db: AsyncSession,
        session_id: str,
        message_data: MessageCreate
    ) -> Message:
        """Create a new message in a session."""
        try:
            session_uuid = uuid.UUID(session_id)
            
            # Verify session exists
            session = await self.get_session(db, session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            message = Message(
                session_id=session_uuid,
                role=message_data.role.value,
                content=message_data.content,
                message_metadata=message_data.message_metadata or {}
            )
            
            db.add(message)
            await db.commit()
            await db.refresh(message)
            
            logger.info("Message created", session_id=session_id, message_id=str(message.message_id))
            return message
        except ValueError:
            logger.warning("Invalid session ID format", session_id=session_id)
            raise
        except Exception as e:
            await db.rollback()
            logger.error("Failed to create message", session_id=session_id, error=str(e))
            raise
    
    async def get_or_create_worker(self, session_id: str):
        
        try:
            # Try to get existing worker
            worker = await self.worker_pool.get_worker(session_id)
            if worker:
                logger.info("Using existing worker", session_id=session_id, worker_id=worker.worker_id)
                return worker
            
            # Create new worker if none exists
            worker = await self.worker_pool.spawn_worker(session_id)
            logger.info("Created new worker", session_id=session_id, worker_id=worker.worker_id)
            return worker
            
        except Exception as e:
            logger.error("Failed to get or create worker", session_id=session_id, error=str(e))
            raise
    
    async def terminate_session(
        self,
        db: AsyncSession,
        session_id: str
    ) -> bool:
        """Terminate a session and its worker."""
        try:
            session = await self.get_session(db, session_id)
            if not session:
                return False
            
            # Terminate the worker if it exists
            await self.worker_pool.terminate_worker(session_id)
            # Update session status
            session.status = "terminated"
            await db.commit()
            
            logger.info("Session terminated", session_id=session_id)
            return True
        except Exception as e:
            await db.rollback()
            logger.error("Failed to terminate session", session_id=session_id, error=str(e))
            raise
    
    async def get_worker_health(self) -> dict:
        """Get health status of all workers."""
        return await self.worker_pool.health_check()