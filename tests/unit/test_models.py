"""Unit tests for Command/Response validation (data-model.md)."""

from __future__ import annotations

import pytest

from jarvis.models import Command, EmptyCommandError, Response


def test_command_rejects_empty_text():
    with pytest.raises(EmptyCommandError):
        Command(text="", source="text")


def test_command_rejects_whitespace_only_text():
    with pytest.raises(EmptyCommandError):
        Command(text="   \t  ", source="voice")


def test_command_accepts_non_empty_text():
    command = Command(text="hello", source="text")
    assert command.text == "hello"
    assert command.id
    assert command.created_at is not None


def test_response_holds_kind_text_and_command_id():
    response = Response(kind="answer", text="Paris", command_id="abc-123")
    assert response.kind == "answer"
    assert response.text == "Paris"
    assert response.command_id == "abc-123"
