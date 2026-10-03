import os

import configcatclient
from configcatclient.user import User
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI(title="Task Manager API")
templates = Jinja2Templates(directory="templates")

CONFIGCAT_KEY = os.getenv("CONFIGCAT_SDK_KEY", "")
client = configcatclient.get(CONFIGCAT_KEY) if CONFIGCAT_KEY else None


def is_tags_enabled(user_id: str | None = None) -> bool:
    if not client:
        return False
    user = User(identifier=user_id) if user_id else None
    return client.get_value("tags_enabled", False, user)


# Base de datos en memoria con etiquetas semilla
tags_db = [
    {"id": 1, "name": "Bug", "color": "#dc3545"},
    {"id": 2, "name": "Feature", "color": "#28a745"},
    {"id": 3, "name": "Urgente", "color": "#ffc107"},
]
tasks_db = [
    {"id": 1, "title": "Aprender CI/CD", "tags": []},
    {"id": 2, "title": "Configurar Render", "tags": []},
]


class TaskCreate(BaseModel):
    title: str


class TagCreate(BaseModel):
    name: str
    color: str = "#007bff"


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request, user_id: str = "user-123"):
    # Evalúa si este usuario en particular cae en el 10%
    has_tags = is_tags_enabled(user_id)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user_id": user_id,
            "tags_enabled": has_tags,
        },
    )


@app.get("/api/tasks")
def get_tasks():
    return tasks_db


@app.post("/api/tasks")
def create_task(task: TaskCreate):
    new_task = {"id": len(tasks_db) + 1, "title": task.title, "tags": []}
    tasks_db.append(new_task)
    return new_task


@app.get("/api/tags")
def get_tags(user_id: str | None = None):
    if not is_tags_enabled(user_id):
        raise HTTPException(status_code=404, detail="Feature tags_enabled is disabled")
    return tags_db


@app.post("/api/tags")
def create_tag(tag: TagCreate, user_id: str | None = None):
    if not is_tags_enabled(user_id):
        raise HTTPException(status_code=404, detail="Feature tags_enabled is disabled")
    new_tag = {"id": len(tags_db) + 1, "name": tag.name, "color": tag.color}
    tags_db.append(new_tag)
    return new_tag


@app.post("/api/tasks/{task_id}/tags/{tag_id}")
def assign_tag_to_task(task_id: int, tag_id: int, user_id: str | None = None):
    if not is_tags_enabled(user_id):
        raise HTTPException(
            status_code=403, detail="Feature tags_enabled is not active for this user"
        )

    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    tag = next((t for t in tags_db if t["id"] == tag_id), None)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if tag not in task["tags"]:
        task["tags"].append(tag)

    return task