import pytest
from pathlib import Path

from app.utils import create_output_directories


def test_create_output_directories(monkeypatch):
    # Mock the Path.exists method to always return False
    monkeypatch.setattr(Path, "exists", lambda x: False)

    # Mock the Path.mkdir method
    monkeypatch.setattr(Path, "mkdir", lambda x, parents=False, exist_ok=False: None)

    # Given
    output_dirs = [Path("/path/to/dir1"), Path("/path/to/dir2")]

    # When
    create_output_directories(output_dirs)

    # Then
    # If the function completes without raising an exception, the test will pass
