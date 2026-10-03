# Crear src/main.py
import os

import configcatclient
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI(title="Task Manager API")
templates = Jinja2Templates(directory="templates")

# ConfigCat Client (Usa SDK Key de entorno o modo local si no hay key)
CONFIGCAT_KEY = os.getenv("CONFIGCAT_SDK_KEY", "")
client = configcatclient.get(CONFIGCAT_KEY) if CONFIGCAT_KEY else None

def is_tags_enabled(user_id: str | None = None) -> bool:
    if not client:
        return False
    user = configcatclient.User(identifier=user_id) if user_id else None
    return client.get_value("tags_enabled", False, user)

# Modelos en memoria
tasks_db = [
    {"id": 1, "title": "Aprender CI/CD", "tags": []},
    {"id": 2, "title": "Configurar Render", "tags": []}
]
tags_db = []

class TaskCreate(BaseModel):
    title: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/tasks")
def get_tasks():
    return tasks_db

@app.post("/api/tasks")
def create_task(task: TaskCreate):
    new_task = {"id": len(tasks_db) + 1, "title": task.title, "tags": []}
    tasks_db.append(new_task)
    return new_task

class TagCreate(BaseModel):
    name: str
    color: str = "#007bff"

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