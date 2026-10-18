"""Contract tests for the skill registry (specs/001-jarvis-core/contracts/skill.md).

Written before src/jarvis/skills/registry.py exists — must fail until T015.
"""

from __future__ import annotations

import pytest

from jarvis.intent.models import Intent
from jarvis.models import Response
from jarvis.skills.base import Skill
from jarvis.skills.registry import SkillRegistry, NoSkillFoundError


class StubSkill(Skill):
    def __init__(self, name: str, handles: str):
        self.name = name
        self.handles = handles

    def can_handle(self, intent: Intent) -> bool:
        return intent.name == self.handles

    def execute(self, intent: Intent) -> Response:
        return Response(kind="answer", text=f"handled by {self.name}", command_id="x")


def test_registry_dispatches_to_the_matching_skill():
    registry = SkillRegistry([StubSkill("q", "question"), StubSkill("r", "create_reminder")])
    response = registry.dispatch(Intent(name="create_reminder", confidence=1.0))
    assert response.text == "handled by r"


def test_registry_raises_clear_error_when_no_skill_matches():
    registry = SkillRegistry([StubSkill("q", "question")])
    with pytest.raises(NoSkillFoundError):
        registry.dispatch(Intent(name="create_reminder", confidence=1.0))
