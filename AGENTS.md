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
  procedures, and Docker setup. See `examples/README.md` for its commands.

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
  The document has four H2 sections: Scope and engine, Structure, Population, and
  Procedure references. Population details only create/insert procedures or
  equivalent application methods. Other operations are listed in a compact
  reference table with target, qualified name, operation, and source path; omit
  their parameter tables and detailed behavior. Re-analysis replaces old
  read/update/delete details with references, including shared behavior specific
  to those operations. Inspect creation bodies fully and other operations only
  enough to verify their classification and references, never by filename alone.
  Before calling `generate`, the host agent reads Scope and engine and Structure
  in `.sandboxer/schema.md` to prepare actual table/collection `target_options`.
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
  (destination paths, including reused copies), and integer `record_count`.
  The count is elicited, not a caller-supplied tool argument. The tool does not
  parse schema.md, scan for related files, return a prompt, or generate data.
  No arbitrary option-count limit is imposed.
  Changes to tool arguments, return fields, CSV format, or content-scanning
  behavior must be intentional and documented.
- Keep MCP stdout reserved for protocol traffic; send diagnostic logging to stderr.
  MCP host authentication is separate from direct provider API authentication.

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
