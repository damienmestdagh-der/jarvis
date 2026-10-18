"""Integration test: a text question returns an answer (US1 Acceptance Scenarios 1 & 2)."""

from __future__ import annotations

from jarvis.app import JarvisApp
from jarvis.intent.models import Intent
from jarvis.intent.router import IntentRouter
from jarvis.skills.question import QuestionAnsweringSkill
from jarvis.skills.registry import SkillRegistry


class FakeLLMClient:
    def classify_intent(self, text: str) -> Intent:
        return Intent(name="question", confidence=0.95, payload={"question_text": text})

    def answer_question(self, text: str) -> str:
        return "Paris is the capital of France."


def _build_app() -> JarvisApp:
    llm = FakeLLMClient()
    router = IntentRouter(llm)
    registry = SkillRegistry([QuestionAnsweringSkill(llm)])
    return JarvisApp(router, registry)


def test_text_question_returns_an_answer():
    app = _build_app()
    response = app.handle_text("What's the capital of France?")
    assert response is not None
    assert response.kind == "answer"
    assert "Paris" in response.text
