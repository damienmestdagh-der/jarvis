"""Local speech-to-text via faster-whisper (research.md #1).

Runs entirely on-device: raw audio never leaves the machine, only the
resulting text goes any further (Constitution Principle II).
"""

from __future__ import annotations

from pathlib import Path


class TranscriptionError(RuntimeError):
    """Raised when audio can't be turned into usable text (silence,
    unintelligible speech) — callers must surface this as a clear message,
    never fail silently (spec Edge Cases)."""


class MicrophoneError(RuntimeError):
    """Raised when no microphone/audio input device is available — callers
    must surface this as a clear startup error, not a crash (FR-009)."""


_SAMPLE_RATE = 16000


def record_from_microphone(audio_path: Path, duration_seconds: float = 5.0) -> None:
    """Record a fixed-duration push-to-talk clip to `audio_path`."""
    try:
        import sounddevice as sd
        import soundfile as sf
    except ImportError as exc:
        raise MicrophoneError(f"Audio recording is unavailable: {exc}") from exc

    try:
        audio = sd.rec(
            int(duration_seconds * _SAMPLE_RATE), samplerate=_SAMPLE_RATE, channels=1
        )
        sd.wait()
    except Exception as exc:  # noqa: BLE001 - any device failure is "no microphone"
        raise MicrophoneError(f"No microphone available: {exc}") from exc

    sf.write(str(audio_path), audio, _SAMPLE_RATE)


class SpeechToText:
    def __init__(self, model_size: str = "base"):
        self._model_size = model_size
        self._model = None  # loaded lazily so importing this module is cheap

    def _load_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(self._model_size, device="cpu", compute_type="int8")
        return self._model

    def transcribe_file(self, audio_path: Path) -> str:
        model = self._load_model()
        segments, _info = model.transcribe(str(audio_path))
        text = " ".join(segment.text.strip() for segment in segments).strip()
        if not text:
            raise TranscriptionError("Could not understand the audio")
        return text
