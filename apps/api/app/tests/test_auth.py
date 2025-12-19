from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from firebase_admin import auth as firebase_auth

from app.deps.auth import get_subscribed_user, get_user
from app.models.user import User


class TestAuthentication:
    """Test suite for authentication functionality"""

    @patch("app.deps.auth.firebase_auth.verify_id_token")
    @patch("app.deps.auth.get_db")
    def test_get_user_success(self, mock_get_db, mock_verify_token):
        """Test successful user retrieval"""
        # Mock Firebase response
        mock_verify_token.return_value = {
            "uid": "firebase_uid_123",
            "email": "test@example.com",
            "name": "Test User",
        }

        # Mock database session and user
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        mock_user = User(
            id=1,
            firebase_uid="firebase_uid_123",
            email="test@example.com",
            name="Test User",
            is_subscribed=True,
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Create mock credentials
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid_token"
        )

        # Test the function
        result = get_user(mock_credentials, mock_db)

        assert result == mock_user
        mock_verify_token.assert_called_once_with("valid_token")

    @patch("app.deps.auth.firebase_auth.verify_id_token")
    @patch("app.deps.auth.get_db")
    def test_get_user_invalid_token(self, mock_get_db, mock_verify_token):
        """Test user retrieval with invalid token"""
        mock_verify_token.side_effect = Exception("Invalid token")

        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid_token"
        )

        with pytest.raises(HTTPException) as exc_info:
            get_user(mock_credentials, mock_db)

        assert exc_info.value.status_code == 401
        assert "Invalid or expired token" in str(exc_info.value.detail)

    @patch("app.deps.auth.firebase_auth.verify_id_token")
    @patch("app.deps.auth.get_db")
    def test_get_user_not_found(self, mock_get_db, mock_verify_token):
        """Test user retrieval when user doesn't exist in database"""
        # Mock Firebase response
        mock_verify_token.return_value = {
            "uid": "nonexistent_uid",
            "email": "nonexistent@example.com",
            "name": "Nonexistent User",
        }

        # Mock database session with no user found
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None

        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid_token"
        )

        with pytest.raises(HTTPException) as exc_info:
            get_user(mock_credentials, mock_db)

        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)

    @patch("app.deps.auth.get_user")
    def test_get_subscribed_user_success(self, mock_get_user):
        """Test successful subscribed user retrieval"""
        mock_user = User(
            id=1,
            firebase_uid="firebase_uid_123",
            email="test@example.com",
            name="Test User",
            is_subscribed=True,
        )
        mock_get_user.return_value = mock_user

        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid_token"
        )
        mock_db = Mock()

        result = get_subscribed_user(mock_credentials, mock_db)

        assert result == mock_user

    @patch("app.deps.auth.get_user")
    def test_get_subscribed_user_not_subscribed(self, mock_get_user):
        """Test subscribed user retrieval for non-subscribed user"""
        mock_user = User(
            id=1,
            firebase_uid="firebase_uid_123",
            email="test@example.com",
            name="Test User",
            is_subscribed=False,
        )
        mock_get_user.return_value = mock_user

        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid_token"
        )
        mock_db = Mock()

        with pytest.raises(HTTPException) as exc_info:
            get_subscribed_user(mock_credentials, mock_db)

        assert exc_info.value.status_code == 402
        assert "not subscribed" in str(exc_info.value.detail)

    @patch("app.deps.auth.firebase_auth.verify_id_token")
    def test_get_token_firebase_exception(self, mock_verify_token):
        """Test Firebase token verification exception handling"""
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials

        from app.deps.auth import get_token

        # Mock Firebase to raise an exception
        mock_verify_token.side_effect = Exception("Firebase verification failed")

        # Create mock credentials
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid_token"
        )

        # Test that HTTPException is raised
        with pytest.raises(HTTPException) as exc_info:
            get_token(mock_credentials)

        assert exc_info.value.status_code == 401
        assert "Invalid or expired token" in str(exc_info.value.detail)

    @patch("app.deps.auth.firebase_auth.verify_id_token")
    def test_get_token_firebase_exception_http_exception(self, mock_verify):
        """Test HTTPException is raised when Firebase verification fails"""
        from fastapi import HTTPException, status
        from fastapi.security import HTTPAuthorizationCredentials

        from app.deps.auth import get_token

        # Mock Firebase to raise exception
        mock_verify.side_effect = Exception("Firebase verification failed")

        # Create mock credentials
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid-token"
        )

        # Call get_token function directly
        with pytest.raises(HTTPException) as exc_info:
            get_token(mock_credentials)

        # Verify the correct HTTP exception was raised
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid or expired token" in str(exc_info.value.detail)


