"""Reminder entity (data-model.md)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

ReminderStatus = Literal["pending", "done"]


@dataclass(frozen=True)
class Reminder:
    id: int
    description: str
    status: ReminderStatus
    created_at: datetime
