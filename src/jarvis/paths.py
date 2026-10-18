"""Local app-data location for Jarvis's own files (reminders DB, LLM call log).

Keeping this in one place is what lets storage and logging honor the privacy
principle: everything lives under the user's own profile, never bundled with
the source tree or synced anywhere by Jarvis itself.
"""

from __future__ import annotations

import os
from pathlib import Path


def app_data_dir() -> Path:
    """Return the Jarvis app-data directory, creating it if missing."""
    base = os.environ.get("APPDATA")
    root = Path(base) if base else Path.home() / ".jarvis"
    directory = root / "Jarvis"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def db_path() -> Path:
    return app_data_dir() / "jarvis.db"


def llm_log_path() -> Path:
    return app_data_dir() / "llm_calls.jsonl"
