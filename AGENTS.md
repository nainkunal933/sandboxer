# Agent guide for Sandboxer

This file applies to the entire repository. Keep it aligned with the code.

## Project and architecture

Sandboxer is a Python CLI and local MCP server for preparing sandbox data.
Python 3.12 is selected by `.python-version`; `pyproject.toml` requires Python
3.12 or newer and uv 0.12.23 or newer.

- `src/main.py` delegates to `src/cli.py`, which handles argparse, the Rich UI,
  environment loading, provider selection, and MCP startup.
- `src/core/` owns shared context validation, domain models, file inventory, and
  generation prompts. Put reusable business logic here rather than in entry points.
- `src/mcp_integration/` owns MCP tool registration, tool wrappers, and project-root
  elicitation. Keep MCP-specific dependencies and behavior in this layer.
- `src/agent/` owns provider-independent conversation state and request routing.
  `src/models/` defines adapter contracts and provider implementations. The OpenAI
  and Anthropic adapters currently raise errors because they are placeholders.
- `examples/blog/` contains a SQL Server example with table definitions, stored
  procedures, and Docker setup. `entrypoint.sh` waits for SQL Server, then runs
  `init.sql` with sqlcmd to create the Blog database and missing
  tables in foreign key order on startup. Initialization failures stop the
  container; existing tables and data are preserved. See `examples/README.md`
  for its commands.
- `examples/shopping_cart/` contains a MongoDB example with JSON schema files.
  Its entrypoint waits for MongoDB, then runs `data/create_collections.py` to create
  collections or update validators. Setup failures stop the container; existing
  data is preserved. It is an independent, non-packaged uv project with its own
  `pyproject.toml`, `uv.lock`, and local `.venv`. From `examples/shopping_cart`, run
  `uv sync --locked` to install dependencies, then
  `uv run --locked data/create_collections.py` to initialize a running MongoDB
  instance. Docker installs the same locked dependencies; Python and PyMongo are
  bundled in the image.

## Development commands

Run these from the repository root. Use the project's environment; when IDE
interpreter tools are available, check the configured interpreter before invoking
Python tooling. Dependencies and versions are defined in `pyproject.toml` and
`uv.lock`. Keep both consistent when intentionally changing dependencies.

```sh
uv sync --locked
uv run --locked src/main.py --help
uv run --locked src/main.py --version
uv run --locked src/main.py mcp
```

Running `src/main.py` without arguments opens an interactive welcome screen and
waits for Enter. The `configure` command is also interactive. Prefer `--help` and
`--version` for unattended CLI smoke checks. MCP mode is a long-running STDIO
server; exercise it with an MCP client rather than expecting it to exit unaided.

To build and check the standalone executable:

```sh
uv sync --locked --group build
uv pip check
uv run --locked --group build scripts/build.py
```

The executable is `dist/sandboxer` on Linux/macOS and `dist/sandboxer.exe` on
Windows. The build script accepts `--output-dir PATH` and bundles version metadata
from `pyproject.toml`. Keep path handling and packaging portable across platforms.

## Inventory and MCP contracts

- `create_file_inventory()` in `src/core/inventory.py` returns a persistent
  temporary CSV path and file count. Completed output belongs to the caller;
  incomplete output is removed on failure.
- Keep CSV columns `filename,eligible,path`, lowercase `true`/`false`, and paths
  relative to the project root using forward slashes. Counts include every
  inventoried file, including ineligible files.
- Eligibility is a broad candidate filter using `Path.suffix.lower()` and the
  centralized `_SCHEMA_CANDIDATE_EXTENSIONS` allowlist. It does not read contents
  or confirm that a file contains a schema. Ordinary source files, documents, and
  stored procedures can qualify. Unsupported and extensionless files remain false.
- Preserve stable traversal order, avoidance of directory symlinks and junctions,
  and exclusion of the current inventory's output directory.
