
from fastapi.testclient import TestClient

from app.main import app
from app.engines.adapters.hermes import HermesAdapter

client = TestClient(app)


def test_hermes_adapter_import():
    adapter = HermesAdapter()
    assert adapter.engine_id == "hermes"


def test_hermes_health_requires_configuration(monkeypatch):
    monkeypatch.delenv("HERMES_BASE_URL", raising=False)

    response = client.get("/api/agents/hermes/health")

    assert response.status_code == 200
    data = response.json()
    assert data["engine"] == "hermes"
    assert data["connected"] is False
    assert data["status"] == "configuration_required"


def test_hermes_registered():
    response = client.get("/api/engines")

    assert response.status_code == 200
    data = response.json()
    assert "hermes" in data
    assert data["hermes"]["name"] == "Hermes Agent"


def test_hermes_chat_requires_bridge_configuration(monkeypatch):
    monkeypatch.delenv("LYRA_HERMES_BRIDGE_TOKEN", raising=False)

    response = client.post(
        "/api/agents/hermes/chat",
        json={"messages": [{"role": "user", "content": "Halo"}]}
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "bridge_not_configured"


def test_hermes_chat_rejects_invalid_token(monkeypatch):
    monkeypatch.setenv("LYRA_HERMES_BRIDGE_TOKEN", "correct-token")

    response = client.post(
        "/api/agents/hermes/chat",
        headers={"Authorization": "Bearer wrong-token"},
        json={"messages": [{"role": "user", "content": "Halo"}]}
    )

    assert response.status_code == 401


def test_hermes_chat_validates_messages(monkeypatch):
    monkeypatch.setenv("LYRA_HERMES_BRIDGE_TOKEN", "correct-token")

    response = client.post(
        "/api/agents/hermes/chat",
        headers={"Authorization": "Bearer correct-token"},
        json={"messages": []}
    )

    assert response.status_code == 422


def test_hermes_chat_returns_mocked_reply(monkeypatch):
    monkeypatch.setenv("LYRA_HERMES_BRIDGE_TOKEN", "correct-token")

    async def fake_chat(self, messages):
        assert messages[0]["content"] == "Halo Hermes"
        return {
            "engine": "hermes",
            "connected": True,
            "status": "ok",
            "model": "test-model",
            "reply": "Halo dari Hermes."
        }

    monkeypatch.setattr(HermesAdapter, "chat", fake_chat)

    response = client.post(
        "/api/agents/hermes/chat",
        headers={"Authorization": "Bearer correct-token"},
        json={
            "messages": [
                {"role": "user", "content": "Halo Hermes"}
            ]
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["reply"] == "Halo dari Hermes."
    
