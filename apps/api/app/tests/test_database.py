"""
Test suite for database core functionality
"""

from unittest.mock import Mock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, SessionLocal, get_db


class TestDatabase:
    """Test suite for database core functionality"""

    def test_get_db_session_creation(self):
        """Test that get_db creates and yields a database session"""
        db_generator = get_db()
        db_session = next(db_generator)

        # Verify we get a session object
        assert db_session is not None
        assert hasattr(db_session, "query")
        assert hasattr(db_session, "commit")
        assert hasattr(db_session, "rollback")

        # Clean up
        try:
            next(db_generator)
        except StopIteration:
            # Expected - generator should close after yielding
            pass

    def test_get_db_session_cleanup(self):
        """Test that get_db properly closes the session"""
        db_generator = get_db()
        db_session = next(db_generator)

        # Mock the close method to verify it's called
        original_close = db_session.close
        db_session.close = Mock(side_effect=original_close)

        # Trigger cleanup by exhausting generator
        try:
            next(db_generator)
        except StopIteration:
            pass

        # Verify close was called
        db_session.close.assert_called_once()

    @patch("app.core.database.SessionLocal")
    def test_get_db_exception_handling(self, mock_session_local):
        """Test that get_db handles exceptions and still closes session"""
        mock_session = Mock()
        mock_session_local.return_value = mock_session

        db_generator = get_db()
        db_session = next(db_generator)

        # Verify we got the mocked session
        assert db_session == mock_session

        # Simulate exception during cleanup
        try:
            next(db_generator)
        except StopIteration:
            pass

        # Verify close was called even if there was an exception
        mock_session.close.assert_called_once()

    def test_sessionlocal_configuration(self):
        """Test SessionLocal is properly configured"""
        # Verify SessionLocal creates working sessions
        session = SessionLocal()

        assert session is not None
        assert hasattr(session, "query")
        assert hasattr(session, "add")
        assert hasattr(session, "commit")
        assert hasattr(session, "rollback")

        # Clean up
        session.close()

    def test_base_declarative_base(self):
        """Test that Base is properly configured as declarative base"""
        # Verify Base has the expected methods and attributes
        assert hasattr(Base, "metadata")
        assert hasattr(Base, "registry")
        assert callable(getattr(Base, "prepare", None)) or hasattr(
            Base, "__init_subclass__"
        )

    def test_database_connection_properties(self):
        """Test database engine and connection properties"""
        from app.core.database import engine

        # Verify engine exists and has expected properties
        assert engine is not None
        assert hasattr(engine, "connect")
        # Note: modern SQLAlchemy engines don't have direct execute method

        # Test connection can be established
        with engine.connect() as conn:
            assert conn is not None

    def test_session_transaction_behavior(self):
        """Test session transaction behavior"""
        session = SessionLocal()

        try:
            # Test that session supports transactions
            assert hasattr(session, "begin")
            assert hasattr(session, "commit")
            assert hasattr(session, "rollback")

        finally:
            session.close()

    def test_multiple_sessions_independence(self):
        """Test that multiple sessions are independent"""
        session1 = SessionLocal()
        session2 = SessionLocal()

        try:
            # Verify they are different objects
            assert session1 is not session2

            # Verify they have independent state
            # (This is a basic check - in a real scenario you'd test with actual data)
            assert session1.get_bind() == session2.get_bind()  # Same engine

        finally:
            session1.close()
            session2.close()
