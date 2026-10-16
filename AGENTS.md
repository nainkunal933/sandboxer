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
- `analyze` validates context, resolves the project root through elicitation, and
  returns the inventory path, count, and context. `generate` returns a prompt for
  the host model to execute. Changes to tool arguments, return fields, CSV format,
  or content-scanning behavior must be intentional and documented.
- Keep MCP stdout reserved for protocol traffic; send diagnostic logging to stderr.
  MCP host authentication is separate from direct provider API authentication.

## Implementation conventions

- We are building the MVP. Keep changes focused on the requested functionality
  and avoid speculative features or unnecessary abstractions.
- Adding tests for every edit is not required during the MVP phase. Add tests
  when explicitly requested or when they provide meaningful coverage for complex
  or high-impact behavior; use focused smoke checks for routine changes.
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
