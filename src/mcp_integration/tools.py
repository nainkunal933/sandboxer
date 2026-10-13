"""Tools exposed by the Sandboxer MCP server."""

from core import build_context, build_generation_prompt


def analyze(
    objective: str,
    values: dict[str, str] | None = None,
) -> dict[str, object]:
    """Validate and normalize a sandbox objective and additional context."""
    context = build_context(objective, values)
    return {"objective": context.objective, "values": dict(context.values)}


def generate(
    objective: str,
    values: dict[str, str] | None = None,
) -> dict[str, str]:
    """Prepare a sandbox data generation prompt for the host model to execute."""
    context = build_context(objective, values)
    return {"prompt": build_generation_prompt(context)}
