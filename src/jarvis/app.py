"""Core orchestration: Command -> IntentRouter -> SkillRegistry -> Response.

This is the one path both voice and text inputs share (Constitution
Principle I). Building it here, before any skill exists, is what makes US1
and US2 "just" a matter of registering a new Skill.
"""

from __future__ import annotations

import logging

from jarvis.intent.claude_client import ClaudeLLMClient
from jarvis.intent.models import Intent
from jarvis.intent.router import IntentRouter
from jarvis.models import Command, CommandSource, EmptyCommandError, Response
from jarvis.skills.question import QuestionAnsweringSkill
from jarvis.skills.registry import SkillRegistry
from jarvis.skills.reminders import ReminderSkill
from jarvis.storage.reminder_repository import ReminderRepository

logger = logging.getLogger(__name__)

_CLARIFICATION_TEXT = {
    "llm_unavailable": "I can't process that request right now - please try again shortly.",
    "low_confidence": "I'm not sure what you mean - could you rephrase that?",
    "missing_reminder_description": "What would you like me to remind you about?",
}
_DEFAULT_CLARIFICATION = "I didn't understand that - could you rephrase it?"


class JarvisApp:
    def __init__(self, router: IntentRouter, registry: SkillRegistry):
        self._router = router
        self._registry = registry

    def handle_text(self, text: str, source: CommandSource = "text") -> Response | None:
        """Process one raw command string. Returns None for empty/whitespace
        input, per the Edge Case: it must not be treated as a valid command
        or trigger any action."""
        try:
            command = Command(text=text, source=source)
        except EmptyCommandError:
            return None

        intent = self._router.classify(command)
        if intent.name == "unclear":
            return self._clarification_response(command.id, intent)

        return self._registry.dispatch(intent)

    @staticmethod
    def _clarification_response(command_id: str, intent: Intent) -> Response:
        reason = intent.payload.get("reason", "")
        text = _CLARIFICATION_TEXT.get(reason, _DEFAULT_CLARIFICATION)
        return Response(kind="clarification", text=text, command_id=command_id)


def build_app(api_key: str | None = None) -> JarvisApp:
    """Composition root: wires the concrete LLMClient and every registered
    Skill into a ready-to-use JarvisApp."""
    llm = ClaudeLLMClient(api_key=api_key)
    router = IntentRouter(llm)
    registry = SkillRegistry([
        QuestionAnsweringSkill(llm),
        ReminderSkill(ReminderRepository()),
    ])
    return JarvisApp(router, registry)
