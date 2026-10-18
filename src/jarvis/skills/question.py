"""QuestionAnsweringSkill (contracts/skill.md)."""

from __future__ import annotations

import logging
import uuid

from jarvis.intent.llm_client import LLMClient
from jarvis.intent.models import Intent
from jarvis.models import Response
from jarvis.skills.base import Skill

logger = logging.getLogger(__name__)


class QuestionAnsweringSkill(Skill):
    def __init__(self, llm_client: LLMClient):
        self._llm = llm_client

    def can_handle(self, intent: Intent) -> bool:
        return intent.name == "question"

    def execute(self, intent: Intent) -> Response:
        question_text = intent.payload.get("question_text", "")
        command_id = str(uuid.uuid4())
        try:
            answer = self._llm.answer_question(question_text)
        except Exception as exc:  # noqa: BLE001 - never fabricate an answer on failure
            logger.warning("answer_question failed: %s", exc)
            return Response(
                kind="error",
                text="I can't answer that right now - please try again shortly.",
                command_id=command_id,
            )
        return Response(kind="answer", text=answer, command_id=command_id)
