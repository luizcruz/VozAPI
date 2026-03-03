"""Whisper local transcription with pause detection."""

import os
import whisper

PAUSE_THRESHOLD = float(os.getenv("PAUSE_THRESHOLD", "1.5"))

_model_cache: dict[str, whisper.Whisper] = {}


def load_model(model_name: str) -> whisper.Whisper:
    if model_name not in _model_cache:
        _model_cache[model_name] = whisper.load_model(model_name)
    return _model_cache[model_name]


def transcribe(audio_path: str, language: str = "Portuguese", model_name: str = "base") -> dict:
    """Transcribe audio file and insert [...] at pauses between segments.

    Returns:
        {"text": str, "duration": float}
    """
    model = load_model(model_name)
    result = model.transcribe(audio_path, language=language, verbose=False)

    segments = result.get("segments", [])
    parts: list[str] = []

    for i, seg in enumerate(segments):
        parts.append(seg["text"].strip())
        if i < len(segments) - 1:
            gap = segments[i + 1]["start"] - seg["end"]
            if gap >= PAUSE_THRESHOLD:
                parts.append("[...]")

    text = " ".join(parts)

    duration: float = 0.0
    if segments:
        duration = segments[-1]["end"]

    return {"text": text, "duration": duration}
