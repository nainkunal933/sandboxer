"""Generate synthetic CSV data from SQL Server procedure input parameters."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import timezone
from decimal import Decimal, localcontext
from pathlib import Path
import re
from typing import TextIO

from faker import Faker


_SQL_NOISE = re.compile(r"--[^\r\n]*|/\*.*?\*/|'(?:''|[^'])*'", re.DOTALL)
_IDENTIFIER = r"(?:\[(?:[^\]]|\]\])+\]|[A-Za-z_]\w*)"
_PROCEDURE = re.compile(
    rf"\b(?:CREATE(?:\s+OR\s+ALTER)?|ALTER)\s+PROC(?:EDURE)?\s+"
    rf"(?P<name>{_IDENTIFIER}(?:\s*\.\s*{_IDENTIFIER})*)",
    re.IGNORECASE,
)
_PARAMETER = re.compile(
    r"^\s*@(?P<name>[A-Za-z_]\w*)\s+"
    r"(?P<type>\[?\w+\]?)(?:\s*\((?P<arguments>[^)]*)\))?"
    r"(?P<tail>.*)$",
    re.DOTALL,
)
_INTEGER_MAXIMUMS = {
    "tinyint": 255, "smallint": 32767, "int": 2147483647,
    "integer": 2147483647, "bigint": 9223372036854775807,
}


@dataclass(frozen=True, slots=True)
class ProcedureParameter:
    """A procedure parameter, retaining its declared type and output direction."""

    name: str
    sql_type: str
    arguments: tuple[str, ...]
    is_output: bool = False


def read_procedure_names(source: str) -> list[str]:
    """Read declared procedure names while excluding comments and string values."""
    masked = _SQL_NOISE.sub(lambda match: " " * len(match[0]), source)
    return [match["name"] for match in _PROCEDURE.finditer(masked)]


def read_procedure_signature(path: Path) -> tuple[str, list[ProcedureParameter]]:
    """Read one T-SQL procedure's name and parameters for CSV workflows."""
    if path.suffix.lower() != ".sql":
        raise ValueError(f"CSV generation requires a SQL Server procedure file: {path}")
    source = path.read_text(encoding="utf-8-sig")
    masked = _SQL_NOISE.sub(lambda match: " " * len(match[0]), source)
    declarations = list(_PROCEDURE.finditer(masked))
    if len(declarations) != 1:
        raise ValueError(f"Expected exactly one SQL Server procedure in {path.name}.")
    signature = masked[declarations[0].end():]
    body = re.search(r"\bAS\b", signature, re.IGNORECASE)
    if body is None:
        raise ValueError(f"Procedure body delimiter AS is missing in {path.name}.")
    signature = signature[:body.start()].strip()
    parameters = []
    seen_names = set()
    for declaration in re.split(r",\s*(?=@)", signature):
        match = _PARAMETER.fullmatch(declaration)
        if match is None:
            raise ValueError(f"Unsupported procedure parameter declaration in {path.name}.")
        tail = match["tail"].strip()
        is_output = bool(re.search(r"\b(?:OUT|OUTPUT)\b", tail, re.IGNORECASE))
        if is_output:
            tail = re.sub(r"\b(?:OUT|OUTPUT)\b", "", tail, flags=re.IGNORECASE).strip()
        if (tail and not tail.startswith("=")) or "@" in tail:
            raise ValueError(f"Unsupported parameter syntax for @{match['name']}.")
        name = match["name"]
        if name.lower() in seen_names:
            raise ValueError(f"Duplicate procedure parameter: @{name}")
        seen_names.add(name.lower())
        arguments = tuple(
            argument.strip().lower()
            for argument in (match["arguments"] or "").split(",")
            if argument.strip()
        )
        parameters.append(ProcedureParameter(
            name=name,
            sql_type=match["type"].strip("[]").lower(),
            arguments=arguments,
            is_output=is_output,
        ))
    if not any(not parameter.is_output for parameter in parameters):
        raise ValueError(f"No input parameters found in {path.name}.")
    return declarations[0]["name"], parameters


def _string_generator(
    parameter: ProcedureParameter, fake: Faker, length: int,
) -> Callable[[int], str]:
    """Choose realistic text by field name while honoring the declared length."""
    name = parameter.name.lower().replace("_", "")
    if "password" in name or name.endswith("hash"):
        if length < 64:
            raise ValueError(f"@{parameter.name} cannot fit a synthetic SHA-256 hash.")
        provider = fake.sha256
    elif "email" in name:
        provider = fake.email
    elif "username" in name:
        provider = fake.user_name
    elif "firstname" in name:
        provider = fake.first_name
    elif "lastname" in name:
        provider = fake.last_name
    elif "name" in name:
        provider = fake.name
    elif "phone" in name:
        provider = fake.phone_number
    elif "url" in name or "picture" in name:
        provider = fake.image_url if "picture" in name else fake.url
    elif "address" in name:
        provider = fake.address
    else:
        provider = fake.text

    def value(row_number: int) -> str:
        text = provider()[:length]
        if parameter.sql_type in {"char", "nchar"}:
            text = text.ljust(length)
        return text

    return value


