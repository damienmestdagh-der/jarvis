# Contract: ReminderRepository

Storage interface used only by `ReminderSkill` (Constitution III: skills own their data; no
other skill touches this).

## `create(description: str) -> Reminder`

Preconditions: `description` is non-empty after trimming (caller/skill responsibility — see
data-model.md Intent validation for `create_reminder`).
Postconditions: Inserts a new row with `status="pending"`, `created_at=now (UTC)`, returns the
created `Reminder` including its generated `id`.

## `list(status: Optional[str] = None) -> list[Reminder]`

Returns all stored reminders, optionally filtered by `status`. Ordered by `created_at`
ascending. Returns an empty list (not an error) when none exist.

## `mark_done(reminder_id: int) -> Reminder`

Transitions a reminder's `status` from `pending` to `done`. Raises a lookup error if
`reminder_id` does not exist (caller/skill converts this to an error Response).

## Persistence requirement

Backed by the SQLite file under the user's app-data directory (research.md §5). Data MUST
survive process restart — this is the contract directly backing FR-007 and SC-004.

## Test cases (contract tests, written before implementation)

1. `create` then `list()` → the created reminder is present with `status="pending"`.
2. Two `create` calls, then a fresh `ReminderRepository` instance pointed at the same file
   (simulating a restart) → `list()` still returns both (FR-007 / SC-004).
3. `mark_done` on an existing id → subsequent `list(status="pending")` excludes it,
   `list(status="done")` includes it.
4. `mark_done` on a non-existent id → raises a lookup error (no silent no-op).
