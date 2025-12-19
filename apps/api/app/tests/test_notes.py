from datetime import date

import pytest


def test_get_or_create_note(client):
    """
    Tests getting or creating a note for today's date.
    """
    # Get note for today's date
    today = date.today().isoformat()
    res = client.get(f"/notes/?date={today}")

    # Check response
    assert res.status_code == 200
    data = res.json()
    assert data["date"] == today
    assert data["entry"] == ""


def test_post_new_note_success(client):
    """
    Tests creating a new note entry.
    """
    # Create a new note
    new_date = date.today().replace(day=1).isoformat()
    res = client.post(
        "/notes/",
        json={
            "date": new_date,
            "entry": "Testing note POST",
        },
    )

    # Check response
    assert res.status_code == 200
    data = res.json()
    assert data["date"] == new_date
    assert data["entry"] == "Testing note POST"


def test_post_note_already_exists(client):
    """
    Tests creating a note entry when one already exists for the date.
    """
    # Create a new note
    today = date.today().isoformat()
    client.post(
        "/notes/",
        json={
            "date": today,
            "entry": "Testing duplicate",
        },
    )

    # Try to create another note for the same date
    res = client.post(
        "/notes/",
        json={
            "date": today,
            "entry": "This should fail",
        },
    )

    # Check response
    assert res.status_code == 400
    assert res.json()["detail"] == "Note already exists for this date"


def test_patch_note(client):
    """
    Tests updating a note entry.
    """
    # Get note for today's date
    today = date.today().isoformat()
    note = client.get(f"/notes/?date={today}").json()

    # Update note entry
    note_id = note["id"]
    res = client.patch(
        f"/notes/{note_id}",
        json={
            "entry": "Updated entry text.",
        },
    )

    # Check response
    assert res.status_code == 200
    updated = res.json()
    assert updated["entry"] == "Updated entry text."


def test_patch_nonexistent_note(client):
    """
    Tests updating a note that doesn't exist.
    """
    # Try to update a note that doesn't exist
    res = client.patch("/notes/9999", json={"entry": "Ghost update"})

    # Check response
    assert res.status_code == 404
    assert res.json()["detail"] == "Note not found"


def test_get_or_create_note_creates_new_empty_note(client):
    """Test that a new note is created when none exists for the date"""
    # Use a unique date to ensure no note exists
    unique_date = "2025-12-25"  # Future date
    res = client.get(f"/notes/?date={unique_date}")

    assert res.status_code == 200
    data = res.json()
    assert data["date"] == unique_date
    assert data["entry"] == ""  # Should be empty string for new note

    # Verify the note was actually created by querying again
    res2 = client.get(f"/notes/?date={unique_date}")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["id"] == data["id"]  # Should be the same note


def test_patch_note_with_existing_seeded_client(seeded_client):
    """Test patching a note with the seeded client to cover missing lines"""
    # Create a note first
    test_date = "2025-02-14"
    res = seeded_client.post(
        "/notes/",
        json={
            "date": test_date,
            "entry": "Original Entry",
        },
    )
    assert res.status_code == 200
    note_id = res.json()["id"]

    # Patch the note - this should cover the missing lines
    patch_res = seeded_client.patch(f"/notes/{note_id}", json={"entry": "New Entry"})
    assert patch_res.status_code == 200

    data = patch_res.json()
    assert data["entry"] == "New Entry"


def test_clear_note_function_directly():
    """Test the clear_note function directly to achieve 100% coverage"""
    from unittest.mock import Mock

    from app.models.note import Note
    from app.models.user import User
    from app.routes.notes import clear_note

    # Create mock objects
    mock_db = Mock()
    mock_user = User(
        id=1,
        firebase_uid="test-uid",
        name="Test User",
        email="test@example.com",
        is_subscribed=True,
    )

    # Mock a note to be cleared
    mock_note = Mock()
    mock_note.entry = "Original Entry"

    # Mock the database query chain
    mock_db.query.return_value.filter.return_value.first.return_value = mock_note

    # Call the function directly
    result = clear_note(note_id=1, db=mock_db, user=mock_user)

    # Verify the note was cleared
    assert mock_note.entry == ""

    # Verify database operations were called
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_note)

    # The function should return the note
    assert result == mock_note


def test_clear_note_function_not_found():
    """Test the clear_note function when note is not found"""
    from unittest.mock import Mock

    import pytest
    from fastapi import HTTPException

    from app.models.user import User
    from app.routes.notes import clear_note

    # Create mock objects
    mock_db = Mock()
    mock_user = User(
        id=1,
        firebase_uid="test-uid",
        name="Test User",
        email="test@example.com",
        is_subscribed=True,
    )

    # Mock database query to return None (note not found)
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Call the function and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        clear_note(note_id=999, db=mock_db, user=mock_user)

    assert exc_info.value.status_code == 404
    assert "Note not found" in str(exc_info.value.detail)
