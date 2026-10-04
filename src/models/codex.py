"""Codex local-agent adapter."""

from dataclasses import dataclass

from .base import ModelRequest, ModelResponse


@dataclass(slots=True)
class CodexAdapter:
    """Placeholder for the local Codex SDK integration."""

    model: str | None = None
    provider: str = "codex"

    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate a response through Codex once its SDK is configured."""
        raise RuntimeError("The Codex adapter has not been configured yet.")
