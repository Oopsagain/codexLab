from datetime import datetime, timezone
from app import store

def get_tasks(status: str | None = None, q: str | None = None):
    tasks = store.load_tasks()

    if status:
        tasks = [t for t in tasks if t.get("status") == status]

    if q:
        query = q.lower()
        tasks = [
            t for t in tasks
            if query in t.get("title", "").lower() 
            or query in t.get("description", "").lower()
        ]

    return tasks

def get_task(task_id: int):
    tasks = store.load_tasks()
    for task in tasks:
        if task.get("id") == task_id:
            return task
    return None

def complete_task(task_id: int):
    tasks = store.load_tasks()
    for task in tasks:
        if task.get("id") == task_id:
            task["status"] = "done"
            task["completed_at"] = datetime.now(timezone.utc).isoformat()
            store.save_tasks(tasks)
            return task
    return None
