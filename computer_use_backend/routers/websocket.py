"""
WebSocket endpoints for real-time streaming.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session
from ..services import get_shared_stream_handler
from ..services.session_manager import SessionManager
from ..services.worker import WorkerPool
from ..logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


def get_worker_pool() -> WorkerPool:
    """Get shared worker pool instance."""
    from ..services import get_shared_worker_pool
    return get_shared_worker_pool()


@router.websocket("/{session_id}/stream")
async def websocket_stream(
    websocket: WebSocket,
    session_id: str,
    worker_pool: WorkerPool = Depends(get_worker_pool),
):
    """
    WebSocket endpoint for real-time agent execution streaming.
    
    Clients connect to this endpoint to receive real-time updates
    from the Computer Use Agent as it processes messages.
    """
    await websocket.accept()
    logger.info("WebSocket connection established", session_id=session_id)
    
    stream_handler = get_shared_stream_handler()
    
    try:
        # Register this WebSocket connection for the session
        await stream_handler.register_client(session_id, websocket)
        
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "Connected to agent stream"
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Receive messages from client (for ping/pong or commands)
                data = await websocket.receive_text()
                
                # Handle ping
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
                    
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected", session_id=session_id)
                break
            except Exception as e:
                logger.error("Error in WebSocket loop", session_id=session_id, error=str(e))
                break
    
    except Exception as e:
        logger.error("WebSocket error", session_id=session_id, error=str(e))
    
    finally:
        # Unregister the client when connection closes
        await stream_handler.unregister_client(session_id, websocket)
        logger.info("WebSocket connection closed", session_id=session_id)
