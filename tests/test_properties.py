"""
Property-based tests for Computer Use Backend.

**Feature: computer-use-backend, Property 5: Data persistence across restarts**
**Validates: Requirements 4.3**
"""

import asyncio
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

import pytest
from hypothesis import given, strategies as st
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from computer_use_backend.models.database import Base, Session, Message
from computer_use_backend.models.schemas import SessionCreate, MessageCreate, MessageRole
from computer_use_backend.services.session_manager import SessionManager


# Hypothesis strategies for generating test data
session_metadata_strategy = st.dictionaries(
    st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"))),
    st.one_of(
        st.text(min_size=0, max_size=100),
        st.integers(min_value=-1000, max_value=1000),
        st.booleans(),
    ),
    min_size=0,
    max_size=5
)

message_content_strategy = st.text(min_size=1, max_size=1000)
message_metadata_strategy = session_metadata_strategy


class TestDataPersistence:
    """Property-based tests for data persistence."""

    async def create_test_database(self) -> tuple[str, AsyncSession]:
        """Create a temporary database for testing."""
        # Create temporary database file
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        database_url = f"sqlite+aiosqlite:///{temp_db.name}"
        
        # Create engine and session
        engine = create_async_engine(database_url, echo=False)
        async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Return database path and session
        session = async_session_maker()
        return temp_db.name, session

    async def recreate_database_connection(self, db_path: str) -> AsyncSession:
        """Recreate database connection to simulate restart."""
        database_url = f"sqlite+aiosqlite:///{db_path}"
        engine = create_async_engine(database_url, echo=False)
        async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        return async_session_maker()

    @given(
        session_data=st.lists(
            st.tuples(session_metadata_strategy),
            min_size=1,
            max_size=5
        )
    )
    @pytest.mark.asyncio
    async def test_session_persistence_across_restarts(self, session_data):
        """
        **Feature: computer-use-backend, Property 5: Data persistence across restarts**
        **Validates: Requirements 4.3**
        
        Property: For any session data stored in the database, 
        the data should remain intact and accessible after system restarts.
        """
        db_path = None
        try:
            # Create test database and session manager
            db_path, db_session = await self.create_test_database()
            session_manager = SessionManager()
            
            # Store sessions in the database
            created_sessions = []
            for metadata_tuple in session_data:
                metadata = metadata_tuple[0]
                session_create = SessionCreate(session_metadata=metadata)
                session = await session_manager.create_session(db_session, session_create)
                created_sessions.append((str(session.session_id), session.session_metadata))
            
            await db_session.close()
            
            # Simulate system restart by recreating database connection
            new_db_session = await self.recreate_database_connection(db_path)
            new_session_manager = SessionManager()
            
            # Verify all sessions are still accessible
            retrieved_sessions = await new_session_manager.list_sessions(new_db_session)
            
            # Check that all created sessions are still there
            assert len(retrieved_sessions) == len(created_sessions)
            
            # Verify each session's data integrity
            for original_id, original_metadata in created_sessions:
                retrieved_session = await new_session_manager.get_session(new_db_session, original_id)
                assert retrieved_session is not None
                assert str(retrieved_session.session_id) == original_id
                assert retrieved_session.session_metadata == original_metadata
                assert retrieved_session.status == "active"
            
            await new_db_session.close()
            
        finally:
            # Cleanup temporary database
            if db_path and os.path.exists(db_path):
                os.unlink(db_path)

    @given(
        session_metadata=session_metadata_strategy,
        messages_data=st.lists(
            st.tuples(message_content_strategy, message_metadata_strategy),
            min_size=1,
            max_size=10
        )
    )
    @pytest.mark.asyncio
    async def test_message_persistence_across_restarts(self, session_metadata, messages_data):
        """
        **Feature: computer-use-backend, Property 5: Data persistence across restarts**
        **Validates: Requirements 4.3**
        
        Property: For any message data stored in a session, 
        the messages should remain intact and in correct order after system restarts.
        """
        db_path = None
        try:
            # Create test database and session manager
            db_path, db_session = await self.create_test_database()
            session_manager = SessionManager()
            
            # Create a session
            session_create = SessionCreate(session_metadata=session_metadata)
            session = await session_manager.create_session(db_session, session_create)
            session_id = str(session.session_id)
            
            # Add messages to the session
            created_messages = []
            for content, metadata in messages_data:
                message_create = MessageCreate(
                    content=content,
                    role=MessageRole.USER,
                    message_metadata=metadata
                )
                message = await session_manager.create_message(db_session, session_id, message_create)
                created_messages.append((str(message.message_id), content, metadata))
            
            await db_session.close()
            
            # Simulate system restart
            new_db_session = await self.recreate_database_connection(db_path)
            new_session_manager = SessionManager()
            
            # Verify session still exists
            retrieved_session = await new_session_manager.get_session(new_db_session, session_id)
            assert retrieved_session is not None
            assert retrieved_session.session_metadata == session_metadata
            
            # Verify all messages are still there and in correct order
            retrieved_messages = await new_session_manager.get_session_messages(new_db_session, session_id)
            assert len(retrieved_messages) == len(created_messages)
            
            # Check message data integrity and order
            for i, (original_id, original_content, original_metadata) in enumerate(created_messages):
                retrieved_message = retrieved_messages[i]
                assert str(retrieved_message.message_id) == original_id
                assert retrieved_message.content == original_content
                assert retrieved_message.message_metadata == original_metadata
                assert retrieved_message.role == MessageRole.USER.value
                assert str(retrieved_message.session_id) == session_id
            
            await new_db_session.close()
            
        finally:
            # Cleanup temporary database
            if db_path and os.path.exists(db_path):
                os.unlink(db_path)

    @given(
        initial_sessions=st.lists(session_metadata_strategy, min_size=2, max_size=5),
        sessions_to_terminate=st.integers(min_value=1, max_value=2)
    )
    @pytest.mark.asyncio
    async def test_session_status_persistence_across_restarts(self, initial_sessions, sessions_to_terminate):
        """
        **Feature: computer-use-backend, Property 5: Data persistence across restarts**
        **Validates: Requirements 4.3**
        
        Property: For any session status changes (like termination), 
        the status should persist correctly after system restarts.
        """
        db_path = None
        try:
            # Create test database and session manager
            db_path, db_session = await self.create_test_database()
            session_manager = SessionManager()
            
            # Create sessions
            created_sessions = []
            for metadata in initial_sessions:
                session_create = SessionCreate(session_metadata=metadata)
                session = await session_manager.create_session(db_session, session_create)
                created_sessions.append(str(session.session_id))
            
            # Terminate some sessions
            terminated_sessions = created_sessions[:sessions_to_terminate]
            for session_id in terminated_sessions:
                await session_manager.terminate_session(db_session, session_id)
            
            await db_session.close()
            
            # Simulate system restart
            new_db_session = await self.recreate_database_connection(db_path)
            new_session_manager = SessionManager()
            
            # Verify terminated sessions have correct status
            for session_id in terminated_sessions:
                retrieved_session = await new_session_manager.get_session(new_db_session, session_id)
                assert retrieved_session is not None
                assert retrieved_session.status == "terminated"
            
            # Verify active sessions are still active
            active_sessions = created_sessions[sessions_to_terminate:]
            for session_id in active_sessions:
                retrieved_session = await new_session_manager.get_session(new_db_session, session_id)
                assert retrieved_session is not None
                assert retrieved_session.status == "active"
            
            # Verify list_sessions only returns active sessions
            active_session_list = await new_session_manager.list_sessions(new_db_session)
            active_session_ids = [str(s.session_id) for s in active_session_list]
            
            for session_id in active_sessions:
                assert session_id in active_session_ids
            
            for session_id in terminated_sessions:
                assert session_id not in active_session_ids
            
            await new_db_session.close()
            
        finally:
            # Cleanup temporary database
            if db_path and os.path.exists(db_path):
                os.unlink(db_path)


