"""Tools exposed by the Sandboxer MCP server."""

from pathlib import Path
from typing import Annotated

from mcp.server.mcpserver import Elicit, Resolve
from pydantic import BaseModel, ConfigDict, Field, field_validator

from core import build_context, build_generation_prompt


def _remove_elicitation_metadata(schema: dict[str, object]) -> None:
    """Remove model metadata that Codex rejects at the form schema's root."""
    schema.pop("title", None)
    schema.pop("description", None)


class ProjectRootInput(BaseModel):
    """Project root explicitly supplied by the user through elicitation."""

    model_config = ConfigDict(json_schema_extra=_remove_elicitation_metadata)

    project_root: str = Field(
        description=(
            "Absolute path to an existing project directory on the machine "
            "running Sandboxer."
        )
    )

    @field_validator("project_root")
    @classmethod
    def validate_project_root(cls, value: str) -> str:
        path = Path(value.strip()).expanduser()
        if not value.strip() or not path.is_absolute():
            raise ValueError("Project root must be an absolute directory path.")
        try:
            path = path.resolve(strict=True)
        except (OSError, RuntimeError) as error:
            raise ValueError("Project root does not exist or cannot be accessed.") from error
        if not path.is_dir():
            raise ValueError("Project root must be a directory.")
        return str(path)


def resolve_project_root() -> Elicit[ProjectRootInput]:
    """Always ask the user to explicitly choose the project root."""
    return Elicit(
        "What is the absolute path to your project's root directory?",
        ProjectRootInput,
    )


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
