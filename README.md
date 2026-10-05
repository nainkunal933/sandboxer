# sandboxer

A small command-line application with a Rich welcome screen.

## Run from source

Use Python 3.12 and install the pinned dependencies in a virtual environment:

```sh
python -m venv .venv
```

On Linux and macOS:

```sh
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/main.py
```

On Windows (PowerShell):

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe src\main.py
```

## Build a standalone executable

Run the build helper using the virtual environment's Python:

```sh
# Linux and macOS
.venv/bin/python scripts/build.py
```

```powershell
# Windows
.venv\Scripts\python.exe scripts\build.py
```

The output is `dist/sandboxer` on Linux/macOS or `dist/sandboxer.exe`
on Windows. Use `--output-dir PATH` to choose a different destination.
The helper can be run from any working directory; a relative output path is
resolved from that directory. Temporary build files are removed when it exits.

PyInstaller builds for the current operating system and architecture. Build
Windows, Linux, and macOS executables on native machines for each target;
this helper does not cross-compile. Linux executables require a compatible
glibc version (build on the oldest Linux version you intend to support).
The executables are unsigned; code signing and macOS notarization require
separate release credentials.

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
pushes to `main`, and manual dispatch. It builds and smoke-tests each executable
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

Run the same smoke checks locally with the virtual environment's Python:

```sh
.venv/bin/python scripts/smoke_test.py dist/sandboxer
```

On Windows use `.venv\Scripts\python.exe scripts\smoke_test.py dist\sandboxer.exe`.
The smoke test runs from a temporary directory outside the checkout and verifies
help, version, welcome/Enter input, and invalid-option exit status.
