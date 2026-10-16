"""Tools exposed by the Sandboxer MCP server."""

from pathlib import Path
from typing import Annotated

from mcp.server.mcpserver import Resolve

from core import build_context, build_generation_prompt, create_file_inventory

from .elicitation import ProjectRootInput, resolve_project_root


def analyze(
    objective: str,
    resolved_root: Annotated[ProjectRootInput, Resolve(resolve_project_root)],
    values: dict[str, str] | None = None,
) -> dict[str, object]:
    """Choose a project root and inventory nonignored files in a temporary CSV.

    Return inventory_csv_path and file_count alongside validated context.
    The bundled .schemaignore excludes matching files and prunes directories.
    Eligibility marks schema candidates by extension; file contents are not scanned.
    """
    context = build_context(objective, values)
    inventory_csv_path, file_count = create_file_inventory(Path(resolved_root.project_root))
    return {
        "project_root": resolved_root.project_root,
        "objective": context.objective,
        "values": dict(context.values),
        "inventory_csv_path": str(inventory_csv_path),
        "file_count": file_count,
    }


def generate(
    objective: str,
    values: dict[str, str] | None = None,
) -> dict[str, str]:
    """Prepare a sandbox data generation prompt for the host model to execute."""
    context = build_context(objective, values)
    return {"prompt": build_generation_prompt(context)}
