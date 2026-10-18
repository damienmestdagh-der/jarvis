"""Skill registry: routes an Intent to the one registered Skill that handles it.

This is the only component allowed to know about more than one Skill at a
time (Constitution Principle III).
"""

from __future__ import annotations

from jarvis.intent.models import Intent
from jarvis.models import Response
from jarvis.skills.base import Skill


class NoSkillFoundError(RuntimeError):
    """Raised when no registered skill can handle a given (non-unclear) Intent."""


class SkillRegistry:
    def __init__(self, skills: list[Skill]):
        self._skills = list(skills)

    def dispatch(self, intent: Intent) -> Response:
        for skill in self._skills:
            if skill.can_handle(intent):
                return skill.execute(intent)
        raise NoSkillFoundError(f"No skill registered for intent '{intent.name}'")
