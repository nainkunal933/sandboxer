"""OpenAI model adapter."""

from dataclasses import dataclass

from .base import ModelRequest, ModelResponse


@dataclass(slots=True)
class OpenAIAdapter:
    """Placeholder for the OpenAI API integration."""

    model: str
    provider: str = "openai"

    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate a response through OpenAI once its SDK is configured."""
        raise RuntimeError("The OpenAI adapter has not been configured yet.")