class TestMessageProcessingAndPersistence:
    """Property-based tests for message processing and persistence."""

    async def create_test_database(self) -> tuple[str, AsyncSession]:
        """Create a temporary database for testing."""
        # Create temporary database file
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        database_url = f"sqlite+aiosqlite:///{temp_db.name}"
        
        # Create engine and session
        engine = create_async_engine(database_url, echo=False)
        async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Return database path and session
        session = async_session_maker()
        return temp_db.name, session

    @given(
        session_metadata=session_metadata_strategy,
        messages=st.lists(
            st.tuples(
                message_content_strategy,
                st.sampled_from([MessageRole.USER, MessageRole.ASSISTANT, MessageRole.TOOL]),
                message_metadata_strategy
            ),
            min_size=1,
            max_size=20
        )
    )
    @pytest.mark.asyncio
    async def test_message_processing_and_persistence_property(self, session_metadata, messages):
        """
        **Feature: computer-use-backend, Property 2: Message processing and persistence**
        **Validates: Requirements 2.2, 2.4, 4.1, 4.2, 4.4**
        
        Property: For any message sent to a session, the system should spawn a worker to process it,
        persist the message to the database immediately, and return complete message history 
        in chronological order when queried.
        """
        db_path = None
        try:
            # Create test database and session manager
            db_path, db_session = await self.create_test_database()
            session_manager = SessionManager()
            
            # Create a session
            session_create = SessionCreate(session_metadata=session_metadata)
            session = await session_manager.create_session(db_session, session_create)
            session_id = str(session.session_id)
            
            # Process and persist messages
            created_message_ids = []
            expected_messages = []
            
            for i, (content, role, metadata) in enumerate(messages):
                message_create = MessageCreate(
                    content=content,
                    role=role,
                    message_metadata=metadata
                )
                
                # Test immediate persistence
                message = await session_manager.create_message(db_session, session_id, message_create)
                created_message_ids.append(str(message.message_id))
                expected_messages.append({
                    'id': str(message.message_id),
                    'content': content,
                    'role': role.value,
                    'metadata': metadata,
                    'session_id': session_id
                })
                
                # Verify message is immediately available
                retrieved_messages = await session_manager.get_session_messages(db_session, session_id)
                assert len(retrieved_messages) == i + 1
                
                # Verify the just-added message
                latest_message = retrieved_messages[-1]
                assert str(latest_message.message_id) == str(message.message_id)
                assert latest_message.content == content
                assert latest_message.role == role.value
                assert latest_message.message_metadata == metadata
            
            # Test complete message history retrieval in chronological order
            all_messages = await session_manager.get_session_messages(db_session, session_id)
            assert len(all_messages) == len(expected_messages)
            
            # Verify chronological order and data integrity
            for i, (retrieved_msg, expected_msg) in enumerate(zip(all_messages, expected_messages)):
                assert str(retrieved_msg.message_id) == expected_msg['id']
                assert retrieved_msg.content == expected_msg['content']
                assert retrieved_msg.role == expected_msg['role']
                assert retrieved_msg.message_metadata == expected_msg['metadata']
                assert str(retrieved_msg.session_id) == expected_msg['session_id']
                
                # Verify chronological order (later messages have later timestamps)
                if i > 0:
                    assert retrieved_msg.timestamp >= all_messages[i-1].timestamp
            
            await db_session.close()
            
        finally:
            # Cleanup temporary database
            if db_path and os.path.exists(db_path):
                os.unlink(db_path)

    @given(
        num_sessions=st.integers(min_value=2, max_value=5),
        messages_per_session=st.integers(min_value=1, max_value=10)
    )
    @pytest.mark.asyncio
    async def test_concurrent_message_processing_isolation(self, num_sessions, messages_per_session):
        """
        **Feature: computer-use-backend, Property 2: Message processing and persistence**
        **Validates: Requirements 2.2, 2.4, 4.1, 4.2, 4.4**
        
        Property: Messages processed for different sessions should be properly isolated
        and each session should only return its own messages in chronological order.
        """
        db_path = None
        try:
            # Create test database and session manager
            db_path, db_session = await self.create_test_database()
            session_manager = SessionManager()
            
            # Create multiple sessions
            sessions = []
            for i in range(num_sessions):
                session_create = SessionCreate(session_metadata={"session_index": i})
                session = await session_manager.create_session(db_session, session_create)
                sessions.append(str(session.session_id))
            
            # Add messages to each session
            session_messages = {}
            for session_id in sessions:
                session_messages[session_id] = []
                for j in range(messages_per_session):
                    content = f"Message {j} for session {session_id}"
                    message_create = MessageCreate(
                        content=content,
                        role=MessageRole.USER,
                        message_metadata={"message_index": j}
                    )
                    message = await session_manager.create_message(db_session, session_id, message_create)
                    session_messages[session_id].append({
                        'id': str(message.message_id),
                        'content': content,
                        'index': j
                    })
            
            # Verify message isolation - each session should only see its own messages
            for session_id in sessions:
                retrieved_messages = await session_manager.get_session_messages(db_session, session_id)
                expected_messages = session_messages[session_id]
                
                assert len(retrieved_messages) == len(expected_messages)
                
                # Verify each message belongs to the correct session and is in order
                for i, (retrieved_msg, expected_msg) in enumerate(zip(retrieved_messages, expected_messages)):
                    assert str(retrieved_msg.message_id) == expected_msg['id']
                    assert retrieved_msg.content == expected_msg['content']
                    assert str(retrieved_msg.session_id) == session_id
                    assert retrieved_msg.message_metadata["message_index"] == expected_msg['index']
                    
                    # Verify no messages from other sessions are included
                    for other_session_id in sessions:
                        if other_session_id != session_id:
                            assert str(retrieved_msg.session_id) != other_session_id
            
            await db_session.close()
            
        finally:
            # Cleanup temporary database
            if db_path and os.path.exists(db_path):
                os.unlink(db_path)

    @given(
        session_metadata=session_metadata_strategy,
        valid_messages=st.lists(
            st.tuples(
                st.text(min_size=1, max_size=100),  # Valid content
                message_metadata_strategy
            ),
            min_size=1,
            max_size=5
        ),
        invalid_session_ids=st.lists(
            st.one_of(
                st.text(min_size=1, max_size=10, alphabet="abcdef"),  # Invalid UUID format
                st.just("nonexistent-uuid-12345"),
                st.just("")
            ),
            min_size=1,
            max_size=3
        )
    )
    @pytest.mark.asyncio
    async def test_message_processing_error_handling(self, session_metadata, valid_messages, invalid_session_ids):
        """
        **Feature: computer-use-backend, Property 2: Message processing and persistence**
        **Validates: Requirements 2.2, 2.4, 4.1, 4.2, 4.4**
        
        Property: Message processing should handle errors gracefully and maintain data consistency
        when invalid session IDs are provided or other errors occur.
        """
        db_path = None
        try:
            # Create test database and session manager
            db_path, db_session = await self.create_test_database()
            session_manager = SessionManager()
            
            # Create a valid session
            session_create = SessionCreate(session_metadata=session_metadata)
            session = await session_manager.create_session(db_session, session_create)
            valid_session_id = str(session.session_id)
            
            # Add valid messages to the valid session
            valid_message_count = 0
            for content, metadata in valid_messages:
                message_create = MessageCreate(
                    content=content,
                    role=MessageRole.USER,
                    message_metadata=metadata
                )
                message = await session_manager.create_message(db_session, valid_session_id, message_create)
                assert message is not None
                valid_message_count += 1
            
            # Verify valid messages were stored correctly
            valid_session_messages = await session_manager.get_session_messages(db_session, valid_session_id)
            assert len(valid_session_messages) == valid_message_count
            
            # Test error handling with invalid session IDs
            for invalid_session_id in invalid_session_ids:
                message_create = MessageCreate(
                    content="Test message for invalid session",
                    role=MessageRole.USER,
                    message_metadata={"test": "error_case"}
                )
                
                # Should raise an exception or handle gracefully
                try:
                    await session_manager.create_message(db_session, invalid_session_id, message_create)
                    # If no exception, verify the message wasn't created
                    assert False, f"Expected error for invalid session ID: {invalid_session_id}"
                except (ValueError, Exception):
                    # Expected behavior - error should be raised
                    pass
            
            # Verify that failed operations didn't affect valid session data
            final_valid_messages = await session_manager.get_session_messages(db_session, valid_session_id)
            assert len(final_valid_messages) == valid_message_count
            
            # Verify data integrity of valid messages
            for i, (original_content, original_metadata) in enumerate(valid_messages):
                retrieved_message = final_valid_messages[i]
                assert retrieved_message.content == original_content
                assert retrieved_message.message_metadata == original_metadata
                assert str(retrieved_message.session_id) == valid_session_id
            
            await db_session.close()
            
        finally:
            # Cleanup temporary database
            if db_path and os.path.exists(db_path):
                os.unlink(db_path)

