"""PWA, offline shell and settings view checks."""

import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_manifest_is_served_and_installable():
    response = client.get("/manifest.webmanifest")
    assert response.status_code == 200
    manifest = json.loads(response.text)
    assert manifest["name"] == "LYRA AI STUDIO"
    assert manifest["display"] == "standalone"
    assert manifest["start_url"] == "/"
    assert manifest["icons"]


def test_service_worker_is_served():
    response = client.get("/sw.js")
    assert response.status_code == 200
    assert "lyra-shell" in response.text
    assert "/api/" in response.text  # API traffic is never SW-cached


def test_icon_is_served():
    response = client.get("/icons/icon.svg")
    assert response.status_code == 200
    assert "<svg" in response.text


def test_index_links_manifest_and_has_settings_view():
    response = client.get("/")
    assert response.status_code == 200
    assert 'rel="manifest"' in response.text
    assert 'data-view="settings"' in response.text
    assert 'id="settings-form"' in response.text


def test_app_js_registers_service_worker_and_settings():
    response = client.get("/app.js")
    assert response.status_code == 200
    assert "serviceWorker" in response.text
    assert "lyra.settings" in response.text
    assert "lyra.cache.engines" in response.text
