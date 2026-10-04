"""Provider-independent agent runtime."""

from models.base import ModelAdapter, ModelRequest, ModelResponse


class AgentRuntime:
    """Route model requests through registered provider adapters."""

    def __init__(self) -> None:
        self._adapters: dict[str, ModelAdapter] = {}

    def register(self, adapter: ModelAdapter) -> None:
        """Register or replace a model adapter by provider name."""
        self._adapters[adapter.provider] = adapter

    @property
    def providers(self) -> tuple[str, ...]:
        """Return the names of all configured model providers."""
        return tuple(sorted(self._adapters))

    async def run(self, provider: str, request: ModelRequest) -> ModelResponse:
        """Send a request through the selected provider adapter."""
        try:
            adapter = self._adapters[provider]
        except KeyError as error:
            available = ", ".join(self.providers) or "none"
            raise ValueError(
                f"Unknown model provider {provider!r}. Available: {available}."
            ) from error

        return await adapter.generate(request)
