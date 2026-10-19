"""Models, types, and helpers for MCP elicitation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Awaitable, Callable, Literal, Mapping

from mcp.server.mcpserver import Elicit, Resolve
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel, ConfigDict, Field, create_model, field_validator

from core import normalize_target_options


@dataclass(frozen=True, slots=True)
class ElicitationRequest:
    """A structured request for additional user input."""

    message: str
    schema: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ElicitationResponse:
    """The user's response to an elicitation request."""

    accepted: bool
    content: Mapping[str, object] | None = None


ElicitationHandler = Callable[
    [ElicitationRequest],
    Awaitable[ElicitationResponse],
]


def _remove_elicitation_metadata(schema: dict[str, object]) -> None:
    """Remove model metadata that Codex rejects at the form schema's root."""
    schema.pop("title", None)
    schema.pop("description", None)


class ProjectRootChoice(BaseModel):
    """Whether to use the current folder or choose another directory."""

    model_config = ConfigDict(json_schema_extra=_remove_elicitation_metadata)

    choice: Literal["Use current folder", "Use another folder"] = Field(
        description="Choose the project folder to use."
    )


class ProjectRootInput(BaseModel):
    """Validated project root chosen by the user through elicitation."""

    model_config = ConfigDict(json_schema_extra=_remove_elicitation_metadata)

    project_root: str = Field(
        description=(
            "Relative or absolute path to an existing project directory on the "
            "machine running Sandboxer. Relative paths start from the current folder."
        )
    )

    @field_validator("project_root")
    @classmethod
    def validate_project_root(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Project root must be a non-empty directory path.")
        path = Path(value.strip()).expanduser()
        try:
            path = path.resolve(strict=True)
        except (OSError, RuntimeError) as error:
            raise ValueError("Project root does not exist or cannot be accessed.") from error
        if not path.is_dir():
            raise ValueError("Project root must be a directory.")
        return str(path)


def _choose_project_root() -> Elicit[ProjectRootChoice]:
    """Offer the current folder first, with an option to override it."""
    return Elicit(
        f"Use the project in the current folder: {Path.cwd()}\n"
        "Use this folder or choose another folder with a relative or absolute path.",
        ProjectRootChoice,
    )


def resolve_project_root(
    selection: Annotated[ProjectRootChoice, Resolve(_choose_project_root)],
) -> ProjectRootInput | Elicit[ProjectRootInput]:
    """Resolve the selected folder, requesting an override only when needed."""
    if selection.choice == "Use current folder":
        return ProjectRootInput(project_root=str(Path.cwd()))
    return Elicit(
        "Enter the project's relative or absolute directory path. "
        f"Relative paths start from: {Path.cwd()}",
        ProjectRootInput,
    )


class GenerationTargetInput(BaseModel):
    """The table or collection selected from the host agent's options."""

    model_config = ConfigDict(
        json_schema_extra=_remove_elicitation_metadata,
        str_strip_whitespace=True,
    )

    target: str = Field(
        min_length=1,
        description="Choose the table or collection to target.",
    )


def request_generation_target(
    project_root: str,
    target_options: list[str],
) -> Elicit[GenerationTargetInput]:
    """Validate the supplied inputs and ask the user to select a target."""
    try:
        resolved_root = ProjectRootInput(project_root=project_root)
        options = normalize_target_options(target_options)
    except ValueError as error:
        raise ToolError(str(error)) from error

    def validate_target(value: str) -> str:
        if value not in options:
            raise ValueError("Choose one of the supplied target options.")
        return value

    choice_model = create_model(
        "GenerationTargetChoice",
        __base__=GenerationTargetInput,
        __validators__={"validate_target": field_validator("target")(validate_target)},
        target=(
            str,
            Field(
                description="Choose the table or collection to target.",
                json_schema_extra={"enum": options},
            ),
        ),
    )
    return Elicit(
        "Choose the table or collection to target in the project at: "
        f"{resolved_root.project_root}",
        choice_model,
    )
