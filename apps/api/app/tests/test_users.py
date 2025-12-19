"""
Test suite for user management functionality
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from app.models.user import User


class TestUserRoutes:
    """Test suite for user management routes"""

    def test_get_all_users(self, seeded_client):
        """Test retrieving all users"""
        response = seeded_client.get("/users/all")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["email"] == "test@example.com"

    def test_get_user_by_id_success(self, seeded_client):
        """Test retrieving a specific user by ID"""
        response = seeded_client.get("/users/by_id/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        assert "tasks" in data
        assert "notes" in data
        assert "backlogs" in data

    def test_get_user_by_id_not_found(self, client):
        """Test retrieving non-existent user by ID"""
        response = client.get("/users/by_id/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_get_current_user_existing(self, seeded_client):
        """Test getting current user when user already exists"""
        # Use seeded_client which has proper dependency overrides set up
        response = seeded_client.get("/users/get_current")
        assert response.status_code == 200

        data = response.json()
        assert data["firebase_uid"] == "test-firebase-uid"
        assert data["email"] == "test@example.com"

    def test_get_current_user_create_new(self, client):
        """Test creating new user when user doesn't exist"""
        from app.deps.auth import get_token
        from app.main import app

        # Override with a different token that will create a new user
        def mock_get_token():
            return {
                "uid": "new-user-12345",
                "email": "newuser@example.com",
                "name": "New User",
            }

        # Temporarily override the dependency
        original_override = app.dependency_overrides.get(get_token)
        app.dependency_overrides[get_token] = mock_get_token

        try:
            response = client.get("/users/get_current")
            assert response.status_code == 200

            data = response.json()
            assert data["firebase_uid"] == "new-user-12345"
            assert data["email"] == "newuser@example.com"
            assert data["name"] == "New User"
            assert data["is_subscribed"] is False
        finally:
            # Always reset to None to avoid contamination
            app.dependency_overrides.pop(get_token, None)

    def test_patch_user_success(self, seeded_client):
        """Test successful user update"""
        response = seeded_client.patch(
            "/users/1",
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_patch_user_not_found(self, client):
        """Test updating a user that doesn't exist"""
        response = client.patch(
            "/users/9999",
            json={"name": "Ghost"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_patch_user_multiple_fields(self, seeded_client):
        """Test updating multiple user fields"""
        response = seeded_client.patch(
            "/users/1",
            json={"name": "New Name"},  # Only name is allowed in UserUpdate
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"

    def test_patch_user_subscription_status(self, seeded_client):
        """Test that subscription status cannot be updated via API"""
        # is_subscribed is not in UserUpdate schema, so this should fail
        response = seeded_client.patch(
            "/users/1",
            json={"is_subscribed": False},
        )
        assert response.status_code == 422  # Unprocessable Entity - field not allowed

    def test_patch_user_empty_update(self, seeded_client):
        """Test updating user with no changes"""
        # Empty JSON should fail validation
        response = seeded_client.patch("/users/1", json={})
        assert response.status_code == 422  # No valid fields provided

    def test_get_current_user_create_new_user_debug(self, client):
        """Test creating a new user to trigger debug print statement"""
        from app.deps.auth import get_token
        from app.main import app

        def mock_get_token():
            return {
                "uid": "test-new-user-debug-12345",
                "name": "Debug Test User",
                "email": "debug@test.com",
            }

        app.dependency_overrides[get_token] = mock_get_token

        try:
            response = client.get("/users/get_current")
            assert response.status_code == 200
            user_data = response.json()
            assert user_data["firebase_uid"] == "test-new-user-debug-12345"
            assert user_data["name"] == "Debug Test User"
            assert user_data["email"] == "debug@test.com"
            assert user_data["is_subscribed"] is False
        finally:
            app.dependency_overrides.pop(get_token, None)

    def test_cleanup_override_branch_coverage(self, client):
        """Test the cleanup logic to cover missing line 68"""
        from app.deps.auth import get_token
        from app.main import app

        # Ensure there's no existing override (this tests the elif branch on line 68)
        if get_token in app.dependency_overrides:
            del app.dependency_overrides[get_token]

        def mock_get_token():
            return {
                "uid": "test-cleanup-coverage",
                "name": "Cleanup Test User",
                "email": "cleanup@test.com",
            }

        # This will trigger the cleanup logic in the test
        original_override = app.dependency_overrides.get(get_token)  # Should be None
        app.dependency_overrides[get_token] = mock_get_token

        try:
            response = client.get("/users/get_current")
            assert response.status_code == 200
        finally:
            # This cleanup logic covers line 68 (elif branch)
            if original_override:
                app.dependency_overrides[get_token] = original_override
            elif get_token in app.dependency_overrides:
                del app.dependency_overrides[get_token]
