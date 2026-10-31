
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

        self.model = self.config.get(
            "model",
            os.getenv("HERMES_MODEL", "hermes-agent")
        )

        self.health_path = self.config.get(
            "health_path",
            os.getenv("HERMES_HEALTH_PATH", "/health")
        )

        self.timeout = float(self.config.get("timeout", 30.0))

    def get_capabilities(self) -> list[str]:
        return [
            "agent_chat",
            "memory",
            "skills",
            "tool_integration"
        ]

    def get_info(self) -> dict[str, Any]:
        info = super().get_info()
        info["configured"] = bool(
            self.base_url and self.api_key
        )
        return info

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            return {}
        return {
            "Authorization": f"Bearer {self.api_key}"
        }

    async def health_check(self) -> dict[str, Any]:
        if not self.base_url:
            return {
                "engine": self.engine_id,
                "connected": False,
                "status": "configuration_required"
            }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:
                response = await client.get(
                    f"{self.base_url}{self.health_path}",
                    headers=self._headers()
                )

            return {
                "engine": self.engine_id,
                "connected": response.is_success,
                "status_code": response.status_code
            }

        except httpx.HTTPError:
            return {
                "engine": self.engine_id,
                "connected": False,
                "status": "unreachable"
            }

    async def chat(
        self,
        messages: list[dict[str, str]]
    ) -> dict[str, Any]:

        if not self.base_url or not self.api_key:
            return {
                "engine": self.engine_id,
                "connected": False,
                "status": "configuration_required"
            }

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self._headers(),
                    json=payload
                )

            if not response.is_success:
                return {
                    "engine": self.engine_id,
                    "connected": False,
                    "status": "upstream_error",
                    "status_code": response.status_code
                }

            data = response.json()
            choices = data.get("choices", [])
            message = (
                choices[0].get("message", {})
                if choices else {}
            )
            reply = message.get("content")

            if not isinstance(reply, str):
                return {
                    "engine": self.engine_id,
                    "connected": True,
                    "status": "invalid_response"
                }

            return {
                "engine": self.engine_id,
                "connected": True,
                "status": "ok",
                "model": data.get("model", self.model),
                "reply": reply
            }

        except httpx.HTTPError:
            return {
                "engine": self.engine_id,
                "connected": False,
                "status": "unreachable"
            }
        except (ValueError, TypeError, IndexError, KeyError):
            return {
                "engine": self.engine_id,
                "connected": False,
                "status": "invalid_response"
            }
                
