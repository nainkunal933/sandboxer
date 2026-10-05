"""Context collection and validation shared by all entry points."""

from typing import Mapping

from .schemas import SandboxContext


def build_context(
    objective: str,
    values: Mapping[str, str] | None = None,
) -> SandboxContext:
    """Validate raw input and create a normalized sandbox context."""
    normalized_objective = objective.strip()
    if not normalized_objective:
        raise ValueError("A sandbox objective is required.")

    normalized_values = {
        key.strip(): value.strip()
        for key, value in (values or {}).items()
        if key.strip() and value.strip()
    }
    return SandboxContext(
        objective=normalized_objective,
        values=normalized_values,
    )
