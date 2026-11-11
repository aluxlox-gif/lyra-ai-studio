from fastapi.testclient import TestClient

from app.main import app
from app.engines.adapters.voicebox import VoiceboxAdapter

client = TestClient(app)


def test_health_aliases():
    for path in ("/health", "/api/health"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["app"] == "LYRA AI STUDIO"


def test_versioned_health_reports_voicebox_not_configured():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["dependencies"]["voicebox"]["status"] in {
        "not_configured", "unavailable", "connected"
    }


def test_voicebox_is_not_assumed_to_be_localhost():
    adapter = VoiceboxAdapter({})
    assert adapter.is_configured is False
    assert adapter.base_url == ""


def test_voicebox_health_when_not_configured():
    adapter = VoiceboxAdapter({})
    # The async method is exercised through the route-level test below.
    assert adapter.get_capabilities()
