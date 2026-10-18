# Contract: LLMClient

Internal protocol isolating all skills/routing from the concrete LLM provider (Constitution:
"LLM access MUST be behind an internal interface"). Each concrete adapter is the only module
allowed to import its provider's SDK — currently `openai_client.py` (in use, `openai` SDK) and
`claude_client.py` (unused, kept as a working second adapter; see research.md §3 amendment).

## `classify_intent(text: str) -> IntentResult`

Returns a structured result (`name`, `confidence`, `payload`) built from the LLM's structured
tool-output, never from free-text regex parsing (see research.md §4). Raises only for
transport-level failures (network/auth); the caller (`IntentRouter.classify`) is responsible
for converting that into an `unclear` Intent — this method does not swallow errors itself.

## `answer_question(text: str) -> str`

Returns a plain-text answer. Raises only for transport-level failures; the caller
(`QuestionAnsweringSkill.execute`) converts that into an error Response.

## Privacy/logging requirement (applies to both methods)

Every call MUST append one line to the local LLM call log (timestamp, truncated input text,
provider name) before returning — this is how the constitution's "external calls MUST be
logged locally in a way the user can inspect" requirement is satisfied for this feature. No
audio is ever passed to this interface — only already-transcribed text.

## Test cases (contract tests, written before implementation)

1. A call to either method appends exactly one well-formed line to the local call log.
2. A simulated transport failure (e.g., mocked network error) propagates as an exception from
   `LLMClient`, not swallowed here.
3. `classify_intent` on provider output missing the expected structured fields → raises (not a
   silently-wrong `IntentResult`); `IntentRouter` is responsible for turning that into
   `unclear`.
