"""Contract tests for QuestionAnsweringSkill (contracts/skill.md cases 1-3).

Written before src/jarvis/skills/question.py exists — must fail until T024.
"""

from __future__ import annotations

from jarvis.intent.models import Intent
from jarvis.skills.question import QuestionAnsweringSkill


class FakeLLMClient:
    def __init__(self, answer: str | None = None, raises: Exception | None = None):
        self._answer = answer
        self._raises = raises

    def classify_intent(self, text: str) -> Intent:  # pragma: no cover - unused here
        raise NotImplementedError

    def answer_question(self, text: str) -> str:
        if self._raises is not None:
            raise self._raises
        assert self._answer is not None
        return self._answer


def test_can_handle_is_true_only_for_question_intent():
    skill = QuestionAnsweringSkill(FakeLLMClient(answer="Paris"))
    assert skill.can_handle(Intent(name="question")) is True
    assert skill.can_handle(Intent(name="create_reminder")) is False
    assert skill.can_handle(Intent(name="unclear")) is False


def test_execute_returns_answer_on_success():
    skill = QuestionAnsweringSkill(FakeLLMClient(answer="Paris is the capital of France."))
    response = skill.execute(Intent(name="question", payload={"question_text": "capital of France?"}))
    assert response.kind == "answer"
    assert "Paris" in response.text


def test_execute_returns_error_not_fabricated_answer_on_llm_failure():
    skill = QuestionAnsweringSkill(FakeLLMClient(raises=ConnectionError("down")))
    response = skill.execute(Intent(name="question", payload={"question_text": "anything?"}))
    assert response.kind == "error"
