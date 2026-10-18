# Phase 0 Research: Jarvis Core Assistant Loop

## 1. Speech-to-text engine

- **Decision**: `faster-whisper` (local Whisper inference, CPU-friendly) for voice-to-text.
- **Rationale**: Runs entirely on-device, so raw audio never leaves the machine — required by
  Constitution Principle II (Privacy & Local Control). Good accuracy for French/English,
  actively maintained, no per-request cost, no network dependency for this step.
- **Alternatives considered**:
  - Cloud STT (Google Speech-to-Text, Azure Speech): rejected — sends raw audio off-device,
    conflicts directly with the privacy principle for no added benefit at this project's scale.
  - Windows built-in Speech Recognition (SAPI): rejected — ties the project to Windows-only
    APIs and has historically weaker non-English accuracy; `faster-whisper` keeps the STT layer
    portable even though the first target platform is Windows.

## 2. Text-to-speech engine

- **Decision**: `pyttsx3` (offline TTS, uses SAPI5 on Windows).
- **Rationale**: Offline, zero cost, zero added network dependency, consistent with the same
  privacy rationale as STT. Voice quality is robotic but acceptable for a v1 personal assistant.
- **Alternatives considered**:
  - Cloud TTS (ElevenLabs, Azure/Google TTS): higher quality voices, but adds a second
    always-on external dependency and cost; deferred to a future enhancement behind the same
    opt-in pattern as the LLM call, not required for this spec's success criteria.

## 3. LLM provider & integration pattern

- **Decision**: Anthropic Claude API via the official `anthropic` Python SDK, accessed only
  through an internal `LLMClient` protocol (methods: `classify_intent(text)`,
  `answer_question(text)`). No skill or I/O module imports the `anthropic` package directly.
- **Rationale**: Satisfies Constitution's "LLM access behind an internal interface" constraint
  directly — swapping to OpenAI or another provider later means writing one new adapter class,
  not touching skills or routing logic. Claude's tool-use/structured-output support makes
  reliable intent classification straightforward.
- **Alternatives considered**:
  - Calling the LLM SDK directly from skills/router: rejected — violates the constitution's
    "pluggable LLM" constraint and would hard-couple core logic to one vendor.
  - Local LLM (Ollama) as the only option: rejected for v1 per the user's explicit choice of a
    cloud API; the `LLMClient` interface is shaped so a local-LLM adapter can be added later
    without redesign (constitution already anticipates this).

## 4. Intent classification mechanism

- **Decision**: A single Claude API call per command using structured tool-output to return
  `{intent: "question" | "create_reminder" | "unclear", confidence, payload}`.
- **Rationale**: Structured output avoids brittle free-text parsing and directly produces the
  `IntentResult` shape the router needs. One call keeps latency low (supports the 5s SC-001
  target) compared to a multi-step chain.
- **Alternatives considered**:
  - Rule-based/keyword classifier: rejected — too rigid for natural voice phrasing and would
    need constant hand-tuning; doesn't scale to future skills.
  - Free-text LLM response parsed with regex: rejected — fragile, breaks silently on phrasing
    drift, harder to test as a contract.

## 5. Reminder/task storage

- **Decision**: SQLite via the Python stdlib `sqlite3` module, one local file under the user's
  app-data directory.
- **Rationale**: No extra dependency (stdlib), supports simple queries (list pending reminders)
  more robustly than a flat file, and satisfies FR-007/FR-008 (persistence across restarts,
  on-demand listing) with minimal code.
- **Alternatives considered**:
  - Flat JSON file: simpler to read by hand, but no safe concurrent-write story and no real
    query capability; rejected once more than "append a line" is needed (status updates, listing).
  - A full database server (Postgres, etc.): rejected outright — violates Constitution
    Principle V (Simplicity) for a single-user local app.

## 6. Activation / trigger mechanism

- **Decision**: Manual trigger only for v1 — either a typed command (text fallback) or a
  "press Enter, then speak" push-to-talk prompt in the terminal/app window. No background
  listening process.
- **Rationale**: Matches the spec's documented assumption (no always-on wake word) and keeps
  v1 minimal per Constitution Principle V; avoids the added complexity and OS-level permissions
  a global hotkey/always-listening service would require.
- **Alternatives considered**:
  - Global hotkey library (e.g., `keyboard`) for push-to-talk outside the terminal: useful
    future enhancement, deferred — not required to satisfy any Functional Requirement in this
    spec.
  - Continuous wake-word listening (e.g., Porcupine): explicitly out of scope per spec
    Assumptions; would also raise the privacy bar (continuous microphone capture) beyond what
    this spec covers.

## 7. Auditability of external calls

- **Decision**: Every call to the LLM is appended as one line to a local JSONL log file
  (timestamp, truncated command text, provider name) under the same app-data directory as the
  SQLite file.
- **Rationale**: Directly satisfies the constitution's "Technology & Integration Constraints"
  requirement that external calls be logged locally in a user-inspectable way. Plain file
  append needs no new dependency.
- **Alternatives considered**: Structured logging framework (e.g., `structlog`) — unnecessary
  dependency for a single append-only local log at this scale; can be adopted later if logging
  needs grow.

## 8. Microphone capture

- **Decision**: `sounddevice` + `soundfile` to record a fixed-duration (5s) push-to-talk clip
  to a local WAV file, which `faster-whisper` then transcribes.
- **Rationale**: `faster-whisper` only transcribes audio, it does not capture it; a small,
  well-maintained recording library was needed to actually implement "press Enter, then speak"
  (research.md §6). A fixed duration keeps this minimal for a P3 fallback feature rather than
  building voice-activity detection.
- **Alternatives considered**: `pyaudio` — works but has a historically rougher install story
  on Windows; `sounddevice` wraps PortAudio with simpler packaging and was preferred for a
  Windows-first personal project.

**Output**: All "NEEDS CLARIFICATION" technical unknowns from the Technical Context are
resolved above; none remain.
