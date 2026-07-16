import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def task_ids(response) -> list[int]:
    assert response.status_code == 200
    return [task["id"] for task in response.json()]


def test_list_tasks_without_filters_returns_every_task() -> None:
    assert task_ids(client.get("/tasks")) == [1, 2, 3, 4]


def test_list_tasks_filters_by_status() -> None:
    assert task_ids(client.get("/tasks", params={"status": "open"})) == [1, 3, 4]
    assert task_ids(client.get("/tasks", params={"status": "done"})) == [2]


def test_list_tasks_searches_title_and_description_case_insensitively() -> None:
    assert task_ids(client.get("/tasks", params={"q": "LAUNCH"})) == [1]
    assert task_ids(client.get("/tasks", params={"q": "shared archive"})) == [4]


def test_list_tasks_combines_status_and_search() -> None:
    response = client.get("/tasks", params={"status": "open", "q": "plan"})
    assert task_ids(response) == [3]


def test_complete_task_persists_done_state(isolated_data_file: Path) -> None:
    complete_response = client.post("/tasks/3/complete")
    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "done"
    assert complete_response.json()["completed_at"] is not None

    stored_tasks = json.loads(isolated_data_file.read_text(encoding="utf-8"))
    stored_task = next(task for task in stored_tasks if task["id"] == 3)
    assert stored_task["status"] == "done"
    assert stored_task["completed_at"] is not None

    refreshed_response = client.get("/tasks/3")
    assert refreshed_response.status_code == 200
    assert refreshed_response.json()["status"] == "done"
    assert refreshed_response.json()["completed_at"] is not None


def test_complete_missing_task_returns_not_found() -> None:
    response = client.post("/tasks/999/complete")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}
