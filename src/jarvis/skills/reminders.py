"""ReminderSkill (contracts/skill.md): create and list reminders/tasks."""

from __future__ import annotations

import logging
import uuid

from jarvis.intent.models import Intent
from jarvis.models import Response
from jarvis.skills.base import Skill
from jarvis.storage.reminder_repository import ReminderRepository

logger = logging.getLogger(__name__)


class ReminderSkill(Skill):
    def __init__(self, repository: ReminderRepository):
        self._repository = repository

    def can_handle(self, intent: Intent) -> bool:
        return intent.name in ("create_reminder", "list_reminders")

    def execute(self, intent: Intent) -> Response:
        command_id = str(uuid.uuid4())
        try:
            if intent.name == "create_reminder":
                return self._create(intent, command_id)
            return self._list(command_id)
        except Exception as exc:  # noqa: BLE001 - storage failures must not crash the app
            logger.warning("ReminderSkill failed: %s", exc)
            return Response(
                kind="error",
                text="I couldn't access your reminders right now - please try again.",
                command_id=command_id,
            )

    def _create(self, intent: Intent, command_id: str) -> Response:
        description = intent.payload.get("description", "").strip()
        reminder = self._repository.create(description)
        return Response(
            kind="confirmation",
            text=f"Okay, I'll remember: {reminder.description}",
            command_id=command_id,
        )

    def _list(self, command_id: str) -> Response:
        reminders = self._repository.list(status="pending")
        if not reminders:
            text = "You have no pending reminders."
        else:
            items = "; ".join(r.description for r in reminders)
            text = f"Your reminders: {items}"
        return Response(kind="answer", text=text, command_id=command_id)
