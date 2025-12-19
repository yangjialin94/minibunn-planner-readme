from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps.auth import get_subscribed_user
from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteOut, NoteUpdate

# Create a router
router = APIRouter()


@router.get("/", response_model=NoteOut)
def get_or_create_note(
    date: date,
    db: Session = Depends(get_db),
    user: User = Depends(get_subscribed_user),
):
    """
    Get the note for the given date.
    If it doesn't exist, create a new one and return it.
    """
    # Get the note for the specified date
    user_id = user.id
    note = db.query(Note).filter(Note.user_id == user_id, Note.date == date).first()
    if note:
        return note

    # Create a new note if it doesn't exist
    new_note = Note(date=date, user_id=user_id, entry="")
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


@router.post("/", response_model=NoteOut)
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_subscribed_user),
):
    """
    Create a new note for the current user.
    """
    # Check if note already exists for this date
    user_id = user.id
    existing = (
        db.query(Note).filter(Note.user_id == user_id, Note.date == note.date).first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Note already exists for this date")

    # Create the note
    db_note = Note(**note.model_dump(), user_id=user_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.patch("/{note_id}", response_model=NoteOut)
def update_note(
    note_id: int,
    updates: NoteUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_subscribed_user),
):
    """
    Update a note for the current user.
    """
    # Check if note exists
    user_id = user.id
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Update the note
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(note, key, value)

    db.commit()
    db.refresh(note)
    return note


@router.patch("/{note_id}", response_model=NoteOut)
def clear_note(
    note_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_subscribed_user),
):
    """
    Update a note for the current user.
    """
    # Check if note exists
    user_id = user.id
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Update the note
    setattr(note, "entry", "")

    db.commit()
    db.refresh(note)
    return note
