"""SQLite schema for the `reminders` table (data-model.md: Reminder)."""

from __future__ import annotations

import sqlite3

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'done')),
    created_at TEXT NOT NULL
)
"""


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(_CREATE_TABLE)
    conn.commit()
