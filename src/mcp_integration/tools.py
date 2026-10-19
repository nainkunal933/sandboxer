"""Tools exposed by the Sandboxer MCP server."""

from pathlib import Path
from typing import Annotated

from mcp.server.mcpserver import Resolve

from core import (
    build_context,
    build_schema_analysis_prompt,
    create_file_inventory,
)

from .elicitation import (
    GenerationTargetInput,
    ProjectRootInput,
    request_generation_target,
    resolve_project_root,
)


def analyze(
    objective: str,
    resolved_root: Annotated[ProjectRootInput, Resolve(resolve_project_root)],
    values: dict[str, str] | None = None,
) -> dict[str, object]:
    """Choose a project root, create .sandboxer, and inventory nonignored files.

    Return inventory_csv_path, file_count, validated context, and a prompt.
    The host agent should execute the returned prompt to inspect candidate files
    and create .sandboxer/schema.md relative to the project root.
    The bundled .schemaignore excludes matching files and prunes directories.
    Eligibility marks schema candidates by extension; file contents are not scanned.
    """
    context = build_context(objective, values)
    project_root = Path(resolved_root.project_root)
    (project_root / ".sandboxer").mkdir(exist_ok=True)
    inventory_csv_path, file_count = create_file_inventory(project_root)
    return {
        "project_root": resolved_root.project_root,
        "objective": context.objective,
        "values": dict(context.values),
        "inventory_csv_path": str(inventory_csv_path),
        "file_count": file_count,
        "prompt": build_schema_analysis_prompt(
            resolved_root.project_root,
            str(inventory_csv_path),
        ),
    }


def generate(
    objective: str,
    project_root: str,
    target_options: list[str],
    selection: Annotated[GenerationTargetInput, Resolve(request_generation_target)],
    values: dict[str, str] | None = None,
) -> dict[str, object]:
    """Ask the user to select a table or collection from host-prepared options.

    Before calling, use the project_root returned by analyze and read only Scope
    and engine and Structure in its .sandboxer/schema.md. Supply actual table or
    collection names as target_options, preserving qualified names and excluding
    descriptive headings. If the document is missing, request analyze instead of
    inventing options. Do not read Population to prepare this list.

    Return project_root, target, objective, and values. The tool validates the
    supplied root without folder elicitation and does not read project files,
    generate data, return a prompt, or write files.
    """
    context = build_context(objective, values)
    resolved_root = ProjectRootInput(project_root=project_root)
    return {
        "project_root": resolved_root.project_root,
        "target": selection.target,
        "objective": context.objective,
        "values": dict(context.values),
    }
