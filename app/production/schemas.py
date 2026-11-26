"""Typed API contracts for cinematic production projects."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=4000)
    language: str = Field(default="id", min_length=2, max_length=12)
    aspect_ratio: Literal["16:9", "9:16", "1:1", "4:3", "3:4"] = "16:9"
    visual_style: str = Field(default="cinematic", min_length=1, max_length=80)
    target_duration_seconds: int = Field(default=60, ge=5, le=3600)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProjectRead(BaseModel):
    id: str
    title: str
    description: str
    language: str
    aspect_ratio: str
    visual_style: str
    target_duration_seconds: int
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ProductionHealth(BaseModel):
    status: Literal["ready"]
    storage: Literal["sqlite"]
    worker_enabled: Literal[False] = False
    implemented_capabilities: list[str]
