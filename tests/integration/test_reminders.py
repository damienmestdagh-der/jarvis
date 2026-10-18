"""Integration test: create then list a reminder (US2 Acceptance Scenarios 1 & 2)."""

from __future__ import annotations

from jarvis.app import JarvisApp
from jarvis.intent.models import Intent
from jarvis.intent.router import IntentRouter
from jarvis.skills.reminders import ReminderSkill
from jarvis.skills.registry import SkillRegistry
from jarvis.storage.reminder_repository import ReminderRepository


class ScriptedLLMClient:
    """Classifies based on simple substring matching — good enough for a
    deterministic integration test without a real LLM call."""

    def classify_intent(self, text: str) -> Intent:
        lowered = text.lower()
        if "remind me" in lowered:
            description = lowered.split("remind me to", 1)[-1].strip() or lowered.split(
                "remind me", 1
            )[-1].strip()
            return Intent(name="create_reminder", confidence=0.95, payload={"description": description})
        if "reminders" in lowered:
            return Intent(name="list_reminders", confidence=0.95)
        return Intent(name="question", confidence=0.9, payload={"question_text": text})

    def answer_question(self, text: str) -> str:  # pragma: no cover - unused here
        raise NotImplementedError


def _build_app(db_path) -> JarvisApp:
    llm = ScriptedLLMClient()
    router = IntentRouter(llm)
    registry = SkillRegistry([ReminderSkill(ReminderRepository(db_path))])
    return JarvisApp(router, registry)


def test_create_then_list_reminder(tmp_path):
    app = _build_app(tmp_path / "jarvis.db")

    create_response = app.handle_text("Remind me to call the plumber tomorrow")
    assert create_response is not None
    assert create_response.kind == "confirmation"

    list_response = app.handle_text("What are my reminders?")
    assert list_response is not None
    assert "call the plumber" in list_response.text
