# Contract: IntentRouter

Internal interface between input capture (voice/text) and skills. This is the seam that User
Stories 1–3 share, and the one contract-tested ahead of implementation (Constitution IV).

## `classify(command: Command) -> Intent`

**Preconditions**:
- `command.text` is non-empty after trimming (callers must not invoke this with blank input —
  see data-model.md Command validation).

**Postconditions**:
- Always returns an `Intent` (never raises for a merely-ambiguous command).
- Returns `Intent(name="unclear", ...)` when:
  - The LLM call fails or the provider is unreachable (FR-009: must surface as "cannot
    process", not crash/hang).
  - The LLM's own confidence is below the router's configured threshold.
  - A `create_reminder` intent is returned with an empty/missing `description`.
- Returns `Intent(name="question" | "create_reminder" | "list_reminders", confidence >=
  threshold, payload=...)` otherwise.

**Error handling**: Any exception from the underlying `LLMClient` is caught inside `classify`
and converted to an `unclear` Intent with a payload reason the caller can turn into a
Response — the router never lets an LLM/network failure propagate as an unhandled exception
(FR-009).

## Test cases (contract tests, written before implementation)

1. Clear factual-question text → `Intent(name="question")`.
2. Clear "remind me to X" text → `Intent(name="create_reminder", payload.description="X")`.
3. Ambiguous text (could be either) → `Intent(name="unclear")`.
4. "Remind me about stuff" (no concrete description) → `Intent(name="unclear")`.
5. `LLMClient` raises/times out → `Intent(name="unclear")`, no exception escapes `classify`.
6. Empty/whitespace-only command text → `classify` is never called (caller responsibility,
   verified at the Command-ingestion boundary, not inside this contract).
