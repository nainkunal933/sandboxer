"""Types for presenting MCP elicitation requests in the CLI."""

from dataclasses import dataclass, field
from typing import Awaitable, Callable, Mapping


@dataclass(frozen=True, slots=True)
class ElicitationRequest:
    """A structured request for additional user input."""

    message: str
    schema: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ElicitationResponse:
    """The user's response to an elicitation request."""

    accepted: bool
    content: Mapping[str, object] | None = None


ElicitationHandler = Callable[
    [ElicitationRequest],
    Awaitable[ElicitationResponse],
]
