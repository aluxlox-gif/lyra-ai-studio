"""
Hermes Agent adapter for LYRA AI STUDIO.
"""

import os
from typing import Any

import httpx

from app.engines.adapters.base import BaseEngineAdapter


class HermesAdapter(BaseEngineAdapter):
    engine_id = "hermes"
    engine_name = "Hermes Agent"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)

        self.base_url = self.config.get(
            "base_url",
            os.getenv("HERMES_BASE_URL", "")
        ).rstrip("/")

        self.api_key = self.config.get(
            "api_key",
            os.getenv("HERMES_API_KEY", "")
        )

        self.health_path = self.config.get(
            "health_path",
            os.getenv("HERMES_HEALTH_PATH", "/health")
        )

        self.timeout = float(
            self.config.get("timeout", 10.0)
        )

    def get_capabilities(self) -> list[str]:
        return [
            "agent_chat",
            "memory",
            "skills",
            "tool_integration"
        ]

    def get_info(self) -> dict[str, Any]:
        info = super().get_info()
        info["configured"] = bool(self.base_url)
        return info

    async def health_check(self) -> dict[str, Any]:
        if not self.base_url:
            return {
                "engine": self.engine_id,
                "connected": False,
                "status": "configuration_required"
            }

        headers = {}

        if self.api_key:
            headers["Authorization"] = (
                f"Bearer {self.api_key}"
            )

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:
                response = await client.get(
                    f"{self.base_url}{self.health_path}",
                    headers=headers
                )

            return {
                "engine": self.engine_id,
                "connected": response.is_success,
                "status_code": response.status_code
            }

        except httpx.HTTPError as exc:
            return {
                "engine": self.engine_id,
                "connected": False,
                "error": str(exc)
            }
