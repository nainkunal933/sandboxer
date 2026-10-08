"""Package sandboxer as a standalone executable for the current platform."""

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
import re
import shutil


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", type=Path, default=Path("dist"),
        help="Executable output directory (default: dist in the current directory)",
    )
    parser.add_argument("--version", help="Semantic version embedded in the executable")
    args = parser.parse_args()
    if args.version and not re.fullmatch(
        r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
        r"(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?"
        r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?", args.version
    ):
        parser.error("--version must be a valid semantic version")
    entrypoint = Path(__file__).resolve().parents[1] / "src" / "main.py"
    output_dir = args.output_dir.resolve()
    with tempfile.TemporaryDirectory(prefix="sandboxer-build-") as build_dir:
        source_dir = Path(build_dir) / "src"
        shutil.copytree(entrypoint.parent, source_dir, ignore=shutil.ignore_patterns("__pycache__"))
        if args.version:
            (source_dir / "_version.py").write_text(f"VERSION = {args.version!r}\n", encoding="utf-8")
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--noconfirm", "--clean", "--onefile", "--console",
            "--name", "sandboxer",
            "--distpath", str(output_dir),
            "--workpath", str(Path(build_dir) / "work"),
            "--specpath", build_dir,
            str(source_dir / "main.py"),
        ])
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
