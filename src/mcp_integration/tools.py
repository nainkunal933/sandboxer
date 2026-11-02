"""Tools exposed by the Sandboxer MCP server."""

from pathlib import Path
from typing import Annotated

from mcp.server.mcpserver import Resolve
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import StringConstraints

from core import (
    build_context,
    build_schema_analysis_prompt,
    create_file_inventory,
    create_population_sql,
    execute_population_sql,
    generate_csv_files,
)
from core.schemas import DataModel

from .elicitation import (
    DockerChoiceInput,
    PreparedGeneration,
    ProjectRootInput,
    RecordCountInput,
    prepare_generation,
    request_docker_container,
    request_docker_context,
    resolve_record_count,
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
    and create .sandboxer/schema.md relative to the project root, detailing
    create/insert interfaces in Population and listing other procedures briefly
    under Procedure references. Database metadata records data models, engines,
    and source-declared database names without selecting a target database.
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
    data_model: DataModel,
    engine: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)],
    target_options: list[str],
    target_procedures: dict[str, list[str]],
    prepared: Annotated[PreparedGeneration, Resolve(prepare_generation)],
    count: Annotated[RecordCountInput, Resolve(resolve_record_count)],
    values: dict[str, str] | None = None,
) -> dict[str, object]:
    """Select a target, stage creation procedures, and ask for a record count.

    Before calling, use the project_root returned by analyze. Read Database
    metadata and Structure in .sandboxer/schema.md to prepare target_options from
    actual table or collection names, preserving qualified names and excluding
    descriptive headings. Supply the source-verified data_model enum value and
    engine from Database metadata for those targets. Both arguments are required;
    engine is trimmed and must be non-empty. If the project has multiple models
    or engines, group targets into separate calls with one model/engine pair per
    call. If classification is undetermined, resolve it from source or user input
    before calling rather than guessing. These arguments carry classification
    metadata; generation still uses SQL Server procedures and does not dispatch
    strategies based on these values yet.
    Read Population to identify each target's existing
    create/insert procedure source files. Supply target_procedures as a mapping
    from those exact target names to root-relative source paths; use an empty list
    when no creation procedures exist. Exclude read/update/delete procedures,
    including any detailed in older schema.md files. Procedure references are
    guidance only. Do not include schema definitions or application methods.
    If schema.md is missing, request analyze instead of inventing options or paths.

    After selection, Python copies only the selected target's mapped creation
    files into .sandboxer/generate, preserving filenames and contents. Existing
    staged files are not deleted. Identical copies are reused; missing sources
    and filename/content conflicts fail without replacing existing files.
    Once copying succeeds, always ask how many records to create: 10, 50, 100,
    or Custom. Custom requests a positive whole number with no upper limit.
    Context values do not bypass this question. Decline/cancel aborts completion
    without a default count; already copied files remain.
    Return project_root, target, objective, values, copied_files (destination
    paths, including reused copies), integer record_count, and csv_files.
    After count acceptance, Python uses Faker to generate that many data rows per
    copied SQL Server Create procedure. CSV columns follow input parameter names
    and datatypes, excluding output parameters. Files are written beside the
    copied procedures as <procedure filename stem>.csv; existing CSVs are preserved
    by adding a numeric suffix. Unsupported types fail rather than guessing.
    No database commands are executed and no prompt is returned.
    """
    try:
        csv_files = generate_csv_files(
            [Path(path) for path in prepared.copied_files], count.record_count
        )
    except (OSError, ValueError) as error:
        raise ToolError(str(error)) from error
    return {
        "project_root": prepared.project_root,
        "target": prepared.target,
        "objective": prepared.context.objective,
        "values": dict(prepared.context.values),
        "copied_files": list(prepared.copied_files),
        "record_count": count.record_count,
        "csv_files": [str(path) for path in csv_files],
    }


def populate(
    project_root: str,
    csv_files: list[str],
    copied_files: list[str],
    database: str,
    docker_context: Annotated[DockerChoiceInput, Resolve(request_docker_context)],
    container: Annotated[DockerChoiceInput, Resolve(request_docker_container)],
) -> dict[str, object]:
    """Generate population SQL and execute it against the selected Docker container.

    Supply project_root from analyze and csv_files and copied_files from generate.
    Supply the target database name explicitly, using verified schema information
    or user input. This tool writes records to that database.
    Keep both lists in matching order, with one CSV per copied Create procedure.
    Python creates the output folder, lists Docker contexts, and asks the user
    which environment contains the container. Then it lists running containers
    only in that context and asks the user to select a container name.
    After selection, Python writes one SQL file per pair in .sandboxer/populate.
    The file includes the copied definition and a new parameterless procedure
    calling it once per CSV record. Names use the copied filename stem and actual
    CSV row count: User_Create_Populate_50.sql. A matching count replaces that
    script; a different count creates another file. CSV text is escaped and
    converted by SQL Server to the source procedure's declared parameter types.
    Then execute each file with docker exec and sqlcmd in the selected context
    and container, applying the definitions and invoking the generated population
    procedure. Authentication uses the container's SQLCMDPASSWORD or
    MSSQL_SA_PASSWORD for the sa login. Docker's active context is unchanged.
    Return populate_path, docker_context, container_name, database, sql_files, and
    status="executed" only after all scripts execute successfully. Execution
    failures raise a tool error; generated SQL files remain available.
    """
    root = ProjectRootInput(project_root=project_root).project_root
    populate_path = Path(root) / ".sandboxer" / "populate"
    try:
        if not database.strip():
            raise ValueError("The target database name is required.")
        sql_files = create_population_sql(Path(root), copied_files, csv_files)
        for sql_file in sql_files:
            execute_population_sql(sql_file, docker_context.choice, container.choice, database)
    except (OSError, ValueError) as error:
        raise ToolError(str(error)) from error
    return {
        "populate_path": str(populate_path),
        "docker_context": docker_context.choice,
        "container_name": container.choice,
        "database": database,
        "sql_files": [str(path) for path in sql_files],
        "status": "executed",
    }
