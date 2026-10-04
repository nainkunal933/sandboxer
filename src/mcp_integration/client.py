"""MCP client used by the Sandboxer agent runtime."""

from typing import Mapping


class MCPClient:
    """Provider-neutral facade for MCP server connections."""

    def __init__(self) -> None:
        self._connected = False

    @property
    def connected(self) -> bool:
        """Report whether an MCP transport is connected."""
        return self._connected

    async def connect(self) -> None:
        """Connect after an MCP SDK transport has been configured."""
        raise RuntimeError("The MCP client transport has not been configured yet.")

    async def call_tool(
        self,
        name: str,
        arguments: Mapping[str, object],
    ) -> object:
        """Invoke a tool on the connected MCP server."""
        if not self.connected:
            raise RuntimeError("The MCP client is not connected.")
        raise NotImplementedError(
            f"Tool execution is not configured: {name!r} "
            f"with {len(arguments)} argument(s)."
        )

    async def close(self) -> None:
        """Close the current MCP connection."""
        self._connected = False
