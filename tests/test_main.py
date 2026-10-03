from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

import src.main as main_mod
from src.main import app, is_tags_enabled

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


def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "Tablero de Tareas" in response.text


def test_is_tags_enabled_with_client():
    mock_client = MagicMock()
    mock_client.get_value.return_value = True
    original_client = main_mod.client
    try:
        main_mod.client = mock_client
        assert is_tags_enabled("test-user") is True
        mock_client.get_value.assert_called_once()
    finally:
        main_mod.client = original_client