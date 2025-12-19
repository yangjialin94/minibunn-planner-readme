# app/scheduler.py

from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal
from app.models.note import Note


def delete_empty_notes():
    """
    Deletes all note entries that are empty (i.e., have no entry).
    """
    db = SessionLocal()

    try:
        empty_notes = db.query(Note).filter(Note.entry == "").all()
        for note in empty_notes:
            db.delete(note)
        db.commit()
        print(f"{datetime.now()}: Deleted {len(empty_notes)} empty notes.")
    except Exception as e:
        db.rollback()
        print(f"Error deleting empty notes: {e}")
    finally:
        db.close()


def start_scheduler():
    """
    Initializes the APScheduler and schedules the delete_empty_notes job
    to run every day at midnight.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_empty_notes, "cron", hour=0, minute=0)
    scheduler.start()
