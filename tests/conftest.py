from pathlib import Path

import pytest

from app import store


@pytest.fixture(autouse=True)
def isolated_data_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Give every test a fresh copy of the task data."""
    source = store.DATA_FILE
    destination = tmp_path / "tasks.json"
    destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(store, "DATA_FILE", destination)
    return destination
