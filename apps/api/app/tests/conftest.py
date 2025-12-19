import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.deps.auth import get_subscribed_user, get_token, get_user
from app.main import app
from app.models.user import User

# Force SQLite for tests - override any environment DATABASE_URL
os.environ["DATABASE_URL"] = "sqlite:///file::memory:?cache=shared"
TEST_DATABASE_URL = "sqlite:///file::memory:?cache=shared"

# Create a new engine and session for each test
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override FastAPI dependencies
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_user():
    return User(
        id=1,
        firebase_uid="test-firebase-uid",
        name="Test User",
        email="test@example.com",
        is_subscribed=True,
    )


def override_get_subscribed_user():
    return User(
        id=1,
        firebase_uid="test-firebase-uid",
        name="Test User",
        email="test@example.com",
        is_subscribed=True,
    )


def override_get_token():
    return {
        "uid": "test-firebase-uid",
        "email": "test@example.com",
        "name": "Test User",
    }


# Create tables before running tests
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Setup and teardown dependency overrides
@pytest.fixture(scope="session", autouse=True)
def setup_dependency_overrides():
    # Set up overrides
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_user] = override_get_user
    app.dependency_overrides[get_subscribed_user] = override_get_subscribed_user
    app.dependency_overrides[get_token] = override_get_token
    yield
    # Clean up overrides
    app.dependency_overrides.clear()


# Provide a new client for each test with clean database
@pytest.fixture
def client():
    # Create a new engine and session for each test to ensure isolation
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Clean slate for each test
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    # Override the database dependency
    original_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db

    try:
        yield TestClient(app)
    finally:
        # Restore original override if it existed
        if original_override:
            app.dependency_overrides[get_db] = original_override
        else:
            app.dependency_overrides.pop(get_db, None)
        # Clean up
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


# Create new user for each test
@pytest.fixture
def seeded_client(client):
    # Get a test database session
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestSessionLocal()
    try:
        db.add(
            User(
                id=1,
                firebase_uid="test-firebase-uid",
                name="Test User",
                email="test@example.com",
                is_subscribed=True,
            )
        )
        db.commit()
    finally:
        db.close()
    return client
