"""Integration test: the full question + reminder flow works entirely
through text, never touching speech_to_text/text_to_speech (US3 Acceptance
Scenario 1)."""

from __future__ import annotations

import sys

from jarvis.app import JarvisApp
from jarvis.intent.models import Intent
from jarvis.intent.router import IntentRouter
from jarvis.io.text_io import print_response, read_command_text
from jarvis.skills.question import QuestionAnsweringSkill
from jarvis.skills.registry import SkillRegistry
from jarvis.skills.reminders import ReminderSkill
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
        if "reminders" in lowered:
            return Intent(name="list_reminders", confidence=0.95)
        return Intent(name="question", confidence=0.9, payload={"question_text": text})

    def answer_question(self, text: str) -> str:
        return "Paris is the capital of France."


def test_question_and_reminder_flow_never_imports_voice_modules(tmp_path, capsys):
    llm = ScriptedLLMClient()
    router = IntentRouter(llm)
    registry = SkillRegistry(
        [QuestionAnsweringSkill(llm), ReminderSkill(ReminderRepository(tmp_path / "jarvis.db"))]
    )
    app = JarvisApp(router, registry)

    for raw in ["What's the capital of France?", "Remind me to call the plumber", "What are my reminders?"]:
        text = read_command_text(raw)
        response = app.handle_text(text)
        print_response(response)

    out = capsys.readouterr().out
    assert "Paris" in out
    assert "call the plumber" in out

    assert "faster_whisper" not in sys.modules
    assert "pyttsx3" not in sys.modules
