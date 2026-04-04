import os
import sys
import subprocess
from enum import Enum
from typing import Optional


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
    """Print exit message."""
    print("\n👋 Goodbye! Thanks for using ACHEM.\n")
    sys.exit(0)


def print_help():
    """Print help message."""
    help_text = """
╔══════════════════════════════════════════════════════════════╗
║                       ACHEM Commands                        ║
╠══════════════════════════════════════════════════════════════╣
║  clear, cls     - Clear the screen                       ║
║  exit, quit, q  - Exit the program                       ║
║  export, save   - Export last summary to file             ║
║  help, ?        - Show this help message                  ║
║  version, v     - Show version info                       ║
╠══════════════════════════════════════════════════════════════╣
║  Just type your search query to get started!               ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(help_text)


def print_version():
    """Print version info."""
    from .output_formatter import VERSION

    print(f"\n📦 ACHEM v{VERSION}\n")
