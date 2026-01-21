"""
Services package with shared instances.
"""

from .stream_handler import StreamHandler
from .worker import WorkerPool

# Shared global instances
_stream_handler: StreamHandler | None = None
_worker_pool: WorkerPool | None = None


def get_shared_stream_handler() -> StreamHandler:
    """Get the shared StreamHandler instance."""
    global _stream_handler
    if _stream_handler is None:
        _stream_handler = StreamHandler()
    return _stream_handler


def get_shared_worker_pool() -> WorkerPool:
    """Get the shared WorkerPool instance."""
    global _worker_pool
    if _worker_pool is None:
        _worker_pool = WorkerPool()
    return _worker_pool