def value_generator(
    parameter: ProcedureParameter, fake: Faker, record_count: int,
) -> Callable[[int], str]:
    """Compile a supported SQL type into a per-row Faker-backed generator."""
    sql_type, arguments = parameter.sql_type, parameter.arguments
    if sql_type in {"char", "nchar", "varchar", "nvarchar", "text", "ntext", "sysname"}:
        maximum = 4000 if sql_type in {"nchar", "nvarchar"} else 8000
        if sql_type in {"text", "ntext", "sysname"}:
            if arguments:
                raise ValueError(f"Unexpected type dimensions for @{parameter.name}.")
            length = 128 if sql_type == "sysname" else 200
        elif arguments == ("max",) and sql_type in {"varchar", "nvarchar"}:
            length = 200
        else:
            if len(arguments) > 1:
                raise ValueError(f"Invalid string length for @{parameter.name}.")
            length = int(arguments[0]) if arguments else 1
            if not 1 <= length <= maximum:
                raise ValueError(f"Invalid string length for @{parameter.name}.")
        return _string_generator(parameter, fake, length)
    if sql_type in _INTEGER_MAXIMUMS:
        if arguments:
            raise ValueError(f"Unexpected type dimensions for @{parameter.name}.")
        maximum = _INTEGER_MAXIMUMS[sql_type]
        if parameter.name.lower() == "id" or parameter.name.endswith("ID") or parameter.name.lower().endswith("_id"):
            if record_count > maximum:
                raise ValueError(f"Record count exceeds the ID range for @{parameter.name}.")
            return lambda row_number: str(row_number)
        return lambda row_number: str(fake.random_int(min=0, max=maximum))
    if sql_type in {"decimal", "numeric", "money", "smallmoney"}:
        if sql_type in {"money", "smallmoney"}:
            if arguments:
                raise ValueError(f"Unexpected type dimensions for @{parameter.name}.")
            precision, scale = 19, 4
            maximum = 9223372036854775807 if sql_type == "money" else 2147483647
        else:
            if len(arguments) > 2:
                raise ValueError(f"Invalid decimal dimensions for @{parameter.name}.")
            precision = int(arguments[0]) if arguments else 18
            scale = int(arguments[1]) if len(arguments) == 2 else 0
            if not 1 <= precision <= 38 or not 0 <= scale <= precision:
                raise ValueError(f"Invalid decimal dimensions for @{parameter.name}.")
            maximum = 10**precision - 1

        def decimal_value(row_number: int) -> str:
            with localcontext() as context:
                context.prec = precision
                number = Decimal(fake.random_int(min=0, max=maximum)).scaleb(-scale)
                return format(number, f".{scale}f")

        return decimal_value
    if sql_type in {"float", "real"}:
        if arguments and (sql_type == "real" or len(arguments) != 1 or not 1 <= int(arguments[0]) <= 53):
            raise ValueError(f"Invalid floating-point precision for @{parameter.name}.")
        return lambda row_number: str(fake.pyfloat(left_digits=5, right_digits=6, positive=True))
    if sql_type in {"datetime2", "datetimeoffset", "time"}:
        if len(arguments) > 1:
            raise ValueError(f"Invalid time precision for @{parameter.name}.")
        scale = int(arguments[0]) if arguments else 7
        if not 0 <= scale <= 7:
            raise ValueError(f"Invalid time precision for @{parameter.name}.")
    else:
        if arguments:
            raise ValueError(f"Unexpected type dimensions for @{parameter.name}.")
        scale = 3 if sql_type == "datetime" else 0
    if sql_type in {"date", "datetime", "datetime2", "datetimeoffset", "smalldatetime", "time"}:
        def date_value(row_number: int) -> str:
            value = fake.date_time(tzinfo=timezone.utc if sql_type == "datetimeoffset" else None)
            if sql_type == "date":
                return value.date().isoformat()
            if sql_type == "smalldatetime":
                value = value.replace(second=0, microsecond=0)
            text = value.strftime("%H:%M:%S" if sql_type == "time" else "%Y-%m-%dT%H:%M:%S")
            if scale:
                text += "." + (f"{value.microsecond:06d}" + "0")[:scale]
            return text + ("+00:00" if sql_type == "datetimeoffset" else "")

        return date_value
    if sql_type == "bit":
        return lambda row_number: str(int(fake.pybool()))
    if sql_type == "uniqueidentifier":
        return lambda row_number: fake.uuid4()
    raise ValueError(f"Unsupported SQL datatype {sql_type!r} for @{parameter.name}.")


def open_csv(procedure: Path) -> tuple[Path, TextIO]:
    """Create a CSV alongside the source, choosing a free name on repeated runs."""
    index = 1
    while True:
        suffix = "" if index == 1 else f"_{index}"
        destination = procedure.with_name(f"{procedure.stem}{suffix}.csv")
        try:
            return destination, destination.open("x", encoding="utf-8", newline="")
        except FileExistsError:
            index += 1
