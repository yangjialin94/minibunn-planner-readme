import os

import stripe
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file into environment

# Set up Stripe API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# App environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "")
WEB_URL = os.getenv("WEB_URL", "*")
ENV = os.getenv("ENV", "dev")

# Stripe environment variables
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Firebase environment variables
FIREBASE_TYPE = os.getenv("FIREBASE_TYPE")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_PRIVATE_KEY_ID = os.getenv("FIREBASE_PRIVATE_KEY_ID")
FIREBASE_PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")
FIREBASE_CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL")
FIREBASE_CLIENT_ID = os.getenv("FIREBASE_CLIENT_ID")
FIREBASE_AUTH_URI = os.getenv("FIREBASE_AUTH_URI")
FIREBASE_TOKEN_URI = os.getenv("FIREBASE_TOKEN_URI")
FIREBASE_AUTH_PROVIDER_CERT_URL = os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL")
FIREBASE_CLIENT_CERT_URL = os.getenv("FIREBASE_CLIENT_CERT_URL")
