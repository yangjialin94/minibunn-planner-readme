from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Backlog(Base):
    """
    Backlog Database Schema / SQLAlchemy ORM Model
    """

    __tablename__ = "backlogs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date)
    detail = Column(String)
    order = Column(Integer)

    user = relationship("User", back_populates="backlogs")
