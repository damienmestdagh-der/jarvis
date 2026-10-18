# Implementation Plan: Jarvis Core Assistant Loop

**Branch**: `001-jarvis-core` | **Date**: 2026-10-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-jarvis-core/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Build the core request/response loop of Jarvis: capture a command (voice via local
speech-to-text, or typed text as fallback), send the text to an LLM to classify intent
(question vs. create-reminder vs. unclear), execute the matching skill, and respond to the
user (spoken via local text-to-speech, and/or printed). Reminders persist locally in SQLite.
Only the command text (never raw audio) is sent to the cloud LLM, and every such call is
logged locally, per the constitution's privacy principle.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `anthropic` (Claude API SDK, behind an internal `LLMClient`
interface), `faster-whisper` (local speech-to-text), `sounddevice`/`soundfile` (local
microphone capture, research.md §8), `pyttsx3` (local text-to-speech, uses Windows SAPI5),
stdlib `sqlite3` (storage), `pytest` (testing)

**Storage**: SQLite, single local file (`%APPDATA%/Jarvis/jarvis.db`) for reminders/tasks

**Testing**: pytest — contract tests for the intent router and skill interfaces, integration
tests for the text-only end-to-end flow (User Story 1–3), unit tests for individual skills

**Target Platform**: Windows 11 desktop, running locally as a Python process (user's own
machine, single user)

**Project Type**: Single project — local desktop CLI/assistant app (no backend/frontend split,
no web service)

**Performance Goals**: Answer delivered within 5s end-to-end for 90% of requests (SC-001);
reminder creation completes in a single command round-trip (SC-002)

**Constraints**: Core pipeline must work with only the command text (not audio) leaving the
device; must run on Windows without requiring admin rights; no continuous/always-on listening
(push-to-talk or typed trigger only, per spec Assumptions)

**Scale/Scope**: Single user; two intents at launch (question-answering, create-reminder) via
an extensible skill registry; reminders list expected to stay in the tens-to-hundreds range

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Voice-First Interaction**: Voice (STT) and text input both feed the same
  `IntentRouter` → `Skill` → `Response` path; no behavior is voice-only. **PASS**
- **II. Privacy & Local Control**: STT and TTS run entirely locally (`faster-whisper`,
  `pyttsx3`); only command text goes to the Claude API, and only to fulfill that request.
  Every LLM call is appended to a local, user-readable log (timestamp, truncated text,
  provider). API key read from a local env var/config file, never committed. **PASS**
- **III. Modular Skills Architecture**: `QuestionAnsweringSkill` and `ReminderSkill` each
  implement a shared `Skill` contract, are registered in a router, and are unit-testable
  without starting STT/TTS. Skills do not reach into each other's state. **PASS**
- **IV. Test-First for Core Logic**: `IntentRouter` and both skill contracts get contract
  tests written before implementation (enforced in tasks.md ordering); STT/TTS glue code with
  no branching logic is exempt. **PASS**
- **V. Simplicity & Incremental Delivery**: Single project, no multi-service split, SQLite
  instead of a DB server, manual push-to-talk instead of a wake-word pipeline, no plugin
  marketplace. **PASS**

No violations — Complexity Tracking left empty.

*Post-Phase 1 re-check*: data-model.md and contracts/ introduce no new dependencies, services,
or cross-skill coupling beyond what was assessed above (each contract maps to exactly one
principle's concern: IntentRouter/Skill → III & IV, LLMClient → II, ReminderRepository → V).
All gates remain **PASS**.

## Project Structure

### Documentation (this feature)

```text
specs/001-jarvis-core/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/
└── jarvis/
    ├── app.py              # Wiring: input source -> IntentRouter -> Skill -> output
    ├── intent/
    │   ├── router.py       # IntentRouter: text -> IntentResult
    │   └── llm_client.py   # LLMClient protocol + Claude API implementation
    ├── skills/
    │   ├── base.py         # Skill contract (can_handle / execute)
    │   ├── question.py     # QuestionAnsweringSkill
    │   └── reminders.py    # ReminderSkill
    ├── io/
    │   ├── speech_to_text.py   # faster-whisper wrapper
    │   ├── text_to_speech.py   # pyttsx3 wrapper
    │   └── text_io.py          # stdin/stdout fallback
    └── storage/
        └── reminder_repository.py  # SQLite-backed CRUD for Reminder

tests/
├── contract/      # IntentRouter contract, Skill contract, LLMClient contract
├── integration/   # End-to-end text-mode flows for User Stories 1-3
└── unit/          # Per-skill and per-module unit tests
```

**Structure Decision**: Single project (Option 1). No frontend/backend split and no
mobile/API split are needed — Jarvis runs as one local Python process on the user's machine.
The `src/jarvis/` package separates intent understanding, skills, I/O (voice/text), and
storage so each stays independently testable per Constitution Principle III.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
