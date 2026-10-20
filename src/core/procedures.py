"""Stage procedure source files identified by the host agent."""

import filecmp
from pathlib import Path
import shutil


def copy_procedure_files(project_root: Path, source_paths: list[str]) -> list[Path]:
    """Copy root-relative sources unchanged, preserving names and existing files.

    Validate all sources and destinations before copying. Identical existing
    copies are reused; missing sources, paths outside the root, and filename or
    content conflicts raise an error. Return destination paths in source order.
    """
    root = project_root.resolve(strict=True)
    output = (root / ".sandboxer" / "generate").resolve()
    if not output.is_relative_to(root):
        raise ValueError("The generate directory must be inside the project root.")
    if output.exists() and not output.is_dir():
        raise ValueError("The generate directory path is not a directory.")

    sources: dict[Path, Path] = {}
    for source_path in source_paths:
        relative_path = Path(source_path.strip())
        if not source_path.strip() or relative_path.is_absolute() or relative_path.drive:
            raise ValueError("Procedure source paths must be non-empty and root-relative.")
        source = (root / relative_path).resolve(strict=True)
        if not source.is_relative_to(root) or source.is_relative_to(output):
            raise ValueError(
                "Procedure source must be inside the project, outside generate: "
                f"{source_path}"
            )
        if not source.is_file():
            raise ValueError(f"Procedure source is not a file: {source_path}")

        destination = output / relative_path.name
        if destination in sources and sources[destination] != source:
            raise ValueError(f"Procedure sources share the filename: {destination.name}")
        if destination.is_symlink():
            raise ValueError(f"Procedure destination must not be a symlink: {destination}")
        if destination.exists():
            if not destination.is_file() or not filecmp.cmp(
                source, destination, shallow=False
            ):
                raise ValueError(f"Procedure destination has conflicting content: {destination}")
        sources[destination] = source

    output.mkdir(parents=True, exist_ok=True)
    for destination, source in sources.items():
        if not destination.exists():
            shutil.copyfile(source, destination)
    return list(sources)
