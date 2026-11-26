"""Structured story review contracts."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StorySceneBeat(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scene_number: int = Field(ge=1, le=200)
    beat_type: Literal[
        "hook", "setup", "inciting_incident", "escalation", "midpoint",
        "reversal", "climax", "payoff", "cliffhanger", "other"
    ] = "other"
    title: str = Field(min_length=1, max_length=160)
    visual_action: str = Field(default="", max_length=2000)
    dramatic_question: str = Field(default="", max_length=500)
    turning_point: bool = False
    payoff: str = Field(default="", max_length=1000)
    estimated_duration_seconds: int = Field(default=8, ge=1, le=300)


class StoryReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    logline: str = Field(min_length=10, max_length=500)
    premise: str = Field(min_length=20, max_length=4000)
    protagonist_goal: str = Field(min_length=5, max_length=1000)
    stakes: str = Field(min_length=5, max_length=1000)
    central_conflict: str = Field(min_length=5, max_length=1500)
    scenes: list[StorySceneBeat] = Field(min_length=1, max_length=100)


class StoryDimensionScore(BaseModel):
    score: int = Field(ge=0, le=100)
    rationale: str


class StoryReviewResponse(BaseModel):
    evaluation_mode: Literal["deterministic_heuristic"] = "deterministic_heuristic"
    overall_score: int = Field(ge=0, le=100)
    rating: Literal["weak", "developing", "promising", "strong"]
    dimensions: dict[str, StoryDimensionScore]
    issues: list[str]
    suggestions: list[str]
    scene_count: int
    estimated_duration_seconds: int
