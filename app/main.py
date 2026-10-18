from app.engines.registry import (
    get_engine,
    get_engine_status,
    list_engines,
)
from pathlib import from
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

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


# --------------------------------------------------
# FRONTEND
# --------------------------------------------------

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
        return FileResponse(index_file)

    return {
        "application": APP_NAME,
        "status": "running",
        "message": "Frontend is not configured yet.",
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "success": True,
        "application": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
    }


# --------------------------------------------------
# ENGINE MANAGER API
# --------------------------------------------------

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


@app.get("/api/engines/{engine_id}", tags=["Engines"])
async def api_get_engine(engine_id: str):
    engine = get_engine(engine_id)

    if engine is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail=f"Engine '{engine_id}' tidak ditemukan.",
        )

    return {
        "success": True,
        "engine": engine,
    }


# --------------------------------------------------
# SYSTEM INFORMATION
# --------------------------------------------------

@app.get("/api/info", tags=["System"])
async def application_info():
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "architecture": "modular",
        "engines": ["image", "voice", "video"],
        "integrations": {
            "voicebox": "not_connected",
            "openmontage": "not_connected",
            "image_engine": "not_connected",
        },
    }
