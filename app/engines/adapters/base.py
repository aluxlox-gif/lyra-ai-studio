"""
Base interface for LYRA AI STUDIO engine adapters.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseEngineAdapter(ABC):
    """Standard interface for AI engine integrations."""

    engine_id = "unknown"
    engine_name = "Unknown Engine"

    def __init__(
        self,
        config: dict[str, Any] | None = None,
    ):
        self.config = config or {}

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check whether the engine is reachable."""
        raise NotImplementedError

    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """Return supported engine capabilities."""
        raise NotImplementedError

    def get_info(self) -> dict[str, Any]:
        """Return basic engine information."""
        return {
            "engine_id": self.engine_id,
            "engine_name": self.engine_name,
            "capabilities": self.get_capabilities(),
        }
