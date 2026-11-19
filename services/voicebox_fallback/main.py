"""
Voicebox fallback service for LYRA AI STUDIO.

A drop-in replacement for a Voicebox server. It implements the
exact API surface LYRA's VoiceboxAdapter already expects:

- GET  /health    -> service status
- GET  /profiles  -> available voice profiles
- POST /generate  -> {"text", "profile_id", "language"} in,
                     audio bytes out

Speech synthesis is provided by edge-tts (free Microsoft Edge
neural voices, including Indonesian). Because the contract and
the default port (17493) match Voicebox, LYRA needs no code
change: point VOICEBOX_BASE_URL at this service and set
VOICEBOX_DEFAULT_PROFILE_ID to one of the profiles below.

This is a backup/stand-in engine, not a Voicebox clone: the
voices are Microsoft neural voices, not custom Voicebox voice
profiles, and synthesis needs internet access to Microsoft's
speech service.
"""

import os

import edge_tts
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field


PROFILES: dict[str, dict[str, str]] = {
    "id-gadis": {
        "id": "id-gadis",
        "name": "Gadis - Indonesian (female)",
        "voice": "id-ID-GadisNeural",
        "language": "id",
    },
    "id-ardi": {
        "id": "id-ardi",
        "name": "Ardi - Indonesian (male)",
        "voice": "id-ID-ArdiNeural",
        "language": "id",
    },
    "en-aria": {
        "id": "en-aria",
        "name": "Aria - English US (female)",
        "voice": "en-US-AriaNeural",
        "language": "en",
    },
    "en-guy": {
        "id": "en-guy",
        "name": "Guy - English US (male)",
        "voice": "en-US-GuyNeural",
        "language": "en",
    },
}

DEFAULT_PROFILE_BY_LANGUAGE = {
    "id": "id-gadis",
    "en": "en-aria",
}


def resolve_voice(profile_id: str | None, language: str) -> str:
    """Map a profile id to an edge-tts voice name.

    Known fallback profiles map to their voice. A full edge-tts
    voice name (e.g. "id-ID-GadisNeural") is accepted as-is.
    Anything else (for example a real Voicebox profile id, when
    this service runs as backup) falls back to the default voice
    for the requested language.
    """
    if profile_id:
        profile = PROFILES.get(profile_id)
        if profile:
            return profile["voice"]
        if len(profile_id) >= 6 and profile_id[2] == "-":
            return profile_id

    language_key = (language or "id").split("-")[0].lower()
    default_profile = DEFAULT_PROFILE_BY_LANGUAGE.get(
        language_key, "id-gadis"
    )
    return PROFILES[default_profile]["voice"]


async def synthesize(text: str, voice: str) -> bytes:
    """Synthesize speech with edge-tts and return MP3 bytes.

    Set EDGE_TTS_PROXY (e.g. "http://host:3128") when the host
    reaches the internet through an HTTP proxy; unset means a
    direct connection.
    """
    communicate = edge_tts.Communicate(
        text, voice, proxy=os.getenv("EDGE_TTS_PROXY") or None
    )
    chunks: list[bytes] = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    return b"".join(chunks)


class GenerateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    profile_id: str | None = None
    language: str = Field(default="id", min_length=2, max_length=12)


app = FastAPI(
    title="LYRA Voicebox Fallback",
    version="1.0.0",
    description="Drop-in Voicebox replacement backed by edge-tts",
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "voicebox-fallback"}


@app.get("/profiles")
async def profiles():
    return list(PROFILES.values())


@app.post("/generate")
async def generate(payload: GenerateRequest):
    voice = resolve_voice(payload.profile_id, payload.language)
    try:
        audio = await synthesize(payload.text, voice)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="speech_synthesis_failed",
        ) from exc

    if not audio:
        raise HTTPException(
            status_code=502,
            detail="speech_synthesis_returned_empty_audio",
        )

    return Response(content=audio, media_type="audio/mpeg")
