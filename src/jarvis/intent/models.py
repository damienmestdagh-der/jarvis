"""Intent — the LLM-derived understanding of a Command's purpose.

Not persisted: produced per-request by IntentRouter and consumed immediately
by the matching Skill.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

IntentName = Literal["question", "create_reminder", "list_reminders", "unclear"]

#: Below this confidence, a classification is treated as "unclear" rather
#: than acted on (see contracts/intent_router.md).
CONFIDENCE_THRESHOLD = 0.5


@dataclass(frozen=True)
class Intent:
    name: IntentName
    confidence: float = 1.0
    payload: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0.0, 1.0]")


def unclear(reason: str = "") -> Intent:
    """Build an `unclear` Intent, optionally noting why (for logs/clarification text)."""
    return Intent(name="unclear", confidence=0.0, payload={"reason": reason} if reason else {})
