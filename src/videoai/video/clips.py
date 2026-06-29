from dataclasses import dataclass
from pathlib import Path

from videoai.config import settings
from videoai.video.ffmpeg import FFmpegProcessor


@dataclass
class ClipSpec:
    start: float
    end: float
    title: str = ""
    score: float = 0.0

    @property
    def duration(self) -> float:
        return self.end - self.start


class ClipGenerator:
    def __init__(self) -> None:
        self.ffmpeg = FFmpegProcessor()

    def generate(
        self,
        video_path: Path | str,
        clips: list[ClipSpec],
        output_dir: Path | None = None,
        social_format: bool = True,
    ) -> list[Path]:
        video_path = Path(video_path)
        out_dir = output_dir or settings.data_output_dir / "clips"
        out_dir.mkdir(parents=True, exist_ok=True)

        results = []
        for i, clip in enumerate(clips):
            stem = clip.title or f"clip_{i+1:03d}"
            raw = settings.data_temp_dir / f"{stem}_raw.mp4"
            self.ffmpeg.cut(video_path, clip.start, clip.end, raw)

            if social_format:
                final = out_dir / f"{stem}.mp4"
                self.ffmpeg.to_social_format(raw, final)
                results.append(final)
            else:
                final = out_dir / f"{stem}.mp4"
                raw.rename(final)
                results.append(final)

        return results

    def from_highlights(
        self,
        video_path: Path | str,
        timestamps: list[dict],
        max_duration: int | None = None,
        **kwargs,
    ) -> list[Path]:
        max_dur = max_duration or settings.clip_max_duration
        clips = [
            ClipSpec(
                start=t["start"],
                end=min(t["end"], t["start"] + max_dur),
                title=t.get("title", ""),
                score=t.get("score", 0.0),
            )
            for t in timestamps
        ]
        clips.sort(key=lambda c: c.score, reverse=True)
        return self.generate(video_path, clips, **kwargs)
