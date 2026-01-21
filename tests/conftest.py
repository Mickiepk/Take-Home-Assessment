"""
Pytest configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from computer_use_backend.main import create_app
from computer_use_backend.database import get_db_session


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine):
    """Create test database session."""
    async_session_maker = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session


@pytest.fixture
def test_app(test_db_session):
    """Create test FastAPI application."""
    app = create_app()
    
    # Override database dependency
    app.dependency_overrides[get_db_session] = lambda: test_db_session
    
    return app


@pytest.fixture
def test_client(test_app):
    """Create test client."""
    return TestClient(test_app)