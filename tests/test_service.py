from datetime import datetime
from typing import Any
from unittest.mock import Mock

from app import service


def make_task(
    task_id: int,
    title: str,
    description: str,
    status: str = "open",
) -> dict[str, Any]:
    return {
        "id": task_id,
        "title": title,
        "description": description,
        "status": status,
        "priority": "medium",
        "created_at": "2026-01-01T00:00:00+00:00",
        "completed_at": None,
    }


def test_list_tasks_filters_by_status_and_search(monkeypatch) -> None:
    tasks = [
        make_task(1, "Write launch recap", "Product launch summary"),
        make_task(2, "Fix login redirect", "OAuth callback", status="done"),
        make_task(3, "Plan workshop agenda", "Partner onboarding session"),
    ]
    monkeypatch.setattr(service, "load_tasks", lambda: tasks)

    assert [task["id"] for task in service.list_tasks(status="open")] == [1, 3]
    assert [task["id"] for task in service.list_tasks(q="LAUNCH")] == [1]
    assert [task["id"] for task in service.list_tasks(status="open", q="plan")] == [3]


def test_complete_task_persists_updated_task(monkeypatch) -> None:
    tasks = [make_task(1, "Write launch recap", "Product launch summary")]
    save_tasks = Mock()
    monkeypatch.setattr(service, "load_tasks", lambda: tasks)
    monkeypatch.setattr(service, "save_tasks", save_tasks)

    completed_task = service.complete_task(1)

    assert completed_task is tasks[0]
    assert completed_task["status"] == "done"
    assert datetime.fromisoformat(completed_task["completed_at"]) is not None
    save_tasks.assert_called_once_with(tasks)
