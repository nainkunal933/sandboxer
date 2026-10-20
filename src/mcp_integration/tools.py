"""Tools exposed by the Sandboxer MCP server."""

from pathlib import Path
from typing import Annotated

from mcp.server.mcpserver import Resolve
from mcp.server.mcpserver.exceptions import ToolError

from core import (
    build_context,
    build_schema_analysis_prompt,
    create_file_inventory,
    copy_procedure_files,
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
    target_procedures: dict[str, list[str]],
    selection: Annotated[GenerationTargetInput, Resolve(request_generation_target)],
    values: dict[str, str] | None = None,
) -> dict[str, object]:
    """Ask the user to select a table or collection from host-prepared options.

    Before calling, use the project_root returned by analyze. Read Scope and
    engine and Structure in .sandboxer/schema.md to prepare target_options from
    actual table or collection names, preserving qualified names and excluding
    descriptive headings. Read Population to identify each target's existing
    CRUD procedure source files. Supply target_procedures as a mapping from those
    exact target names to root-relative source paths; use an empty list when no
    procedures exist. Do not include schema definitions or application methods.
    If schema.md is missing, request analyze instead of inventing options or paths.

    After selection, Python copies only the selected target's mapped files into
    .sandboxer/generate, preserving filenames and contents. Identical copies are
    reused; missing sources and filename/content conflicts fail without replacing
    existing files. Return project_root, target, objective, values, and copied_files
    (destination paths, including reused copies). No prompt or data is generated.
    """
    context = build_context(objective, values)
    resolved_root = ProjectRootInput(project_root=project_root)
    if selection.target not in target_procedures:
        raise ToolError(f"No procedure file mapping supplied for target: {selection.target}")
    try:
        copied_files = copy_procedure_files(
            Path(resolved_root.project_root), target_procedures[selection.target]
        )
    except (OSError, ValueError) as error:
        raise ToolError(str(error)) from error
    return {
        "project_root": resolved_root.project_root,
        "target": selection.target,
        "objective": context.objective,
        "values": dict(context.values),
        "copied_files": [str(path) for path in copied_files],
    }
