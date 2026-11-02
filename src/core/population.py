"""Build and execute population procedures from staged Create procedures and CSVs."""

import csv
from pathlib import Path
import re
import subprocess
from uuid import uuid4

from .generation_strategies.sqlserver_generation import (
    read_procedure_names,
    read_procedure_signature,
)


def _staged_input(root: Path, path: str, suffix: str) -> Path:
    """Resolve an input file returned by generate inside its staging folder."""
    source = (root / path).resolve(strict=True)
    directory = (root / ".sandboxer" / "generate").resolve(strict=True)
    if not directory.is_relative_to(root) or not source.is_relative_to(directory):
        raise ValueError("Population inputs must be inside .sandboxer/generate.")
    if not source.is_file() or source.suffix.lower() != suffix:
        raise ValueError(f"Expected a {suffix} input file: {source}")
    return source


def create_population_sql(
    project_root: Path, copied_files: list[str], csv_files: list[str],
) -> list[Path]:
    """Write <procedure stem>_Populate_<CSV row count>.sql for each ordered pair.

    Each script contains the copied definition and a new, parameterless population
    procedure with one EXEC per CSV record. Values are escaped Unicode literals;
    SQL Server converts them to the Create procedure's declared input types.
    Stage complete scripts before replacing matching files, preserving other
    dataset sizes and leaving existing scripts intact if CSV validation fails.
    """
    if not copied_files or len(copied_files) != len(csv_files):
        raise ValueError("Supply one CSV per copied procedure, in the order returned by generate.")
    root = project_root.resolve(strict=True)
    output = (root / ".sandboxer" / "populate").resolve()
    if not output.is_relative_to(root):
        raise ValueError("The populate directory must be inside the project root.")
    output.mkdir(parents=True, exist_ok=True)
    pending: dict[Path, Path] = {}
    temporary_files = []
    try:
        for procedure_path, csv_path in zip(copied_files, csv_files, strict=True):
            procedure = _staged_input(root, procedure_path, ".sql")
            data_file = _staged_input(root, csv_path, ".csv")
            name, all_parameters = read_procedure_signature(procedure)
            parameters = [parameter for parameter in all_parameters if not parameter.is_output]
            names = [parameter.name for parameter in parameters]
            with data_file.open(encoding="utf-8-sig", newline="") as data:
                reader = csv.reader(data, strict=True)
                header = next(reader, None)
                if header is None or len(header) != len(names) or set(header) != set(names):
                    raise ValueError(f"CSV headers must match the input parameters of {procedure.name}.")
                columns = [header.index(parameter) for parameter in names]
                count = sum(1 for _ in reader)
                if not count:
                    raise ValueError(f"CSV contains no data records: {data_file.name}")
                suffix = f"_Populate_{count}"
                destination = output / f"{procedure.stem}{suffix}.sql"
                if destination.is_symlink() or (destination.exists() and not destination.is_file()):
                    raise ValueError(f"Population output must be a regular file: {destination}")
                if destination in pending:
                    raise ValueError(f"Multiple input pairs target the same output: {destination.name}")
                population_name = name[:-1] + suffix + "]" if name.endswith("]") else name + suffix
                temporary = output / f".populate-{uuid4().hex}.tmp"
                with temporary.open("x", encoding="utf-8", newline="\n") as stream:
                    temporary_files.append(temporary)
                    stream.write(procedure.read_text(encoding="utf-8-sig").rstrip() + "\nGO\n\n")
                    stream.write(
                        f"CREATE OR ALTER PROCEDURE {population_name}\nAS\nBEGIN\n"
                        "    SET NOCOUNT ON;\n    SET XACT_ABORT ON;\n\n"
                    )
                    data.seek(0)
                    reader = csv.reader(data, strict=True)
                    next(reader)
                    written = 0
                    for row in reader:
                        if len(row) != len(header):
                            raise ValueError(f"CSV record {written + 1} has the wrong number of fields.")
                        arguments = []
                        for parameter, column in zip(parameters, columns, strict=True):
                            value = row[column].replace("'", "''")
                            arguments.append(f"        @{parameter.name} = N'{value}'")
                        arguments.extend(
                            f"        @{parameter.name} = NULL"
                            for parameter in all_parameters if parameter.is_output
                        )
                        stream.write(f"    EXEC {name}\n" + ",\n".join(arguments) + ";\n\n")
                        written += 1
                    if written != count:
                        raise ValueError("CSV record count changed while creating the population script.")
                    stream.write("END;\nGO\n")
                pending[destination] = temporary
        for destination, temporary in pending.items():
            temporary.replace(destination)
        return list(pending)
    except csv.Error as error:
        raise ValueError(f"Invalid CSV data: {error}") from error
    finally:
        for temporary in temporary_files:
            temporary.unlink(missing_ok=True)


def execute_population_sql(
    sql_file: Path,
    docker_context: str,
    container_name: str,
    database: str,
    procedure_name: str | None = None,
    *,
    username: str = "sa",
    timeout: int = 300,
) -> str:
    """Apply a generated SQL file and invoke its population procedure in Docker.

    Pass the elicited context and container name, the target database, and
    optionally the procedure's actual name, e.g. [dbo].[User_Create_Populate_50].
    Otherwise invoke the last procedure declared in the generated SQL file.
    This requires a Linux SQL Server container with /opt/mssql-tools18/bin/sqlcmd.
    Authentication uses SQLCMDPASSWORD or MSSQL_SA_PASSWORD inside the container;
    passwords are never passed in command arguments. SQL is streamed over stdin,
    followed by EXEC for the supplied procedure. Return captured sqlcmd output;
    Docker/SQL failures or timeouts raise ValueError. Calling this writes data.
    """
    if any(not value.strip() for value in (
        docker_context, container_name, database, username,
    )):
        raise ValueError("Docker context, container, database, and username are required.")
    source = Path(sql_file).resolve(strict=True)
    if not source.is_file() or source.suffix.lower() != ".sql":
        raise ValueError("Population execution requires a SQL file.")
    script = source.read_text(encoding="utf-8-sig")
    if procedure_name is None:
        names = read_procedure_names(script)
        if not names:
            raise ValueError("No population procedure found in the generated SQL file.")
        procedure_name = names[-1]
    identifier = r"(?:\[(?:[^\]]|\]\])+\]|[A-Za-z_]\w*)"
    if re.fullmatch(rf"{identifier}(?:\s*\.\s*{identifier})?", procedure_name) is None:
        raise ValueError("Supply a procedure name, optionally qualified with its schema.")
    script += f"\nGO\nEXEC {procedure_name};\nGO\n"
    command = [
        "docker", "--context", docker_context, "exec", "-i", container_name,
        "/bin/sh", "-c",
        'set -eu; '
        'export SQLCMDPASSWORD="${SQLCMDPASSWORD:-${MSSQL_SA_PASSWORD:?'
        'Set SQLCMDPASSWORD or MSSQL_SA_PASSWORD in the container.}}"; '
        'exec /opt/mssql-tools18/bin/sqlcmd -S localhost -U "$1" -d "$2" -C -b -r 1 -x',
        "sandboxer-populate", username, database,
    ]
    try:
        result = subprocess.run(
            command, input=script, capture_output=True, encoding="utf-8",
            check=True, timeout=timeout,
        )
    except FileNotFoundError as error:
        raise ValueError("Docker CLI is not installed or is not on PATH.") from error
    except subprocess.TimeoutExpired as error:
        raise ValueError(f"Population execution timed out after {timeout} seconds.") from error
    except subprocess.CalledProcessError as error:
        raise ValueError(f"Population execution failed: {error.stderr.strip()}") from error
    return result.stdout
