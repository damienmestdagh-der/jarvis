"""IntentRouter (contracts/intent_router.md): the one seam voice and text
commands both pass through before reaching a Skill.
"""

from __future__ import annotations

import logging

from jarvis.intent.llm_client import LLMClient
from jarvis.intent.models import CONFIDENCE_THRESHOLD, Intent, unclear
from jarvis.models import Command

logger = logging.getLogger(__name__)


class IntentRouter:
    def __init__(self, llm_client: LLMClient):
        self._llm = llm_client

    def classify(self, command: Command) -> Intent:
        """Always returns an Intent; never lets an LLMClient failure escape."""
        try:
            intent = self._llm.classify_intent(command.text)
        except Exception as exc:  # noqa: BLE001 - any provider failure maps to "unclear"
            logger.warning("LLM classification failed: %s", exc)
            return unclear(reason="llm_unavailable")

        if intent.confidence < CONFIDENCE_THRESHOLD:
            return unclear(reason="low_confidence")

        if intent.name == "create_reminder" and not intent.payload.get("description", "").strip():
            return unclear(reason="missing_reminder_description")

        return intent
