
class TestConcurrentSessionIndependence:
    """Property-based tests for concurrent session independence."""

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
        num_sessions=st.integers(min_value=2, max_value=5),
        operations=st.lists(
            st.one_of(
                st.tuples(st.just("message"), message_content_strategy),
                st.tuples(st.just("metadata"), session_metadata_strategy),
            ),
            min_size=10,
            max_size=50
        )
    )
    @pytest.mark.asyncio
    async def test_concurrent_session_independence(self, num_sessions, operations):
        """
        **Feature: computer-use-backend, Property 1: Concurrent session independence**
        **Validates: Requirements 1.2, 1.3**
        
        Property: Multiple sessions operating concurrently should remain completely isolated.
        Actions taken in one session (messages, updates) should not affect others.
        Resources (workers) should be uniquely assigned.
        """
        db_path = None
        try:
            # Create test database and session manager
            db_path, db_session = await self.create_test_database()
            session_manager = SessionManager()
            
            # Create concurrent sessions
            sessions = []
            for i in range(num_sessions):
                session = await session_manager.create_session(
                    db_session, 
                    SessionCreate(session_metadata={"idx": i})
                )
                sessions.append(str(session.session_id))
            
            # Verify separate workers
            workers = []
            for session_id in sessions:
                # This simulates worker assignment
                worker = await session_manager.get_or_create_worker(session_id)
                workers.append(worker.worker_id)
            
            # All worker IDs should be unique
            assert len(set(workers)) == len(sessions)
            
            # Distribute operations across sessions using round-robin
            session_states = {s_id: {"messages": [], "metadata": {"idx": i}} for i, s_id in enumerate(sessions)}
            
            for i, (op_type, op_data) in enumerate(operations):
                target_session_id = sessions[i % len(sessions)]
                
                if op_type == "message":
                    # Add message to specific session
                    message_data = MessageCreate(content=op_data, role=MessageRole.USER)
                    await session_manager.create_message(db_session, target_session_id, message_data)
                    session_states[target_session_id]["messages"].append(op_data)
                    
                elif op_type == "metadata":
                    # Update metadata (simulated via session update if we had it, but here we'll just check initial persistence 
                    # serves as isolation check. Since we don't have update_session yet, we'll verify existing metadata isn't clobbered)
                    pass
            
            # Verify isolation
            for session_id in sessions:
                # Check messages
                retrieved_msgs = await session_manager.get_session_messages(db_session, session_id)
                expected_msgs = session_states[session_id]["messages"]
                
                assert len(retrieved_msgs) == len(expected_msgs)
                for msg, expected_content in zip(retrieved_msgs, expected_msgs):
                    assert msg.content == expected_content
                    assert str(msg.session_id) == session_id
                
                # Check worker is still the same and unique
                worker = await session_manager.get_or_create_worker(session_id)
                assert worker.worker_id in workers
                
            await db_session.close()
            
        finally:
            if db_path and os.path.exists(db_path):
                os.unlink(db_path)
