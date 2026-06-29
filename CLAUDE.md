# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VideoAI is a Python toolkit for AI-powered video processing. Core capabilities:
- Whisper transcription → SRT/VTT subtitle generation
- AI analysis (Claude, ChatGPT, Ollama) to extract highlights and social content
- FFmpeg-based clip cutting and social-format resizing (9:16 for TikTok/Reels)
- Adobe Premiere Pro automation via CEP HTTP bridge
- File organization by type and project
- FastAPI REST layer for a future React frontend

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # then fill in API keys
```

## Common Commands

```bash
# CLI entry point
videoai --help
videoai transcribe video.mp4
videoai clips video.mp4 --max-clips 5 --platform tiktok
videoai analyze video.mp4 --provider claude
videoai serve                      # start REST API on :8000

# Tests
pytest
pytest tests/test_transcription.py::test_to_srt -v

# Lint / format
ruff check .
ruff format .
```

## Architecture

```
src/videoai/
├── config.py          # pydantic-settings; single Settings instance imported everywhere
├── cli.py             # typer CLI; each command wires modules together end-to-end
├── transcription/
│   └── whisper.py     # WhisperTranscriber (lazy model load); TranscriptionResult → .to_srt()/.to_vtt()
├── video/
│   ├── ffmpeg.py      # FFmpegProcessor: probe, extract_audio, cut, resize, to_social_format
│   ├── clips.py       # ClipGenerator: cut + optionally reformat; from_highlights() accepts AI output
│   └── subtitles.py   # SubtitleBurner: burn SRT/VTT into video with ffmpeg vf subtitles filter
├── analysis/
│   ├── claude_ai.py   # ClaudeAnalyzer: analyze_transcript, find_highlights, generate_social_content
│   ├── chatgpt.py     # ChatGPTAnalyzer: thin wrapper around openai chat completions
│   └── ollama.py      # OllamaAnalyzer: local LLM via HTTP; is_available() for graceful fallback
├── automation/
│   └── premiere.py    # PremiereConnector: HTTP client for CEP extension; import, captions, export
├── organizer/
│   └── files.py       # FileOrganizer: move files by extension, group_by_project, cleanup_temp
└── api/
    └── app.py         # FastAPI app; /transcribe and /analyze endpoints; CORS open for localhost:3000/5173
```

### Key data flow

```
video file
  → FFmpegProcessor.extract_audio()       WAV (16kHz mono)
  → WhisperTranscriber.transcribe()       TranscriptionResult (segments with timestamps)
  → ClaudeAnalyzer.find_highlights()      list[HighlightTimestamp]
  → ClipGenerator.from_highlights()       list[Path]  (cut + resized MP4s)
  → SubtitleBurner.from_result()          MP4 with burned captions
```

### AI provider selection

All three analyzers expose the same `analyze_transcript(transcript: str)` interface. The CLI uses `--provider claude|chatgpt|ollama`; production code can auto-select via `OllamaAnalyzer.is_available()`.

### Adobe Premiere integration

`PremiereConnector` is an HTTP client — it requires a companion CEP extension running inside Premiere Pro that listens on `localhost:3000`. The extension is not yet implemented; see `automation/premiere.py` docstring.

### Future React frontend

`api/app.py` is the entry point. Run `videoai serve` and point the React dev server proxy at `http://localhost:8000`. CORS is pre-configured for `localhost:3000` and `localhost:5173`.
