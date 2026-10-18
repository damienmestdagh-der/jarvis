"""Local, user-inspectable log of every call made to an LLM provider.

Satisfies the constitution's requirement that external calls be logged
locally in a way the user can audit: one JSON line per call, truncated text
only (never the full transcript history, never audio).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from jarvis.paths import llm_log_path

_MAX_LOGGED_CHARS = 200


def log_call(text: str, provider: str) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "text": text[:_MAX_LOGGED_CHARS],
    }
    with llm_log_path().open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
