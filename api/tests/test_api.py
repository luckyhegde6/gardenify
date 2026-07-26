import pytest
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_identify_no_images(client):
    response = client.post("/api/identify")
    assert response.status_code == 422  # Validation error


def test_identify_empty_images(client):
    response = client.post("/api/identify", files=[])
    assert response.status_code == 422
