import os
import re
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.style import Style
from rich.table import Table
from typing import List, Optional, Callable, Dict
import psutil
import time

console = Console()
VERSION = "1.0.0-stable"


class ThemeColors:
    """Theme color definitions for different search categories."""

    CYBERPUNK = {
        "name": "Cyberpunk",
        "primary": "red",
        "secondary": "black",
        "accent": "bright_red",
        "glow": "bright_red",
    }

    NEON_SCIENCE = {
        "name": "Science",
        "primary": "bright_blue",
        "secondary": "cyan",
        "accent": "bright_cyan",
        "glow": "bright_blue",
    }

    NATURE = {
        "name": "Nature",
        "primary": "green",
        "secondary": "bright_green",
        "accent": "yellow",
        "glow": "bright_green",
    }

    HISTORY = {
        "name": "History",
        "primary": "yellow",
        "secondary": "dark_yellow",
        "accent": "orange3",
        "glow": "bright_yellow",
    }

    ART = {
        "name": "Art",
        "primary": "magenta",
        "secondary": "bright_magenta",
        "accent": "pink",
        "glow": "magenta",
    }

    MUSIC = {
        "name": "Music",
        "primary": "purple",
        "secondary": "bright_purple",
        "accent": "violet",
        "glow": "bright_magenta",
    }

    TECH = {
        "name": "Technology",
        "primary": "cyan",
        "secondary": "bright_cyan",
        "accent": "white",
        "glow": "bright_cyan",
    }

    SPORTS = {
        "name": "Sports",
        "primary": "green",
        "secondary": "bright_green",
        "accent": "yellow",
        "glow": "green",
    }

    FOOD = {
        "name": "Food",
        "primary": "orange",
        "secondary": "bright_red",
        "accent": "yellow",
        "glow": "orange",
    }

    TRAVEL = {
        "name": "Travel",
        "primary": "bright_blue",
        "secondary": "cyan",
        "accent": "white",
        "glow": "bright_blue",
    }

    DEFAULT = {
        "name": "Default",
        "primary": "cyan",
        "secondary": "dim",
        "accent": "white",
        "glow": "cyan",
    }


THEME_KEYWORDS = {
    "cyberpunk": ThemeColors.CYBERPUNK,
    "manga": ThemeColors.CYBERPUNK,
    "anime": ThemeColors.CYBERPUNK,
    "japan": ThemeColors.CYBERPUNK,
    "gaming": ThemeColors.CYBERPUNK,
    "video games": ThemeColors.CYBERPUNK,
    "science": ThemeColors.NEON_SCIENCE,
    "physics": ThemeColors.NEON_SCIENCE,
    "chemistry": ThemeColors.NEON_SCIENCE,
    "biology": ThemeColors.NEON_SCIENCE,
    "quantum": ThemeColors.NEON_SCIENCE,
    "space": ThemeColors.NEON_SCIENCE,
    "nasa": ThemeColors.NEON_SCIENCE,
    "nature": ThemeColors.NATURE,
    "animal": ThemeColors.NATURE,
    "plant": ThemeColors.NATURE,
    "ecology": ThemeColors.NATURE,
    "history": ThemeColors.HISTORY,
    "war": ThemeColors.HISTORY,
    "ancient": ThemeColors.HISTORY,
    "empire": ThemeColors.HISTORY,
    "art": ThemeColors.ART,
    "museum": ThemeColors.ART,
    "painting": ThemeColors.ART,
    "music": ThemeColors.MUSIC,
    "song": ThemeColors.MUSIC,
    "band": ThemeColors.MUSIC,
    "ai": ThemeColors.TECH,
    "computer": ThemeColors.TECH,
    "tech": ThemeColors.TECH,
    "software": ThemeColors.TECH,
    "football": ThemeColors.SPORTS,
    "basketball": ThemeColors.SPORTS,
    "soccer": ThemeColors.SPORTS,
    "olympics": ThemeColors.SPORTS,
    "food": ThemeColors.FOOD,
    "recipe": ThemeColors.FOOD,
    "cuisine": ThemeColors.FOOD,
    "travel": ThemeColors.TRAVEL,
    "tourism": ThemeColors.TRAVEL,
    "country": ThemeColors.TRAVEL,
}


def detect_theme(query: str) -> Dict:
    """Detect theme based on search query."""
    query_lower = query.lower()
    for keyword, theme in THEME_KEYWORDS.items():
        if keyword in query_lower:
            return theme
    return ThemeColors.DEFAULT


def get_terminal_width() -> int:
    """Get terminal width, default to 100 if unavailable."""
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 100


