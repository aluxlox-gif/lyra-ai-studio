
import os
from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.engines.registry import get_engine_status
from app.engines.adapters.hermes import HermesAdapter

APP_NAME = "LYRA AI STUDIO"
APP_VERSION = "1.0.0"

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

VOICEBOX_BASE_URL = os.getenv(
    "VOICEBOX_BASE_URL",
    "http://127.0.0.1:17493"
).rstrip("/")

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Unified AI Studio API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    index_file = FRONTEND_DIR / "index.html"

    if index_file.exists():
        return FileResponse(index_file)

    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "status": "running"
    }


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "app": APP_NAME,
        "version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/ping")
async def ping():
    return {"message": "LYRA AI STUDIO is online"}


@app.get("/api/info")
async def info():
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "environment": os.getenv("APP_ENV", "development")
    }


@app.get("/api/engines")
async def engines():
    return get_engine_status()


@app.get("/api/engines/status")
async def engine_status():
    return get_engine_status()


@app.get("/api/engines/voicebox/health")
async def voicebox_health():
    import httpx

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{VOICEBOX_BASE_URL}/health"
            )

        return {
            "engine": "voicebox",
            "connected": response.is_success,
            "status_code": response.status_code
        }

    except httpx.HTTPError:
        return {
            "engine": "voicebox",
            "connected": False,
            "message": "Voicebox is unreachable"
        }
        
@app.get("/api/agents/hermes/health")
async def hermes_health():
    adapter = HermesAdapter()
    return await adapter.health_check()

@app.get("/api/status")
async def status():
    return {
        "backend": "online",
        "engines": get_engine_status()
    }


if FRONTEND_DIR.exists():
    app.mount(
        "/",
        StaticFiles(directory=FRONTEND_DIR, html=True),
        name="frontend"
    )
    
