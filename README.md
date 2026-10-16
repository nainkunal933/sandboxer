# Sandboxer

Sandboxer is a context aware CLI that generates the data needed for your sandbox.

## API keys

Standalone CLI mode requires an API key for the selected model provider. Set the
standard environment variable for each provider you want to use:

| Provider | Environment variable |
| --- | --- |
| OpenAI | `OPENAI_API_KEY` |
| Claude (Anthropic) | `ANTHROPIC_API_KEY` |

To use both providers, configure both variables. Only the selected provider's key
is required for a given request.

For PowerShell session:

```powershell
$env:OPENAI_API_KEY = "your-openai-api-key"
$env:ANTHROPIC_API_KEY = "your-anthropic-api-key"
```

For Linux or macOS terminal session (Bash or Zsh):

```sh
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

When Sandboxer is used through MCP from Codex or Claude Code, the host manages its
own model authentication. Sandboxer API keys are needed only if Sandboxer makes
direct calls to a model provider.

The provider adapters are currently scaffolds; API key loading and model calls
have not yet been implemented.

## Run from source

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.12.23 or newer separately
from the project's virtual environment. Then, from the project root, run:

```sh
uv sync --locked
uv run --locked src/main.py
```

## MCP server

Start the local STDIO server with:

```sh
uv run --locked src/main.py mcp
```

The server exposes two tools, both accepting `objective` and optional `values`:

- `analyze`: validates context, prompts for a project folder through MCP elicitation,
  and recursively inventories files in a temporary CSV (`filename,eligible,path`).
  Marks schema candidates eligible by extension; contents are not scanned. Returns
  `inventory_csv_path` and `file_count` alongside the context.
- `generate`: returns a data generation prompt for the host model to execute.

The standalone executable supports `sandboxer mcp` with the same tools.

## Build a standalone executable

Run the build helper with the build dependency group:

```sh
uv run --locked --group build scripts/build.py
```

The output is `dist/sandboxer` on Linux/macOS or `dist/sandboxer.exe`
on Windows. Use `--output-dir PATH` to choose a different destination.
The helper can be run from any working directory; a relative output path is
resolved from that directory. Temporary build files are removed when it exits.

## Verify and run the executable

```sh
./dist/sandboxer --help
./dist/sandboxer --version
./dist/sandboxer
```

On Windows, use `.\dist\sandboxer.exe` instead. Version output is
`sandboxer <version>`; running without arguments displays the welcome screen and
waits for Enter. The standalone executable does not require Python to be
installed. Copy it to a directory on your `PATH` to run it as `sandboxer`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for automated native builds and the release process.
