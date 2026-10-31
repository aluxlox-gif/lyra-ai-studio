
import os
import secrets
from pathlib import Path
from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

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


class HermesMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=12000)


class HermesChatRequest(BaseModel):
    messages: list[HermesMessage] = Field(min_length=1, max_length=40)


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Unified AI Studio API"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
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


@app.post("/api/agents/hermes/chat")
async def hermes_chat(
    payload: HermesChatRequest,
    authorization: str | None = Header(default=None)
):
    expected_token = os.getenv("LYRA_HERMES_BRIDGE_TOKEN", "")

    if not expected_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="bridge_not_configured"
        )

    scheme, separator, supplied_token = (authorization or "").partition(" ")

    if (
        not separator
        or scheme.lower() != "bearer"
        or not supplied_token
        or not secrets.compare_digest(supplied_token, expected_token)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_or_missing_bridge_token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    messages = [
        message.model_dump() if hasattr(message, "model_dump") else message.dict()
        for message in payload.messages
    ]

    result = await HermesAdapter().chat(messages)

    if result.get("status") == "configuration_required":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="hermes_not_configured"
        )

    if result.get("status") in {
        "unreachable",
        "upstream_error",
        "invalid_response"
    }:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=result.get("status")
        )

    return result


@app.get("/api/status")
async def status_endpoint():
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
    
