import os
import sys

# Add parent directory to path so 'api' package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from api.main import app
from fastapi.testclient import TestClient


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


def test_favicon_served(client):
    response = client.get("/favicon.png")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 0


def test_sitemap_served(client):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")
    assert "sasyakashi.vercel.app" in response.text
    assert "<url>" in response.text


def test_unknown_page_returns_branded_html_404(client):
    response = client.get("/contact")
    assert response.status_code == 404
    assert "text/html" in response.headers["content-type"]
    assert "Gardenify" in response.text


def test_unknown_api_path_returns_json_404(client):
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"detail": "Not found"}
