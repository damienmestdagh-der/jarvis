<!--
Sync Impact Report
Version change: [TEMPLATE] → 1.0.0 (initial ratification)
Modified principles: n/a (initial adoption)
Added sections:
  - I. Voice-First Interaction
  - II. Privacy & Local Control
  - III. Modular Skills Architecture
  - IV. Test-First for Core Logic
  - V. Simplicity & Incremental Delivery
  - Technology & Integration Constraints
  - Development Workflow
  - Governance
Removed sections: none
Deferred TODOs:
  - TODO(TECH_STACK): concrete language/runtime/platform (mobile, desktop, server) not yet chosen —
    to be decided during /speckit-specify and /speckit-plan for the first feature.
Templates requiring follow-up: none (plan/spec/tasks templates reference principles generically)
-->

# Jarvis Constitution

## Core Principles

### I. Voice-First Interaction
Every user-facing capability MUST be operable by voice command, with a text/CLI fallback for
development, debugging, and environments without audio. Voice command parsing and intent
routing MUST be decoupled from the underlying skill implementation, so a skill can be invoked
identically from voice, text, or an automated trigger.
Rationale: Jarvis's core value is hands-free assistance; if voice is treated as an add-on,
interaction design drifts toward screen/keyboard-first patterns that defeat the product's purpose.

### II. Privacy & Local Control
Audio, transcripts, and command data MUST NOT leave the user's control unless an external call
(e.g., a cloud LLM or home-automation API) is strictly required for that request, and the user has
explicitly enabled that integration. No telemetry, analytics, or data collection beyond what is
required for the feature to function. Secrets and API keys MUST be stored in local configuration
or an OS secret store, never committed to the repository or hardcoded.
Rationale: An assistant with microphone access and home/device control is high-trust; silent data
exfiltration or opaque cloud dependencies would undermine that trust and create real-world risk.

### III. Modular Skills Architecture
Each capability (e.g., a home-automation action, a task/reminder feature, an LLM query) MUST be
implemented as an independent "skill" module with a documented contract (inputs, outputs, side
effects). Skills MUST be independently testable without starting the full voice pipeline, and
MUST NOT reach into another skill's internal state directly — cross-skill interaction goes through
the shared command router.
Rationale: Keeps the assistant extensible; new capabilities should be addable without touching
unrelated code, and a broken skill must not be able to take down the whole assistant.

### IV. Test-First for Core Logic
Command parsing, intent routing, and every skill contract MUST have tests written and reviewed
before implementation (red-green-refactor). UI/voice-glue code that has no branching logic is
exempt, but anything that decides *what* to do in response to a command is not.
Rationale: Misrouted commands (e.g., triggering the wrong home-automation action) have real
physical consequences, so correctness of routing/dispatch logic is non-negotiable.

### V. Simplicity & Incremental Delivery
Start with the smallest assistant that is actually useful (one interaction surface, one or two
skills) before adding scope. Do not build speculative infrastructure (plugin marketplaces,
multi-user support, multi-LLM abstraction layers, etc.) until a concrete feature needs it (YAGNI).
Each new capability goes through the full spec → plan → tasks → implement cycle rather than being
bolted on ad hoc.
Rationale: A personal assistant project is easy to over-architect before it does anything useful;
incremental delivery keeps every stage demoable and avoids unused abstraction.

## Technology & Integration Constraints

- The concrete tech stack (language, runtime, target platform) is intentionally left open at the
  constitution level and MUST be decided and recorded in the first feature's plan.md
  (`/speckit-plan`), not here.
- LLM access MUST be behind an internal interface so the underlying provider/model can change
  without rewriting skills (no skill calls a specific vendor SDK directly).
- Home-automation or third-party integrations MUST use documented, authorized APIs only; no
  scraping, undocumented endpoints, or credential sharing across services.
- All external calls (LLM, home automation, any network API) MUST be logged locally in a way the
  user can inspect (what was sent, to whom, when), to keep Principle II auditable.

## Development Workflow

- New capabilities follow the Spec Kit flow: `/speckit-specify` → `/speckit-plan` →
  `/speckit-tasks` → `/speckit-implement`, in that order.
- Every `/speckit-plan` MUST include an explicit Constitution Check against the principles above
  before implementation starts; unresolved violations must be justified in the plan's Complexity
  Tracking section or the plan must be revised.
- Tests for routing/skill-contract logic (Principle IV) are part of "done" for a task, not a
  follow-up item.

## Governance

This constitution supersedes ad hoc technical decisions for this project. Amendments require:
1. A documented reason for the change (what problem the current principle causes).
2. An explicit version bump following semantic versioning (MAJOR: incompatible principle
   removal/redefinition; MINOR: new principle or materially expanded guidance; PATCH: wording/
   clarification only).
3. Updating the Sync Impact Report at the top of this file.

Compliance is checked at the Constitution Check gate of every `/speckit-plan` run. Any deviation
must be recorded and justified there, not silently absorbed into the implementation.

**Version**: 1.0.0 | **Ratified**: 2026-10-18 | **Last Amended**: 2026-10-18
