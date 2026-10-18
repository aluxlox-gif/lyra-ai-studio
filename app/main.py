"""
LYRA AI STUDIO
Main FastAPI application.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.engines.registry import (
    get_engine,
    get_engine_status,
    list_engines,
)


# APPLICATION CONFIGURATION

APP_NAME = "LYRA AI STUDIO"
APP_VERSION = "0.1.0"

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

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
                "status": "planned",
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


@app.get("/api      },
    }
