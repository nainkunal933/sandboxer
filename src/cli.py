import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from rich.align import Align
from rich.console import Console, Group
from rich.prompt import Prompt
from rich.text import Text


console = Console()

PROVIDERS = ("OpenAI", "Claude")
API_KEY_VARIABLES = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")

LETTER_PATTERNS = {
    "A": (" ███ ", "█   █", "█████", "█   █", "█   █"),
    "B": ("████ ", "█   █", "████ ", "█   █", "████ "),
    "D": ("████ ", "█   █", "█   █", "█   █", "████ "),
    "E": ("█████", "█    ", "████ ", "█    ", "█████"),
    "N": ("█   █", "██  █", "█ █ █", "█  ██", "█   █"),
    "O": (" ███ ", "█   █", "█   █", "█   █", " ███ "),
    "R": ("████ ", "█   █", "████ ", "█  █ ", "█   █"),
    "S": ("█████", "█    ", "█████", "    █", "█████"),
    "X": ("█   █", " █ █ ", "  █  ", " █ █ ", "█   █"),
}


def render_banner(message: str) -> str:
    """Render a message using large block letters."""
    return "\n".join(
        "  ".join(LETTER_PATTERNS[letter][row] for letter in message)
        for row in range(5)
    )


def show_welcome_screen() -> None:
    """Display the Rich welcome screen and wait for the user."""
    heading = Text.assemble(
        ("✦ ", "bold bright_blue"),
        ("Welcome to ", "white"),
        ("SANDBOXER", "bold bright_blue"),
        ("!", "white"),
    )
    banner = Text(render_banner("SANDBOXER"), style="bold bright_blue")
    status = Text("✓ Ready. Press Enter to continue", style="bold blue")
    content = Group(
        Align.center(heading),
        Text(""),
        Align.center(banner),
        Text(""),
        Align.center(status),
    )
    console.print(content)
    console.input("[bold bright_blue]>[/bold bright_blue] ")


def configure() -> None:
    """Let the user select the model provider to configure."""
    provider = Prompt.ask(
        "[bold bright_blue]Select a provider[/bold bright_blue]",
        choices=list(PROVIDERS),
        default=PROVIDERS[0],
        case_sensitive=False,
        console=console,
    )
    console.print(f"[bold blue]Selected provider:[/bold blue] {provider}")


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="sandboxer",
        description=(
            "Sandboxer is a context aware CLI that generates the data needed "
            "for your sandbox"
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser(
        "configure",
        help="Configure a model provider.",
        description="Select a model provider to configure.",
    )
    return parser


def main() -> None:
    """Parse command-line arguments and run the application."""
    load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)
    parser = create_parser()
    args = parser.parse_args()
    if args.command == "configure":
        missing_keys = [
            name for name in API_KEY_VARIABLES if not os.getenv(name, "").strip()
        ]
        if missing_keys:
            parser.exit(
                status=1,
                message=(
                    f"sandboxer: error: Missing API keys: {', '.join(missing_keys)}.\n"
                    "Refer to the Sandboxer README.md and add the API keys to the "
                    "project's .env file or your environment variables.\n"
                ),
            )
        configure()
        return

    show_welcome_screen()
