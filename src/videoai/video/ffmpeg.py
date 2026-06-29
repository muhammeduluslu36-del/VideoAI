import subprocess
from dataclasses import dataclass
from pathlib import Path

from videoai.config import settings


@dataclass
class VideoInfo:
    path: Path
    duration: float
    width: int
    height: int
    fps: float
    has_audio: bool


class FFmpegProcessor:
    def probe(self, video_path: Path | str) -> VideoInfo:
        import json

        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_streams", "-show_format", str(video_path),
        ]
        out = subprocess.check_output(cmd)
        data = json.loads(out)

        video_stream = next(s for s in data["streams"] if s["codec_type"] == "video")
        has_audio = any(s["codec_type"] == "audio" for s in data["streams"])
        fps_parts = video_stream.get("r_frame_rate", "30/1").split("/")
        fps = int(fps_parts[0]) / int(fps_parts[1])

        return VideoInfo(
            path=Path(video_path),
            duration=float(data["format"]["duration"]),
            width=int(video_stream["width"]),
            height=int(video_stream["height"]),
            fps=fps,
            has_audio=has_audio,
        )

    def extract_audio(self, video_path: Path | str, output_path: Path | None = None) -> Path:
        video_path = Path(video_path)
        output_path = output_path or settings.data_temp_dir / f"{video_path.stem}.wav"
        cmd = [
            settings.ffmpeg_path, "-y", "-i", str(video_path),
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            str(output_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def cut(self, video_path: Path | str, start: float, end: float, output_path: Path) -> Path:
        cmd = [
            settings.ffmpeg_path, "-y",
            "-ss", str(start), "-to", str(end),
            "-i", str(video_path),
            "-c", "copy", str(output_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def resize(
        self,
        video_path: Path | str,
        output_path: Path,
        width: int,
        height: int,
    ) -> Path:
        vf = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
        cmd = [
            settings.ffmpeg_path, "-y", "-i", str(video_path),
            "-vf", vf, "-c:a", "copy", str(output_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def to_social_format(
        self,
        video_path: Path | str,
        output_path: Path,
        aspect_ratio: str | None = None,
    ) -> Path:
        ratio = aspect_ratio or settings.clip_aspect_ratio
        w, h = (1080, 1920) if ratio == "9:16" else (1920, 1080)
        return self.resize(video_path, output_path, w, h)
