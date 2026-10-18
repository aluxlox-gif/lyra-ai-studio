"""
Voicebox adapter for LYRA AI STUDIO.

Connects LYRA to a running Voicebox REST API.
"""

from typing import Any

import httpx

from app.engines.adapters.base import BaseEngineAdapter


class VoiceboxAdapter(BaseEngineAdapter):
    """Adapter for Voicebox voice generation and transcription."""

    engine_id = "voice"
    engine_name = "Voicebox"

    def __init__(
        self,
        config: dict[str, Any] | None = None,
    ):
        super().__init__(config)

        self.base_url = (
            self.config.get("base_url")
            or "http://127.0.0.1:17493"
        ).rstrip("/")

        self.timeout = float(
            self.config.get("timeout", 30)
        )

        self.client_id = self.config.get(
            "client_id",
            "lyra-ai-studio",
        )

    def get_capabilities(self) -> list[str]:
        return [
            "text_to_speech",
            "speech_to_text",
            "voice_profiles",
            "voice_generation",
        ]

    async def health_check(self) -> dict[str, Any]:
        """Check Voicebox connectivity through its profiles endpoint."""

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:
                response = await client.get(
                    f"{self.base_url}/profiles"
                )

                response.raise_for_status()

            return {
                "engine_id": self.engine_id,
                "engine_name": self.engine_name,
                "connected": True,
                "status": "connected",
                "base_url": self.base_url,
            }

        except httpx.HTTPError as exc:
            return {
                "engine_id": self.engine_id,
                "engine_name": self.engine_name,
                "connected": False,
                "status": "unavailable",
                "base_url": self.base_url,
                "error": str(exc),
            }

    async def list_profiles(self) -> Any:
        """Retrieve available Voicebox voice profiles."""

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:
            response = await client.get(
                f"{self.base_url}/profiles"
            )

            response.raise_for_status()

            return response.json()

    async def generate_speech(
        self,
        text: str,
        profile_id: str,
        language: str = "en",
    ) -> dict[str, Any]:
        """Generate speech using a Voicebox voice profile."""

        if not text.strip():
            raise ValueError("Text tidak boleh kosong.")

        if not profile_id.strip():
            raise ValueError("Profile ID tidak boleh kosong.")

        payload = {
            "text": text,
            "profile_id": profile_id,
            "language": language,
        }

        headers = {
            "Content-Type": "application/json",
            "X-Voicebox-Client-Id": self.client_id,
        }

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:
            response = await client.post(
                f"{self.base_url}/generate",
                json=payload,
                headers=headers,
            )

            response.raise_for_status()

            return {
                "status_code": response.status_code,
                "content_type": response.headers.get(
                    "content-type",
                    "application/octet-stream",
                ),
                "audio": response.content,
            }
