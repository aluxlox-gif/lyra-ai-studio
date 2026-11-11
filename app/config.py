"""Environment-backed configuration for LYRA AI STUDIO."""

import os
from dataclasses import dataclass
from functools import lru_cache


def _csv_values(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_env: str
    voicebox_base_url: str
    voicebox_api_key: str
    voicebox_api_key_header: str
    voicebox_default_profile_id: str
    voicebox_timeout: float
    cors_origins: list[str]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    base_url = os.getenv("VOICEBOX_BASE_URL", "").strip().rstrip("/")
    api_key = os.getenv("VOICEBOX_API_KEY", "").strip()
    api_key_header = os.getenv("VOICEBOX_API_KEY_HEADER", "X-API-Key").strip()
    timeout_raw = os.getenv("VOICEBOX_TIMEOUT", "30").strip()

    try:
        timeout = max(1.0, min(float(timeout_raw), 180.0))
    except ValueError:
        timeout = 30.0

    return Settings(
        app_env=os.getenv("APP_ENV", "development").strip(),
        voicebox_base_url=base_url,
        voicebox_api_key=api_key,
        voicebox_api_key_header=api_key_header or "X-API-Key",
        voicebox_default_profile_id=os.getenv(
            "VOICEBOX_DEFAULT_PROFILE_ID", ""
        ).strip(),
        voicebox_timeout=timeout,
        cors_origins=_csv_values(os.getenv("CORS_ORIGINS", "")),
    )
