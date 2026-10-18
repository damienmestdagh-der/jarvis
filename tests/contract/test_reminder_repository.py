"""Contract tests for ReminderRepository (contracts/reminder_repository.md cases 1-4).

Written before src/jarvis/storage/reminder_repository.py exists — must fail until T033.
"""

from __future__ import annotations

import pytest

from jarvis.storage.reminder_repository import ReminderNotFoundError, ReminderRepository


def test_create_then_list_shows_the_new_reminder(tmp_path):
    repo = ReminderRepository(tmp_path / "jarvis.db")
    repo.create("call the plumber")

    reminders = repo.list()

    assert len(reminders) == 1
    assert reminders[0].description == "call the plumber"
    assert reminders[0].status == "pending"


def test_reminders_survive_reopening_the_repository_same_file(tmp_path):
    db_path = tmp_path / "jarvis.db"
    ReminderRepository(db_path).create("water the plants")
    ReminderRepository(db_path).create("call the plumber")

    reopened = ReminderRepository(db_path)

    assert {r.description for r in reopened.list()} == {"water the plants", "call the plumber"}


def test_mark_done_moves_a_reminder_out_of_pending(tmp_path):
    repo = ReminderRepository(tmp_path / "jarvis.db")
    created = repo.create("call the plumber")

    repo.mark_done(created.id)

    assert [r.id for r in repo.list(status="pending")] == []
    assert [r.id for r in repo.list(status="done")] == [created.id]


def test_mark_done_on_unknown_id_raises(tmp_path):
    repo = ReminderRepository(tmp_path / "jarvis.db")
    with pytest.raises(ReminderNotFoundError):
        repo.mark_done(999999)
