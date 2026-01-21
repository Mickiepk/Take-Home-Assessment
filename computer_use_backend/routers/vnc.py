"""
VNC proxy endpoints for desktop access.
"""

from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import Response

from ..services import get_shared_worker_pool
from ..logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/{session_id}/info")
async def get_vnc_info(session_id: str):
    """
    Get VNC connection information for a session.
    """
    worker_pool = get_shared_worker_pool()
    worker = await worker_pool.get_worker(session_id)
    
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found for session"
        )
    
    if not worker.vnc_server:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="VNC server not available for this session"
        )
    
    health = await worker.vnc_server.health_check()
    
    return {
        "session_id": session_id,
        "worker_id": worker.worker_id,
        "vnc_port": worker.vnc_port,
        "vnc_url": worker.vnc_server.get_vnc_url(),
        "display": worker.vnc_server.get_display(),
        "health": health
    }


@router.websocket("/{session_id}/stream")
async def vnc_websocket_proxy(websocket: WebSocket, session_id: str):
    """
    WebSocket proxy for VNC connections.
    This allows web-based VNC clients (like noVNC) to connect.
    """
    await websocket.accept()
    logger.info("VNC WebSocket connection established", session_id=session_id)
    
    worker_pool = get_shared_worker_pool()
    worker = await worker_pool.get_worker(session_id)
    
    if not worker or not worker.vnc_server:
        await websocket.close(code=1008, reason="VNC server not available")
        return
    
    try:
        # TODO: Implement VNC protocol proxying
        # This would require:
        # 1. Connect to the VNC server (localhost:vnc_port)
        # 2. Proxy RFB protocol between WebSocket and VNC server
        # 3. Handle bidirectional data flow
        
        # For now, send a message indicating VNC is available
        await websocket.send_json({
            "type": "vnc_info",
            "vnc_port": worker.vnc_port,
            "message": "VNC server is running. Use a VNC client to connect.",
            "vnc_url": worker.vnc_server.get_vnc_url()
        })
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
            except WebSocketDisconnect:
                break
    
    except Exception as e:
        logger.error("VNC WebSocket error", session_id=session_id, error=str(e))
    
    finally:
        logger.info("VNC WebSocket connection closed", session_id=session_id)