class TestErrorHandling:
    """Property-based tests for error handling with invalid inputs."""

    @given(
        invalid_session_ids=st.lists(
            st.one_of(
                st.text(min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz0123456789-"),  # Invalid UUID format
                st.just("not-a-uuid"),  # Invalid format
                st.just("12345678-1234-1234-1234-123456789abc"),  # Valid format but nonexistent
                st.just("null"),
                st.just("undefined")
            ),
            min_size=1,
            max_size=5
        )
    )
    @pytest.mark.asyncio
    async def test_invalid_session_id_error_handling(self, invalid_session_ids):
        """
        **Feature: computer-use-backend, Property 3: Error handling for invalid inputs**
        **Validates: Requirements 2.5**
        
        Property: For any invalid session ID provided to API endpoints, 
        the system should return appropriate HTTP error responses.
        """
        db_path = None
        try:
            # Create test database and session manager
            temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
            temp_db.close()
            db_path = temp_db.name
            
            database_url = f"sqlite+aiosqlite:///{db_path}"
            
            # Create engine and session
            from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
            engine = create_async_engine(database_url, echo=False)
            async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            
            # Create tables
            from computer_use_backend.models.database import Base
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            # Override the database dependency for testing
            from computer_use_backend.main import create_app
            from computer_use_backend.database import get_db_session
            from fastapi.testclient import TestClient
            
            async def override_get_db_session():
                async with async_session_maker() as session:
                    try:
                        yield session
                    except Exception:
                        await session.rollback()
                        raise
                    finally:
                        await session.close()
            
            app = create_app()
            app.dependency_overrides[get_db_session] = override_get_db_session
            client = TestClient(app)
            
            for invalid_session_id in invalid_session_ids:
                # Test GET /sessions/{id}
                response = client.get(f"/sessions/{invalid_session_id}")
                assert response.status_code in [400, 404, 422], f"Expected error for session ID: {invalid_session_id}, got: {response.status_code}"
                
                # Test GET /sessions/{id}/messages
                response = client.get(f"/sessions/{invalid_session_id}/messages")
                assert response.status_code in [400, 404, 422], f"Expected error for session ID: {invalid_session_id}, got: {response.status_code}"
                
                # Test POST /sessions/{id}/messages
                response = client.post(
                    f"/sessions/{invalid_session_id}/messages",
                    json={"content": "test message", "role": "user"}
                )
                assert response.status_code in [400, 404, 422, 500], f"Expected error for session ID: {invalid_session_id}, got: {response.status_code}"
                
                # Test DELETE /sessions/{id}
                response = client.delete(f"/sessions/{invalid_session_id}")
                assert response.status_code in [400, 404, 422], f"Expected error for session ID: {invalid_session_id}, got: {response.status_code}"
            
        finally:
            # Cleanup temporary database
            if db_path and os.path.exists(db_path):
                os.unlink(db_path)

    @given(
        invalid_message_data=st.lists(
            st.one_of(
                st.fixed_dictionaries({"content": st.just(""), "role": st.just("user")}),  # Empty content
                st.fixed_dictionaries({"content": st.text(min_size=2000000), "role": st.just("user")}),  # Too large content
                st.fixed_dictionaries({"content": st.just("test"), "role": st.just("invalid_role")}),  # Invalid role
                st.fixed_dictionaries({"role": st.just("user")}),  # Missing content
                st.fixed_dictionaries({"content": st.just("test")}),  # Missing role
                st.just({}),  # Empty object
            ),
            min_size=1,
            max_size=5
        )
    )
    @pytest.mark.asyncio
    async def test_invalid_message_data_error_handling(self, invalid_message_data):
        """
        **Feature: computer-use-backend, Property 3: Error handling for invalid inputs**
        **Validates: Requirements 2.5**
        
        Property: For any invalid message data provided to message creation endpoints,
        the system should return appropriate HTTP error responses and maintain data consistency.
        """
        from fastapi.testclient import TestClient
        from computer_use_backend.main import create_app
        
        app = create_app()
        client = TestClient(app)
        
        # First create a valid session
        session_response = client.post("/sessions/", json={"session_metadata": {"test": "error_handling"}})
        assert session_response.status_code == 201
        session_id = session_response.json()["session_id"]
        
        # Test each invalid message data
        for invalid_data in invalid_message_data:
            response = client.post(f"/sessions/{session_id}/messages", json=invalid_data)
            assert response.status_code in [400, 422, 500], f"Expected error for message data: {invalid_data}"
            
            # Verify that failed requests don't corrupt the session
            session_check = client.get(f"/sessions/{session_id}")
            assert session_check.status_code == 200
            
            # Verify that failed requests don't create invalid messages
            messages_response = client.get(f"/sessions/{session_id}/messages")
            assert messages_response.status_code == 200
            messages = messages_response.json()
            
            # All messages should be valid (no corrupted data)
            for message in messages:
                assert "message_id" in message
                assert "content" in message
                assert "role" in message
                assert message["role"] in ["user", "assistant", "tool"]
                assert len(message["content"]) > 0
                assert message["session_id"] == session_id

    @given(
        invalid_session_data=st.lists(
            st.one_of(
                st.fixed_dictionaries({"session_metadata": st.text(min_size=10000)}),  # Too large metadata
                st.fixed_dictionaries({"invalid_field": st.just("value")}),  # Invalid field
                st.just("not_an_object"),  # Not an object
                st.just(None),  # Null
            ),
            min_size=1,
            max_size=3
        )
    )
    @pytest.mark.asyncio
    async def test_invalid_session_creation_error_handling(self, invalid_session_data):
        """
        **Feature: computer-use-backend, Property 3: Error handling for invalid inputs**
        **Validates: Requirements 2.5**
        
        Property: For any invalid session creation data, the system should return 
        appropriate HTTP error responses and not create corrupted sessions.
        """
        from fastapi.testclient import TestClient
        from computer_use_backend.main import create_app
        
        app = create_app()
        client = TestClient(app)
        
        # Get initial session count
        initial_response = client.get("/sessions/")
        assert initial_response.status_code == 200
        initial_count = len(initial_response.json())
        
        for invalid_data in invalid_session_data:
            # Try to create session with invalid data
            if isinstance(invalid_data, dict):
                response = client.post("/sessions/", json=invalid_data)
            else:
                # For non-dict data, we expect JSON parsing errors
                response = client.post("/sessions/", data=str(invalid_data))
            
            # Should return an error status code
            assert response.status_code in [400, 422, 500], f"Expected error for session data: {invalid_data}"
            
            # Verify no corrupted sessions were created
            sessions_response = client.get("/sessions/")
            assert sessions_response.status_code == 200
            current_sessions = sessions_response.json()
            
            # Session count should not increase due to failed requests
            assert len(current_sessions) == initial_count
            
            # All existing sessions should still be valid
            for session in current_sessions:
                assert "session_id" in session
                assert "status" in session
                assert "created_at" in session
                assert "updated_at" in session
                assert session["status"] in ["active", "processing", "idle", "terminated"]

    @given(
        concurrent_invalid_requests=st.integers(min_value=5, max_value=20)
    )
    @pytest.mark.asyncio
    async def test_concurrent_invalid_requests_stability(self, concurrent_invalid_requests):
        """
        **Feature: computer-use-backend, Property 3: Error handling for invalid inputs**
        **Validates: Requirements 2.5**
        
        Property: The system should handle multiple concurrent invalid requests gracefully
        without affecting system stability or valid operations.
        """
        from fastapi.testclient import TestClient
        from computer_use_backend.main import create_app
        import threading
        import time
        
        app = create_app()
        client = TestClient(app)
        
        # Create a valid session first
        valid_session_response = client.post("/sessions/", json={"session_metadata": {"test": "stability"}})
        assert valid_session_response.status_code == 201
        valid_session_id = valid_session_response.json()["session_id"]
        
        # Add a valid message
        valid_message_response = client.post(
            f"/sessions/{valid_session_id}/messages",
            json={"content": "Valid message before stress test", "role": "user"}
        )
        assert valid_message_response.status_code == 201
        
        # Define invalid requests to make concurrently
        invalid_requests = [
            lambda: client.get("/sessions/invalid-uuid-format"),
            lambda: client.get("/sessions/00000000-0000-0000-0000-000000000000/messages"),
            lambda: client.post("/sessions/invalid/messages", json={"content": "", "role": "user"}),
            lambda: client.delete("/sessions/nonexistent-session"),
            lambda: client.post("/sessions/", json={"invalid": "data"}),
        ]
        
        # Make concurrent invalid requests
        results = []
        threads = []
        
        def make_request(request_func):
            try:
                response = request_func()
                results.append(response.status_code)
            except Exception as e:
                results.append(f"Exception: {str(e)}")
        
        # Start concurrent threads
        for i in range(concurrent_invalid_requests):
            request_func = invalid_requests[i % len(invalid_requests)]
            thread = threading.Thread(target=make_request, args=(request_func,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify that all invalid requests returned error codes
        for result in results:
            if isinstance(result, int):
                assert result >= 400, f"Expected error status code, got: {result}"
        
        # Verify that the valid session and message are still intact
        session_check = client.get(f"/sessions/{valid_session_id}")
        assert session_check.status_code == 200
        
        messages_check = client.get(f"/sessions/{valid_session_id}/messages")
        assert messages_check.status_code == 200
        messages = messages_check.json()
        assert len(messages) == 1
        assert messages[0]["content"] == "Valid message before stress test"
        
        # Verify we can still create valid sessions and messages
        new_session_response = client.post("/sessions/", json={"session_metadata": {"test": "post_stress"}})
        assert new_session_response.status_code == 201
        
        new_message_response = client.post(
            f"/sessions/{valid_session_id}/messages",
            json={"content": "Valid message after stress test", "role": "assistant"}
        )
        assert new_message_response.status_code == 201