# Feature Specification: Jarvis Core Assistant Loop

**Feature Branch**: `001-jarvis-core`

**Created**: 2026-10-18

**Status**: Draft

**Input**: User description: "Jarvis — assistant vocal/IA personnel. Première fonctionnalité à spécifier : le cœur de l'assistant — recevoir une commande vocale (ou texte en fallback), la faire comprendre par un LLM pour déterminer l'intention, et exécuter une action simple (ex: répondre à une question, créer un rappel/tâche). L'automatisation domotique est une extension future, pas le scope de cette première spec. Aucune stack technique n'est encore choisie."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask a question and get an answer (Priority: P1)

A user speaks (or types) a question to the assistant and receives a spoken and/or text answer.

**Why this priority**: This is the smallest end-to-end slice that proves the whole pipeline works
(input capture → intent understanding → action → response). Without it, nothing else in the
assistant has a foundation.

**Independent Test**: Can be fully tested by giving the assistant a factual question (voice or
text) and confirming it returns a relevant, audible/visible answer — no other feature required.

**Acceptance Scenarios**:

1. **Given** the assistant is running and idle, **When** the user asks a factual question by
   voice, **Then** the assistant transcribes the question, determines the intent is "answer a
   question," and responds with an answer.
2. **Given** the assistant is running, **When** the user types the same question as text instead
   of speaking, **Then** the assistant produces an equivalent answer through the same intent path.
3. **Given** the user asks a question the assistant cannot answer, **When** the assistant
   processes it, **Then** it clearly tells the user it doesn't know rather than inventing an
   answer or staying silent.

---

### User Story 2 - Create a reminder/task by command (Priority: P2)

A user tells the assistant to remember or do something later (a reminder or a simple task), and
the assistant stores it and can report it back when asked.

**Why this priority**: Demonstrates the assistant can take a concrete action (not just answer
questions), which is the second core capability named in scope.

**Independent Test**: Can be fully tested by giving a command like "remind me to call the
plumber tomorrow," then asking the assistant to list reminders, and confirming it appears —
independent of the Q&A path.

**Acceptance Scenarios**:

1. **Given** the assistant is running, **When** the user asks (voice or text) to create a
   reminder/task with a clear description, **Then** the assistant confirms it was created and
   stores it.
2. **Given** at least one reminder/task has been created, **When** the user asks the assistant to
   list their reminders/tasks, **Then** the assistant reports the ones currently stored.
3. **Given** the assistant has been restarted since a reminder/task was created, **When** the user
   asks to list reminders/tasks, **Then** previously created items are still present.

---

### User Story 3 - Fall back to text when voice isn't usable (Priority: P3)

A user interacts with the assistant entirely through typed text, with no voice input/output
involved, and gets the same behavior as the voice path.

**Why this priority**: Required for development/debugging and for environments without reliable
audio, but the product's primary interaction mode is voice (User Stories 1–2), so this is lower
priority than proving the voice path itself.

**Independent Test**: Can be fully tested by disabling/ignoring audio entirely and driving both
User Story 1 and User Story 2 through text only.

**Acceptance Scenarios**:

1. **Given** voice input is unavailable or not used, **When** the user types a command, **Then**
   the assistant processes it through the same intent-understanding and action path as a voice
   command.

### Edge Cases

- What happens when the assistant cannot transcribe the audio at all (silence, unintelligible
  speech, unsupported language)? → The assistant MUST tell the user it didn't understand and ask
  them to repeat or type instead, rather than guessing or failing silently.
- What happens when the command is understandable but the intent is genuinely ambiguous (e.g.,
  could be a question or a reminder)? → The assistant MUST ask a clarifying question instead of
  picking one interpretation silently.
- What happens when the LLM or any required external service is unreachable? → The assistant MUST
  inform the user it cannot process the request right now, rather than hanging indefinitely or
  crashing.
- What happens when the user gives an empty or near-empty command (e.g., background noise picked
  up as a short utterance)? → The assistant MUST NOT treat it as a valid command or take any
  action.
- What happens when a reminder/task command omits a clear description (e.g., "remind me about
  stuff")? → The assistant MUST ask the user to clarify what to remind them about before storing
  anything.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a spoken command from the user and convert it to text for
  processing.
- **FR-002**: System MUST accept a typed text command as a fallback input path, processed through
  the same understanding/action logic as voice.
- **FR-003**: System MUST send the user's command (as text) to an LLM-based process to determine
  the user's intent before acting.
- **FR-004**: System MUST support, at minimum, two distinct intents: answering a question and
  creating a reminder/task.
- **FR-005**: System MUST respond to the user with the outcome of the action it took (an answer,
  a confirmation of creation, or a clarification/error message).
- **FR-006**: System MUST ask a clarifying question when it cannot determine the user's intent
  with reasonable confidence, instead of guessing.
- **FR-007**: System MUST persist created reminders/tasks so they remain available after the
  assistant is restarted.
- **FR-008**: System MUST let the user retrieve/list their previously created reminders/tasks on
  request.
- **FR-009**: System MUST clearly inform the user when a request cannot be processed (unreachable
  LLM, failed transcription, etc.) rather than failing silently.
- **FR-010**: System MUST NOT send the user's command content to the LLM or any external service
  for purposes other than fulfilling that specific request (per the project's privacy principle).
- **FR-011**: The assistant MUST only start processing a command following an explicit user
  activation (push-to-talk / manual trigger or typed input) for this feature; continuous
  always-on listening is out of scope for this spec.
- **FR-012**: The assistant MUST only passively store reminders/tasks for on-demand retrieval
  (User Story 2); proactively alerting the user when a reminder becomes due is out of scope for
  this spec.

### Key Entities

- **Command**: A single user request, either transcribed from voice or typed as text, with a
  timestamp and source (voice/text).
- **Intent**: The understood purpose of a Command (e.g., "question", "create_reminder"), derived
  by the LLM-based understanding step, with an indication of confidence/ambiguity.
- **Reminder/Task**: A user-created item to be remembered, with a description, creation time, and
  status (pending/done). Does not include a due-time alerting mechanism in this spec.
- **Response**: The assistant's reply to a Command (an answer, confirmation, clarification
  question, or error message).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user asking a factual question (voice or text) receives a relevant answer within
  5 seconds for at least 90% of requests.
- **SC-002**: A user can create a reminder/task in a single command, without repeating themselves,
  at least 90% of the time it is attempted with a clear description.
- **SC-003**: 100% of commands the assistant cannot understand or process result in a clear
  message to the user (never silence, a crash, or an invented answer).
- **SC-004**: 100% of reminders/tasks created by a user are still retrievable after the assistant
  has been restarted.
- **SC-005**: A new user can successfully get an answer to a question and create a reminder within
  their first 3 attempts at each, without external help.

## Assumptions

- The assistant is activated explicitly by the user (e.g., pressing a button or typing), not by a
  continuously-listening wake word, for this first feature.
- Reminders/tasks are retrieved on demand by asking the assistant; proactively notifying the user
  when something becomes due is a future feature, not part of this spec.
- Single-user usage is assumed; multi-user accounts/permissions are out of scope.
- The assistant's primary interaction language matches the user's own language; multi-language
  support beyond that is not required for this spec.
- Home automation, and any action beyond answering questions and managing reminders/tasks, is out
  of scope for this spec (explicitly excluded by the feature description).
- Concrete technology choices (language, runtime, specific LLM provider, storage mechanism) are
  deliberately not addressed here and will be decided in `/speckit-plan`.
