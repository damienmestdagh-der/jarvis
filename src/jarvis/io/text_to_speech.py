"""Local text-to-speech via pyttsx3 (research.md #2) — runs entirely
on-device, consistent with the privacy rationale for speech-to-text."""

from __future__ import annotations


class TextToSpeech:
    def __init__(self):
        self._engine = None  # loaded lazily so importing this module is cheap

    def _load_engine(self):
        if self._engine is None:
            import pyttsx3

            self._engine = pyttsx3.init()
        return self._engine

    def speak(self, text: str) -> None:
        engine = self._load_engine()
        engine.say(text)
        engine.runAndWait()
