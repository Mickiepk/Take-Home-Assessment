"""
Stream handler for managing WebSocket connections and broadcasting updates.
"""

import asyncio
from typing import Dict, Set
from datetime import datetime
from fastapi import WebSocket

from ..models.schemas import AgentUpdate, UpdateType
from ..logging_config import get_logger

logger = get_logger(__name__)

class StreamHandler:
    """
    Manages WebSocket connections and broadcasts agent updates to connected clients.
    """
    
    def __init__(self):
        # Map of session_id -> set of WebSocket connections
        self.connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()
        logger.info("StreamHandler initialized")
    
    async def register_client(self, session_id: str, websocket: WebSocket) -> None:
        
        async with self._lock:
            if session_id not in self.connections:
                self.connections[session_id] = set()
            
            self.connections[session_id].add(websocket)
            logger.info("Client registered", 
                       session_id=session_id, 
                       total_clients=len(self.connections[session_id]))
    
    async def unregister_client(self, session_id: str, websocket: WebSocket) -> None:
        
        async with self._lock:
            if session_id in self.connections:
                self.connections[session_id].discard(websocket)
                
                # Clean up empty session entries
                if not self.connections[session_id]:
                    del self.connections[session_id]
                
                logger.info("Client unregistered", 
                           session_id=session_id,
                           remaining_clients=len(self.connections.get(session_id, [])))
    
    async def broadcast_update(self, session_id: str, update: AgentUpdate) -> None:
        if session_id not in self.connections:
            # No clients connected, skip broadcasting
            return
        
        # Convert update to JSON-serializable dict
        update_data = {
            "type": "agent_update",
            "update_type": update.update_type.value,
            "content": update.content,
            "timestamp": update.timestamp.isoformat(),
            "metadata": update.metadata
        }
        
        # Get a copy of connections to avoid modification during iteration
        async with self._lock:
            clients = list(self.connections.get(session_id, []))
        
        # Broadcast to all clients
        disconnected_clients = []
        for websocket in clients:
            try:
                await websocket.send_json(update_data)
            except Exception as e:
                logger.warning("Failed to send update to client", 
                             session_id=session_id,
                             error=str(e))
                disconnected_clients.append(websocket)
        
        # Clean up disconnected clients
        if disconnected_clients:
            async with self._lock:
                for websocket in disconnected_clients:
                    if session_id in self.connections:
                        self.connections[session_id].discard(websocket)
    
    async def send_status(self, session_id: str, status: str, message: str) -> None:
        
        update = AgentUpdate(
            update_type=UpdateType.THINKING,
            content=message,
            timestamp=datetime.utcnow(),
            metadata={"status": status}
        )
        await self.broadcast_update(session_id, update)
    
    async def send_error(self, session_id: str, error_message: str) -> None:
        
        update = AgentUpdate(
            update_type=UpdateType.ERROR,
            content=error_message,
            timestamp=datetime.utcnow(),
            metadata={"error": True}
        )
        await self.broadcast_update(session_id, update)
    
    def get_client_count(self, session_id: str) -> int:
        
        return len(self.connections.get(session_id, []))
    
    def get_total_connections(self) -> int:
        """
        Get the total number of WebSocket connections across all sessions.
        
        Returns:
            int: Total number of connections
        """
        return sum(len(clients) for clients in self.connections.values())
