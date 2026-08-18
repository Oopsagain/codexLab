from fastapi import FastAPI
from app import service, schemas

app = FastAPI()

@app.get("/tasks")
def read_tasks(status: str | None = None, q: str | None = None):
    return service.get_tasks(status=status, q=q)

@app.get("/tasks/{task_id}")
def read_task(task_id: int):
    return service.get_task(task_id)

@app.post("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    return service.complete_task(task_id)
