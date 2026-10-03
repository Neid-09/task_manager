from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_tasks():
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert len(response.json()) >= 2

def test_tags_disabled_by_default():
    response = client.get("/api/tags")
    assert response.status_code == 404