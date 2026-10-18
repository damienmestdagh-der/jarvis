"""Unit tests for Intent validation (data-model.md)."""

from __future__ import annotations

import pytest

from jarvis.intent.models import Intent, unclear


def test_confidence_must_be_within_zero_and_one():
    with pytest.raises(ValueError):
        Intent(name="question", confidence=1.5)
    with pytest.raises(ValueError):
        Intent(name="question", confidence=-0.1)


def test_unclear_helper_builds_an_unclear_intent_with_zero_confidence():
    intent = unclear(reason="low_confidence")
    assert intent.name == "unclear"
    assert intent.confidence == 0.0
    assert intent.payload["reason"] == "low_confidence"


def test_unclear_helper_with_no_reason_has_empty_payload():
    intent = unclear()
    assert intent.payload == {}
