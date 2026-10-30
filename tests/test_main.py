
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ping():
    response = client.get("/api/ping")

    assert response.status_code == 200
    assert "online" in response.json()["message"]


def test_info():
    response = client.get("/api/info")

    assert response.status_code == 200
    assert response.json()["name"] == "LYRA AI STUDIO"


def test_engines():
    response = client.get("/api/engines")

    assert response.status_code == 200

    data = response.json()

    assert "image" in data
    assert "video" in data
    assert "voice" in data


def test_status():
    response = client.get("/api/status")

    assert response.status_code == 200
    assert response.json()["backend"] == "online"


def test_root():
    response = client.get("/")

    assert response.status_code == 200
  
