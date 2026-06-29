"""
Adobe Premiere Pro automation via CEP (Common Extensibility Platform).

Requires the companion CEP extension installed in Premiere Pro.
The extension exposes a local HTTP server that accepts commands.

Extension setup: scripts/premiere_extension/
"""
from pathlib import Path

import httpx

from videoai.config import settings
from videoai.transcription.whisper import TranscriptionResult


class PremiereConnector:
    def __init__(self) -> None:
        self.base_url = f"http://{settings.premiere_host}:{settings.premiere_port}"

    def _post(self, endpoint: str, payload: dict) -> dict:
        response = httpx.post(
            f"{self.base_url}/{endpoint}",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def is_connected(self) -> bool:
        try:
            httpx.get(f"{self.base_url}/ping", timeout=2).raise_for_status()
            return True
        except Exception:
            return False

    def import_clip(self, video_path: Path | str) -> dict:
        return self._post("import", {"path": str(Path(video_path).absolute())})

    def add_subtitles(self, result: TranscriptionResult, track: int = 1) -> dict:
        captions = [
            {"start": s.start, "end": s.end, "text": s.text.strip()}
            for s in result.segments
        ]
        return self._post("captions", {"track": track, "captions": captions})

    def create_sequence(self, name: str, clips: list[dict]) -> dict:
        return self._post("sequence", {"name": name, "clips": clips})

    def export(self, output_path: Path | str, preset: str = "H264") -> dict:
        return self._post("export", {
            "path": str(Path(output_path).absolute()),
            "preset": preset,
        })
