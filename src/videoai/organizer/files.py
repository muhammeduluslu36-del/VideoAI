import shutil
from pathlib import Path


VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".aac", ".m4a", ".flac"}
SUBTITLE_EXTENSIONS = {".srt", ".vtt", ".ass"}


class FileOrganizer:
    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)

    def organize(self, source_dir: Path | str) -> dict[str, list[Path]]:
        source = Path(source_dir)
        moved: dict[str, list[Path]] = {"videos": [], "audio": [], "subtitles": [], "other": []}

        for file in source.rglob("*"):
            if not file.is_file():
                continue
            ext = file.suffix.lower()
            if ext in VIDEO_EXTENSIONS:
                dest = self.root / "videos" / file.name
                category = "videos"
            elif ext in AUDIO_EXTENSIONS:
                dest = self.root / "audio" / file.name
                category = "audio"
            elif ext in SUBTITLE_EXTENSIONS:
                dest = self.root / "subtitles" / file.name
                category = "subtitles"
            else:
                dest = self.root / "other" / file.name
                category = "other"

            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), dest)
            moved[category].append(dest)

        return moved

    def group_by_project(self, clips: list[Path], project_name: str) -> Path:
        project_dir = self.root / "projects" / project_name
        for subdir in ["raw", "clips", "subtitles", "exports"]:
            (project_dir / subdir).mkdir(parents=True, exist_ok=True)

        for clip in clips:
            dest = project_dir / "clips" / clip.name
            shutil.copy2(clip, dest)

        return project_dir

    def cleanup_temp(self, temp_dir: Path | None = None) -> int:
        from videoai.config import settings
        target = temp_dir or settings.data_temp_dir
        count = 0
        for f in target.iterdir():
            if f.is_file():
                f.unlink()
                count += 1
        return count
