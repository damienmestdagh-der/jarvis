"""Contract tests for ReminderSkill (contracts/skill.md cases 4-6).

Written before src/jarvis/skills/reminders.py exists — must fail until T034.
"""

from __future__ import annotations

from jarvis.intent.models import Intent
from jarvis.skills.reminders import ReminderSkill
from jarvis.storage.reminder_repository import ReminderRepository


def test_can_handle_create_and_list_reminder_intents(tmp_path):
    skill = ReminderSkill(ReminderRepository(tmp_path / "jarvis.db"))
    assert skill.can_handle(Intent(name="create_reminder", payload={"description": "x"})) is True
    assert skill.can_handle(Intent(name="list_reminders")) is True
    assert skill.can_handle(Intent(name="question")) is False


def test_execute_create_persists_exactly_one_pending_reminder(tmp_path):
    repo = ReminderRepository(tmp_path / "jarvis.db")
    skill = ReminderSkill(repo)

    response = skill.execute(Intent(name="create_reminder", payload={"description": "call the plumber"}))

    assert response.kind == "confirmation"
    reminders = repo.list()
    assert len(reminders) == 1
    assert reminders[0].status == "pending"


def test_execute_list_after_two_creates_mentions_both(tmp_path):
    repo = ReminderRepository(tmp_path / "jarvis.db")
    skill = ReminderSkill(repo)
    skill.execute(Intent(name="create_reminder", payload={"description": "call the plumber"}))
    skill.execute(Intent(name="create_reminder", payload={"description": "water the plants"}))

    response = skill.execute(Intent(name="list_reminders"))

    assert response.kind == "answer"
    assert "call the plumber" in response.text
    assert "water the plants" in response.text


def test_reminders_persist_across_a_simulated_restart(tmp_path):
    db_path = tmp_path / "jarvis.db"
    ReminderSkill(ReminderRepository(db_path)).execute(
        Intent(name="create_reminder", payload={"description": "call the plumber"})
    )

    # Simulate a restart: brand new repository instance, same file.
    response = ReminderSkill(ReminderRepository(db_path)).execute(Intent(name="list_reminders"))

    assert "call the plumber" in response.text
