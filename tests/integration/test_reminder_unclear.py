"""Integration test: a reminder command with no concrete description asks
for clarification and creates nothing (Edge Case / FR-012)."""

from __future__ import annotations

from jarvis.app import JarvisApp
from jarvis.intent.models import Intent
from jarvis.intent.router import IntentRouter
from jarvis.skills.reminders import ReminderSkill
from jarvis.skills.registry import SkillRegistry
from jarvis.storage.reminder_repository import ReminderRepository


class VagueLLMClient:
    """Always returns a create_reminder intent with an empty description,
    simulating the LLM failing to extract a concrete description."""

    def classify_intent(self, text: str) -> Intent:
        return Intent(name="create_reminder", confidence=0.9, payload={"description": ""})

    def answer_question(self, text: str) -> str:  # pragma: no cover - unused here
        raise NotImplementedError


def test_vague_reminder_command_asks_for_clarification_and_creates_nothing(tmp_path):
    db_path = tmp_path / "jarvis.db"
    repo = ReminderRepository(db_path)
    router = IntentRouter(VagueLLMClient())
    registry = SkillRegistry([ReminderSkill(repo)])
    app = JarvisApp(router, registry)

    response = app.handle_text("remind me about stuff")

    assert response is not None
    assert response.kind == "clarification"
    assert repo.list() == []
