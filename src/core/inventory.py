"""List project files without reading their contents."""

import csv
import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

from .schemas import FileInventoryEntry


_SCHEMA_CANDIDATE_EXTENSIONS = frozenset({
    # Schema and definition formats.
    ".sql", ".ddl", ".cql", ".prisma", ".dbml", ".avsc", ".avdl",
    ".proto", ".graphql", ".gql", ".xsd",
    # Structured documents.
    ".json", ".jsonc", ".json5", ".yaml", ".yml", ".xml",
    # Common ORM and model sources.
    ".py", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts",
    ".java", ".kt", ".cs", ".go", ".rb", ".php", ".scala",
})


def _is_schema_candidate(path: Path) -> bool:
    """Identify potential schema sources by extension without reading contents."""
    return path.suffix.lower() in _SCHEMA_CANDIDATE_EXTENSIONS


def _iter_files(root: Path, output_directory: Path) -> Iterator[FileInventoryEntry]:
    """Walk directories in a stable order without following directory links."""
    directories = [root]
    while directories:
        directory = directories.pop()
        with os.scandir(directory) as iterator:
            entries = sorted(iterator, key=lambda item: item.name)
        children = []
        for entry in entries:
            path = Path(entry.path)
            if path == output_directory:
                continue
            if entry.is_dir(follow_symlinks=False):
                if not path.is_junction():
                    children.append(path)
            elif entry.is_file():
                yield FileInventoryEntry(
                    filename=entry.name,
                    path=path.relative_to(root).as_posix(),
                    eligible=_is_schema_candidate(path),
                )
        directories.extend(reversed(children))


def create_file_inventory(project_root: Path) -> tuple[Path, int]:
    """Write a persistent temporary CSV and return its path and file count.

    Eligibility marks potential schema sources by extension only; file contents
    are not read. A failed inventory is removed rather than returned as a complete
    result. Completed inventories are left for the caller.
    """
    root = project_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"Project root must be a directory: {root}")

    output_directory = None
    csv_path = None
    try:
        output_directory = Path(tempfile.mkdtemp(prefix="sandboxer-inventory-")).resolve()
        csv_path = output_directory / "file_inventory.csv"
        count = 0
        with csv_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("filename", "eligible", "path"))
            for entry in _iter_files(root, output_directory):
                writer.writerow((entry.filename, str(entry.eligible).lower(), entry.path))
                count += 1
        return csv_path, count
    except Exception as error:
        failure = OSError(f"Could not create file inventory for '{root}': {error}")
        try:
            if csv_path is not None:
                csv_path.unlink(missing_ok=True)
            if output_directory is not None:
                output_directory.rmdir()
        except OSError as cleanup_error:
            failure.add_note(f"Could not remove incomplete inventory: {cleanup_error}")
        raise failure from error
