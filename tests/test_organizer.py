import shutil
from pathlib import Path

import pytest

from videoai.organizer.files import FileOrganizer


@pytest.fixture
def tmp_dirs(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    root = tmp_path / "organized"
    root.mkdir()
    return source, root


def test_organize_video(tmp_dirs):
    source, root = tmp_dirs
    (source / "clip.mp4").touch()
    (source / "notes.txt").touch()

    organizer = FileOrganizer(root)
    moved = organizer.organize(source)

    assert len(moved["videos"]) == 1
    assert len(moved["other"]) == 1
    assert (root / "videos" / "clip.mp4").exists()
