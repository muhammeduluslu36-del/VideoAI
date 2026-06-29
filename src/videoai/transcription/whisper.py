from dataclasses import dataclass, field
from pathlib import Path

from faster_whisper import WhisperModel

from videoai.config import settings


@dataclass
class Segment:
    start: float
    end: float
    text: str


@dataclass
class TranscriptionResult:
    segments: list[Segment] = field(default_factory=list)
    language: str = ""
    language_probability: float = 0.0

    @property
    def full_text(self) -> str:
        return " ".join(s.text.strip() for s in self.segments)

    def to_srt(self) -> str:
        lines = []
        for i, seg in enumerate(self.segments, 1):
            start = _format_timestamp(seg.start)
            end = _format_timestamp(seg.end)
            lines.append(f"{i}\n{start} --> {end}\n{seg.text.strip()}\n")
        return "\n".join(lines)

    def to_vtt(self) -> str:
        lines = ["WEBVTT\n"]
        for seg in self.segments:
            start = _format_timestamp(seg.start, vtt=True)
            end = _format_timestamp(seg.end, vtt=True)
            lines.append(f"{start} --> {end}\n{seg.text.strip()}\n")
        return "\n".join(lines)


def _format_timestamp(seconds: float, vtt: bool = False) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    sep = "." if vtt else ","
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


class WhisperTranscriber:
    def __init__(self) -> None:
        self._model: WhisperModel | None = None

    def _load(self) -> WhisperModel:
        if self._model is None:
            self._model = WhisperModel(
                settings.whisper_model,
                device=settings.whisper_device,
                compute_type="auto",
            )
        return self._model

    def transcribe(self, audio_path: Path | str, language: str | None = None) -> TranscriptionResult:
        model = self._load()
        segments_gen, info = model.transcribe(
            str(audio_path),
            language=language,
            word_timestamps=False,
        )
        segments = [Segment(s.start, s.end, s.text) for s in segments_gen]
        return TranscriptionResult(
            segments=segments,
            language=info.language,
            language_probability=info.language_probability,
        )

    def transcribe_and_save(
        self, audio_path: Path | str, output_dir: Path | None = None, fmt: str = "srt"
    ) -> Path:
        result = self.transcribe(audio_path)
        audio_path = Path(audio_path)
        out_dir = output_dir or settings.data_output_dir
        out_path = out_dir / f"{audio_path.stem}.{fmt}"

        content = result.to_srt() if fmt == "srt" else result.to_vtt()
        out_path.write_text(content, encoding="utf-8")
        return out_path
