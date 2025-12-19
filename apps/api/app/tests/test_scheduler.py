"""
Test suite for scheduler functionality
"""

from unittest.mock import Mock, patch

import pytest
from sqlalchemy.orm import Session

from app.models.note import Note
from app.models.user import User
from app.scheduler import delete_empty_notes, start_scheduler


class TestScheduler:
    """Test suite for background task scheduler"""

    @patch("app.scheduler.SessionLocal")
    def test_delete_empty_notes_success(self, mock_session_local):
        """Test successful deletion of empty notes"""
        # Mock database session and data
        mock_db = Mock()
        mock_session_local.return_value = mock_db

        # Mock empty notes to be deleted
        mock_empty_note1 = Mock()
        mock_empty_note2 = Mock()
        mock_empty_notes = [mock_empty_note1, mock_empty_note2]

        mock_db.query.return_value.filter.return_value.all.return_value = (
            mock_empty_notes
        )

        with patch("builtins.print") as mock_print:
            delete_empty_notes()

            # Verify empty notes were queried and deleted
            mock_db.query.assert_called()
            mock_db.delete.assert_any_call(mock_empty_note1)
            mock_db.delete.assert_any_call(mock_empty_note2)
            mock_db.commit.assert_called_once()
            mock_db.close.assert_called_once()

            # Verify success message was printed
            mock_print.assert_called()
            success_call = [
                call for call in mock_print.call_args_list if "Deleted 2" in str(call)
            ]
            assert len(success_call) > 0

    @patch("app.scheduler.SessionLocal")
    def test_delete_empty_notes_database_error(self, mock_session_local):
        """Test error handling when database operation fails"""
        # Mock database session that raises an exception
        mock_db = Mock()
        mock_session_local.return_value = mock_db
        mock_db.query.side_effect = Exception("Database connection failed")

        # Capture print output to verify error handling
        with patch("builtins.print") as mock_print:
            delete_empty_notes()

            # Verify error was handled gracefully
            mock_db.rollback.assert_called_once()
            mock_db.close.assert_called_once()
            mock_print.assert_called()
            # Check that error message was printed
            error_call = [
                call for call in mock_print.call_args_list if "Error" in str(call)
            ]
            assert len(error_call) > 0

    @patch("app.scheduler.SessionLocal")
    def test_delete_empty_notes_no_empty_notes(self, mock_session_local):
        """Test function when there are no empty notes to delete"""
        # Mock database session with no empty notes
        mock_db = Mock()
        mock_session_local.return_value = mock_db

        # Mock empty list - no empty notes found
        mock_db.query.return_value.filter.return_value.all.return_value = []

        with patch("builtins.print") as mock_print:
            delete_empty_notes()

            # Verify query was made
            mock_db.query.assert_called()
            # Verify no delete calls were made
            mock_db.delete.assert_not_called()
            mock_db.commit.assert_called_once()
            mock_db.close.assert_called_once()

            # Verify success message was printed
            mock_print.assert_called()
            success_call = [
                call for call in mock_print.call_args_list if "Deleted 0" in str(call)
            ]
            assert len(success_call) > 0

    @patch("app.scheduler.BackgroundScheduler")
    def test_start_scheduler(self, mock_scheduler_class):
        """Test scheduler initialization and job scheduling"""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        # Call the function
        start_scheduler()

        # Verify scheduler was created and configured
        mock_scheduler_class.assert_called_once()
        mock_scheduler.add_job.assert_called_once_with(
            delete_empty_notes, "cron", hour=0, minute=0
        )
        mock_scheduler.start.assert_called_once()

    @patch("app.scheduler.BackgroundScheduler")
    def test_start_scheduler_job_parameters(self, mock_scheduler_class):
        """Test that scheduler job is configured with correct parameters"""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        start_scheduler()

        # Verify job was added with correct function and schedule
        call_args = mock_scheduler.add_job.call_args
        assert call_args[0][0] == delete_empty_notes  # Function
        assert call_args[0][1] == "cron"  # Trigger type
        assert call_args[1]["hour"] == 0  # Midnight hour
        assert call_args[1]["minute"] == 0  # Midnight minute
