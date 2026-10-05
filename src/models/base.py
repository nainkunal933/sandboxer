"""Shared contracts for LLM provider adapters."""

from dataclasses import dataclass, field
from typing import Mapping, Protocol


@dataclass(frozen=True, slots=True)
class ModelRequest:
    """A provider-neutral model request."""

    prompt: str
    system_prompt: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ModelResponse:
    """A provider-neutral model response."""

    text: str
    model: str
    metadata: Mapping[str, object] = field(default_factory=dict)


class ModelAdapter(Protocol):
    """Interface implemented by every LLM provider adapter."""

    @property
    def provider(self) -> str:
        """Return the stable provider name used by the runtime."""
        ...

    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate a response for a provider-neutral request."""
        ...
