from .output_formatter import (
    console,
    detect_theme,
    ThemeColors,
    c,
)


def get_user_input():
    """Get search terms from user. Returns tuple of (query, terms, theme) or None for exit."""
    try:
        prompt = f"\n[{c('accent_blue')}][bold]❯[/bold][/{c('accent_blue')}] "
        query = console.input(prompt)
    except KeyboardInterrupt:
        console.print(
            f"\n\n[{c('accent_blue')}]Goodbye! Happy researching with ACHEM![/{c('accent_blue')}]\n"
        )
        return None

    if query.strip():
        terms = [t.strip() for t in query.split(",") if t.strip()]
        if terms:
            theme = detect_theme(terms[0])
            return query, terms, theme

    return "", [], ThemeColors.DEFAULT
