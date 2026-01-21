"""
Logging configuration using structlog.
"""

import logging
import sys
from typing import Any, Dict

import structlog


def setup_logging(log_level: str = "INFO") -> None:
    """Setup structured logging configuration."""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            # Add log level and timestamp
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # Use JSON formatting for production
            structlog.processors.JSONRenderer() if log_level.upper() != "DEBUG"
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration: float,
    **kwargs: Any
) -> None:
    """Log HTTP request details."""
    logger = get_logger("http")
    logger.info(
        "HTTP request",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=round(duration * 1000, 2),
        **kwargs
    )


def log_worker_event(
    session_id: str,
    event: str,
    **kwargs: Any
) -> None:
    """Log worker-related events."""
    logger = get_logger("worker")
    logger.info(
        "Worker event",
        session_id=session_id,
        event=event,
        **kwargs
    )


def log_database_event(
    operation: str,
    table: str,
    duration: float,
    **kwargs: Any
) -> None:
    """Log database operation events."""
    logger = get_logger("database")
    logger.info(
        "Database operation",
        operation=operation,
        table=table,
        duration_ms=round(duration * 1000, 2),
        **kwargs
    )