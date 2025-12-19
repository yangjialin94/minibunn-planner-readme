from datetime import date as date_
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    """
    Task Create Pydantic Schema (for POST requests)
    """

    date: date_
    title: Optional[str] = ""
    note: Optional[str] = ""
    is_completed: bool = False


class TaskUpdate(BaseModel):
    """
    Task Update Pydantic Schema (for PUT requests)
    """

    date: Optional[date_] = None
    title: Optional[str] = None
    note: Optional[str] = None
    is_completed: Optional[bool] = None
    order: Optional[int] = None


class TaskOut(BaseModel):
    """
    Task Out Pydantic Schema (response to client)
    """

    id: int
    date: date_
    title: Optional[str]
    note: Optional[str]
    is_completed: bool
    order: int

    model_config = ConfigDict(from_attributes=True)


class CompletionOut(BaseModel):
    """
    Completion Out Pydantic Schema (response to client)
    """

    date: date_
    total: int
    completed: int

    model_config = ConfigDict(from_attributes=True)
