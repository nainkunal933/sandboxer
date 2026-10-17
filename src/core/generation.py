"""Provider-neutral prompts shared by the CLI and MCP server."""

from importlib.resources import files

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


def build_schema_analysis_prompt(
    project_root: str,
    inventory_csv_path: str,
) -> str:
    """Render schema analysis instructions for the host agent to execute."""
    template = (
        files("core")
        .joinpath("prompts", "schema_analysis.md")
        .read_text(encoding="utf-8")
    )
    return template.format(
        project_root=project_root,
        inventory_csv_path=inventory_csv_path,
    )
