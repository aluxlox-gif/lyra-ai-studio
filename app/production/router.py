"""Authenticated HTTP endpoints for the production project foundation."""

import hmac
import os

from fastapi import APIRouter, Header, HTTPException, status

from app.production.schemas import ProjectCreate, ProjectRead, ProductionHealth
from app.production.store import store

router = APIRouter(prefix="/api/production", tags=["production"])


def _authorize(token: str | None) -> None:
    expected = os.getenv("LYRA_PRODUCTION_API_TOKEN", "")
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="production_api_token_not_configured",
        )
    if not token or not hmac.compare_digest(token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_or_missing_production_token",
        )


@router.get("/health", response_model=ProductionHealth)
async def production_health():
    return ProductionHealth(
        status="ready",
        storage="sqlite",
        worker_enabled=False,
        implemented_capabilities=["project_persistence", "production_contracts"],
    )


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    x_lyra_production_token: str | None = Header(default=None),
):
    _authorize(x_lyra_production_token)
    return store.create_project(payload)


@router.get("/projects/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: str,
    x_lyra_production_token: str | None = Header(default=None),
):
    _authorize(x_lyra_production_token)
    project = store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="production_project_not_found")
    return project
