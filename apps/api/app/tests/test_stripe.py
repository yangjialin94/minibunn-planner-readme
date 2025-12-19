import json
from contextlib import contextmanager
from unittest.mock import ANY, Mock, patch

import pytest
import stripe
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User

# Set up test database
TEST_DATABASE_URL = "sqlite:///file::memory:?cache=shared"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestStripeRoutes:
    """Test suite for Stripe payment integration"""

    @contextmanager
    def override_get_user(self, mock_user_attrs):
        """Context manager to temporarily override get_user dependency"""
        from app.deps.auth import get_user
        from app.main import app

        def mock_get_user():
            mock_user = Mock()
            # Set default attributes
            default_attrs = {
                "stripe_subscription_id": None,
                "subscription_status": None,
                "is_subscribed": False,
                "stripe_customer_id": "cus_test123",
            }
            default_attrs.update(mock_user_attrs)

            # Configure mock to handle both attribute access and getattr()
            for key, value in default_attrs.items():
                setattr(mock_user, key, value)

            return mock_user

        original_override = app.dependency_overrides.get(get_user)
        app.dependency_overrides[get_user] = mock_get_user

        try:
            yield
        finally:
            if original_override:
                app.dependency_overrides[get_user] = original_override
            else:
                app.dependency_overrides.pop(get_user, None)

    @contextmanager
    def override_get_subscribed_user(self, mock_user_attrs):
        """Context manager to temporarily override get_subscribed_user dependency"""
        from app.deps.auth import get_subscribed_user
        from app.main import app

        def mock_get_subscribed_user():
            mock_user = Mock()
            mock_user.configure_mock(**mock_user_attrs)
            return mock_user

        original_override = app.dependency_overrides.get(get_subscribed_user)
        app.dependency_overrides[get_subscribed_user] = mock_get_subscribed_user

        try:
            yield
        finally:
            if original_override:
                app.dependency_overrides[get_subscribed_user] = original_override
            mock_user = Mock()
            mock_user.configure_mock(**mock_user_attrs)
            return mock_user

        original_override = app.dependency_overrides.get(get_user)
        app.dependency_overrides[get_user] = mock_get_user

        try:
            yield
        finally:
            if original_override:
                app.dependency_overrides[get_user] = original_override

    def test_get_subscription_status_no_subscription(self, client):
        """Test subscription status for user without subscription"""
        with self.override_get_user(
            {"stripe_subscription_id": None, "subscription_status": None}
        ):
            response = client.get("/api/stripe/subscription-status")
            assert response.status_code == 200
            data = response.json()
            assert data["is_subscribed"] is False
            assert data["status"] == "none"
            assert data["period_end_date"] is None

    def test_get_subscription_status_lifetime(self, client):
        """Test subscription status for user with lifetime subscription"""
        with self.override_get_user(
            {"stripe_subscription_id": None, "subscription_status": "lifetime"}
        ):
            response = client.get("/api/stripe/subscription-status")
            assert response.status_code == 200
            data = response.json()
            assert data["is_subscribed"] is True
            assert data["status"] == "lifetime"
            assert data["plan_name"] == "Lifetime Access"
            assert data["price_amount"] == 29.99

    @patch("stripe.Subscription.retrieve")
    def test_get_subscription_status_active(self, mock_retrieve, client):
        """Test subscription status for user with active Stripe subscription"""
        # Mock Stripe subscription response
        mock_subscription = {
            "status": "active",
            "cancel_at_period_end": False,
            "items": {
                "data": [
                    {
                        "current_period_end": 1640995200,  # Jan 1, 2022
                        "price": {
                            "unit_amount": 999,  # $9.99 in cents
                            "currency": "usd",
                            "product": {"name": "Monthly Plan"},
                        },
                    }
                ]
            },
        }
        mock_retrieve.return_value = mock_subscription

        with self.override_get_user({"stripe_subscription_id": "sub_123"}):
            response = client.get("/api/stripe/subscription-status")
            assert response.status_code == 200
            data = response.json()
            assert data["is_subscribed"] is True
            assert data["status"] == "active"
            assert data["plan_name"] == "Monthly Plan"
            assert data["price_amount"] == 9.99

    @patch("stripe.Subscription.retrieve")
    def test_get_subscription_status_stripe_error(self, mock_retrieve, client):
        """Test subscription status when Stripe API fails"""
        mock_retrieve.side_effect = stripe.StripeError("API Error")

        with self.override_get_user({"stripe_subscription_id": "sub_123"}):
            response = client.get("/api/stripe/subscription-status")
            assert response.status_code == 502
            assert "API Error" in response.json()["detail"]

    @patch("stripe.Customer.create")
    @patch("stripe.checkout.Session.create")
    def test_create_checkout_session_new_customer(
        self, mock_session_create, mock_customer_create, client
    ):
        """Test creating checkout session for new customer"""
        # Mock Stripe responses
        mock_customer_create.return_value = Mock(id="cus_123")
        mock_session_create.return_value = Mock(
            url="https://checkout.stripe.com/pay/session_123"
        )

        with self.override_get_user(
            {"stripe_customer_id": None, "email": "test@example.com"}
        ):
            response = client.post(
                "/api/stripe/create-checkout-session",
                json={
                    "price_id": "price_123",
                    "mode": "subscription",
                    "success_url": "https://example.com/success",
                    "cancel_url": "https://example.com/cancel",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["url"] == "https://checkout.stripe.com/pay/session_123"
            mock_customer_create.assert_called_once()

    @patch("stripe.checkout.Session.create")
    def test_create_checkout_session_existing_customer(
        self, mock_session_create, client
    ):
        """Test creating checkout session for existing customer"""
        mock_session_create.return_value = Mock(
            url="https://checkout.stripe.com/pay/session_123"
        )

        with self.override_get_user(
            {"stripe_customer_id": "cus_123", "email": "test@example.com"}
        ):
            response = client.post(
                "/api/stripe/create-checkout-session",
                json={
                    "price_id": "price_123",
                    "mode": "payment",
                    "success_url": "https://example.com/success",
                    "cancel_url": "https://example.com/cancel",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["url"] == "https://checkout.stripe.com/pay/session_123"

    @patch("stripe.Customer.create")
    def test_create_checkout_session_stripe_customer_error(
        self, mock_customer_create, client
    ):
        """Test checkout session creation when Stripe customer creation fails"""
        mock_customer_create.side_effect = stripe.StripeError(
            "Customer creation failed"
        )

        with self.override_get_user(
            {"stripe_customer_id": None, "email": "test@example.com"}
        ):
            response = client.post(
                "/api/stripe/create-checkout-session",
                json={
                    "price_id": "price_123",
                    "mode": "subscription",
                    "success_url": "https://example.com/success",
                    "cancel_url": "https://example.com/cancel",
                },
            )

            assert response.status_code == 502
            assert "Customer creation failed" in response.json()["detail"]

    @patch("stripe.checkout.Session.create")
    def test_create_checkout_session_stripe_session_error(
        self, mock_session_create, client
    ):
        """Test checkout session creation when Stripe session creation fails"""
        mock_session_create.side_effect = stripe.StripeError("Session creation failed")

        with self.override_get_user(
            {"stripe_customer_id": "cus_123", "email": "test@example.com"}
        ):
            response = client.post(
                "/api/stripe/create-checkout-session",
                json={
                    "price_id": "price_123",
                    "mode": "subscription",
                    "success_url": "https://example.com/success",
                    "cancel_url": "https://example.com/cancel",
                },
            )

            assert response.status_code == 502
            assert "Session creation failed" in response.json()["detail"]

    @patch("stripe.Subscription.modify")
    def test_cancel_subscription_success(self, mock_modify, client):
        """Test successful subscription cancellation"""
        mock_modify.return_value = Mock()

        with self.override_get_subscribed_user({"stripe_subscription_id": "sub_123"}):
            response = client.post("/api/stripe/cancel-subscription")
            assert response.status_code == 200
            data = response.json()
            assert "canceled" in data["message"]
            mock_modify.assert_called_once_with("sub_123", cancel_at_period_end=True)

    def test_cancel_subscription_no_subscription(self, seeded_client):
        """Test cancellation when user has no subscription"""
        with patch("app.routes.stripe.get_subscribed_user") as mock_get_user:
            mock_user = Mock()
            mock_user.configure_mock(**{"stripe_subscription_id": None})
            mock_get_user.return_value = mock_user

            response = seeded_client.post("/api/stripe/cancel-subscription")
            assert response.status_code == 400
            assert "No active subscription" in response.json()["detail"]

    @patch("stripe.Subscription.modify")
    def test_cancel_subscription_stripe_error(self, mock_modify, client):
        """Test subscription cancellation when Stripe API fails"""
        mock_modify.side_effect = stripe.StripeError("Cancellation failed")

        with self.override_get_subscribed_user({"stripe_subscription_id": "sub_123"}):
            response = client.post("/api/stripe/cancel-subscription")
            assert response.status_code == 502
            assert "Cancellation failed" in response.json()["detail"]

    @patch("stripe.Webhook.construct_event")
    def test_stripe_webhook_checkout_completed_subscription(
        self, mock_construct_event, seeded_client
    ):
        """Test webhook handling for completed subscription checkout"""
        mock_event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_123",
                    "subscription": "sub_123",
                    "mode": "subscription",
                }
            },
        }
        mock_construct_event.return_value = mock_event

        # Mock request with proper headers
        response = seeded_client.post(
            "/api/stripe/webhook",
            json={"test": "data"},
            headers={"stripe-signature": "test_sig"},
        )

        assert response.status_code == 200
        assert response.json() == {"received": True}

    @patch("stripe.Webhook.construct_event")
    def test_stripe_webhook_checkout_completed_payment(
        self, mock_construct_event, seeded_client
    ):
        """Test webhook handling for completed one-time payment"""
        mock_event = {
            "type": "checkout.session.completed",
            "data": {"object": {"customer": "cus_123", "mode": "payment"}},
        }
        mock_construct_event.return_value = mock_event

        response = seeded_client.post(
            "/api/stripe/webhook",
            json={"test": "data"},
            headers={"stripe-signature": "test_sig"},
        )

        assert response.status_code == 200
        assert response.json() == {"received": True}

    @patch("stripe.Webhook.construct_event")
    def test_stripe_webhook_invalid_signature(
        self, mock_construct_event, seeded_client
    ):
        """Test webhook handling with invalid signature"""
        mock_construct_event.side_effect = stripe.SignatureVerificationError(
            "Invalid signature", "sig_header"
        )

        response = seeded_client.post(
            "/api/stripe/webhook",
            json={"test": "data"},
            headers={"stripe-signature": "invalid_sig"},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid signature"

    @patch("stripe.Webhook.construct_event")
    def test_stripe_webhook_subscription_updated(
        self, mock_construct_event, seeded_client
    ):
        """Test webhook handling for subscription updates"""
        mock_event = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {"id": "sub_123", "customer": "cus_123", "status": "active"}
            },
        }
        mock_construct_event.return_value = mock_event

        response = seeded_client.post(
            "/api/stripe/webhook",
            json={"test": "data"},
            headers={"stripe-signature": "test_sig"},
        )

        assert response.status_code == 200
        assert response.json() == {"received": True}

    @patch("stripe.Webhook.construct_event")
    def test_stripe_webhook_subscription_deleted(
        self, mock_construct_event, seeded_client
    ):
        """Test webhook handling for subscription deletion"""
        mock_event = {
            "type": "customer.subscription.deleted",
            "data": {"object": {"id": "sub_123", "customer": "cus_123"}},
        }
        mock_construct_event.return_value = mock_event

        response = seeded_client.post(
            "/api/stripe/webhook",
            json={"test": "data"},
            headers={"stripe-signature": "test_sig"},
        )

        assert response.status_code == 200
        assert response.json() == {"received": True}

    @patch("stripe.Webhook.construct_event")
    def test_stripe_webhook_payment_failed(self, mock_construct_event, seeded_client):
        """Test webhook handling for payment failures"""
        mock_event = {
            "type": "invoice.payment_failed",
            "data": {"object": {"customer": "cus_123"}},
        }
        mock_construct_event.return_value = mock_event

        response = seeded_client.post(
            "/api/stripe/webhook",
            json={"test": "data"},
            headers={"stripe-signature": "test_sig"},
        )

        assert response.status_code == 200
        assert response.json() == {"received": True}

    def test_stripe_webhook_invalid_payload(self, seeded_client):
        """Test webhook handling with invalid payload"""
        response = seeded_client.post(
            "/api/stripe/webhook",
            content="invalid json",  # Use content instead of data
            headers={
                "stripe-signature": "test_sig",
                "content-type": "application/json",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid signature"  # Signature fails first

    @patch("stripe.Webhook.construct_event")
    def test_stripe_webhook_invoice_paid(self, mock_construct_event, seeded_client):
        """Test webhook handling for invoice paid events"""
        mock_event = {
            "type": "invoice.paid",
            "data": {"object": {"customer": "cus_123"}},
        }
        mock_construct_event.return_value = mock_event

        response = seeded_client.post(
            "/api/stripe/webhook",
            json={"test": "data"},
            headers={"stripe-signature": "test_sig"},
        )

        assert response.status_code == 200
        assert response.json() == {"received": True}

    @patch("stripe.Webhook.construct_event")
    def test_stripe_webhook_unknown_event_type(
        self, mock_construct_event, seeded_client
    ):
        """Test webhook handling for unknown event types"""
        mock_event = {
            "type": "unknown.event.type",
            "data": {"object": {"customer": "cus_unknown"}},
        }
        mock_construct_event.return_value = mock_event

        response = seeded_client.post(
            "/api/stripe/webhook",
            json={"test": "data"},
            headers={"stripe-signature": "test_sig"},
        )

        assert response.status_code == 200
        assert response.json() == {"received": True}

    @patch("app.routes.stripe.stripe")
    def test_webhook_invalid_payload(self, mock_stripe, client):
        """Test webhook with invalid payload"""
        mock_stripe.Webhook.construct_event.side_effect = ValueError("Invalid payload")

        payload = "invalid-payload"
        headers = {"stripe-signature": "test-signature"}

        response = client.post("/api/stripe/webhook", data=payload, headers=headers)

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid payload"

    @patch("app.routes.stripe.stripe")
    def test_webhook_invalid_signature(self, mock_stripe, client):
        """Test webhook with invalid signature"""

        # Create a custom exception class that properly inherits from BaseException
        class MockSignatureVerificationError(Exception):
            pass

        mock_stripe.Webhook.construct_event.side_effect = (
            MockSignatureVerificationError("Invalid signature")
        )
        mock_stripe.SignatureVerificationError = MockSignatureVerificationError

        payload = json.dumps({"type": "test.event"})
        headers = {"stripe-signature": "invalid-signature"}

        response = client.post("/api/stripe/webhook", data=payload, headers=headers)

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid signature"

    @patch("app.routes.stripe.stripe")
    def test_webhook_unhandled_event_type_with_unknown_customer(
        self, mock_stripe, client
    ):
        """Test webhook with unhandled event type and unknown customer ID"""
        # Mock Stripe webhook event with unhandled type
        mock_event = {
            "type": "some.unhandled.event",
            "data": {"object": {"customer": "cus_unknown123"}},
        }
        mock_stripe.Webhook.construct_event.return_value = mock_event

        payload = json.dumps(mock_event)
        headers = {"stripe-signature": "test-signature"}

        with patch("app.routes.stripe.logger") as mock_logger:
            response = client.post("/api/stripe/webhook", data=payload, headers=headers)

            assert response.status_code == 200
            assert response.json() == {"received": True}
            # Verify warning was logged for unknown customer
            mock_logger.warning.assert_called()
