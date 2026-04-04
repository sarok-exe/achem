import sys
from .output_formatter import (
    console,
    detect_theme,
    ThemeColors,
)


def get_user_input():
    """Get search terms from user. Returns tuple of (query, terms, theme) or None for exit."""
    try:
        query = console.input("\n[bold cyan]❯[/bold cyan] ")
    except KeyboardInterrupt:
        console.print("\n\n[cyan]Goodbye! Happy researching with ACHEM![/cyan]\n")
        return None

    if query.strip():
        terms = [t.strip() for t in query.split(",") if t.strip()]
        if terms:
            theme = detect_theme(terms[0])
            return query, terms, theme

    return "", [], ThemeColors.DEFAULT
