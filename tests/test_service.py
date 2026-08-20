import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from app.service import complete_task, list_tasks
from app.store import load_tasks


class ListTasksTests(unittest.TestCase):
    def test_filters_tasks_by_requested_status(self) -> None:
        tasks = [
            {"id": 1, "status": "open"},
            {"id": 2, "status": "done"},
            {"id": 3, "status": "open"},
        ]

        with patch("app.service.load_tasks", return_value=tasks):
            result = list_tasks(status="open")

        self.assertEqual([task["id"] for task in result], [1, 3])

    def test_searches_task_titles_case_insensitively(self) -> None:
        tasks = [
            {"id": 1, "title": "Write launch recap", "description": "Summary", "status": "open"},
            {"id": 2, "title": "Plan workshop", "description": "Agenda", "status": "open"},
        ]

        with patch("app.service.load_tasks", return_value=tasks):
            result = list_tasks(q="LAUNCH")

        self.assertEqual([task["id"] for task in result], [1])

    def test_searches_task_descriptions_case_insensitively(self) -> None:
        tasks = [
            {"id": 1, "title": "Write recap", "description": "Product launch summary", "status": "open"},
            {"id": 2, "title": "Plan workshop", "description": "Agenda", "status": "open"},
        ]

        with patch("app.service.load_tasks", return_value=tasks):
            result = list_tasks(q="LAUNCH")

        self.assertEqual([task["id"] for task in result], [1])

    def test_combines_search_with_status_filter(self) -> None:
        tasks = [
            {"id": 1, "title": "Plan workshop", "description": "Agenda", "status": "open"},
            {"id": 2, "title": "Write recap", "description": "Summary", "status": "open"},
            {"id": 3, "title": "Plan launch", "description": "Agenda", "status": "done"},
        ]

        with patch("app.service.load_tasks", return_value=tasks):
            result = list_tasks(status="open", q="PLAN")

        self.assertEqual([task["id"] for task in result], [1])


class CompleteTaskTests(unittest.TestCase):
    def test_persists_completed_task(self) -> None:
        with TemporaryDirectory() as directory:
            data_file = Path(directory) / "tasks.json"
            data_file.write_text(
                json.dumps(
                    [
                        {
                            "id": 1,
                            "status": "open",
                            "completed_at": None,
                        }
                    ]
                ),
                encoding="utf-8",
            )

            with patch("app.store.DATA_FILE", data_file):
                completed_task = complete_task(1)
                stored_task = load_tasks()[0]

        self.assertEqual(completed_task["status"], "done")
        self.assertEqual(stored_task["status"], "done")
        self.assertIsNotNone(stored_task["completed_at"])
