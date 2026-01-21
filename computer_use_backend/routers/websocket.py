"""
WebSocket endpoints for real-time streaming.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session
from ..services import get_shared_stream_handler
from ..logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.websocket("/sessions/{session_id}/stream")
async def websocket_session_stream(
    websocket: WebSocket,
    session_id: str,
) -> None:
    """WebSocket endpoint for real-time session streaming."""
    await websocket.accept()
    logger.info("WebSocket connection established", session_id=session_id)
    
    # Get shared stream handler
    stream_handler = get_shared_stream_handler()
    
    try:
        await stream_handler.handle_connection(websocket, session_id)
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed", session_id=session_id)
    except Exception as e:
        logger.error(
            "WebSocket error",
            session_id=session_id,
            error=str(e)
        )
        await websocket.close(code=1011, reason="Internal server error")