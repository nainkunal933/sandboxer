"""Package sandboxer as a standalone executable for the current platform."""

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", type=Path, default=Path("dist"),
        help="Executable output directory (default: dist in the current directory)",
    )
    args = parser.parse_args()
    entrypoint = Path(__file__).resolve().parents[1] / "src" / "main.py"
    output_dir = args.output_dir.resolve()
    with tempfile.TemporaryDirectory(prefix="sandboxer-build-") as build_dir:
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--noconfirm", "--clean", "--onefile", "--console",
            "--name", "sandboxer",
            "--distpath", str(output_dir),
            "--workpath", str(Path(build_dir) / "work"),
            "--specpath", build_dir,
            str(entrypoint),
        ])
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
