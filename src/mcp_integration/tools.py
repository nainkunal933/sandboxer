"""Tools exposed by the Sandboxer MCP server."""

from pathlib import Path
from typing import Annotated

from mcp.server.mcpserver import Elicit, Resolve
from pydantic import BaseModel, Field, field_validator

from core import build_context, build_generation_prompt


class ProjectRootInput(BaseModel):
    """Project root supplied by the host or through elicitation."""

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


def resolve_project_root(
    project_root: str | None = None,
) -> ProjectRootInput | Elicit[ProjectRootInput]:
    """Ask the user for a project root when the host did not provide one."""
    if project_root is not None and project_root.strip():
        return ProjectRootInput(project_root=project_root)
    return Elicit(
        "What is the absolute path to your project's root directory?",
        ProjectRootInput,
    )


def analyze(
    objective: str,
    resolved_root: Annotated[ProjectRootInput, Resolve(resolve_project_root)],
    values: dict[str, str] | None = None,
    project_root: Annotated[
        str | None,
        Field(description="Absolute project root path; omitted paths are requested from the user."),
    ] = None,
) -> dict[str, object]:
    """Validate sandbox context and its project root, eliciting the path if omitted."""
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
