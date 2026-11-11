"""Adapter for the user's self-hosted LYRA VOICEBOX CLOUD API."""

from typing import Any

import httpx

from app.engines.adapters.base import BaseEngineAdapter


class VoiceboxNotConfiguredError(RuntimeError):
    """Raised when the self-hosted Voicebox URL has not been configured."""


class VoiceboxAdapter(BaseEngineAdapter):
    engine_id = "voice"
    engine_name = "LYRA VOICEBOX CLOUD"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.base_url = (self.config.get("base_url") or "").strip().rstrip("/")
        self.api_key = (self.config.get("api_key") or "").strip()
        self.api_key_header = (
            self.config.get("api_key_header") or "X-API-Key"
        ).strip()
        self.timeout = float(self.config.get("timeout", 30))

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url)

    def _require_configured(self) -> None:
        if not self.is_configured:
            raise VoiceboxNotConfiguredError(
                "VOICEBOX_BASE_URL belum diatur."
            )

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers[self.api_key_header] = self.api_key
        return headers

    def get_capabilities(self) -> list[str]:
        return [
            "text_to_speech",
            "speech_to_text",
            "voice_profiles",
            "voice_generation",
        ]

    async def health_check(self) -> dict[str, Any]:
        if not self.is_configured:
            return {
                "engine_id": self.engine_id,
                "engine_name": self.engine_name,
                "configured": False,
                "connected": False,
                "status": "not_configured",
            }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self._headers(),
                )
                response.raise_for_status()

            return {
                "engine_id": self.engine_id,
                "engine_name": self.engine_name,
                "configured": True,
                "connected": True,
                "status": "connected",
            }
        except httpx.HTTPError:
            return {
                "engine_id": self.engine_id,
                "engine_name": self.engine_name,
                "configured": True,
                "connected": False,
                "status": "unavailable",
            }

    async def list_profiles(self) -> Any:
        self._require_configured()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/profiles",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    async def generate_speech(
        self,
        text: str,
        profile_id: str,
        language: str = "id",
    ) -> tuple[bytes, str]:
        self._require_configured()

        if not text.strip():
            raise ValueError("Teks tidak boleh kosong.")
        if not profile_id.strip():
            raise ValueError("Profile ID tidak boleh kosong.")

        payload = {
            "text": text,
            "profile_id": profile_id,
            "language": language,
        }

        headers = self._headers()
        headers["Accept"] = "audio/*, application/octet-stream"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/generate",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()

        content_type = response.headers.get(
            "content-type", "application/octet-stream"
        ).split(";", 1)[0].strip()

        if content_type == "application/json" or content_type.endswith("+json"):
            raise ValueError(
                "Voicebox mengembalikan JSON, bukan data audio. "
                "Pastikan POST /generate mengembalikan audio bytes."
            )

        if not response.content:
            raise ValueError("Voicebox mengembalikan audio kosong.")

        return response.content, content_type
