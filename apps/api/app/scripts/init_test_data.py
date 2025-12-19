import os

from app.core.database import get_db
from app.core.init_test_data import init_test_data

"""
Script to initialize test data in the database.
Run this manually in dev: `python app/scripts/init_test_data.py`
"""

if __name__ == "__main__":
    if os.getenv("ENV") == "dev":
        db = next(get_db())
        try:
            # init_test_data(db)  # just insert if missing
            init_test_data(db, reset=True)  # wipe & reload
            print("✅ Test data loaded.")
        finally:
            db.close()
    else:
        print("Skipping test data insert: ENV is not 'dev'")