def get_grid_width() -> int:
    """Get grid width (80% of terminal or 100 max)."""
    term_width = get_terminal_width()
    return min(100, int(term_width * 0.8))


GRID_WIDTH = get_grid_width()


def center_text(text: str) -> str:
    """Center text within grid width."""
    return text.center(GRID_WIDTH)


def get_gradient_logo(theme: Dict = None) -> str:
    """Generate gradient logo using pyfiglet with theme colors."""
    try:
        import pyfiglet

        logo = pyfiglet.figlet_format("ACHEM", font="banner3", width=GRID_WIDTH)
        lines = logo.split("\n")
        gradient_lines = []

        if theme and theme["name"] != "Default":
            gradient_colors = [
                theme["secondary"],
                theme["primary"],
                theme["accent"],
                theme["primary"],
                theme["glow"],
                theme["primary"],
                theme["secondary"],
            ]
        else:
            gradient_colors = [
                "#1e3a5f",
                "#1e5a8f",
                "#2a6aaf",
                "#2a8acf",
                "#3a9adf",
                "#4aaeee",
                "#5abeff",
            ]

        for i, line in enumerate(lines):
            if line.strip():
                color_idx = min(i % len(gradient_colors), len(gradient_colors) - 1)
                color = gradient_colors[color_idx]
                centered = line.center(GRID_WIDTH)
                gradient_lines.append(f"[bold {color}]{centered}[/bold {color}]")
            else:
                gradient_lines.append("")
        return "\n".join(gradient_lines)
    except Exception:
        return (
            f"[bold cyan]{center_text('╔═╗┌─┐┌─┐┌─┐┬─┐┌─┐┬ ┬   ╦  ┌┐┌')}[/bold cyan]\n"
            + f"[bold cyan]{center_text('╠╦╝├┤ └─┐├┤ ├┬┘│  ├─┤───║  │││')}[/bold cyan]\n"
            + f"[bold cyan]{center_text('╩╚═└─┘└─┘└─┘┴└─└─┘┴ ┴   ╩═╝┘└┘')}[/bold cyan]"
        )


def get_raw_logo() -> list:
    """Get logo lines for Rich display."""
    return [
        " █████╗  ██████╗██╗  ██╗███████╗███╗   ███╗",
        "██╔══██╗██╔════╝██║  ██║██╔════╝████╗ ████║",
        "███████║██║     ███████║█████╗  ██╔████╔██║",
        "██╔══██║██║     ██╔══██║██╔══╝  ██║╚██╔╝██║",
        "██║  ██║╚██████╗██║  ██║███████╗██║ ╚═╝ ██║",
        "╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝",
    ]


def escape_rich(text: str) -> str:
    """Escape text for Rich by doubling backslashes before brackets."""
    return text.replace("\\", "\\\\")


def get_description() -> str:
    """Get italic description below logo."""
    return f"[dim i]{center_text('Your AI Research Assistant')}[/dim i]"


def print_logo(theme: Dict = None):
    """Print the centered logo with tagline."""
    theme = theme or ThemeColors.DEFAULT
    primary = theme["primary"]
    accent = theme["accent"]

    console.print()
    console.print()

    term_width = get_terminal_width()
    logo_lines = get_raw_logo()
    max_len = max(len(line) for line in logo_lines)
    margin = (term_width - max_len) // 2

    for line in logo_lines:
        console.print(" " * margin + line)

    console.print()


def get_examples() -> List[dict]:
    """Get example search topics with icons."""
    return [
        {"icon": "🔬", "label": "Science", "query": "quantum physics"},
        {"icon": "🏛️", "label": "History", "query": "moroccan empire"},
        {"icon": "🎨", "label": "Art", "query": "van gogh"},
        {"icon": "🧠", "label": "AI", "query": "neural networks"},
        {"icon": "🌍", "label": "Geography", "query": "sahara desert"},
    ]


def print_examples():
    """Print quick search options in a grid table."""
    examples = get_examples()

    table = Table(
        show_header=True,
        header_style="bold cyan",
        box=None,
        show_edge=False,
        pad_edge=False,
        padding=(0, 2, 0, 2),
    )

    table.add_column("Option", style="bold cyan", width=4)
    table.add_column("Category", width=12)
    table.add_column("Query", style="dim")

    for i, ex in enumerate(examples, 1):
        option = f"[bold cyan]{i}[/bold cyan]"
        cat = f"{ex['icon']} {ex['label']}"
        query = f"[dim]→[/dim] {ex['query']}"
        table.add_row(option, cat, query)

    console.print(table)
    console.print()


