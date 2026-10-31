from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware

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


def test_cors_has_no_wildcard_origin():
    cors = next(
        middleware
        for middleware in app.user_middleware
        if middleware.cls is CORSMiddleware
    )

    assert "*" not in cors.kwargs["allow_origins"]


def test_cors_allowed_methods_and_headers():
    cors = next(
        middleware
        for middleware in app.user_middleware
        if middleware.cls is CORSMiddleware
    )

    assert cors.kwargs["allow_methods"] == [
        "GET", "POST", "OPTIONS"
    ]

    assert cors.kwargs["allow_headers"] == [
        "Authorization", "Content-Type"
    ]
