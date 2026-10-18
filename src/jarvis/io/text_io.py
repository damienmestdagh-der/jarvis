"""Text input/output fallback: reads a command from a CLI arg or stdin,
prints a Response. Deliberately has no dependency on speech_to_text or
text_to_speech, so text-only mode (US3) never touches voice code."""

from __future__ import annotations

from jarvis.models import Response


def read_command_text(cli_text: str | None) -> str:
    """Return the command text from --text, or prompt on stdin if not given."""
    if cli_text is not None:
        return cli_text
    return input("You: ")


def print_response(response: Response | None) -> None:
    if response is None:
        return
    print(f"Jarvis: {response.text}")
