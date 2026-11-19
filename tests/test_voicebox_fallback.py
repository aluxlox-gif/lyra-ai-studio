import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("edge_tts")

from fastapi.testclient import TestClient

SERVICE_MAIN = (
    Path(__file__).resolve().parent.parent
    / "services"
    / "voicebox_fallback"
    / "main.py"
)

spec = importlib.util.spec_from_file_location(
    "voicebox_fallback_main", SERVICE_MAIN
)
fallback = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fallback)

client = TestClient(fallback.app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_profiles_include_indonesian_voices():
    response = client.get("/profiles")
    assert response.status_code == 200
    ids = {profile["id"] for profile in response.json()}
    assert {"id-gadis", "id-ardi", "en-aria", "en-guy"} <= ids


def test_resolve_voice_mapping():
    assert fallback.resolve_voice("id-ardi", "id") == "id-ID-ArdiNeural"
    assert (
        fallback.resolve_voice("id-ID-GadisNeural", "id")
        == "id-ID-GadisNeural"
    )
    # Unknown (e.g. real Voicebox) profile ids fall back by language
    assert fallback.resolve_voice("some-voicebox-uuid", "en") == (
        "en-US-AriaNeural"
    )
    assert fallback.resolve_voice(None, "id") == "id-ID-GadisNeural"


def test_generate_returns_audio(monkeypatch):
    async def fake_synthesize(text, voice):
        assert text == "Halo LYRA"
        assert voice == "id-ID-GadisNeural"
        return b"fake-mp3-bytes"

    monkeypatch.setattr(fallback, "synthesize", fake_synthesize)
    response = client.post(
        "/generate",
        json={"text": "Halo LYRA", "profile_id": "id-gadis"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert response.content == b"fake-mp3-bytes"


def test_generate_rejects_empty_text():
    response = client.post("/generate", json={"text": ""})
    assert response.status_code == 422
