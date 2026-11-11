import asyncio

from fastapi.testclient import TestClient

from app.main import app, get_voicebox_adapter
from app.engines.adapters.voicebox import VoiceboxAdapter

client = TestClient(app)


def test_health_aliases():
    for path in ("/health", "/api/health"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["app"] == "LYRA AI STUDIO"


def test_versioned_health_uses_adapter_dependency():
    class StubVoicebox:
        async def health_check(self):
            return {
                "engine_id": "voice",
                "engine_name": "LYRA VOICEBOX CLOUD",
                "configured": False,
                "connected": False,
                "status": "not_configured",
            }

    app.dependency_overrides[get_voicebox_adapter] = lambda: StubVoicebox()
    try:
        response = client.get("/api/v1/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dependencies"]["voicebox"]["status"] == "not_configured"


def test_voicebox_is_not_assumed_to_be_localhost():
    adapter = VoiceboxAdapter({})
    assert adapter.is_configured is False
    assert adapter.base_url == ""


def test_voicebox_health_when_not_configured():
    adapter = VoiceboxAdapter({})
    result = asyncio.run(adapter.health_check())
    assert result["status"] == "not_configured"
    assert result["connected"] is False


def test_static_assets_are_served_from_static_prefix():
    response = client.get("/static/styles.css")
    assert response.status_code == 200
