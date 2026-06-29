import subprocess
from pathlib import Path

from videoai.config import settings
from videoai.transcription.whisper import TranscriptionResult


class SubtitleBurner:
    def burn(
        self,
        video_path: Path | str,
        subtitle_path: Path | str,
        output_path: Path,
        style: str = "default",
    ) -> Path:
        styles = {
            "default": "FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2",
            "social": "FontSize=32,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=3",
        }
        vf = f"subtitles={subtitle_path}:force_style='{styles.get(style, styles['default'])}'"
        cmd = [
            settings.ffmpeg_path, "-y", "-i", str(video_path),
            "-vf", vf, "-c:a", "copy", str(output_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def from_result(
        self,
        video_path: Path | str,
        result: TranscriptionResult,
        output_path: Path,
        fmt: str = "srt",
        style: str = "default",
    ) -> Path:
        video_path = Path(video_path)
        sub_path = settings.data_temp_dir / f"{video_path.stem}_sub.{fmt}"
        content = result.to_srt() if fmt == "srt" else result.to_vtt()
        sub_path.write_text(content, encoding="utf-8")
        return self.burn(video_path, sub_path, output_path, style=style)
