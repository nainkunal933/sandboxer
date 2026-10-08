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

On Windows, use `.\dist\sandboxer.exe` instead. Version output should be
`sandboxer 0.1.0`; running without arguments displays the welcome screen and
waits for Enter. The standalone executable does not require Python to be
installed. Copy it to a directory on your `PATH` to run it as `sandboxer`.

## Automated native builds

The **Build executables** GitHub Actions workflow runs on pull requests,
pushes to `main`, and manual dispatch. It installs the locked build dependencies
with uv and builds each executable
on a native runner, then uploads an archive containing the executable, this
README, and the license:

| Artifact | Target |
| --- | --- |
| `sandboxer-linux-x86_64` | Linux x86_64, glibc 2.35 or newer (Ubuntu 22.04 baseline) |
| `sandboxer-windows-x86_64` | Windows x86_64 |
| `sandboxer-macos-arm64` | macOS 15 or newer, Apple Silicon |
| `sandboxer-macos-x86_64` | macOS 15 or newer, Intel |

Download an artifact from a successful workflow run and extract both the
GitHub artifact wrapper and the archive inside it. Windows uses ZIP; Linux
and macOS use tar.gz to retain executable permissions. These are portable
executables, not OS installer packages. Artifacts expire after 30 days; the
workflow does not publish a GitHub Release.
