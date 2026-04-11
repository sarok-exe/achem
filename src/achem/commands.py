import os
import sys
from enum import Enum
from rich.console import Console
from rich.table import Table

console = Console()


class Command(Enum):
    """Available commands."""

    SEARCH = "search"
    CLEAR = "clear"
    EXIT = "exit"
    EXPORT = "export"
    HELP = "help"
    VERSION = "version"


COMMAND_ALIASES = {
    "clear": Command.CLEAR,
    "cls": Command.CLEAR,
    "exit": Command.EXIT,
    "quit": Command.EXIT,
    "q": Command.EXIT,
    "bye": Command.EXIT,
    "export": Command.EXPORT,
    "save": Command.EXPORT,
    "download": Command.EXPORT,
    "help": Command.HELP,
    "?": Command.HELP,
    "h": Command.HELP,
    "version": Command.VERSION,
    "ver": Command.VERSION,
    "v": Command.VERSION,
}


def is_command(text: str) -> bool:
    """Check if input is a command."""
    return text.lower().strip() in COMMAND_ALIASES


def parse_command(text: str) -> Command:
    """Parse text into a Command."""
    return COMMAND_ALIASES.get(text.lower().strip(), Command.SEARCH)


def execute_command(command: Command, data: dict = None) -> bool:
    """Execute a command. Returns True if program should continue, False to exit."""
    if command == Command.CLEAR:
        clear_screen()
        return True

    elif command == Command.EXIT:
        print_exit_message()
        return False

    elif command == Command.EXPORT:
        if data:
            from .export_manager import export_summary

            success = export_summary(
                summary=data.get("summary", ""),
                query=data.get("query", ""),
                keywords=data.get("keywords", []),
                source_count=data.get("source_count", 0),
                format=data.get("format", "md"),
            )
            if success:
                return True
        return True

    elif command == Command.HELP:
        print_help()
        return True

    elif command == Command.VERSION:
        print_version()
        return True

    return True


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def print_exit_message():
    """Print exit message with Catppuccin styling."""
    console.print(
        f"\n[{c('accent_blue')}]👋 Goodbye! Thanks for using ACHEM.[/{c('accent_blue')}]\n"
    )
    sys.exit(0)


def print_help():
    """Print help message with Catppuccin styling."""
    from .output_formatter import c, VERSION

    table = Table(
        title="ACHEM Commands",
        show_header=True,
        header_style=f"bold {c('accent_blue')}",
        border_style=c("surface2"),
        title_style=f"bold {c('mauve')}",
    )

    table.add_column("Command", style=f"{c('green')}", width=18)
    table.add_column("Description", style=f"{c('text')}")

    commands = [
        ("clear, cls", "Clear the screen"),
        ("exit, quit, q", "Exit the program"),
        ("export, save", "Export last summary to file"),
        ("help, ?", "Show this help message"),
        ("version, v", "Show version info"),
    ]

    for cmd, desc in commands:
        table.add_row(cmd, desc)

    console.print()
    console.print(table)
    console.print(
        f"\n[{c('overlay0')}]└── Just type your search query to get started![/{c('overlay0')}]\n"
    )


def print_version():
    """Print version info with Catppuccin styling."""
    from .output_formatter import VERSION, c

    console.print(
        f"\n[{c('mauve')}]ACHEM[/{c('mauve')}] [{c('accent_blue')}]v{VERSION}[/{c('accent_blue')}]\n"
    )


def c(name: str) -> str:
    """Get Catppuccin color by name for Rich formatting."""
    from .output_formatter import c as get_color

    return get_color(name)
