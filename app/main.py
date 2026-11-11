import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.config import Settings, get_settings
from app.engines.adapters.voicebox import (
    VoiceboxAdapter,
    VoiceboxNotConfiguredError,
)
from app.engines.registry import get_engine_status

APP_NAME = "LYRA AI STUDIO"
APP_VERSION = "1.0.1"

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


def get_voicebox_adapter(
    settings: Settings = Depends(get_settings),
) -> VoiceboxAdapter:
    return VoiceboxAdapter(
        {
            "base_url": settings.voicebox_base_url,
            "api_key": settings.voicebox_api_key,
            "api_key_header": settings.voicebox_api_key_header,
            "timeout": settings.voicebox_timeout,
        }
    )


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Unified AI Studio API",
)

settings_at_startup = get_settings()
if settings_at_startup.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings_at_startup.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-API-Key"],
    )


class VoiceGenerateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
    profile_id: str | None = Field(default=None, min_length=1, max_length=128)
    language: str = Field(default="id", min_length=2, max_length=16)


@app.get("/")
async def root():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)

    return {"app": APP_NAME, "version": APP_VERSION, "status": "running"}


@app.get("/health")
@app.get("/api/health")
async def health():
    timestamp = datetime.now(timezone.utc).isoformat()
    return {
        "status": "healthy",
        "app": APP_NAME,
        "application": APP_NAME,
        "version": APP_VERSION,
        "timestamp": timestamp,
    }


@app.get("/api/v1/health")
async def versioned_health(
    adapter: VoiceboxAdapter = Depends(get_voicebox_adapter),
):
    voicebox_status = await adapter.health_check()
    return {
        "status": "healthy",
        "app": APP_NAME,
        "version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dependencies": {"voicebox": voicebox_status},
    }


@app.get("/api/ping")
async def ping():
    return {"message": "LYRA AI STUDIO is online"}


@app.get("/api/info")
async def info(settings: Settings = Depends(get_settings)):
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "environment": settings.app_env,
    }


@app.get("/api/engines")
async def engines(settings: Settings = Depends(get_settings)):
    return get_engine_status(voicebox_configured=bool(settings.voicebox_base_url))


@app.get("/api/engines/status")
async def engine_status(settings: Settings = Depends(get_settings)):
    return get_engine_status(voicebox_configured=bool(settings.voicebox_base_url))


@app.get("/api/engines/voicebox/health")
async def voicebox_health(
    adapter: VoiceboxAdapter = Depends(get_voicebox_adapter),
):
    return await adapter.health_check()


@app.get("/api/voice/profiles")
async def voice_profiles(
    adapter: VoiceboxAdapter = Depends(get_voicebox_adapter),
):
    try:
        return await adapter.list_profiles()
    except VoiceboxNotConfiguredError:
        raise HTTPException(status_code=503, detail="Voicebox belum dikonfigurasi.")
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Tidak dapat mengambil profil Voicebox.")


@app.post("/api/voice/generate")
async def generate_voice(
    payload: VoiceGenerateRequest,
    adapter: VoiceboxAdapter = Depends(get_voicebox_adapter),
    settings: Settings = Depends(get_settings),
):
    profile_id = payload.profile_id or settings.voicebox_default_profile_id
    if not profile_id:
        raise HTTPException(
            status_code=422,
            detail="profile_id wajib diisi atau atur VOICEBOX_DEFAULT_PROFILE_ID.",
        )

    try:
        audio, content_type = await adapter.generate_speech(
            text=payload.text,
            profile_id=profile_id,
            language=payload.language,
        )
    except VoiceboxNotConfiguredError:
        raise HTTPException(status_code=503, detail="Voicebox belum dikonfigurasi.")
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Voicebox gagal memproses permintaan audio.")
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return Response(
        content=audio,
        media_type=content_type,
        headers={"Content-Disposition": 'inline; filename="lyra-voice-output"'},
    )


@app.get("/api/status")
async def status(settings: Settings = Depends(get_settings)):
    return {
        "backend": "online",
        "engines": get_engine_status(
            voicebox_configured=bool(settings.voicebox_base_url)
        ),
    }


if FRONTEND_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=FRONTEND_DIR),
        name="static",
    )
