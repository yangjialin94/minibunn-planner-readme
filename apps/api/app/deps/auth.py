from datetime import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.firebase_admin import firebase_auth

# Use HTTPBearer to extract the token from the Authorization header.
security = HTTPBearer()


def get_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Retrieves the user from the Firebase token.
    """
    # Verify the token using Firebase Admin SDK
    token = credentials.credentials

    try:
        decoded_token = firebase_auth.verify_id_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    firebase_uid = decoded_token.get("uid")
    name = decoded_token.get("name")
    email = decoded_token.get("email")

    # Check if the user exists by Firebase UID
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if user:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


def get_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Retrieves the token from the Firebase token.
    """
    # Verify the token using Firebase Admin SDK
    token = credentials.credentials

    try:
        decoded_token = firebase_auth.verify_id_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    return decoded_token


def get_subscribed_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Retrieves the user from the Firebase token and checks if they are subscribed.
    """
    # Verify the token using Firebase Admin SDK
    user = get_user(credentials, db)

    # Check if the user is subscribed
    if user.is_subscribed is True:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="User is not subscribed",
        )
