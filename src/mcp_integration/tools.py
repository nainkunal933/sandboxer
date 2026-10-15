"""Tools exposed by the Sandboxer MCP server."""

from typing import Annotated

from mcp.server.mcpserver import Resolve

from core import build_context, build_generation_prompt

from .elicitation import ProjectRootInput, resolve_project_root


def analyze(
    objective: str,
    resolved_root: Annotated[ProjectRootInput, Resolve(resolve_project_root)],
    values: dict[str, str] | None = None,
) -> dict[str, object]:
    """Validate sandbox context after asking the user to explicitly choose a project root."""
    context = build_context(objective, values)
    return {
        "project_root": resolved_root.project_root,
        "objective": context.objective,
        "values": dict(context.values),
    }


def generate(
    objective: str,
    values: dict[str, str] | None = None,
) -> dict[str, str]:
    """Prepare a sandbox data generation prompt for the host model to execute."""
    context = build_context(objective, values)
    return {"prompt": build_generation_prompt(context)}
