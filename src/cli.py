import argparse

from rich.align import Align
from rich.console import Console, Group
from rich.text import Text


console = Console()

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
    return parser


def main() -> None:
    """Parse command-line arguments and run the application."""
    create_parser().parse_args()
    show_welcome_screen()
