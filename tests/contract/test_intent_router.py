"""Contract tests for IntentRouter (specs/001-jarvis-core/contracts/intent_router.md).

Written before the implementation (src/jarvis/intent/router.py) exists, per
Constitution Principle IV — these must fail until T014 is done.
"""

from __future__ import annotations

import pytest

from jarvis.intent.models import Intent
from jarvis.intent.router import IntentRouter
from jarvis.models import Command


class FakeLLMClient:
    """Test double implementing the LLMClient protocol."""

    def __init__(self, result: Intent | None = None, raises: Exception | None = None):
        self._result = result
        self._raises = raises

    def classify_intent(self, text: str) -> Intent:
        if self._raises is not None:
            raise self._raises
        assert self._result is not None
        return self._result

    def answer_question(self, text: str) -> str:  # pragma: no cover - unused here
        raise NotImplementedError


def _cmd(text: str) -> Command:
    return Command(text=text, source="text")


def test_clear_question_is_classified_as_question():
    llm = FakeLLMClient(result=Intent(name="question", confidence=0.9))
    router = IntentRouter(llm)
    intent = router.classify(_cmd("What's the capital of France?"))
    assert intent.name == "question"


def test_clear_reminder_is_classified_as_create_reminder():
    llm = FakeLLMClient(
        result=Intent(name="create_reminder", confidence=0.9, payload={"description": "call the plumber"})
    )
    router = IntentRouter(llm)
    intent = router.classify(_cmd("Remind me to call the plumber"))
    assert intent.name == "create_reminder"
    assert intent.payload["description"] == "call the plumber"


def test_ambiguous_text_is_unclear():
    llm = FakeLLMClient(result=Intent(name="question", confidence=0.2))
    router = IntentRouter(llm)
    intent = router.classify(_cmd("hmm, maybe, I dunno"))
    assert intent.name == "unclear"


def test_reminder_without_description_is_unclear():
    llm = FakeLLMClient(
        result=Intent(name="create_reminder", confidence=0.9, payload={"description": ""})
    )
    router = IntentRouter(llm)
    intent = router.classify(_cmd("remind me about stuff"))
    assert intent.name == "unclear"


def test_llm_failure_becomes_unclear_not_an_exception():
    llm = FakeLLMClient(raises=ConnectionError("network down"))
    router = IntentRouter(llm)
    intent = router.classify(_cmd("What time is it?"))
    assert intent.name == "unclear"


def test_classify_requires_non_empty_command():
    with pytest.raises(ValueError):
        Command(text="   ", source="text")
