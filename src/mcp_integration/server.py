"""Sandboxer's MCP server definition."""

from mcp.server import MCPServer

from .tools import analyze, generate, populate


class SandboxerMCPServer:
    """Expose Sandboxer capabilities to MCP-compatible agent hosts."""

    def __init__(self) -> None:
        self.mcp = MCPServer("Sandboxer")
        self.mcp.tool()(analyze)
        self.mcp.tool()(generate)
        self.mcp.tool()(populate)

    def run(self) -> None:
        """Serve MCP requests over STDIO for a local agent host."""
        self.mcp.run(transport="stdio")
