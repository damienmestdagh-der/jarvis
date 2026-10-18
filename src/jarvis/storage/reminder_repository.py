"""ReminderRepository (contracts/reminder_repository.md): SQLite-backed CRUD
for Reminder, used only by ReminderSkill (Constitution III: a skill owns its
own storage)."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from jarvis.paths import db_path as default_db_path
from jarvis.storage.models import Reminder, ReminderStatus
from jarvis.storage.schema import init_db


class ReminderNotFoundError(LookupError):
    """Raised by mark_done() when no reminder has the given id."""


class ReminderRepository:
    def __init__(self, db_file: Path | None = None):
        self._db_file = db_file or default_db_path()
        conn = self._connect()
        try:
            init_db(conn)
        finally:
            conn.close()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_file)

    def create(self, description: str) -> Reminder:
        description = description.strip()
        if not description:
            raise ValueError("description must not be empty")
        created_at = datetime.now(timezone.utc)
        conn = self._connect()
        try:
            cursor = conn.execute(
                "INSERT INTO reminders (description, status, created_at) VALUES (?, 'pending', ?)",
                (description, created_at.isoformat()),
            )
            conn.commit()
            return Reminder(id=cursor.lastrowid, description=description, status="pending", created_at=created_at)
        finally:
            conn.close()

    def list(self, status: ReminderStatus | None = None) -> list[Reminder]:
        conn = self._connect()
        try:
            if status is None:
                rows = conn.execute(
                    "SELECT id, description, status, created_at FROM reminders ORDER BY created_at ASC"
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, description, status, created_at FROM reminders "
                    "WHERE status = ? ORDER BY created_at ASC",
                    (status,),
                ).fetchall()
            return [
                Reminder(id=row[0], description=row[1], status=row[2], created_at=datetime.fromisoformat(row[3]))
                for row in rows
            ]
        finally:
            conn.close()

    def mark_done(self, reminder_id: int) -> Reminder:
        conn = self._connect()
        try:
            cursor = conn.execute("UPDATE reminders SET status = 'done' WHERE id = ?", (reminder_id,))
            conn.commit()
            if cursor.rowcount == 0:
                raise ReminderNotFoundError(f"No reminder with id {reminder_id}")
            row = conn.execute(
                "SELECT id, description, status, created_at FROM reminders WHERE id = ?", (reminder_id,)
            ).fetchone()
            return Reminder(id=row[0], description=row[1], status=row[2], created_at=datetime.fromisoformat(row[3]))
        finally:
            conn.close()
