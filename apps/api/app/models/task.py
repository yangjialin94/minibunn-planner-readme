from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Task(Base):
    """
    Task Database Schema / SQLAlchemy ORM Model
    """

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date)
    title = Column(String)
    note = Column(String)
    is_completed = Column(Boolean, default=False)
    order = Column(Integer)

    user = relationship("User", back_populates="tasks")
