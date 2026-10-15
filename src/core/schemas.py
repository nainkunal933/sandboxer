"""Domain models shared by the CLI and MCP server."""

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True, slots=True)
class FileInventoryEntry:
    """A project file listed for possible future content scanning."""

    filename: str
    path: str
    eligible: bool = False


@dataclass(frozen=True, slots=True)
class SandboxContext:
    """Validated user context used to generate sandbox data."""

    objective: str
    values: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GeneratedSandboxData:
    """Provider-independent result produced for a sandbox."""

    content: str
    metadata: Mapping[str, object] = field(default_factory=dict)
