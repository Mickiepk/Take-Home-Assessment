"""
VNC server management for desktop access.
"""

import asyncio
import subprocess
from typing import Optional
from pathlib import Path

from ..config import get_settings
from ..logging_config import get_logger

logger = get_logger(__name__)

class VNCServer:
    """
    Manages a VNC server instance for a session.
    Provides remote desktop access to the Computer Use Agent's environment.
    """
    def __init__(self, session_id: str, display_num: int):
        self.session_id = session_id
        self.display_num = display_num
        self.settings = get_settings()
        
        # VNC port is base_port + display_num
        self.vnc_port = self.settings.vnc_base_port + display_num
        
        # Process handles
        self.xvfb_process: Optional[subprocess.Popen] = None
        self.x11vnc_process: Optional[subprocess.Popen] = None
        
        self.is_running = False
        
        logger.info("VNCServer created", 
                   session_id=session_id,
                   display_num=display_num,
                   vnc_port=self.vnc_port)
    
    async def start(self) -> None:
        """
        Start the VNC server with Xvfb virtual display.
        """
        try:
            # Start Xvfb (X Virtual Framebuffer)
            await self._start_xvfb()
            
            # Start x11vnc server
            await self._start_x11vnc()
            
            self.is_running = True
            logger.info("VNC server started successfully",
                       session_id=self.session_id,
                       vnc_port=self.vnc_port,
                       display=f":{self.display_num}")
            
        except Exception as e:
            logger.error("Failed to start VNC server",
                        session_id=self.session_id,
                        error=str(e))
            await self.stop()
            raise
    
    async def _start_xvfb(self) -> None:
        """Start Xvfb virtual display."""
        try:
            # Xvfb command: Xvfb :display_num -screen 0 WIDTHxHEIGHTx24
            cmd = [
                "Xvfb",
                f":{self.display_num}",
                "-screen", "0",
                f"{self.settings.width}x{self.settings.height}x24",
                "-ac",  # Disable access control
                "+extension", "RANDR"  # Enable RANDR extension
            ]
            
            logger.info("Starting Xvfb", 
                       session_id=self.session_id,
                       command=" ".join(cmd))
            
            self.xvfb_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Wait a bit for Xvfb to start
            await asyncio.sleep(0.5)
            
            # Check if process is still running
            if self.xvfb_process.poll() is not None:
                stderr = self.xvfb_process.stderr.read().decode() if self.xvfb_process.stderr else ""
                raise RuntimeError(f"Xvfb failed to start: {stderr}")
            
            logger.info("Xvfb started", 
                       session_id=self.session_id,
                       pid=self.xvfb_process.pid)
            
        except FileNotFoundError:
            raise RuntimeError("Xvfb not found. Please install: apt-get install xvfb")
        except Exception as e:
            logger.error("Failed to start Xvfb", 
                        session_id=self.session_id,
                        error=str(e))
            raise
    
    async def _start_x11vnc(self) -> None:
        """Start x11vnc server."""
        try:
            # x11vnc command: x11vnc -display :display_num -rfbport vnc_port -forever -shared
            cmd = [
                "x11vnc",
                "-display", f":{self.display_num}",
                "-rfbport", str(self.vnc_port),
                "-forever",  # Keep running after client disconnects
                "-shared",   # Allow multiple clients
                "-nopw",     # No password (for development)
                "-quiet",    # Reduce log output
                "-bg"        # Run in background
            ]
            
            logger.info("Starting x11vnc",
                       session_id=self.session_id,
                       command=" ".join(cmd))
            
            self.x11vnc_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Wait for x11vnc to start
            await asyncio.sleep(0.5)
            
            # Check if process is still running
            if self.x11vnc_process.poll() is not None:
                stderr = self.x11vnc_process.stderr.read().decode() if self.x11vnc_process.stderr else ""
                raise RuntimeError(f"x11vnc failed to start: {stderr}")
            
            logger.info("x11vnc started",
                       session_id=self.session_id,
                       pid=self.x11vnc_process.pid,
                       vnc_port=self.vnc_port)
            
        except FileNotFoundError:
            raise RuntimeError("x11vnc not found. Please install: apt-get install x11vnc")
        except Exception as e:
            logger.error("Failed to start x11vnc",
                        session_id=self.session_id,
                        error=str(e))
            raise
    
    async def stop(self) -> None:
        """Stop the VNC server and cleanup resources."""
        try:
            logger.info("Stopping VNC server",
                       session_id=self.session_id,
                       vnc_port=self.vnc_port)
            
            # Stop x11vnc
            if self.x11vnc_process:
                try:
                    self.x11vnc_process.terminate()
                    await asyncio.sleep(0.2)
                    if self.x11vnc_process.poll() is None:
                        self.x11vnc_process.kill()
                    logger.info("x11vnc stopped", session_id=self.session_id)
                except Exception as e:
                    logger.warning("Error stopping x11vnc", 
                                 session_id=self.session_id,
                                 error=str(e))
            
            # Stop Xvfb
            if self.xvfb_process:
                try:
                    self.xvfb_process.terminate()
                    await asyncio.sleep(0.2)
                    if self.xvfb_process.poll() is None:
                        self.xvfb_process.kill()
                    logger.info("Xvfb stopped", session_id=self.session_id)
                except Exception as e:
                    logger.warning("Error stopping Xvfb",
                                 session_id=self.session_id,
                                 error=str(e))
            
            self.is_running = False
            logger.info("VNC server stopped successfully",
                       session_id=self.session_id)
            
        except Exception as e:
            logger.error("Error stopping VNC server",
                        session_id=self.session_id,
                        error=str(e))
    
    def get_display(self) -> str:
        """Get the DISPLAY environment variable value."""
        return f":{self.display_num}"
    
    def get_vnc_url(self) -> str:
        """Get the VNC connection URL."""
        return f"vnc://localhost:{self.vnc_port}"
    
    async def health_check(self) -> dict:
        """Check VNC server health."""
        xvfb_running = self.xvfb_process and self.xvfb_process.poll() is None
        x11vnc_running = self.x11vnc_process and self.x11vnc_process.poll() is None
        
        return {
            "is_running": self.is_running,
            "xvfb_running": xvfb_running,
            "x11vnc_running": x11vnc_running,
            "display": self.get_display(),
            "vnc_port": self.vnc_port,
            "vnc_url": self.get_vnc_url()
        }
