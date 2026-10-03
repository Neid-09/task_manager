from unittest.mock import patch

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
@patch("src.main.is_tags_enabled")
def test_assign_tag_when_flag_enabled(mock_is_enabled):
    mock_is_enabled.return_value = True
    # Asignar tag 1 a tarea 1
    response = client.post("/api/tasks/1/tags/1?user_id=beta-user")
    assert response.status_code == 200
    assert any(t["id"] == 1 for t in response.json()["tags"])
@patch("src.main.is_tags_enabled")
def test_assign_tag_when_flag_disabled(mock_is_enabled):
    mock_is_enabled.return_value = False
    response = client.post("/api/tasks/1/tags/1?user_id=regular-user")
    assert response.status_code == 403