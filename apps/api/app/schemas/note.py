from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NoteCreate(BaseModel):
    """
    Note Create Pydantic Schema (for POST requests)
    """

    date: date
    entry: Optional[str] = ""


class NoteUpdate(BaseModel):
    """
    Note Update Pydantic Schema (for PUT requests)
    """

    entry: Optional[str] = None


class NoteOut(BaseModel):
    """
    Note Out Pydantic Schema (response to client)
    """

    id: int
    date: date
    entry: Optional[str] = ""

    model_config = ConfigDict(from_attributes=True)
