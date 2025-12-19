from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.backlog import BacklogOut
from app.schemas.note import NoteOut
from app.schemas.task import TaskOut


class UserOut(BaseModel):
    """
    User Out Pydantic Schema (response to client)
    """

    id: int
    firebase_uid: str
    name: Optional[str]
    email: str

    stripe_customer_id: Optional[str]
    stripe_subscription_id: Optional[str]
    subscription_status: Optional[str]
    is_subscribed: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class UserOutFull(BaseModel):
    """
    User Out Pydantic Schema (response to client)
    """

    id: int
    firebase_uid: str
    name: Optional[str]
    email: str

    stripe_customer_id: Optional[str]
    stripe_subscription_id: Optional[str]
    subscription_status: Optional[str]
    is_subscribed: Optional[bool] = False

    tasks: List[TaskOut] = []
    notes: List[NoteOut] = []
    backlogs: List[BacklogOut] = []

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """
    User Update Pydantic Schema (request from client)
    """

    name: Optional[str]
    # email: Optional[str] # Not allowed to update email for security reasons
