"""Verify the shipped executable without importing the application's source."""

import argparse
from pathlib import Path
import subprocess
import tempfile


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("executable", type=Path)
    executable = parser.parse_args().executable.resolve()
    with tempfile.TemporaryDirectory(prefix="sandboxer-smoke-") as cwd:
        cases = [
            (["--version"], "sandboxer 0.1.0", 0),
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
            if result.returncode != exit_code or expected.encode() not in output:
                raise RuntimeError(
                    f"Smoke check {args} failed: exit={result.returncode}, "
                    f"output={output!r}"
                )
            print(f"Passed: {args or ['welcome and Enter input']}")


if __name__ == "__main__":
    main()
