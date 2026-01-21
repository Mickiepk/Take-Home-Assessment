"""
WebSocket stream handling service for real-time agent updates.
"""

import asyncio
import json
from typing import Dict, Set, Optional
from fastapi import WebSocket
from datetime import datetime

from ..models.schemas import AgentUpdate
from ..logging_config import get_logger

logger = get_logger(__name__)


class StreamHandler:
    """
    Handles WebSocket connections and streaming of agent execution updates.
    Supports multiple clients per session with broadcasting.
    """
    
    def __init__(self):
        # Map of session_id -> set of connected WebSocket clients
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Lock for thread-safe connection management
        self._lock = asyncio.Lock()
        
        logger.info("StreamHandler initialized")
    
    async def handle_connection(self, websocket: WebSocket, session_id: str) -> None:
        """
        Handle a WebSocket connection for session streaming.
        
        Args:
            websocket: The WebSocket connection
            session_id: The session ID to stream updates for
        """
        # Add this connection to the session's connection set
        await self._add_connection(session_id, websocket)
        
        try:
            logger.info("WebSocket client connected", 
                       session_id=session_id,
                       total_connections=len(self.active_connections.get(session_id, set())))
            
            # Send initial connection confirmation
            await websocket.send_json({
                "type": "connection",
                "status": "connected",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Connected to session stream"
            })
            
            # Keep the connection alive and handle incoming messages
            while True:
                try:
                    # Receive messages from client (for ping/pong, commands, etc.)
                    data = await websocket.receive_text()
                    
                    # Handle client messages
                    await self._handle_client_message(websocket, session_id, data)
                    
                except asyncio.CancelledError:
                    logger.info("WebSocket task cancelled", session_id=session_id)
                    break
                    
        except Exception as e:
            logger.error("WebSocket connection error", 
                        session_id=session_id,
                        error=str(e))
        finally:
            # Remove this connection when it closes
            await self._remove_connection(session_id, websocket)
            logger.info("WebSocket client disconnected", 
                       session_id=session_id,
                       remaining_connections=len(self.active_connections.get(session_id, set())))
    
    async def broadcast_update(self, session_id: str, update: AgentUpdate) -> None:
        """
        Broadcast an agent update to all connected clients for a session.
        
        Args:
            session_id: The session ID to broadcast to
            update: The AgentUpdate to broadcast
        """
        async with self._lock:
            connections = self.active_connections.get(session_id, set())
            
            if not connections:
                logger.debug("No active connections for session", session_id=session_id)
                return
            
            # Prepare the update message
            message = {
                "type": "update",
                "update_type": update.update_type.value,
                "content": update.content,
                "timestamp": update.timestamp.isoformat(),
                "metadata": update.update_metadata
            }
            
            # Broadcast to all connected clients
            disconnected = set()
            for websocket in connections:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error("Failed to send update to client", 
                               session_id=session_id,
                               error=str(e))
                    disconnected.add(websocket)
            
            # Remove disconnected clients
            for websocket in disconnected:
                connections.discard(websocket)
            
            logger.debug("Update broadcasted", 
                        session_id=session_id,
                        update_type=update.update_type.value,
                        clients=len(connections))
    
    async def send_error(self, session_id: str, error_message: str) -> None:
        """
        Send an error message to all connected clients for a session.
        
        Args:
            session_id: The session ID to send error to
            error_message: The error message
        """
        async with self._lock:
            connections = self.active_connections.get(session_id, set())
            
            if not connections:
                return
            
            message = {
                "type": "error",
                "error": error_message,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            for websocket in connections:
                try:
                    await websocket.send_json(message)
                except Exception:
                    pass
    
    async def send_status(self, session_id: str, status: str, message: str) -> None:
        """
        Send a status message to all connected clients for a session.
        
        Args:
            session_id: The session ID to send status to
            status: The status type (e.g., "processing", "complete", "idle")
            message: The status message
        """
        async with self._lock:
            connections = self.active_connections.get(session_id, set())
            
            if not connections:
                return
            
            status_message = {
                "type": "status",
                "status": status,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            for websocket in connections:
                try:
                    await websocket.send_json(status_message)
                except Exception:
                    pass
    
    async def _add_connection(self, session_id: str, websocket: WebSocket) -> None:
        """Add a WebSocket connection to the session's connection set."""
        async with self._lock:
            if session_id not in self.active_connections:
                self.active_connections[session_id] = set()
            self.active_connections[session_id].add(websocket)
    
    async def _remove_connection(self, session_id: str, websocket: WebSocket) -> None:
        """Remove a WebSocket connection from the session's connection set."""
        async with self._lock:
            if session_id in self.active_connections:
                self.active_connections[session_id].discard(websocket)
                # Clean up empty session sets
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]
    
    async def _handle_client_message(self, websocket: WebSocket, session_id: str, data: str) -> None:
        """
        Handle messages received from the client.
        
        Args:
            websocket: The WebSocket connection
            session_id: The session ID
            data: The message data from client
        """
        try:
            message = json.loads(data)
            message_type = message.get("type")
            
            if message_type == "ping":
                # Respond to ping with pong
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif message_type == "subscribe":
                # Client wants to subscribe to updates (already subscribed by connection)
                await websocket.send_json({
                    "type": "subscribed",
                    "session_id": session_id,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            else:
                logger.debug("Unknown message type from client", 
                           session_id=session_id,
                           message_type=message_type)
                
        except json.JSONDecodeError:
            logger.warning("Invalid JSON from client", session_id=session_id)
        except Exception as e:
            logger.error("Error handling client message", 
                        session_id=session_id,
                        error=str(e))
    
    def get_connection_count(self, session_id: str) -> int:
        """Get the number of active connections for a session."""
        return len(self.active_connections.get(session_id, set()))
    
    def get_total_connections(self) -> int:
        """Get the total number of active connections across all sessions."""
        return sum(len(connections) for connections in self.active_connections.values())
    
    async def disconnect_all(self, session_id: str) -> None:
        """Disconnect all clients for a session."""
        async with self._lock:
            connections = self.active_connections.get(session_id, set())
            
            for websocket in connections:
                try:
                    await websocket.close(code=1000, reason="Session terminated")
                except Exception:
                    pass
            
            if session_id in self.active_connections:
                del self.active_connections[session_id]
            
            logger.info("All connections disconnected for session", session_id=session_id)