"""Definitions for tools exposed by the Sandboxer MCP server."""

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    """Provider-neutral metadata for an MCP tool."""

    name: str
    description: str
    input_schema: Mapping[str, object]


def default_tools() -> tuple[ToolDefinition, ...]:
    """Return the initial Sandboxer MCP tool catalog."""
    empty_object_schema: Mapping[str, object] = {
        "type": "object",
        "properties": {},
    }
    return (
        ToolDefinition(
            name="collect_context",
            description="Collect context required to prepare a sandbox.",
            input_schema=empty_object_schema,
        ),
        ToolDefinition(
            name="generate_sandbox_data",
            description="Generate data needed by a sandbox.",
            input_schema=empty_object_schema,
        ),
        ToolDefinition(
            name="inspect_workspace",
            description="Inspect workspace metadata relevant to a sandbox.",
            input_schema=empty_object_schema,
        ),
    )
