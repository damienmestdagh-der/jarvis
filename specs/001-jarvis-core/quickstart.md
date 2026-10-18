# Quickstart: Jarvis Core Assistant Loop

Validates the feature end-to-end once implemented. Text-mode steps require no microphone and
cover User Stories 1–3; the voice-mode step covers the voice half of User Story 1/2.

## Prerequisites

- Python 3.12 installed and on `PATH`.
- An Anthropic API key available as the `ANTHROPIC_API_KEY` environment variable (never
  committed to the repo — see Constitution Principle II).
- Project dependencies installed into a virtual environment:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```
- A working microphone, only for the voice-mode step.

## Run the test suite (contracts + integration)

```powershell
pytest
```

Expected: all contract tests under `tests/contract/` and integration tests under
`tests/integration/` pass. These are the executable form of `contracts/*.md` and the
acceptance scenarios in `spec.md`.

## Validate User Story 1 — ask a question (text mode)

```powershell
python -m jarvis --text "What's the capital of France?"
```

Expected: a printed answer referencing Paris, within ~5 seconds (SC-001). The local LLM call
log (`%APPDATA%/Jarvis/llm_calls.jsonl`) gains exactly one new line.

Ask something the assistant cannot know:

```powershell
python -m jarvis --text "What will the weather be on this exact spot in 200 years?"
```

Expected: a clear "I don't know" style response — never a fabricated answer (Acceptance
Scenario 1.3).

## Validate User Story 2 — create and list a reminder (text mode)

```powershell
python -m jarvis --text "Remind me to call the plumber tomorrow"
python -m jarvis --text "What are my reminders?"
```

Expected: a confirmation on the first call, and the plumber reminder listed on the second.

Restart check (FR-007 / SC-004): close the process entirely, then re-run the "What are my
reminders?" command — the reminder must still be listed.

## Validate User Story 3 — text-only fallback

Repeat the two steps above with no microphone connected/used at all. Expected: identical
behavior to the text-mode steps above, since voice and text share the same
`IntentRouter` → `Skill` → `Response` path (no voice-only logic).

## Validate the voice path (manual, User Story 1/2 by voice)

```powershell
python -m jarvis --voice
```

Press Enter when prompted, then speak a question or a "remind me to..." command. Expected:
spoken response via the local TTS engine, equivalent to the text-mode result for the same
phrasing.

## Validate edge cases

- Run with `--text ""` or `--text "   "` → no command is processed, no Response/log entry is
  produced (Edge Case: empty command).
- Run with `--text "Remind me about stuff"` → assistant asks for a clearer description, no
  Reminder is created (Edge Case: reminder without a description).
- Temporarily unset `ANTHROPIC_API_KEY` and run any command → a clear "cannot process this
  right now" message, not a crash or hang (FR-009).
