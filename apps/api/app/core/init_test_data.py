from datetime import date

from sqlalchemy.orm import Session

from app.core.test_data import test_notes, test_tasks
from app.models.note import Note
from app.models.task import Task
from app.models.user import User


def init_test_data(db: Session, reset: bool = False):
    if reset:
        db.query(Task).delete()
        db.query(Note).delete()
        db.query(User).filter(User.id == 1).delete()
        db.commit()
        print("🧹 Reset test data")

    existing = db.query(User).filter(User.id == 1).first()
    if not existing:
        user = User(
            id=1,
            firebase_uid="test_uid",
            name="Test User",
            email="test@example.com",
        )
        db.add(user)
        db.commit()
        print("✅ Inserted default test user")

    for task_data in test_tasks:
        task = Task(**task_data)
        db.merge(task)
    print("✅ Inserted test tasks")

    for note_data in test_notes:
        note = Note(**note_data)
        db.merge(note)
    print("✅ Inserted test notes")

    db.commit()
