"""Unit test for the missing-API-key startup error (found while validating
quickstart.md's edge-case step; see tasks.md T043)."""

from __future__ import annotations

import pytest

from jarvis.intent.claude_client import ClaudeLLMClient, MissingApiKeyError


def test_missing_api_key_raises_a_clear_error(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(MissingApiKeyError):
        ClaudeLLMClient()