class TestAuthenticationIntegration:
    """Integration tests for authentication with actual FastAPI client"""

    def test_protected_endpoint_no_auth(self, client):
        """Test accessing protected endpoint without authentication"""
        # Temporarily remove auth overrides to test real auth behavior
        from app.deps.auth import get_user
        from app.main import app

        # Remove the override temporarily
        original_override = app.dependency_overrides.get(get_user)
        if get_user in app.dependency_overrides:
            del app.dependency_overrides[get_user]

        try:
            response = client.get("/tasks/")
            assert response.status_code == 403
            assert "Not authenticated" in response.json()["detail"]
        finally:
            # Restore the override
            if original_override:
                app.dependency_overrides[get_user] = original_override

    def test_protected_endpoint_invalid_auth(self, client):
        """Test accessing protected endpoint with invalid authentication"""
        # Temporarily remove auth overrides to test real auth behavior
        from app.deps.auth import get_user
        from app.main import app

        # Remove the override temporarily
        original_override = app.dependency_overrides.get(get_user)
        if get_user in app.dependency_overrides:
            del app.dependency_overrides[get_user]

        try:
            response = client.get(
                "/tasks/", headers={"Authorization": "InvalidFormat token"}
            )
            assert response.status_code == 403
            assert "Invalid authentication credentials" in response.json()["detail"]
        finally:
            # Restore the override
            if original_override:
                app.dependency_overrides[get_user] = original_override

    @patch("app.deps.auth.firebase_auth.verify_id_token")
    def test_protected_endpoint_valid_auth(self, mock_verify_token, client):
        """Test accessing protected endpoint with valid authentication"""
        # Temporarily remove auth overrides to test real auth behavior
        from app.deps.auth import get_user
        from app.main import app

        # Remove the override temporarily
        original_override = app.dependency_overrides.get(get_user)
        if get_user in app.dependency_overrides:
            del app.dependency_overrides[get_user]

        try:
            # Mock Firebase verification
            mock_verify_token.return_value = {
                "uid": "test_uid",
                "email": "test@example.com",
                "name": "Test User",
            }

            # This will still fail because the user doesn't exist in the test database,
            # but it shows the auth flow is working
            response = client.get(
                "/tasks/", headers={"Authorization": "Bearer valid_token"}
            )
            assert response.status_code == 404  # User not found in database
            assert "User not found" in response.json()["detail"]
        finally:
            # Restore the override
            if original_override:
                app.dependency_overrides[get_user] = original_override

    def test_subscription_required_endpoint_no_subscription(self, client):
        """Test accessing subscription-required endpoint without subscription"""
        # This test uses the overridden user which is subscribed, so we need to
        # temporarily override with an unsubscribed user
        from app.deps.auth import get_subscribed_user
        from app.main import app

        def mock_unsubscribed_user():
            raise HTTPException(status_code=402, detail="User is not subscribed")

        # Override with unsubscribed user
        original_override = app.dependency_overrides.get(get_subscribed_user)
        app.dependency_overrides[get_subscribed_user] = mock_unsubscribed_user

        try:
            response = client.post("/api/stripe/cancel-subscription")
            assert response.status_code == 402
            assert "not subscribed" in response.json()["detail"]
        finally:
            # Restore original override
            if original_override:
                app.dependency_overrides[get_subscribed_user] = original_override
