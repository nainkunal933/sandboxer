"""Sandbox data generation logic shared by the CLI and MCP server."""

from .schemas import SandboxContext


def build_generation_prompt(context: SandboxContext) -> str:
    """Build a provider-neutral prompt from validated sandbox context."""
    details = "\n".join(
        f"- {key}: {value}"
        for key, value in sorted(context.values.items())
    )
    if not details:
        details = "- No additional context was provided."

    return (
        "Generate the data required for a sandbox with this objective:\n"
        f"{context.objective}\n\n"
        "Additional context:\n"
        f"{details}"
    )
