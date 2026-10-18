"""Integration test: reminders persist after a restart (US2 Acceptance
Scenario 3 / SC-004)."""

from __future__ import annotations

from jarvis.app import JarvisApp
from jarvis.intent.models import Intent
from jarvis.intent.router import IntentRouter
from jarvis.skills.reminders import ReminderSkill
from jarvis.skills.registry import SkillRegistry
from jarvis.storage.reminder_repository import ReminderRepository


class ScriptedLLMClient:
    def classify_intent(self, text: str) -> Intent:
        lowered = text.lower()
        if "remind me" in lowered:
            return Intent(
                name="create_reminder",
                confidence=0.95,
                payload={"description": lowered.split("remind me to", 1)[-1].strip()},
            )
        return Intent(name="list_reminders", confidence=0.95)

    def answer_question(self, text: str) -> str:  # pragma: no cover - unused here
        raise NotImplementedError


def _build_app(db_path) -> JarvisApp:
    llm = ScriptedLLMClient()
    router = IntentRouter(llm)
    registry = SkillRegistry([ReminderSkill(ReminderRepository(db_path))])
    return JarvisApp(router, registry)


def test_reminder_is_still_listed_after_restart(tmp_path):
    db_path = tmp_path / "jarvis.db"

    _build_app(db_path).handle_text("Remind me to call the plumber")

    # "Restart": a brand-new app instance, same underlying db file.
    response = _build_app(db_path).handle_text("What are my reminders?")

    assert response is not None
    assert "call the plumber" in response.text
