"""
Main FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import get_settings
from .database import init_database
from .logging_config import setup_logging
from .routers import sessions, health, websocket, vnc

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    settings = get_settings()
    
    # Setup logging
    setup_logging(settings.log_level)
    logger = logging.getLogger(__name__)
    
    # Initialize database
    logger.info("Initializing database...")
    await init_database()
    
    logger.info("Computer Use Backend started successfully")
    yield
    
    logger.info("Computer Use Backend shutting down...")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Computer Use Backend",
        description="Scalable FastAPI backend for Computer Use Demo with concurrent session support",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
    app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
    app.include_router(vnc.router, prefix="/vnc", tags=["vnc"])
    
    # Serve static files
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Serve the frontend at root
    @app.get("/")
    async def read_root():
        """Serve the web UI."""
        static_file = Path(__file__).parent / "static" / "index.html"
        if static_file.exists():
            return FileResponse(static_file)
        return {"message": "Computer Use Backend API", "docs": "/docs"}
    
    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "computer_use_backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )