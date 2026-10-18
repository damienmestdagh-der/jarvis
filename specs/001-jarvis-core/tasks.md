---

description: "Task list template for feature implementation"
---

# Tasks: Jarvis Core Assistant Loop

**Input**: Design documents from `/specs/001-jarvis-core/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md (all present)

**Tests**: Included — Constitution Principle IV (Test-First for Core Logic) requires contract
tests for routing/skill-contract logic written before implementation.

**Organization**: Tasks are grouped by user story (spec.md) to enable independent
implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Paths below follow the single-project layout fixed in plan.md (`src/jarvis/`, `tests/`)

---

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 Create project directory structure per plan.md: `src/jarvis/{intent,skills,io,storage}/` and `tests/{contract,integration,unit}/`, each with an `__init__.py`
- [X] T002 Create `requirements.txt` at repo root listing `anthropic`, `faster-whisper`, `pyttsx3`, `pytest` (per research.md §1-5)
- [X] T003 [P] Create `pyproject.toml` with pytest test-path configuration (`tests/`) and ruff lint configuration
- [X] T004 [P] Create `.gitignore` excluding `.venv/`, `__pycache__/`, `*.db`, `*.jsonl`, `.env`
- [X] T005 [P] Create `.env.example` documenting the required `ANTHROPIC_API_KEY` variable with no real value (Constitution II: secrets never committed)

**Checkpoint**: Project skeleton exists; no code yet.

---

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: No user story work can begin until this phase is complete — both US1 and US2
route every command through the same `IntentRouter` → `Skill` registry built here.

- [X] T006 [P] Implement local app-data path helper in `src/jarvis/paths.py` resolving `%APPDATA%/Jarvis` and creating the directory if missing (used by storage and the LLM call log)
- [X] T007 [P] Define `Command` and `Response` dataclasses in `src/jarvis/models.py` per data-model.md: `Command{id: str, text: str, source: Literal["voice","text"], created_at: datetime}` — `text` MUST be rejected (treated as no-op) if empty or whitespace-only after trimming; `Response{kind: Literal["answer","confirmation","clarification","error"], text: str, command_id: str}`
- [X] T008 [P] Define `Intent`/`IntentResult` dataclass in `src/jarvis/intent/models.py` per data-model.md: `name: Literal["question","create_reminder","unclear"]`, `confidence: float` in `[0.0, 1.0]`, `payload: dict` — a `create_reminder` intent with an empty/missing `payload.description` MUST be treated as `unclear`
- [X] T009 [P] Define the `Skill` abstract base contract (`can_handle(intent) -> bool`, `execute(intent) -> Response`) in `src/jarvis/skills/base.py` per contracts/skill.md
- [X] T010 [P] Define the `LLMClient` protocol (`classify_intent(text) -> IntentResult`, `answer_question(text) -> str`) in `src/jarvis/intent/llm_client.py` per contracts/llm_client.md
- [X] T011 Implement the local LLM-call JSONL logger (timestamp, truncated input text, provider name; one line per call) in `src/jarvis/intent/call_log.py`, using the path helper from T006 (depends on T006) — satisfies the constitution's local-audit requirement for every external call
- [X] T012 [P] Contract test for `IntentRouter` in `tests/contract/test_intent_router.py` covering contracts/intent_router.md cases 1-6 (clear question, clear reminder, ambiguous text, reminder with no description, LLMClient failure, empty-text precondition) — write first, must fail until T014 exists
- [X] T013 [P] Contract test for the skill registry in `tests/contract/test_skill_registry.py`: exactly one registered skill handles any non-`unclear` Intent, and dispatch never raises — write first, must fail until T015 exists
- [X] T014 [P] Implement `IntentRouter.classify` in `src/jarvis/intent/router.py` (depends on T008, T010, T012): converts LLMClient exceptions, below-threshold confidence, or an empty `create_reminder` description into `Intent(name="unclear")`; never lets an exception escape `classify`
- [X] T015 [P] Implement the skill registry in `src/jarvis/skills/registry.py` (depends on T009, T013): routes an `Intent` to the one matching registered `Skill`
- [X] T016 Implement core orchestration in `src/jarvis/app.py` (depends on T006-T015): ingest a `Command`, reject empty/whitespace text per T007 without calling the router, otherwise call `IntentRouter.classify` then dispatch via the registry, and always emit exactly one `Response`

**Checkpoint**: Foundation ready — US1 and US2 implementation can now begin.

---

## Phase 3: User Story 1 - Ask a question and get an answer (Priority: P1) 🎯 MVP

**Goal**: A user asks a question by voice or text and receives an answer; an unanswerable
question gets a clear "I don't know," never an invented answer.

**Independent Test**: Give the assistant a factual question (voice or text) and confirm it
returns a relevant answer, per quickstart.md "Validate User Story 1" — no other story required.

### Tests for User Story 1

- [X] T017 [P] [US1] Contract test for `QuestionAnsweringSkill` in `tests/contract/test_question_skill.py` per contracts/skill.md cases 1-3 — write first, must fail until T024 exists
- [X] T018 [P] [US1] Integration test: a text question returns an answer (Acceptance Scenarios 1 & 2) in `tests/integration/test_ask_question.py`
- [X] T019 [P] [US1] Integration test: an unanswerable question returns a clear "I don't know" `Response`, never a fabricated answer (Acceptance Scenario 3) in `tests/integration/test_ask_question_unknown.py`

### Implementation for User Story 1

- [X] T020 [P] [US1] Implement the speech-to-text wrapper (faster-whisper) in `src/jarvis/io/speech_to_text.py`: returns transcribed text from a microphone capture, raises a clear, caught error (not a silent failure) when audio is empty/unintelligible
- [X] T021 [P] [US1] Implement the text-to-speech wrapper (pyttsx3) in `src/jarvis/io/text_to_speech.py`: speaks a `Response.text`
- [X] T022 [P] [US1] Implement the text input/output fallback in `src/jarvis/io/text_io.py`: reads a command string from a CLI argument or stdin, prints a `Response.text`
- [X] T023 [P] [US1] Implement `ClaudeLLMClient` in `src/jarvis/intent/claude_client.py`, implementing `classify_intent` (structured tool-output per research.md §4, covering both `question` and `create_reminder` intents) and `answer_question`, logging every call via T011 (depends on T010, T011)
- [X] T024 [US1] Implement `QuestionAnsweringSkill` in `src/jarvis/skills/question.py` per contracts/skill.md (depends on T009, T023): on LLM failure, returns `Response(kind="error")`, never a fabricated answer
- [X] T025 [US1] Register `QuestionAnsweringSkill` in the skill registry wiring in `src/jarvis/app.py` (depends on T015, T024)
- [X] T026 [US1] Implement the CLI entrypoint with `--text` and `--voice` flags in `src/jarvis/__main__.py`, wiring T020-T022 I/O into the T016 orchestration (depends on T016, T020, T021, T022, T025)

**Checkpoint**: User Story 1 is independently functional — run quickstart.md's User Story 1 validation.

---

## Phase 4: User Story 2 - Create a reminder/task by command (Priority: P2)

**Goal**: A user tells the assistant to remember something; it's stored and retrievable later,
including after a restart.

**Independent Test**: Issue a "remind me to X" command, then ask to list reminders, and confirm
it appears, per quickstart.md "Validate User Story 2" — independent of the Q&A path.

### Tests for User Story 2

- [X] T027 [P] [US2] Contract test for `ReminderRepository` in `tests/contract/test_reminder_repository.py` per contracts/reminder_repository.md cases 1-4 — write first, must fail until T033 exists
- [X] T028 [P] [US2] Contract test for `ReminderSkill` in `tests/contract/test_reminder_skill.py` per contracts/skill.md cases 4-6 — write first, must fail until T034 exists
- [X] T029 [P] [US2] Integration test: create then list a reminder (Acceptance Scenarios 1 & 2) in `tests/integration/test_reminders.py`
- [X] T030 [P] [US2] Integration test: reminders persist after restart — reopen the repository against the same file and confirm prior reminders are still listed (Acceptance Scenario 3 / SC-004) in `tests/integration/test_reminders_persistence.py`
- [X] T031 [P] [US2] Integration test: "remind me about stuff" (no concrete description) yields a clarification `Response` and creates no `Reminder` (Edge Case / FR-012) in `tests/integration/test_reminder_unclear.py`

### Implementation for User Story 2

- [X] T032 [P] [US2] Implement SQLite schema initialization in `src/jarvis/storage/schema.py` (depends on T006): `reminders` table with `id INTEGER PRIMARY KEY`, `description TEXT NOT NULL`, `status TEXT NOT NULL DEFAULT 'pending'` (allowed values `pending`/`done`), `created_at TEXT NOT NULL`
- [X] T033 [US2] Implement `ReminderRepository` (`create`, `list`, `mark_done`) in `src/jarvis/storage/reminder_repository.py` per contracts/reminder_repository.md (depends on T032): `create` requires a non-empty `description` and sets `status="pending"`; `list` returns `[]` (not an error) when empty; `mark_done` raises a lookup error for an unknown id
- [X] T034 [US2] Implement `ReminderSkill` (create + list paths) in `src/jarvis/skills/reminders.py` per contracts/skill.md (depends on T009, T033)
- [X] T035 [US2] Register `ReminderSkill` in the skill registry wiring in `src/jarvis/app.py` (depends on T015, T034, and after T025 to avoid clobbering the US1 wiring)
- [X] T036 [P] [US2] Harden `IntentRouter`'s empty-description handling for `create_reminder` in `src/jarvis/intent/router.py` (depends on T014) to guarantee FR-012 / the Edge Case in T031 — already enforced by T014's implementation; verified by T031

**Checkpoint**: User Stories 1 AND 2 both work independently — run quickstart.md's User Story 2 validation.

---

## Phase 5: User Story 3 - Fall back to text when voice isn't usable (Priority: P3)

**Goal**: The assistant behaves identically when driven entirely through typed text, with no
voice input/output involved.

**Independent Test**: Disable/ignore audio entirely and drive both User Story 1 and User Story 2
through text only, per quickstart.md "Validate User Story 3".

### Tests for User Story 3

- [X] T037 [P] [US3] Integration test: the full question + reminder flow runs through `tests/integration/test_text_only_fallback.py` with speech_to_text/text_to_speech never invoked, confirming identical behavior to the voice path (Acceptance Scenario 1)

### Implementation for User Story 3

- [X] T038 [US3] Decouple `src/jarvis/io/text_io.py` and `src/jarvis/__main__.py` (depends on T020, T021, T022, T026) so text-only mode never imports or initializes `speech_to_text`/`text_to_speech` — verified by T037 (`--text` path never imports those modules; confirmed by the `sys.modules` check)
- [X] T039 [US3] Add a clear startup error in `src/jarvis/__main__.py` (depends on T038, same file) when `--voice` is requested but no microphone/TTS engine is available, instead of crashing or hanging — added `MicrophoneError` handling plus the real `record_from_microphone` capture (research.md §8)

**Checkpoint**: All three user stories are independently functional — quickstart.md passes end to end.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T040 [P] Unit tests for `Command`/`Response` validation (empty/whitespace text rejection) in `tests/unit/test_models.py`
- [X] T041 [P] Unit tests for `Intent` payload validation (empty `create_reminder` description → `unclear`) in `tests/unit/test_intent_models.py`
- [X] T042 [P] Write `README.md` at repo root summarizing setup and run instructions from quickstart.md
- [X] T043 Run the full quickstart.md validation end-to-end on Windows and fix any discrepancies found — found and fixed two real issues: (1) `python -m jarvis` needed the package installed (`pip install -e .`, added to pyproject.toml), (2) a missing `ANTHROPIC_API_KEY` and empty/whitespace `--text` both crashed before the fix (now a clean message / silent no-op respectively, see `tests/unit/test_claude_client.py`); also switched user-facing em dashes to plain hyphens after seeing them mis-render on the Windows console
- [X] T044 Privacy audit pass per Constitution Principle II: confirmed `call_log.py` truncates to 200 chars and never logs audio, `.gitignore` excludes `.env`/`*.db`/`*.jsonl`, and no API key is hardcoded anywhere in `src/` (grepped for key-shaped literals)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately.
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories.
- **User Stories (Phase 3-5)**: All depend on Foundational completion.
  - US1 (P1) and US2 (P2) have no dependency on each other and can proceed in parallel if staffed.
  - US3 (P3) depends on US1's I/O modules existing (T020-T022, T026) to decouple them — it is a thin, final-polish story layered on top of US1/US2, not independent of their files.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational — no dependency on US2/US3.
- **User Story 2 (P2)**: Starts after Foundational — no dependency on US1's skill logic, but shares `src/jarvis/app.py` wiring (T035 follows T025 to avoid a merge conflict, not a functional dependency).
- **User Story 3 (P3)**: Starts after US1's I/O/CLI tasks exist (T020-T022, T026), since it decouples and hardens that same code.

### Parallel Opportunities

- Setup: T003, T004, T005 in parallel.
- Foundational: T006-T010 in parallel; then T012, T013 in parallel; then T014, T015 in parallel; T011 and T016 are each single sequential steps.
- US1: T017-T019 (tests) in parallel; T020-T023 (implementation) in parallel; T024-T026 sequential.
- US2: T027-T031 (tests) in parallel; T032 and T036 in parallel with each other; T033-T035 sequential.
- Once Foundational is done, a second developer could start all of US2's [P] tasks while another works US1.

---

## Parallel Example: Foundational Phase

```bash
# Launch independent foundational building blocks together:
Task: "Implement local app-data path helper in src/jarvis/paths.py"
Task: "Define Command and Response dataclasses in src/jarvis/models.py"
Task: "Define Intent/IntentResult dataclass in src/jarvis/intent/models.py"
Task: "Define the Skill abstract base contract in src/jarvis/skills/base.py"
Task: "Define the LLMClient protocol in src/jarvis/intent/llm_client.py"
```

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for QuestionAnsweringSkill in tests/contract/test_question_skill.py"
Task: "Integration test for a text question in tests/integration/test_ask_question.py"
Task: "Integration test for an unanswerable question in tests/integration/test_ask_question_unknown.py"

# Launch independent implementation pieces together:
Task: "Implement speech-to-text wrapper in src/jarvis/io/speech_to_text.py"
Task: "Implement text-to-speech wrapper in src/jarvis/io/text_to_speech.py"
Task: "Implement text input/output fallback in src/jarvis/io/text_io.py"
Task: "Implement ClaudeLLMClient in src/jarvis/intent/claude_client.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational (blocks everything else).
3. Complete Phase 3: User Story 1.
4. **STOP and VALIDATE**: run quickstart.md's User Story 1 steps.
5. This is already a demoable assistant (ask-a-question loop, voice + text).

### Incremental Delivery

1. Setup + Foundational → foundation ready.
2. Add User Story 1 → validate independently → demo (MVP).
3. Add User Story 2 → validate independently → demo (reminders now work).
4. Add User Story 3 → validate independently → demo (confirmed voice-free operation).
5. Polish pass (Phase 6).

### Notes

- Tests marked for a story are written and confirmed failing before that story's implementation
  tasks, per Constitution Principle IV.
- Commit after each task or logical group.
- Stop at any checkpoint to validate a story independently before moving to the next.
