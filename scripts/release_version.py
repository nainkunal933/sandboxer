"""Generate a monotonically increasing prerelease version for a workflow run."""

import argparse
from pathlib import Path
import re
import runpy


def release_version(base: str, sequence: int) -> str:
    match = re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)-([a-zA-Z][a-zA-Z0-9-]*)\.(0|[1-9]\d*)", base)
    if not match or sequence < 1:
        raise ValueError("Automatic releases require a prerelease base (e.g. 0.1.0-alpha.0) and a positive sequence")
    return f"{'.'.join(match.groups()[:3])}-{match[4]}.{sequence}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sequence", type=int, required=True)
    args = parser.parse_args()
    base = runpy.run_path(str(Path(__file__).resolve().parents[1] / "src/_version.py"))["VERSION"]
    print(release_version(base, args.sequence))


if __name__ == "__main__":
    main()
