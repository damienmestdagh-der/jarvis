"""Integration test: an unanswerable question gets a clear "I don't know",
never a fabricated answer (US1 Acceptance Scenario 3)."""

from __future__ import annotations

from jarvis.app import JarvisApp
from jarvis.intent.models import Intent
from jarvis.intent.router import IntentRouter
from jarvis.skills.question import QuestionAnsweringSkill
from jarvis.skills.registry import SkillRegistry


class UnknowingLLMClient:
    def classify_intent(self, text: str) -> Intent:
        return Intent(name="question", confidence=0.9, payload={"question_text": text})

    def answer_question(self, text: str) -> str:
        return "I don't know."


def test_unanswerable_question_gets_a_clear_dont_know_response():
    llm = UnknowingLLMClient()
    router = IntentRouter(llm)
    registry = SkillRegistry([QuestionAnsweringSkill(llm)])
    app = JarvisApp(router, registry)

    response = app.handle_text("What will the weather be here in 200 years?")

    assert response is not None
    assert response.kind == "answer"
    assert "don't know" in response.text.lower()