- `analyze` validates context, resolves the project root through elicitation,
  creates `.sandboxer/`, and returns the inventory path, count, context, and schema
  analysis prompt for the host agent to write `.sandboxer/schema.md`. The bundled
  `.schemaignore` excludes `.sandboxer/` artifacts from the inventory.
  The document has four H2 sections: Database metadata, Structure, Population, and
  Procedure references. Database metadata contains Data model, Engine, and a
  Databases array of all source-declared names, deduplicated in discovery order
  (empty when none are known), without selecting a target. Data model values come
  from the Python DataModel enum rendered into the prompt: relational, document,
  key_value, graph, wide_column, vector, and time_series. Classification uses
  inspected structures and usage, allowing multiple models when demonstrated
  and stating uncertainty rather than guessing. Re-analysis replaces the old
  Scope and engine section and removes its scope narrative.
  Population details only create/insert procedures or
  equivalent application methods. Other operations are listed in a compact
  reference table with target, qualified name, operation, and source path; omit
  their parameter tables and detailed behavior. Re-analysis replaces old
  read/update/delete details with references, including shared behavior specific
  to those operations. Inspect creation bodies fully and other operations only
  enough to verify their classification and references, never by filename alone.
  Before calling `generate`, the host agent reads Database metadata and Structure
  in `.sandboxer/schema.md` to prepare actual table/collection `target_options`.
  It supplies required `data_model` (a DataModel enum value) and `engine`
  (a trimmed, non-empty string) for those targets. Group targets into separate
  calls for different model/engine pairs; resolve undetermined classifications
  from source or user input before calling rather than guessing. MCP validates
  these arguments before elicitation or staging. They carry metadata only;
  strategy dispatch and generation behavior remain unchanged.
  It reads Population to identify procedure source paths and supplies the root
  from `analyze` plus `target_procedures`, a mapping from exact target names to
  root-relative create/insert procedure file paths (empty lists for targets without
  creation procedures). Exclude read/update/delete procedures even when older
  documents detail them in Population; Procedure references are guidance only.
  `generate` validates the root without folder elicitation, trims and deduplicates
  the non-empty options, and elicits one of them. After selection,
  Python copies only that target's mapped files unchanged into
  `.sandboxer/generate/`, preserving filenames. Sources and destinations are
  validated before copying; identical existing copies are reused, while missing
  sources, paths outside the root, and filename/content conflicts fail without
  overwriting existing files. Previously staged files are not deleted.
  Duplicate source paths are copied once. Only after copying succeeds, the tool
  asks for a record count with ordered choices 10, 50, 100, and Custom. Custom
  asks for a positive whole number with no application-imposed upper limit.
  Context values do not skip count elicitation. Decline/cancel aborts completion
  without a default count; staged files remain. Preparation is a resolver
  dependency of count elicitation and reuses identical files on MCP retries.
  The tool returns `project_root`, `target`, `objective`, `values`, `copied_files`
  (destination paths, including reused copies), integer `record_count`, and
  `csv_files`. After count acceptance, Python uses Faker to stream exactly that
  many data rows per copied SQL Server Create procedure into CSV files beside
  the staged sources. Headers are input parameter names without `@`, preserving
  declaration order; output parameters are excluded. Supported types include
  character strings with length bounds, integers, bit, decimal/numeric, money,
  float/real, date/time types, and uniqueidentifier. Unsupported signatures or
  types fail explicitly. Integer ID fields use sequential values starting at 1;
  password fields contain synthetic SHA-256 placeholder hashes, not plaintext.
  Table relationships and application-specific hash formats are not inferred.
  Each CSV is named `<procedure stem>.csv`, with numeric suffixes on repeat runs
  to preserve existing files. Incomplete outputs are removed on failure.
  The count is elicited, not a caller-supplied tool argument. The tool does not
  parse schema.md, scan for related files, return a prompt, or execute SQL.
  No arbitrary option-count limit is imposed.
  Changes to tool arguments, return fields, CSV format, or content-scanning
  behavior must be intentional and documented.
- Keep MCP stdout reserved for protocol traffic; send diagnostic logging to stderr.
  MCP host authentication is separate from direct provider API authentication.
