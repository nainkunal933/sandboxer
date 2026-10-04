"""Anthropic model adapter."""

from dataclasses import dataclass

from .base import ModelRequest, ModelResponse


@dataclass(slots=True)
class AnthropicAdapter:
    """Placeholder for the Anthropic API integration."""

    model: str
    provider: str = "anthropic"

    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate a response through Anthropic once its SDK is configured."""
        raise RuntimeError("The Anthropic adapter has not been configured yet.")
