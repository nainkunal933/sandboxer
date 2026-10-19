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


def normalize_target_options(target_options: list[str]) -> list[str]:
    """Trim and deduplicate target names while preserving their original order."""
    options = list(dict.fromkeys(option.strip() for option in target_options))
    if not options or any(not option for option in options):
        raise ValueError("Provide at least one target option, with no blank names.")
    return options