def get_search_box(is_focused: bool = False, theme: Dict = None) -> str:
    """Get search box with optional focus state and theme colors."""
    theme = theme or ThemeColors.DEFAULT
    primary = theme["primary"]
    glow = theme["glow"]

    border_color = glow if is_focused else primary
    placeholder = f"[dim]Search for topics, people, or events...[/dim]"

    width = 50
    top = f"[{border_color}]┌{'─' * width}┐[/{border_color}]"
    middle = f"[{border_color}]│[/{border_color}] {placeholder} {' ' * (width - len('Search for topics, people, or events...') - 1)} [{border_color}]│[/{border_color}]"
    bottom = f"[{border_color}]└{'─' * width}┘[/{border_color}]"

    return f"\n{top}\n{middle}\n{bottom}\n"


def get_sticky_footer(
    cpu: float, ram: float, cache_stats: dict = None, theme: Dict = None
) -> Panel:
    """Create double-border footer with sub-panels for version, shortcuts, and stats."""
    theme = theme or ThemeColors.DEFAULT
    primary = theme["primary"]
    accent = theme["accent"]

    cache_str = ""
    if cache_stats:
        hits = cache_stats.get("hits", 0)
        misses = cache_stats.get("misses", 0)
        if hits + misses > 0:
            cache_str = f"  [blue]Cache: {hits}/{hits + misses}[/blue]"

    version_text = f"[bold {accent}]v{VERSION}[/bold {accent}]"
    stats_text = (
        f"[green]CPU: {cpu:.1f}%[/green]  [yellow]RAM: {ram:.0f}MB[/yellow]{cache_str}"
    )

    footer_table = Table(
        show_header=False,
        show_edge=False,
        pad_edge=False,
        padding=(0, 3),
    )
    footer_table.add_column(justify="left", width=None)
    footer_table.add_column(justify="right", width=None)
    footer_table.add_row(version_text, stats_text)

    return footer_table


