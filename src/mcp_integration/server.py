"""Sandboxer's MCP server definition."""

from .tools import ToolDefinition, default_tools


class SandboxerMCPServer:
    """Expose Sandboxer capabilities to MCP-compatible agent hosts."""

    def __init__(self) -> None:
        self.tools: tuple[ToolDefinition, ...] = default_tools()

    def run(self) -> None:
        """Start the MCP server once an SDK transport is configured."""
        raise RuntimeError("The MCP server transport has not been configured yet.")
