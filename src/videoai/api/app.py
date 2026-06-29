"""
REST API — future React frontend entry point.

Run: uvicorn videoai.api.app:app --reload
"""
from pathlib import Path

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from videoai.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title="VideoAI API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    @app.post("/transcribe")
    async def transcribe(file: UploadFile) -> dict:
        from videoai.transcription import WhisperTranscriber

        settings.ensure_dirs()
        tmp = settings.data_temp_dir / (file.filename or "upload.mp4")
        tmp.write_bytes(await file.read())

        transcriber = WhisperTranscriber()
        result = transcriber.transcribe(tmp)
        tmp.unlink(missing_ok=True)

        return {
            "language": result.language,
            "text": result.full_text,
            "segments": [
                {"start": s.start, "end": s.end, "text": s.text}
                for s in result.segments
            ],
        }

    @app.post("/analyze")
    async def analyze(payload: dict) -> dict:
        from videoai.analysis import ClaudeAnalyzer

        transcript = payload.get("transcript", "")
        if not transcript:
            raise HTTPException(status_code=400, detail="transcript required")

        analyzer = ClaudeAnalyzer()
        result = analyzer.analyze_transcript(transcript)
        return {
            "summary": result.summary,
            "topics": result.topics,
            "suggested_title": result.suggested_title,
            "hashtags": result.hashtags,
        }

    return app


app = create_app()