def print_search_progress(query: str):
    """Print animated search progress."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"[cyan]Searching: {query}[/cyan]", total=100)
        for i in range(100):
            time.sleep(0.02)
            progress.update(task, advance=1)


def format_relevance(relevance_score: float) -> tuple:
    """Get color for relevance score with warning badge for low relevance."""
    if relevance_score > 50:
        return "green", f"[bold green]Relevance: {relevance_score:.0f}%[/bold green]"
    elif relevance_score >= 40:
        return "yellow", f"[bold yellow]Relevance: {relevance_score:.0f}%[/bold yellow]"
    else:
        return "red", f"[bold red]⚠️ Relevance: {relevance_score:.0f}%[/bold red]"


def get_rtl_text(text: str) -> str:
    """Format Arabic/RTL text for proper display."""
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display

        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except ImportError:
        return text


def is_rtl_text(text: str) -> bool:
    """Check if text contains significant RTL (Arabic) characters."""
    if not text:
        return False
    arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06ff")
    total = len(text)
    return arabic_chars / total > 0.15 if total > 0 else False


import re


def highlight_summary_keywords(text: str, theme_color: str = "cyan") -> str:
    """Apply syntax highlighting to summary text for better scannability.

    Highlights:
    - Step numbers: "Step 1", "Step 2", "1.", "2.", "3.", etc.
    - Commands: text in backticks `code`
    - Important terms: bold markers **text**
    - Lists: "- " bullets
    - Headers: ## headers
    """
    if not text:
        return text

    highlighted = text

    highlighted = re.sub(
        r"\*\*([^*]+)\*\*", f"[bold yellow]\\1[/bold yellow]", highlighted
    )

    highlighted = re.sub(r"`([^`]+)`", f"[bold cyan]\\1[/bold cyan]", highlighted)

    highlighted = re.sub(
        r"(Step\s+\d+[\.:]?)",
        f"[bold bright_cyan]\\1[/bold bright_cyan]",
        highlighted,
        flags=re.IGNORECASE,
    )

    highlighted = re.sub(
        r"^(#{1,3}\s+.+)$",
        f"[bold bright_blue]\\1[/bold bright_blue]",
        highlighted,
        flags=re.MULTILINE,
    )

    highlighted = re.sub(
        r"^(\d+[\.\)]\s)",
        f"[bold bright_cyan]\\1[/bold bright_cyan]",
        highlighted,
        flags=re.MULTILINE,
    )

    highlighted = re.sub(
        r"^(\-\s)", f"[bold dim]\\1[/bold dim]", highlighted, flags=re.MULTILINE
    )

    return highlighted


def print_results(
    articles: List[dict],
    keywords: List[str],
    unified_summary: str = None,
    theme: Dict = None,
):
    """Print search results with colored relevance and theme."""
    theme = theme or ThemeColors.DEFAULT
    primary = theme["primary"]
    glow = theme["glow"]

    console.print()
    console.print(f"[bold {glow}]SEARCH RESULTS[/bold {glow}]")
    console.print()

    for i, article in enumerate(articles, 1):
        title = article.get("title", "Unknown")
        summary = article.get("summary", "No summary available.")
        relevance = article.get("relevance_score", 0)

        rel_color, rel_text = format_relevance(relevance)

        console.print(
            f"[bold yellow][[/bold yellow][bold white]{i}[/bold white][bold yellow]][/bold yellow] [{glow}]{title}[/{glow}] {rel_text}"
        )
        console.print("[dim]" + "-" * 60 + "[/dim]")
        console.print(summary[:350] + ("..." if len(summary) > 350 else ""))
        console.print()

    if keywords:
        console.print(f"[bold {primary}]🔑 Key Topics:[/bold {primary}]")
        kw_text = "  ".join([f"[{primary}]{kw}[/{primary}]" for kw in keywords[:8]])
        console.print(f"  {kw_text}")
        console.print()

    if unified_summary:
        console.print(f"[bold {glow}]Unified Summary:[/bold {glow}]")
        console.print(unified_summary)


def print_unified_result(
    articles: List[dict],
    keywords: List[str],
    unified_summary: str = None,
    theme: Dict = None,
    mode: str = "local",
    source_count: int = None,
):
    """Print unified result - best article + unified summary from all sources."""
    theme = theme or ThemeColors.DEFAULT
    primary = theme["primary"]
    glow = theme["glow"]

    if not articles:
        return

    best_article = max(articles, key=lambda a: a.get("relevance_score", 0))
    best_title = best_article.get("title", "Unknown")
    best_relevance = best_article.get("relevance_score", 0)

    rel_color, rel_text = format_relevance(best_relevance)

    kw_text = ""
    if keywords:
        kw_text = "  ".join([f"[{primary}]{kw}[/{primary}]" for kw in keywords[:8]])

    result_lines = []
    result_lines.append(f"[bold {glow}] {best_title} {rel_text}[/bold {glow}]")

    if best_relevance < 50:
        result_lines.append(
            f"[bold red]⚠️ Low relevance - Results may not match your query[/bold red]"
        )

    mode_badge = (
        f"[bold green]AI[/bold green]"
        if mode == "hf"
        else f"[bold yellow]Local[/bold yellow]"
    )
    count_display = source_count if source_count is not None else len(articles)
    result_lines.append(f"[dim]{count_display} sources • {mode_badge}[/dim]")
    if kw_text:
        result_lines.append(f"[{primary}]{kw_text}[/{primary}]")

    if unified_summary:
        if is_rtl_text(unified_summary):
            display_summary = get_rtl_text(unified_summary)
        else:
            display_summary = highlight_summary_keywords(unified_summary, glow)
        result_lines.append(display_summary)

    console.print()
    console.print("\n".join(result_lines))
    console.print()


def print_spell_suggestions(suggestions: List[str]):
    """Print spell check suggestions with styling."""
    if suggestions:
        console.print("\n[bold yellow]📝 Spell Check Suggestions:[/bold yellow]")
        for suggestion in suggestions[:5]:
            console.print(f"  {suggestion}")
        console.print()


def print_filter_warnings(warnings: List[str]):
    """Print filter warnings with styling."""
    if warnings:
        console.print("\n[bold red]⚠️ Content Warnings:[/bold red]")
        for warning in warnings[:5]:
            console.print(f"  {warning}")
        console.print()


def get_system_info() -> dict:
    """Get current system resource usage."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_mb": memory_info.rss / 1024 / 1024,
    }


def print_clear():
    """Clear the terminal screen."""
    console.clear()


def get_interactive_input() -> Optional[str]:
    """Get interactive input with prompt_toolkit."""
    try:
        from prompt_toolkit import Prompt
        from prompt_toolkit.styles import Style
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.filters import Focus

        bindings = KeyBindings()

        @bindings.add("c-c")
        def _(event):
            event.app.exit(result=None)

        @bindings.add("escape")
        def _(event):
            event.app.exit(result=None)

        style = Style(
            [
                ("prompt", "fg:cyan bold"),
                ("input", "fg:white"),
                ("placeholder", "fg:dim"),
            ]
        )

        prompt_text = [
            ("class:prompt", "❯ "),
        ]

        input_text = Prompt(
            message=prompt_text,
            multiline=False,
            key_bindings=bindings,
            style=style,
            placeholder="Search for topics, people, or events...",
            enable_search=False,
        )

        return input_text.app.run()
    except ImportError:
        from rich.prompt import Prompt

        return Prompt.ask("[cyan]❯[/cyan]")
