from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_hermes_adapter_import():
    from app.engines.adapters.hermes import HermesAdapter

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
