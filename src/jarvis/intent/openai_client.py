"""OpenAI-backed implementation of LLMClient (swap-in for ClaudeLLMClient).

The only module allowed to import the `openai` SDK — everything else depends
on the LLMClient protocol instead, so swapping providers again later means
writing one more adapter here, not touching skills or routing
(Constitution: "LLM access MUST be behind an internal interface").
"""

from __future__ import annotations

import json
import os

from jarvis.intent.call_log import log_call
from jarvis.intent.llm_client import MissingApiKeyError
from jarvis.intent.models import Intent

_MODEL = "gpt-4o-mini"
_PROVIDER_NAME = "openai:gpt-4o-mini"

_CLASSIFY_TOOL = {
    "type": "function",
    "function": {
        "name": "report_intent",
        "description": "Report the classified intent of a user's command to a personal assistant.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "enum": ["question", "create_reminder", "list_reminders", "unclear"],
                },
                "confidence": {
                    "type": "number",
                    "description": "0.0 (no idea) to 1.0 (certain)",
                },
                "question_text": {
                    "type": "string",
                    "description": "Present only when name is 'question': the question to answer.",
                },
                "description": {
                    "type": "string",
                    "description": (
                        "Present only when name is 'create_reminder': what to remind the user "
                        "about. Empty if the command didn't give a concrete description."
                    ),
                },
            },
            "required": ["name", "confidence"],
        },
    },
}

_CLASSIFY_SYSTEM_PROMPT = (
    "You classify a single command given to a personal assistant named Jarvis. "
    "Call report_intent exactly once with your classification. "
    "Use 'question' for anything the user wants answered, 'create_reminder' for anything "
    "the user wants remembered/done later, 'list_reminders' when the user is asking what "
    "reminders/tasks they already have, and 'unclear' if none of those fit or the command is "
    "too vague to act on."
)


class OpenAILLMClient:
    def __init__(self, api_key: str | None = None):
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise MissingApiKeyError(
                "OPENAI_API_KEY is not set. Copy .env.example to .env and fill it in."
            )
        import openai

        self._client = openai.OpenAI(api_key=api_key)

    def classify_intent(self, text: str) -> Intent:
        log_call(text, _PROVIDER_NAME)
        completion = self._client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": _CLASSIFY_SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            tools=[_CLASSIFY_TOOL],
            tool_choice={"type": "function", "function": {"name": "report_intent"}},
        )
        tool_call = completion.choices[0].message.tool_calls[0]
        data = json.loads(tool_call.function.arguments)

        name = data["name"]
        confidence = float(data.get("confidence", 0.0))
        if name == "question":
            payload = {"question_text": data.get("question_text", text)}
        elif name == "create_reminder":
            payload = {"description": data.get("description", "").strip()}
        else:
            payload = {}
        return Intent(name=name, confidence=confidence, payload=payload)

    def answer_question(self, text: str) -> str:
        log_call(text, _PROVIDER_NAME)
        completion = self._client.chat.completions.create(
            model=_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Jarvis, a concise personal assistant. Answer the user's "
                        "question directly. If you don't know or can't be confident, say so "
                        "plainly instead of guessing."
                    ),
                },
                {"role": "user", "content": text},
            ],
        )
        return (completion.choices[0].message.content or "").strip()
