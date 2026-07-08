from __future__ import annotations

from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import store
from app.main import app


@pytest.fixture(autouse=True)
def isolated_tasks_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = Path(__file__).resolve().parents[1] / "data" / "tasks.json"
    temp_data_file = tmp_path / "tasks.json"
    temp_data_file.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(store, "DATA_FILE", temp_data_file)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_list_tasks_filters_by_status(client: TestClient) -> None:
    response = client.get("/tasks", params={"status": "open"})

    assert response.status_code == 200
    payload = response.json()
    assert [task["id"] for task in payload] == [1, 3, 4]
    assert all(task["status"] == "open" for task in payload)


def test_list_tasks_filters_by_query_case_insensitive(client: TestClient) -> None:
    title_response = client.get("/tasks", params={"q": "LAUNCH"})
    description_response = client.get("/tasks", params={"q": "oauth"})

    assert title_response.status_code == 200
    assert [task["id"] for task in title_response.json()] == [1]
    assert description_response.status_code == 200
    assert [task["id"] for task in description_response.json()] == [2]


def test_list_tasks_combines_status_and_query(client: TestClient) -> None:
    response = client.get("/tasks", params={"status": "open", "q": "workshop"})

    assert response.status_code == 200
    assert [task["id"] for task in response.json()] == [3]


def test_list_tasks_without_query_preserves_default_behavior(client: TestClient) -> None:
    response = client.get("/tasks")

    assert response.status_code == 200
    assert [task["id"] for task in response.json()] == [1, 2, 3, 4]


def test_complete_task_persists_status(client: TestClient) -> None:
    complete_response = client.post("/tasks/1/complete")
    read_response = client.get("/tasks/1")

    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "done"
    assert read_response.status_code == 200
    assert read_response.json()["status"] == "done"
    assert read_response.json()["completed_at"] is not None
