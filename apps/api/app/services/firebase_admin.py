import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials

from app.core.config import (
    FIREBASE_AUTH_PROVIDER_CERT_URL,
    FIREBASE_AUTH_URI,
    FIREBASE_CLIENT_CERT_URL,
    FIREBASE_CLIENT_EMAIL,
    FIREBASE_CLIENT_ID,
    FIREBASE_PRIVATE_KEY,
    FIREBASE_PRIVATE_KEY_ID,
    FIREBASE_PROJECT_ID,
    FIREBASE_TOKEN_URI,
    FIREBASE_TYPE,
)

# Construct Firebase credentials from environment variables
firebase_credentials = {
    "type": FIREBASE_TYPE,
    "project_id": FIREBASE_PROJECT_ID,
    "private_key_id": FIREBASE_PRIVATE_KEY_ID,
    "private_key": FIREBASE_PRIVATE_KEY,
    "client_email": FIREBASE_CLIENT_EMAIL,
    "client_id": FIREBASE_CLIENT_ID,
    "auth_uri": FIREBASE_AUTH_URI,
    "token_uri": FIREBASE_TOKEN_URI,
    "auth_provider_x509_cert_url": FIREBASE_AUTH_PROVIDER_CERT_URL,
    "client_x509_cert_url": FIREBASE_CLIENT_CERT_URL,
}

# Check if Firebase Admin has already been initialized to prevent reinitialization errors.
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)


# Re-export firebase_auth for convenience in other modules.
__all__ = ["firebase_auth"]
