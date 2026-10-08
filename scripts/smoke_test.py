"""Verify the shipped executable without importing the application's source."""

import argparse
from pathlib import Path
import subprocess
import tempfile
import runpy


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("executable", type=Path)
    parser.add_argument("--version", help="Expected embedded version")
    args = parser.parse_args()
    executable = args.executable.resolve()
    version = args.version or runpy.run_path(str(Path(__file__).resolve().parents[1] / "src/_version.py"))["VERSION"]
    with tempfile.TemporaryDirectory(prefix="sandboxer-smoke-") as cwd:
        cases = [
            (["--version"], f"sandboxer {version}", 0),
            (["--help"], "usage: sandboxer", 0),
            ([], "Ready. Press Enter to continue", 0),
            (["--invalid-option"], "unrecognized arguments", 2),
        ]
        for args, expected, exit_code in cases:
            result = subprocess.run(
                [str(executable), *args], input=b"\n", capture_output=True,
                cwd=cwd, timeout=60,
            )
            output = result.stdout + result.stderr
            matches = expected.encode() in output
            if args == ["--version"]:
                matches = result.stdout.strip() == expected.encode()
            if result.returncode != exit_code or not matches:
                raise RuntimeError(
                    f"Smoke check {args} failed: exit={result.returncode}, "
                    f"output={output!r}"
                )
            print(f"Passed: {args or ['welcome and Enter input']}")


if __name__ == "__main__":
    main()
