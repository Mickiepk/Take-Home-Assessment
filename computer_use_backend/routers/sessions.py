"""
Session management endpoints.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session
from ..models.schemas import SessionCreate, SessionResponse, MessageResponse, MessageCreate, MessageRole, UpdateType
from ..services.session_manager import SessionManager
from ..services import get_shared_stream_handler, get_shared_worker_pool
from ..logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


def get_session_manager() -> SessionManager:
    """Dependency to get session manager instance with shared worker pool."""
    worker_pool = get_shared_worker_pool()
    return SessionManager(worker_pool)


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db_session),
    session_manager: SessionManager = Depends(get_session_manager),
) -> SessionResponse:
    """Create a new session."""
    try:
        session = await session_manager.create_session(db, session_data)
        logger.info("Session created", session_id=str(session.session_id))
        return SessionResponse.model_validate(session)
    except Exception as e:
        logger.error("Failed to create session", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session"
        )


@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db_session),
    session_manager: SessionManager = Depends(get_session_manager),
) -> List[SessionResponse]:
    """List all active sessions."""
    try:
        sessions = await session_manager.list_sessions(db)
        logger.info("Sessions listed", count=len(sessions))
        return [SessionResponse.model_validate(session) for session in sessions]
    except Exception as e:
        logger.error("Failed to list sessions", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list sessions"
        )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db_session),
    session_manager: SessionManager = Depends(get_session_manager),
) -> SessionResponse:
    """Get a specific session."""
    try:
        session = await session_manager.get_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        return SessionResponse.model_validate(session)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get session", session_id=session_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session"
        )


@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db_session),
    session_manager: SessionManager = Depends(get_session_manager),
) -> List[MessageResponse]:
    """Get message history for a session."""
    try:
        # Verify session exists
        session = await session_manager.get_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        messages = await session_manager.get_session_messages(db, session_id)
        logger.info("Messages retrieved", session_id=session_id, count=len(messages))
        return [MessageResponse.model_validate(message) for message in messages]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get session messages",
            session_id=session_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session messages"
        )


@router.post("/{session_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    session_id: str,
    message_data: MessageCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
    session_manager: SessionManager = Depends(get_session_manager),
) -> MessageResponse:
    """Create a new message in a session and spawn worker for processing."""
    try:
        # Get shared stream handler
        stream_handler = get_shared_stream_handler()
        
        # Verify session exists
        session = await session_manager.get_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Create and persist the message
        message = await session_manager.create_message(db, session_id, message_data)
        
        # Get or create worker for this session
        try:
            worker = await session_manager.get_or_create_worker(session_id)
            logger.info("Worker ready for message processing", 
                       session_id=session_id, 
                       worker_id=worker.worker_id,
                       message_id=str(message.message_id))
            
            # Process the message in the background and stream updates
            async def process_and_stream():
                try:
                    # Send status update
                    await stream_handler.send_status(
                        session_id,
                        "processing",
                        "Processing your message..."
                    )
                    
                    # Collect agent response
                    agent_response_parts = []
                    
                    # Process message and stream updates
                    async for update in worker.process_message(message_data.content):
                        await stream_handler.broadcast_update(session_id, update)
                        
                        # Collect text responses for saving
                        if update.update_type in [UpdateType.THINKING, UpdateType.COMPLETE]:
                            if update.content:
                                agent_response_parts.append(update.content)
                    
                    # Save agent response to database
                    if agent_response_parts:
                        agent_response = "\n".join(agent_response_parts)
                        try:
                            # Get a new database session for the background task
                            async for db_session in get_db_session():
                                assistant_message = MessageCreate(
                                    content=agent_response,
                                    role=MessageRole.ASSISTANT,
                                    message_metadata={"worker_id": worker.worker_id}
                                )
                                await session_manager.create_message(
                                    db_session, 
                                    session_id, 
                                    assistant_message
                                )
                                logger.info("Agent response saved", 
                                          session_id=session_id,
                                          response_length=len(agent_response))
                                break
                        except Exception as save_error:
                            logger.error("Failed to save agent response",
                                       session_id=session_id,
                                       error=str(save_error))
                    
                    # Send completion status
                    await stream_handler.send_status(
                        session_id,
                        "complete",
                        "Message processing completed"
                    )
                    
                except Exception as e:
                    logger.error("Error processing message", 
                               session_id=session_id,
                               error=str(e))
                    await stream_handler.send_error(
                        session_id,
                        f"Error processing message: {str(e)}"
                    )
            
            # Start processing in background
            background_tasks.add_task(process_and_stream)
            
        except Exception as worker_error:
            logger.error("Failed to get/create worker", 
                        session_id=session_id, 
                        error=str(worker_error))
            # Continue anyway - message is saved, worker can be created later
        
        logger.info("Message created", session_id=session_id, message_id=str(message.message_id))
        
        return MessageResponse.model_validate(message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create message", session_id=session_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create message"
        )


@router.get("/workers/health")
async def get_workers_health(
    session_manager: SessionManager = Depends(get_session_manager),
) -> Dict[str, Any]:
    """Get health status of all workers."""
    try:
        health_status = await session_manager.get_worker_health()
        logger.info("Worker health check completed", total_workers=health_status.get("total_workers", 0))
        return health_status
    except Exception as e:
        logger.error("Failed to get worker health", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get worker health status"
        )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def terminate_session(
    session_id: str,
    db: AsyncSession = Depends(get_db_session),
    session_manager: SessionManager = Depends(get_session_manager),
) -> None:
    """Terminate a session."""
    try:
        success = await session_manager.terminate_session(db, session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        logger.info("Session terminated", session_id=session_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to terminate session",
            session_id=session_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to terminate session"
        )