"""
LYRA AI STUDIO
Main FastAPI application.
"""

import os
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.engines.registry import (
    get_engine,
    get_engine_status,
    list_engines,
)
from app.engines.adapters.voicebox import VoiceboxAdapter


# APPLICATION CONFIGURATION

APP_NAME = "LYRA AI STUDIO"
APP_VERSION = "0.1.0"

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

VOICEBOX_URL = os.getenv(
    "VOICEBOX_BASE_URL",
    "http://127.0.0.1:17493",
)

voicebox = VoiceboxAdapter(
    config={
        "base_url": VOICEBOX_URL,
        "timeout": 30,
        "client_id": "lyra-ai-studio",
    }
)

app = FastAPI(
    title=APP_NAME,
    description=(
        "A modular AI production studio for image, "
        "video, and voice workflows."
    ),
    version=APP_VERSION,
)


# FRONTEND

if FRONTEND_DIR.is_dir():
    app.mount(
        "/static",
        StaticFiles(directory=str(FRONTEND_DIR)),
        name="static",
    )


@app.get("/", include_in_schema=False)
async def home():
    index_file = FRONTEND_DIR / "index.html"

    if index_file.is_file():
        return FileResponse(str(index_file))

    return {
        "application": APP_NAME,
        "status": "running",
        "message": "Frontend is not configured yet.",
    }


# SYSTEM HEALTH

@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "success": True,
        "application": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
    }


@app.get("/api/ping", tags=["System"])
async def ping():
    return {
        "success": True,
        "message": "LYRA AI STUDIO API is reachable.",
    }


# APPLICATION INFORMATION

@app.get("/api/info", tags=["System"])
async def application_info():
    return {
        "success": True,
        "application": APP_NAME,
        "version": APP_VERSION,
        "architecture": "modular",
        "integrations": {
            "voicebox": {
                "provider": "Voicebox",
                "status": "integrated",
            },
            "openmontage": {
                "provider": "OpenMontage",
                "status": "planned",
            },
            "image_engine": {
                "provider": None,
                "status": "planned",
            },
        },
    }


# ENGINE MANAGER

@app.get("/api/engines", tags=["Engines"])
async def api_list_engines():
    return {
        "success": True,
        "engines": list_engines(),
    }


@app.get("/api/engines/status", tags=["Engines"])
async def api_engine_status():
    return {
        "success": True,
        "status": get_engine_status(),
    }


# VOICEBOX CONNECTIVITY

@app.get("/api/engines/voice/health", tags=["Voice"])
async def voicebox_health():
    result = await voicebox.health_check()

    return {
        "success": result["connected"],
        "engine": result,
    }


# VOICEBOX PROFILES

@app.get("/api/voice/profiles", tags=["Voice"])
async def voicebox_profiles():
    try:
        profiles = await voicebox.list_profiles()

        return {
            "success": True,
            "profiles": profiles,
        }

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Voicebox tidak dapat dihubungi. "
                "Pastikan Voicebox berjalan dan alamat API benar."
            ),
        ) from exc


# VOICE GENERATION REQUEST

class VoiceGenerationRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=10000,
    )

    profile_id: str = Field(
        min_length=1,
        max_length=200,
    )

    language: str = Field(
        default="en",
        min_length=2,
        max_length=20,
    )


# TEXT TO SPEECH

@app.post("/api/voice/generate", tags=["Voice"])
async def generate_voice(request: VoiceGenerationRequest):
    if not request.text.strip():
        raise HTTPException(
            status_code=422,
            detail="Teks tidak boleh kosong.",
        )

    if not request.profile_id.strip():
        raise HTTPException(
            status_code=422,
            detail="Profile ID tidak boleh kosong.",
        )

    try:
        result = await voicebox.generate_speech(
            text=request.text,
            profile_id=request.profile_id,
            language=request.language,
        )

        return Response(
            content=result["audio"],
            media_type=result["content_type"],
            headers={
                "Content-Disposition": (
                    'inline; filename="lyra-voice-output"'
                ),
                "Cache-Control": "no-store",
            },
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Voicebox gagal menghasilkan audio. "
                "Periksa koneksi dan konfigurasi Voicebox."
            ),
        ) from exc


# ENGINE DETAILS

@app.get("/api/engines/{engine_id}", tags=["Engines"])
async def api_get_engine(engine_id: str):
    engine = get_engine(engine_id)

    if engine is None:
        raise HTTPException(
            status_code=404,
            detail=f"Engine '{engine_id}' tidak ditemukan.",
        )

    return {
        "success": True,
        "engine": engine,
    }


# API STATUS

@app.get("/api/status", tags=["System"])
async def api_status():
    voice_status = await voicebox.health_check()

    return {
        "success": True,
        "application": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "engine_status": get_engine_status(),
        "integrations": {
            "voicebox": voice_status,
        },
    }
