"""Debug script to understand dependency override issue"""

import sys

sys.path.append(
    "/Users/mielegemie/Documents/Minibunn Planner/Repos/minibunn-planner-api"
)

from app.deps.auth import get_user
from app.main import app

# Check what's currently in dependency_overrides
print("Current overrides:")
for key, value in app.dependency_overrides.items():
    print(f"  {key}: {value}")

# Test the context manager
from contextlib import contextmanager
from unittest.mock import Mock


@contextmanager
def override_get_user(mock_user_attrs):
    """Context manager to temporarily override get_user dependency"""

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
    print(f"Before override: {original_override}")
    app.dependency_overrides[get_user] = mock_get_user
    print(f"After override: {app.dependency_overrides[get_user]}")

    try:
        yield
    finally:
        if original_override:
            app.dependency_overrides[get_user] = original_override
            print(f"Restored original: {original_override}")
        else:
            app.dependency_overrides.pop(get_user, None)
            print("Popped override (original was None)")


# Test it
print("\nTesting context manager...")
with override_get_user({"subscription_status": "lifetime"}):
    print(f"Inside context: {app.dependency_overrides[get_user]}")

print(f"After context: {app.dependency_overrides.get(get_user)}")
