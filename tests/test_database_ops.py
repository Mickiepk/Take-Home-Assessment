import pytest
import uuid
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from computer_use_backend.models.database import Base, Session, Message
from computer_use_backend.models.schemas import SessionCreate, MessageCreate, MessageRole
from computer_use_backend.services.session_manager import SessionManager

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def db_session():
    """Create a fresh database session with tables created."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        yield session
        
    await engine.dispose()

@pytest.mark.asyncio
async def test_session_create(db_session):
    """Test creating a session."""
    manager = SessionManager()
    session_data = SessionCreate(session_metadata={"test": "data"})
    
    session = await manager.create_session(db_session, session_data)
    
    assert session.session_id is not None
    assert session.status == "active"
    assert session.session_metadata == {"test": "data"}

@pytest.mark.asyncio
async def test_session_get(db_session):
    """Test retrieving a session."""
    manager = SessionManager()
    session_data = SessionCreate()
    created_session = await manager.create_session(db_session, session_data)
    
    retrieved_session = await manager.get_session(db_session, str(created_session.session_id))
    
    assert retrieved_session is not None
    assert retrieved_session.session_id == created_session.session_id
    
    # Test getting non-existent session
    assert await manager.get_session(db_session, str(uuid.uuid4())) is None

@pytest.mark.asyncio
async def test_session_list(db_session):
    """Test listing sessions."""
    manager = SessionManager()
    
    # Create 3 sessions
    for i in range(3):
        await manager.create_session(db_session, SessionCreate(session_metadata={"idx": i}))
        
    sessions = await manager.list_sessions(db_session)
    assert len(sessions) == 3
    
    # Verify strict ordering if needed, but for now just check count
    # Manager lists by created_at desc

@pytest.mark.asyncio
async def test_message_create_and_retrieve(db_session):
    """Test creating and retrieving messages."""
    manager = SessionManager()
    
    # Create session first
    session = await manager.create_session(db_session, SessionCreate())
    session_id = str(session.session_id)
    
    # Create messages
    msg1_data = MessageCreate(content="Hello", role=MessageRole.USER)
    msg2_data = MessageCreate(content="Hi there", role=MessageRole.ASSISTANT)
    
    msg1 = await manager.create_message(db_session, session_id, msg1_data)
    msg2 = await manager.create_message(db_session, session_id, msg2_data)
    
    # Retrieve messages
    messages = await manager.get_session_messages(db_session, session_id)
    
    assert len(messages) == 2
    assert messages[0].content == "Hello"
    assert messages[0].role == "user"
    assert messages[1].content == "Hi there"
    assert messages[1].role == "assistant"
    
    # Verify chronological order
    assert messages[0].timestamp <= messages[1].timestamp

@pytest.mark.asyncio
async def test_session_terminate(db_session):
    """Test terminating a session."""
    manager = SessionManager()
    session = await manager.create_session(db_session, SessionCreate())
    session_id = str(session.session_id)
    
    await manager.terminate_session(db_session, session_id)
    
    # Should not appear in list_sessions
    sessions = await manager.list_sessions(db_session)
    assert len(sessions) == 0
    
    # But should still get retrieved directly
    retrieved = await manager.get_session(db_session, session_id)
    assert retrieved.status == "terminated"
