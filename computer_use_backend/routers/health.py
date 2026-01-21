"""
Health check endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session
from ..logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/")
async def health_check() -> Dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "computer-use-backend"}

@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check including database connectivity."""
    health_status = {
        "status": "healthy",
        "service": "computer-use-backend",
        "components": {}
    }
    
    # Check database connectivity
    try:
        from ..database import async_session_maker
        if async_session_maker is None:
            health_status["status"] = "degraded"
            health_status["components"]["database"] = {
                "status": "unavailable",
                "error": "Database not initialized"
            }
        else:
            # Try to get a database session and test it
            from ..database import get_db_session
            async for db in get_db_session():
                from sqlalchemy import text
                await db.execute(text("SELECT 1"))
                health_status["components"]["database"] = {"status": "healthy"}
                logger.info("Database health check passed")
                break
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        logger.error("Database health check failed", error=str(e))
    
    return health_status