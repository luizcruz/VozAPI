"""FastAPI application for audio transcription."""

import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

load_dotenv()

from app.transcriber import transcribe
from app.refiner import refine

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

app = FastAPI(title="Transcribe API", description="Audio transcription with Whisper + GPT-4o-mini")


@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("Portuguese"),
    model: str = Form(WHISPER_MODEL),
) -> JSONResponse:
    """Transcribe an uploaded audio file.

    - Runs Whisper locally to get segments
    - Inserts [...] at pauses between segments
    - Refines the text with GPT-4o-mini
    """
    suffix = Path(file.filename or "audio").suffix or ".tmp"
    tmp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            content = await file.read()
            tmp.write(content)

        result = transcribe(audio_path=tmp_path, language=language, model_name=model)
        refined_text = refine(result["text"])

        return JSONResponse({"text": refined_text, "duration": result["duration"]})

    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {exc}") from exc
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