- `populate` is the MCP tool that executes population SQL against the target
  Docker container. It accepts `project_root`, `csv_files`, and `copied_files`
  from the earlier tools, plus a required `database` name from verified schema
  information or user input. It creates `.sandboxer/populate`, lists Docker
  contexts with `docker context ls`, and elicits a context. It then uses explicit
  `docker --context <name> ps --no-trunc` to list running containers and elicits
  a container name. Choices show names, with images in the prompt for context.
  After selection, Python pairs `copied_files` and
  `csv_files` in the order returned by `generate` (one CSV per procedure), and
  writes `.sandboxer/populate/<procedure stem>_Populate_<CSV row count>.sql`.
  Each file includes the copied definition and a new parameterless population
  procedure with one `EXEC` per record. Unicode literals are escaped; SQL Server
  converts values to the source procedure's parameter types. CSV headers must
  match input parameters, in any order; output parameters receive NULL without
  capturing their values. Repeating a count replaces its script;
  other counts are preserved. Complete scripts are staged before replacement
  so CSV errors leave existing scripts intact. It then calls
  `execute_population_sql()` for each generated file, applying its procedure
  definitions and executing its population procedure in the selected context,
  container, and database. It returns `populate_path`, `docker_context`,
  `container_name`, `database`, `sql_files`, and `status="executed"` only after
  all executions succeed. Failures raise a tool error; generated files remain.
  Discovery failures, empty lists, and declined selections abort without a
  default target. Never switch Docker's active context for this workflow.
- `execute_population_sql()` in `src/core/population.py` is the execution helper
  called by the MCP `populate` tool. Supply the SQL file, Docker context,
  container name, and database; the procedure name is optional and defaults to
  the last procedure declared in the generated file, excluding comments and
  string literals. It streams the script and a final `EXEC` through
  `docker exec -i` and sqlcmd in a Linux SQL Server container. Authentication uses
  the container's SQLCMDPASSWORD or MSSQL_SA_PASSWORD without passing a password
  in arguments.
  It captures output and raises on Docker/SQL errors or timeout.

## Implementation conventions

- We are building the MVP. Keep changes focused on the requested functionality
  and avoid speculative features or unnecessary abstractions.
- Do not add automated tests at this stage unless explicitly requested. Use
  focused smoke checks for validation.
- Follow the existing typed Python style: four-space indentation, snake_case
  functions, descriptive docstrings, and `pathlib.Path` for filesystem paths.
- Reuse the existing frozen, slotted dataclasses for immutable domain models and
  Pydantic models for MCP input validation. Keep core logic provider-independent.
- Prefer the standard library and existing dependencies for small changes.
- Keep credentials in environment variables or an untracked `.env`; never include
  secret values in code, documentation, logs, or generated artifacts.
- Leave generated binaries, build output, caches, and local IDE files untracked.
- Update `README.md` only with explicit developer permission. A code change alone
  does not authorize a README update; do not update it routinely with each edit.
- The README is the repository's quick-start guide. Keep approved edits very
  succinct and focused on what users need to install, configure, and run Sandboxer.
  Leave implementation details and exhaustive feature lists out of the README.

## Validation and delivery

- There is currently no committed automated test suite or configured lint/type
  checker. Do not claim a test or lint command exists without checking configuration.
- Run checks proportionate to the change and report what passed or could not run.
  Use `git diff --check` for whitespace validation and review the final diff.
- For inventory changes, smoke-check eligible and ineligible extensions, uppercase
  extensions, extensionless files, final-suffix matching (`schema.sql.bak`), nested
  relative paths, stable ordering, exact counts, and absence of content reads.
  The blog example has 21 SQL files: four table definitions, 16 stored procedures,
  and `init.sql`; all are eligible under the broad candidate policy.
- Use temporary fixtures and remove verification output after checking it. For
  entry-point or packaging changes, check `--help` and `--version` and build when
  relevant. Documentation-only changes do not require rebuilding the executable.
- PR CI checks dependencies and builds native executables for Linux x86_64,
  Windows x86_64, and macOS arm64/x86_64. Release automation runs on `main`; follow
  `CONTRIBUTING.md` for release labels and versioning.
