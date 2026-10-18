# Phase 1 Data Model: Jarvis Core Assistant Loop

## Command

A single user request, as it enters the system — either transcribed from voice or typed.

| Field       | Type                  | Notes                                                        |
|-------------|-----------------------|---------------------------------------------------------------|
| `id`        | string (uuid)         | Generated per command, used to correlate logs/response        |
| `text`      | string                | Transcribed or typed content; MUST NOT be empty/whitespace-only (Edge Case) |
| `source`    | enum: `voice`, `text` | How the command was captured                                   |
| `created_at`| datetime (UTC)        | Capture timestamp                                              |

**Validation rules**:
- `text` is rejected (treated as no-op, per Edge Cases) if empty or only whitespace after
  trimming — never forwarded to the IntentRouter.

## Intent

The LLM-derived understanding of a Command's purpose. Not persisted — produced per-request by
the `IntentRouter` and consumed immediately by the matching skill.

| Field        | Type                                              | Notes |
|--------------|----------------------------------------------------|-------|
| `name`       | enum: `question`, `create_reminder`, `list_reminders`, `unclear` | `unclear` triggers a clarification Response instead of a skill; `list_reminders` is the retrieval half of FR-008, kept distinct from `create_reminder` so each maps to one unambiguous skill action |
| `confidence` | float (0.0–1.0)                                    | Below-threshold confidence is treated as `unclear` |
| `payload`    | object (intent-specific)                           | e.g., for `create_reminder`: `{ description: string }`; for `question`: `{ question_text: string }`; `list_reminders` carries no payload |

**Validation rules**:
- `create_reminder` payload MUST include a non-empty `description`; if the LLM returns one
  empty, the router treats the Intent as `unclear` (Edge Case: reminder without a clear
  description) rather than creating a blank Reminder.

## Reminder (persisted)

A user-created item to remember, stored in SQLite so it survives restarts (FR-007).

| Field         | Type                        | Notes |
|---------------|-----------------------------|-------|
| `id`          | integer (autoincrement, PK) | SQLite rowid |
| `description` | string                      | Required, non-empty |
| `status`      | enum: `pending`, `done`     | Defaults to `pending` on creation |
| `created_at`  | datetime (UTC)              | Set on creation, immutable |

**State transitions**: `pending → done` only (marking a reminder complete). No other status
values in this spec; due-time alerting is explicitly out of scope (spec Assumptions), so there
is no "overdue"/"alerted" state here.

**Relationships**: None — Reminder is a standalone entity in this spec (no linkage to Command,
since a Command is transient and not persisted).

## Response

The assistant's reply to a single Command.

| Field       | Type                                                            | Notes |
|-------------|------------------------------------------------------------------|-------|
| `kind`      | enum: `answer`, `confirmation`, `clarification`, `error`         | Determines phrasing/voice vs. text delivery |
| `text`      | string                                                            | What is spoken and/or printed to the user |
| `command_id`| string (uuid)                                                     | Correlates back to the originating Command for logs |

**Validation rules**:
- Every processed Command MUST produce exactly one Response (FR-005, FR-009) — including the
  `unclear`/error paths; the pipeline must never end without emitting a Response.
