# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Audio transcription project with two interfaces:
1. **CLI** (`transcribe.py`) — single-file script for local transcription
2. **API** (`app/`) — FastAPI REST API with Whisper + GPT-4o-mini refinement

Both default to Portuguese language transcription.

## Structure

```
transcribe/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app + POST /transcribe endpoint
│   ├── transcriber.py   # Whisper local transcription + pause detection
│   └── refiner.py       # GPT-4o-mini text refinement
├── transcribe.py        # Original CLI tool (unchanged)
├── requirements.txt
├── .env.example
└── CLAUDE.md
```

## Setup

```bash
pip install -r requirements.txt
# optional, for certain audio formats:
pip install ffmpeg-python
```

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | (required) | OpenAI API key for GPT-4o-mini refinement |
| `WHISPER_MODEL` | `base` | Whisper model size (tiny/base/small/medium/large) |
| `PAUSE_THRESHOLD` | `1.5` | Silence gap in seconds to insert `[...]` |

## Running the API

```bash
cp .env.example .env  # fill in OPENAI_API_KEY
uvicorn app.main:app --reload
```

Test:
```bash
curl -X POST http://localhost:8000/transcribe \
  -F "file=@audio.m4a" \
  -F "language=Portuguese"
```

Response:
```json
{"text": "texto transcrito e refinado [...]", "duration": 120.5}
```

## API Flow

```
POST /transcribe (UploadFile)
  → tempfile
  → Whisper.transcribe() → segments[]
  → gap detection → text with [...]
  → GPT-4o-mini refinement
  → {"text": "...", "duration": 120.5}
```

## Running the CLI

```bash
# Auto-discovers gravacao.m4u / gravacao.mp3 / gravacao.wav in cwd
python transcribe.py

# Explicit input
python transcribe.py -i audio.mp3 -l Portuguese -o texto.txt

# Choose model size (tiny|base|small|medium|large); default: base
python transcribe.py --model small --language en --input entrevista.wav
```

## Architecture

### CLI (`transcribe.py`, ~175 lines)
- `parse_args()` — CLI argument parsing (`-i`, `-l`, `-o`, `-m`)
- `find_default_recording()` — auto-discovers `gravacao.{m4u,mp3,wav}` in cwd
- `main()` — resolves paths/language, loads Whisper model, transcribes, writes `.txt` output

### API (`app/`)
- `transcriber.py` — loads Whisper model (cached), transcribes with segment-level pause detection
- `refiner.py` — sends transcribed text to GPT-4o-mini for orthographic/semantic correction
- `main.py` — FastAPI app, handles file upload, temp file lifecycle, orchestrates transcription + refinement

## Python Version

Requires Python 3.10+ (uses `str | None` union type syntax).
