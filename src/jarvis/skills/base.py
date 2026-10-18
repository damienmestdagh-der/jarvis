"""Skill contract shared by every skill (contracts/skill.md).

A Skill must not reach into another skill's storage/state directly
(Constitution Principle III: Modular Skills Architecture) — the registry is
the only thing that knows about more than one skill at a time.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from jarvis.intent.models import Intent
from jarvis.models import Response


class Skill(ABC):
    @abstractmethod
    def can_handle(self, intent: Intent) -> bool:
        """Pure predicate, no side effects."""

    @abstractmethod
    def execute(self, intent: Intent) -> Response:
        """Requires can_handle(intent) is True. Must always return a Response,
        never raise — internal errors are caught and turned into
        Response(kind="error", ...) per FR-009."""
