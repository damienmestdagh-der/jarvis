"""CLI entrypoint: `python -m jarvis --text "..."` or `python -m jarvis --voice`."""

from __future__ import annotations

import argparse
import sys

from jarvis.app import build_app
from jarvis.intent.claude_client import MissingApiKeyError
from jarvis.io.text_io import print_response, read_command_text


def _build_app_or_exit():
    try:
        return build_app()
    except MissingApiKeyError as exc:
        print(f"Jarvis: {exc}", file=sys.stderr)
        sys.exit(1)


def _run_text_mode(args: argparse.Namespace) -> None:
    text = read_command_text(args.text)
    if not text or not text.strip():
        return  # Edge Case: empty/whitespace input is a no-op, not an error.
    app = _build_app_or_exit()
    response = app.handle_text(text, source="text")
    print_response(response)


def _run_voice_mode() -> None:
    # Imported here, not at module load, so --text mode never needs these
    # optional, heavier dependencies installed or a microphone present (US3).
    try:
        import tempfile
        from pathlib import Path

        from jarvis.io.speech_to_text import (
            MicrophoneError,
            SpeechToText,
            TranscriptionError,
            record_from_microphone,
        )
        from jarvis.io.text_to_speech import TextToSpeech
    except ImportError as exc:  # pragma: no cover - environment-dependent
        print(f"Jarvis: voice mode is unavailable ({exc}). Try --text instead.", file=sys.stderr)
        sys.exit(1)

    app = _build_app_or_exit()
    stt = SpeechToText()
    tts = TextToSpeech()

    input("Press Enter, then speak your command...")
    audio_path = Path(tempfile.gettempdir()) / "jarvis_capture.wav"
    try:
        record_from_microphone(audio_path)
        text = stt.transcribe_file(audio_path)
    except MicrophoneError as exc:  # pragma: no cover - environment-dependent
        print(f"Jarvis: no microphone available ({exc}). Try --text instead.", file=sys.stderr)
        sys.exit(1)
    except TranscriptionError:
        tts.speak("Sorry, I didn't catch that. Please try again or use text mode.")
        return

    response = app.handle_text(text, source="voice")
    if response is not None:
        tts.speak(response.text)


def main() -> None:
    parser = argparse.ArgumentParser(prog="jarvis")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--text", nargs="?", const=None, default=None,
        help="Send a text command (prompts on stdin if no value given; this is also the "
        "default mode when neither flag is passed)",
    )
    mode.add_argument("--voice", action="store_true", help="Use the microphone/speaker")
    args = parser.parse_args()

    if args.voice:
        _run_voice_mode()
    else:
        _run_text_mode(args)


if __name__ == "__main__":
    main()
