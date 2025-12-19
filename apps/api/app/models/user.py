from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """
    User Database Schema / SQLAlchemy ORM Model
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)

    # Stripe / subscription related fields
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    subscription_status = Column(
        String, nullable=True
    )  # (e.g., "active", "canceled", "past_due", etc.)
    is_subscribed = Column(Boolean, default=False)

    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    backlogs = relationship(
        "Backlog", back_populates="user", cascade="all, delete-orphan"
    )
