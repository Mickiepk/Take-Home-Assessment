"""
Worker implementation for handling Computer Use Agent execution.
"""

import asyncio
import uuid
from typing import Optional, Dict, Any, AsyncIterator
from datetime import datetime

from ..models.schemas import AgentUpdate, UpdateType
from ..logging_config import get_logger
from .agent_service import AgentService

logger = get_logger(__name__)


class Worker:
    """
    Worker class that manages VM and VNC server for a session and executes Computer Use Agent tasks.
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.worker_id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.status = "initializing"
        
        # VM and VNC will be implemented in Task 7
        self.vm_instance: Optional["VMInstance"] = None
        self.vnc_server: Optional["VNCServer"] = None
        self.vnc_port: Optional[int] = None
        
        # Agent service for Computer Use Agent integration
        self.agent_service: Optional[AgentService] = None
        
        logger.info("Worker created", worker_id=self.worker_id, session_id=session_id)
    
    async def initialize(self) -> None:
        """Initialize the worker with VM, VNC, and agent components."""
        try:
            self.status = "initializing"
            
            # TODO: Initialize VM instance (Task 10.2)
            await self._initialize_vm()
            
            # TODO: Initialize VNC server (Task 7.1)
            await self._initialize_vnc()
            
            # Initialize agent service with Computer Use Agent
            await self._initialize_agent()
            
            self.status = "ready"
            logger.info("Worker initialized", worker_id=self.worker_id, session_id=self.session_id)
            
        except Exception as e:
            self.status = "failed"
            logger.error("Worker initialization failed", worker_id=self.worker_id, error=str(e))
            raise
    
    async def process_message(self, message_content: str) -> AsyncIterator[AgentUpdate]:
        """
        Process a message using the Computer Use Agent and yield updates.
        
        Args:
            message_content: The user message to process
            
        Yields:
            AgentUpdate: Real-time updates from agent execution
        """
        if self.status != "ready":
            raise RuntimeError(f"Worker not ready. Status: {self.status}")
        
        if not self.agent_service:
            raise RuntimeError("Agent service not initialized")
        
        try:
            self.status = "processing"
            logger.info("Processing message with Computer Use Agent", 
                       worker_id=self.worker_id, 
                       session_id=self.session_id)
            
            # Use the real Computer Use Agent to process the message
            async for update in self.agent_service.process_message(message_content):
                yield update
            
            self.status = "ready"
            logger.info("Message processing completed", 
                       worker_id=self.worker_id, 
                       session_id=self.session_id)
            
        except Exception as e:
            self.status = "error"
            logger.error("Message processing failed", worker_id=self.worker_id, error=str(e))
            
            yield AgentUpdate(
                update_type=UpdateType.ERROR,
                content=f"Error processing message: {str(e)}",
                timestamp=datetime.utcnow(),
                metadata={"worker_id": self.worker_id, "error": str(e)}
            )
            
            self.status = "ready"  # Reset to ready after error
    
    async def get_vnc_stream(self) -> bytes:
        """Get VNC stream data for desktop access."""
        if not self.vnc_server:
            raise RuntimeError("VNC server not initialized")
        
        # TODO: Implement VNC streaming (Task 7.2)
        # For now, return placeholder data
        return b"VNC_PLACEHOLDER_DATA"
    
    async def cleanup(self) -> None:
        """Clean up worker resources including VM and VNC."""
        try:
            self.status = "terminating"
            logger.info("Cleaning up worker", worker_id=self.worker_id, session_id=self.session_id)
            
            # Cleanup agent service
            if self.agent_service:
                self.agent_service.clear_history()
                self.agent_service = None
            
            # TODO: Cleanup VNC server (Task 7.1)
            if self.vnc_server:
                await self._cleanup_vnc()
            
            # TODO: Cleanup VM instance (Task 10.2)
            if self.vm_instance:
                await self._cleanup_vm()
            
            self.status = "terminated"
            logger.info("Worker cleanup completed", worker_id=self.worker_id, session_id=self.session_id)
            
        except Exception as e:
            logger.error("Worker cleanup failed", worker_id=self.worker_id, error=str(e))
            raise
    
    # Private methods for component initialization (to be implemented in later tasks)
    
    async def _initialize_vm(self) -> None:
        """Initialize VM instance for the session."""
        # TODO: Implement in Task 10.2
        logger.info("VM initialization placeholder", worker_id=self.worker_id)
        await asyncio.sleep(0.1)  # Simulate initialization time
    
    async def _initialize_vnc(self) -> None:
        """Initialize VNC server for the session."""
        # TODO: Implement in Task 7.1
        logger.info("VNC initialization placeholder", worker_id=self.worker_id)
        await asyncio.sleep(0.1)  # Simulate initialization time
        # Simulate VNC port assignment
        self.vnc_port = 5900 + hash(self.session_id) % 1000
    
    async def _initialize_agent(self) -> None:
        """Initialize Computer Use Agent components."""
        try:
            logger.info("Initializing Computer Use Agent", worker_id=self.worker_id)
            
            # Create the agent service with the real Computer Use Agent
            self.agent_service = AgentService(self.session_id)
            
            logger.info("Computer Use Agent initialized successfully", 
                       worker_id=self.worker_id,
                       session_id=self.session_id)
            
        except Exception as e:
            logger.error("Failed to initialize Computer Use Agent", 
                        worker_id=self.worker_id,
                        error=str(e))
            raise
    
    async def _cleanup_vnc(self) -> None:
        """Cleanup VNC server resources."""
        # TODO: Implement in Task 7.1
        logger.info("VNC cleanup placeholder", worker_id=self.worker_id)
        await asyncio.sleep(0.1)  # Simulate cleanup time
    
    async def _cleanup_vm(self) -> None:
        """Cleanup VM instance resources."""
        # TODO: Implement in Task 10.2
        logger.info("VM cleanup placeholder", worker_id=self.worker_id)
        await asyncio.sleep(0.1)  # Simulate cleanup time


class WorkerPool:
    """
    Manages a pool of workers for concurrent session handling.
    """
    
    def __init__(self):
        self.workers: Dict[str, Worker] = {}
        self.max_workers = 100  # From config
        logger.info("WorkerPool initialized")
    
    async def spawn_worker(self, session_id: str) -> Worker:
        """
        Spawn a new worker for a session.
        
        Args:
            session_id: The session ID to create a worker for
            
        Returns:
            Worker: The created and initialized worker
        """
        if session_id in self.workers:
            logger.warning("Worker already exists for session", session_id=session_id)
            return self.workers[session_id]
        
        if len(self.workers) >= self.max_workers:
            raise RuntimeError(f"Maximum number of workers ({self.max_workers}) reached")
        
        try:
            worker = Worker(session_id)
            await worker.initialize()
            
            self.workers[session_id] = worker
            logger.info("Worker spawned", session_id=session_id, worker_id=worker.worker_id, total_workers=len(self.workers))
            
            return worker
            
        except Exception as e:
            logger.error("Failed to spawn worker", session_id=session_id, error=str(e))
            raise
    
    async def get_worker(self, session_id: str) -> Optional[Worker]:
        """
        Get an existing worker for a session.
        
        Args:
            session_id: The session ID to get the worker for
            
        Returns:
            Worker or None: The worker if it exists
        """
        return self.workers.get(session_id)
    
    async def terminate_worker(self, session_id: str) -> bool:
        """
        Terminate and cleanup a worker for a session.
        
        Args:
            session_id: The session ID to terminate the worker for
            
        Returns:
            bool: True if worker was terminated, False if not found
        """
        worker = self.workers.get(session_id)
        if not worker:
            logger.warning("Worker not found for termination", session_id=session_id)
            return False
        
        try:
            await worker.cleanup()
            del self.workers[session_id]
            logger.info("Worker terminated", session_id=session_id, worker_id=worker.worker_id, remaining_workers=len(self.workers))
            return True
            
        except Exception as e:
            logger.error("Failed to terminate worker", session_id=session_id, error=str(e))
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Get health status of all workers.
        
        Returns:
            Dict: Health status information
        """
        worker_statuses = {}
        for session_id, worker in self.workers.items():
            worker_statuses[session_id] = {
                "worker_id": worker.worker_id,
                "status": worker.status,
                "created_at": worker.created_at.isoformat(),
                "vnc_port": worker.vnc_port
            }
        
        return {
            "total_workers": len(self.workers),
            "max_workers": self.max_workers,
            "workers": worker_statuses
        }
    
    async def cleanup_all(self) -> None:
        """Cleanup all workers (for shutdown)."""
        logger.info("Cleaning up all workers", total_workers=len(self.workers))
        
        cleanup_tasks = []
        for session_id, worker in self.workers.items():
            cleanup_tasks.append(worker.cleanup())
        
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        self.workers.clear()
        logger.info("All workers cleaned up")