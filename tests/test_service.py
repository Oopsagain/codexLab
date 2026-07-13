import unittest
from unittest.mock import patch

from app import service


class ListTasksTests(unittest.TestCase):
    def test_filters_tasks_by_status(self) -> None:
        fake_tasks = [
            {"id": 1, "title": "Open task", "status": "open"},
            {"id": 2, "title": "Done task", "status": "done"},
        ]

        with patch("app.service.load_tasks", return_value=fake_tasks):
            result = service.list_tasks(status="open")

        self.assertEqual(result, [fake_tasks[0]])

    def test_filters_tasks_by_query_case_insensitively(self) -> None:
        fake_tasks = [
            {"id": 1, "title": "Launch recap", "description": "", "status": "open"},
            {"id": 2, "title": "Fix login", "description": "Handle launch bug", "status": "done"},
            {"id": 3, "title": "Plan workshop", "description": "Discuss launch timeline", "status": "open"},
        ]

        with patch("app.service.load_tasks", return_value=fake_tasks):
            result = service.list_tasks(q="LAUNCH")

        self.assertEqual(result, [fake_tasks[0], fake_tasks[1], fake_tasks[2]])

    def test_filters_tasks_by_status_and_query_together(self) -> None:
        fake_tasks = [
            {"id": 1, "title": "Launch recap", "description": "", "status": "open"},
            {"id": 2, "title": "Plan workshop", "description": "Prepare launch materials", "status": "done"},
            {"id": 3, "title": "Plan workshop", "description": "Prepare launch materials", "status": "open"},
        ]

        with patch("app.service.load_tasks", return_value=fake_tasks):
            result = service.list_tasks(status="open", q="plan")

        self.assertEqual(result, [fake_tasks[2]])


if __name__ == "__main__":
    unittest.main()
