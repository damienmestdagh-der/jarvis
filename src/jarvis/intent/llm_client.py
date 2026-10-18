"""LLMClient protocol — the only seam through which a concrete LLM provider
may be reached (contracts/llm_client.md).

No skill or I/O module may import a provider SDK (e.g. `anthropic`) directly;
they depend on this protocol instead, so the provider can be swapped by
writing one new adapter (Constitution: "LLM access MUST be behind an
internal interface").
"""

from __future__ import annotations

from typing import Protocol

from jarvis.intent.models import Intent


class LLMClient(Protocol):
    def classify_intent(self, text: str) -> Intent:
        """Raises on transport-level failure (network/auth); does not swallow
        errors itself — IntentRouter.classify is responsible for converting
        that into an `unclear` Intent."""
        ...

    def answer_question(self, text: str) -> str:
        """Raises on transport-level failure; QuestionAnsweringSkill.execute
        converts that into an error Response."""
        ...
