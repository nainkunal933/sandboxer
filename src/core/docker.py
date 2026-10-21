"""Discover Docker contexts and their running containers through the Docker CLI."""

import json
import subprocess


def _run_docker(arguments: list[str]) -> str:
    """Capture Docker output without a shell or MCP stdout traffic."""
    try:
        result = subprocess.run(
            ["docker", *arguments], capture_output=True, text=True,
            check=True, timeout=30,
        )
    except FileNotFoundError as error:
        raise ValueError("Docker CLI is not installed or is not on PATH.") from error
    except subprocess.TimeoutExpired as error:
        raise ValueError("Docker discovery timed out after 30 seconds.") from error
    except subprocess.CalledProcessError as error:
        raise ValueError(f"Docker discovery failed: {error.stderr.strip()}") from error
    return result.stdout


def list_docker_contexts() -> list[str]:
    """List configured Docker environments without connecting to every daemon."""
    output = _run_docker(["context", "ls", "--format", "{{.Name}}"])
    return list(dict.fromkeys(line.strip() for line in output.splitlines() if line.strip()))


def list_running_containers(docker_context: str) -> list[dict[str, str]]:
    """List running containers in the selected context, retaining full IDs."""
    output = _run_docker([
        "--context", docker_context, "ps", "--no-trunc", "--format", "{{json .}}",
    ])
    containers = []
    for line in output.splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            container = {key: item[key] for key in ("ID", "Names", "Image")}
            if not all(isinstance(value, str) and value for value in container.values()):
                raise ValueError("Missing container details.")
        except (ValueError, KeyError, TypeError) as error:
            raise ValueError("Docker returned invalid container details.") from error
        containers.append(container)
    return containers
