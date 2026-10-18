# Contract: Skill

Shared interface implemented by every skill (`QuestionAnsweringSkill`, `ReminderSkill`, and any
future skill), per Constitution Principle III (Modular Skills Architecture).

## `can_handle(intent: Intent) -> bool`

Pure function, no side effects. Returns whether this skill handles the given `Intent.name`.
Exactly one registered skill must return `True` for any non-`unclear` Intent produced by the
router (enforced by the skill registry, not by individual skills).

## `execute(intent: Intent) -> Response`

**Preconditions**: `can_handle(intent)` is `True`.

**Postconditions**:
- Always returns a `Response` (never raises past this boundary — internal errors, e.g. a
  storage failure, are caught and converted to `Response(kind="error", ...)` per FR-009).
- MUST NOT read or write another skill's storage/state directly (Constitution III) — only its
  own data (e.g., `ReminderRepository` for `ReminderSkill`).

## Skill-specific contracts

### QuestionAnsweringSkill

- `can_handle`: `True` iff `intent.name == "question"`.
- `execute`: calls `LLMClient.answer_question(intent.payload.question_text)` and wraps the
  result in `Response(kind="answer", ...)`. If the LLM call fails, returns
  `Response(kind="error", ...)` — never a fabricated answer (spec Acceptance Scenario 1.3).

### ReminderSkill

- `can_handle`: `True` iff `intent.name == "create_reminder"` or `intent.name ==
  "list_reminders"`.
- `execute` (create path): persists a new `Reminder(status="pending")` via
  `ReminderRepository.create(description)`, returns `Response(kind="confirmation", ...)`.
- `execute` (list path): reads via `ReminderRepository.list()`, returns
  `Response(kind="answer", ...)` describing the stored reminders (FR-008).

## Test cases (contract tests, written before implementation)

1. `QuestionAnsweringSkill.can_handle` is `True` only for `name == "question"`.
2. `QuestionAnsweringSkill.execute` on a successful LLM answer → `Response(kind="answer")`.
3. `QuestionAnsweringSkill.execute` when the LLM call fails → `Response(kind="error")`, not an
   invented answer.
4. `ReminderSkill.execute` (create) persists exactly one new Reminder with `status="pending"`.
5. `ReminderSkill.execute` (list), called after two creates, returns a Response mentioning both.
6. Reminders created, then the repository is reopened (simulating a restart) → both still
   present (FR-007 / SC-004).
