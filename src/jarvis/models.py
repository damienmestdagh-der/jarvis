"""Command and Response — the shared envelope every input/output path uses.

Keeping these as plain dataclasses (not tied to voice or text) is what lets
voice and text commands flow through the exact same IntentRouter/Skill path
(Constitution Principle I: Voice-First Interaction treats both as equals).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

CommandSource = Literal["voice", "text"]
ResponseKind = Literal["answer", "confirmation", "clarification", "error"]


class EmptyCommandError(ValueError):
    """Raised when a command's text is empty or whitespace-only."""


@dataclass(frozen=True)
class Command:
    text: str
    source: CommandSource
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.text or not self.text.strip():
            raise EmptyCommandError("Command text must not be empty or whitespace-only")


@dataclass(frozen=True)
class Response:
    kind: ResponseKind
    text: str
    command_id: str
