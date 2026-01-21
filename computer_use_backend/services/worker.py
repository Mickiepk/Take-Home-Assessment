import asyncio
import uuid
import os
from typing import Optional, Dict, Any, AsyncIterator
from datetime import datetime

from ..models.schemas import AgentUpdate, UpdateType
from ..logging_config import get_logger
from ..config import get_settings
from .agent_service import AgentService
from .mock_agent_service import MockAgentService
from .vnc_server import VNCServer

logger = get_logger(__name__)

class Worker:
    
    def __init__(self, sess_id: str):
        self.session_id = sess_id
        self.worker_id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.status = "initializing"
        self.settings = get_settings()
        
        self.vm_instance = None
        self.vnc_server = None
        self.vnc_port = None
        self.display_num = self.settings.display_num + hash(sess_id) % 100
        self.agent_service = None
        
        logger.info("Worker created", worker_id=self.worker_id, session_id=sess_id)
    
    async def initialize(self):
        try:
            self.status = "initializing"
            await self._init_vm()
            await self._init_vnc()
            await self._init_agent()
            
            self.status = "ready"
            logger.info("Worker initialized", worker_id=self.worker_id, session_id=self.session_id)
        except Exception as e:
            self.status = "failed"
            logger.error("Worker initialization failed", worker_id=self.worker_id, error=str(e))
            raise
    
    async def process_message(self, msg_content: str) -> AsyncIterator[AgentUpdate]:
        if self.status != "ready":
            raise RuntimeError(f"Worker not ready. Status: {self.status}")
        
        if not self.agent_service:
            raise RuntimeError("Agent service not initialized")
        
        try:
            self.status = "processing"
            # print(f"Debug: processing msg for {self.session_id}")  # quick debug
            
            async for update in self.agent_service.process_message(msg_content):
                yield update
            
            self.status = "ready"
        except Exception as e:
            self.status = "error"
            logger.error("Message processing failed", worker_id=self.worker_id, error=str(e))
            
            yield AgentUpdate(
                update_type=UpdateType.ERROR,
                content=f"Error processing message: {str(e)}",
                timestamp=datetime.utcnow(),
                metadata={"worker_id": self.worker_id, "error": str(e)}
            )
            self.status = "ready"
    
    async def get_vnc_stream(self) -> bytes:
        if not self.vnc_server:
            raise RuntimeError("VNC server not initialized")
        return b"VNC_PLACEHOLDER_DATA"
    
    async def cleanup(self):
        try:
            self.status = "terminating"
            logger.info("Cleaning up worker", worker_id=self.worker_id, session_id=self.session_id)
            
            if self.agent_service:
                self.agent_service.clear_history()
                self.agent_service = None
            
            if self.vnc_server:
                await self._cleanup_vnc()
            
            if self.vm_instance:
                await self._cleanup_vm()
            
            self.status = "terminated"
        except Exception as e:
            logger.error("Worker cleanup failed", worker_id=self.worker_id, error=str(e))
            raise

    async def _init_vm(self):
        # FIXME: implement actual VM setup later
        await asyncio.sleep(0.1)
    
    async def _init_vnc(self):
        try:
            self.vnc_server = VNCServer(self.session_id, self.display_num)
            await self.vnc_server.start()
            self.vnc_port = self.vnc_server.vnc_port
            os.environ["DISPLAY"] = self.vnc_server.get_display()
        except Exception as e:
            logger.warning("VNC init failed, continuing without it", error=str(e))
            self.vnc_server = None
            self.vnc_port = None
    
    async def _init_agent(self):
        api_key = self.settings.anthropic_api_key
        use_mock = not api_key or api_key == "your_anthropic_api_key_here" or api_key == ""
        
        if use_mock:
            logger.warning("No API key - using mock agent")
            self.agent_service = MockAgentService(self.session_id)
        else:
            self.agent_service = AgentService(self.session_id)
    
    async def _cleanup_vnc(self):
        if self.vnc_server:
            await self.vnc_server.stop()
            self.vnc_server = None
            self.vnc_port = None
    
    async def _cleanup_vm(self):
        await asyncio.sleep(0.1)


class WorkerPool:
    
    def __init__(self):
        self.workers = {}
        self.max_workers = 100
        logger.info("WorkerPool initialized")
    
    async def spawn_worker(self, sess_id: str) -> Worker:
        if sess_id in self.workers:
            return self.workers[sess_id]
        
        if len(self.workers) >= self.max_workers:
            raise RuntimeError(f"Max workers ({self.max_workers}) reached")
        
        worker = Worker(sess_id)
        await worker.initialize()
        self.workers[sess_id] = worker
        
        return worker
    
    async def get_worker(self, sess_id: str):
        return self.workers.get(sess_id)
    
    async def terminate_worker(self, sess_id: str) -> bool:
        worker = self.workers.get(sess_id)
        if not worker:
            return False
        
        await worker.cleanup()
        del self.workers[sess_id]
        return True
    
    async def health_check(self):
        statuses = {}
        for sid, w in self.workers.items():
            statuses[sid] = {
                "worker_id": w.worker_id,
                "status": w.status,
                "created_at": w.created_at.isoformat(),
                "vnc_port": w.vnc_port
            }
        
        return {
            "total_workers": len(self.workers),
            "max_workers": self.max_workers,
            "workers": statuses
        }
    
    async def cleanup_all(self):
        tasks = [w.cleanup() for w in self.workers.values()]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self.workers.clear()