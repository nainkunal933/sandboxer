"""Generation orchestration and prompts shared by the CLI and MCP server."""

import csv
from importlib.resources import files
from pathlib import Path

from faker import Faker

from .generation_strategies.sqlserver_generation import (
    open_csv,
    read_procedure_signature,
    value_generator,
)
from .schemas import DataModel, SandboxContext


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
    descriptions = {
        DataModel.RELATIONAL: "Tables with rows, columns, and declared keys or relationships.",
        DataModel.DOCUMENT: "Documents with fields, nested objects, and arrays.",
        DataModel.KEY_VALUE: "Keys mapped to values treated as opaque by the data model.",
        DataModel.GRAPH: "Entities and relationships represented as nodes and edges.",
        DataModel.WIDE_COLUMN: "Rows with variable columns organized into column families.",
        DataModel.VECTOR: "Embeddings organized for vector similarity search.",
        DataModel.TIME_SERIES: "Time-indexed observations organized for time-range queries.",
    }
    return template.format(
        project_root=project_root,
        inventory_csv_path=inventory_csv_path,
        data_models="\n".join(
            f"- `{model.value}`: {descriptions[model]}" for model in DataModel
        ),
    )


def generate_csv_files(procedure_files: list[Path], record_count: int) -> list[Path]:
    """Stream exactly record_count rows per procedure, removing output on failure.

    Headers are input parameter names without @, in declaration order. Each
    procedure produces a separate CSV beside its staged SQL source. Values honor
    supported parameter types and dimensions; table constraints and application
    rules, including foreign-key existence and password-hash formats, are not
    inferred. Password fields contain synthetic SHA-256 placeholder hashes.
    """
    if type(record_count) is not int or record_count < 1:
        raise ValueError("Record count must be a positive whole number.")
    if not procedure_files:
        raise ValueError("No creation procedure is available to generate CSV data.")
    fake = Faker("en_US")
    plans = []
    for procedure in dict.fromkeys(procedure_files):
        _, parameters = read_procedure_signature(procedure)
        parameters = [parameter for parameter in parameters if not parameter.is_output]
        generators = [value_generator(parameter, fake, record_count) for parameter in parameters]
        plans.append((procedure, parameters, generators))
    outputs = []
    try:
        for procedure, parameters, generators in plans:
            destination, stream = open_csv(procedure)
            outputs.append(destination)
            with stream:
                writer = csv.writer(stream)
                writer.writerow([parameter.name for parameter in parameters])
                for row_number in range(1, record_count + 1):
                    writer.writerow([generate(row_number) for generate in generators])
        return outputs
    except Exception:
        for output in outputs:
            output.unlink(missing_ok=True)
        raise
