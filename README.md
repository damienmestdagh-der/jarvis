# Jarvis

A personal voice/text assistant: ask it a question or ask it to remember something.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # then fill in OPENAI_API_KEY
```

## Run

```powershell
# Text mode
python -m jarvis --text "What's the capital of France?"
python -m jarvis --text "Remind me to call the plumber tomorrow"
python -m jarvis --text "What are my reminders?"

# Voice mode (press Enter, then speak)
python -m jarvis --voice
```

## Test

```powershell
pytest
```

See `specs/001-jarvis-core/quickstart.md` for the full manual validation walkthrough
(including edge cases), and `specs/001-jarvis-core/` for the spec, plan, and design docs this
feature was built from.

## Privacy

Speech-to-text and text-to-speech run entirely on your machine. Only the text of a command is
ever sent to the LLM (OpenAI), and every such call is logged locally and readable at
`%APPDATA%/Jarvis/llm_calls.jsonl`.
