import os
import re
from rich.console import Console
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich import box as rich_box
from typing import List, Optional, Dict
import psutil

console = Console(width=100, force_terminal=True, markup=True)
VERSION = "1.0.4"


class Catppuccin:
    BG = "#1E1E2E"
    SURFACE0 = "#313244"
    SURFACE1 = "#45475A"
    SURFACE2 = "#585B70"
    OVERLAY0 = "#6C7086"
    TEXT = "#CDD6F4"
    SUBTEXT1 = "#BAC2DE"
    BLUE = "#89B4FA"
    LAVENDER = "#B4BEFE"
    TEAL = "#94E2D5"
    GREEN = "#A6E3A1"
    YELLOW = "#F9E2AF"
    PEACH = "#FAB387"
    RED = "#F38BA8"
    PINK = "#F5C2E7"
    MAUVE = "#CBA6F7"


class ThemeColors:
    DEFAULT = {
        "name": "Default",
        "primary": "#89B4FA",
        "secondary": "#6C7086",
        "accent": "#CBA6F7",
    }
    CYBERPUNK = {
        "name": "Cyberpunk",
        "primary": "#F38BA8",
        "secondary": "#313244",
        "accent": "#F5C2E7",
    }
    NEON_SCIENCE = {
        "name": "Science",
        "primary": "#89B4FA",
        "secondary": "#94E2D5",
        "accent": "#74C7EC",
    }
    NATURE = {
        "name": "Nature",
        "primary": "#A6E3A1",
        "secondary": "#94E2D5",
        "accent": "#F9E2AF",
    }


THEME_KEYWORDS = {
    "cyberpunk": ThemeColors.CYBERPUNK,
    "manga": ThemeColors.CYBERPUNK,
    "anime": ThemeColors.CYBERPUNK,
    "science": ThemeColors.NEON_SCIENCE,
    "physics": ThemeColors.NEON_SCIENCE,
    "quantum": ThemeColors.NEON_SCIENCE,
    "nature": ThemeColors.NATURE,
    "animal": ThemeColors.NATURE,
    "plant": ThemeColors.NATURE,
}


def c(name: str) -> str:
    colors = {
        "bg": Catppuccin.BG,
        "surface0": Catppuccin.SURFACE0,
        "surface1": Catppuccin.SURFACE1,
        "surface2": Catppuccin.SURFACE2,
        "overlay0": Catppuccin.OVERLAY0,
        "text": Catppuccin.TEXT,
        "subtext1": Catppuccin.SUBTEXT1,
        "accent_blue": Catppuccin.BLUE,
        "accent_lavender": Catppuccin.LAVENDER,
        "green": Catppuccin.GREEN,
        "yellow": Catppuccin.YELLOW,
        "peach": Catppuccin.PEACH,
        "red": Catppuccin.RED,
        "pink": Catppuccin.PINK,
        "mauve": Catppuccin.MAUVE,
        "teal": Catppuccin.TEAL,
    }
    return colors.get(name, Catppuccin.TEXT)


def detect_theme(query: str) -> Dict:
    query_lower = query.lower()
    for keyword, theme in THEME_KEYWORDS.items():
        if keyword in query_lower:
            return theme
    return ThemeColors.DEFAULT


def get_terminal_width() -> int:
    return console.width


def get_terminal_height() -> int:
    return console.height


def get_raw_logo() -> list:
    return [
        " █████╗  ██████╗██╗  ██╗███████╗███╗   ███╗",
        "██╔══██╗██╔════╝██║  ██║██╔════╝████╗ ████║",
        "███████║██║     ███████║█████╗  ██╔████╔██║",
        "██╔══██║██║     ██╔══██║██╔══╝  ██║╚██╔╝██║",
        "██║  ██║╚██████╗██║  ██║███████╗██║ ╚═╝ ██║",
        "╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝",
    ]


def print_logo(theme: Dict = None):
    theme = theme or ThemeColors.DEFAULT
    term_width = get_terminal_width()
    logo_lines = get_raw_logo()
    max_len = max(len(line) for line in logo_lines)
    margin = (term_width - max_len) // 2
    for line in logo_lines:
        colored = f"[bold {c('accent_blue')}]{line}[/bold {c('accent_blue')}]"
        console.print(" " * margin + colored)


def print_clear():
    console.clear()


def print_home():
    """Print the home screen - called once per loop."""
    print_clear()

    term_width = get_terminal_width()
    term_height = get_terminal_height()

    console.print()

    print_logo()

    console.print()
    console.print(
        f"[{c('subtext1')}][italic]Aggregates 100+ sources, scrapes content, generates AI summaries.[/italic][/{c('subtext1')}]"
    )
    console.print()
    console.print()

    box_width = min(65, term_width - 10)
    search_panel = Panel(
        Text("Type your search query...", style=c("overlay0")),
        title=f" [{c('accent_blue')}][bold]Search[/bold][/{c('accent_blue')}] ",
        border_style=c("accent_blue"),
        box=rich_box.DOUBLE,
        width=box_width,
        style=c("bg"),
    )
    console.print(Align.center(search_panel))

    console.print()
    console.print()

    ex_width = min(55, term_width - 15)
    ex_lines = [
        f"[{c('green')}][bold]Examples[/bold][/{c('green')}]  (paste any of these):",
        "",
        f"  [{c('surface2')}]1.[/{c('surface2')}]  [{c('accent_blue')}]quantum physics[/{c('accent_blue')}]",
        f"  [{c('surface2')}]2.[/{c('surface2')}]  [{c('accent_blue')}]machine learning[/{c('accent_blue')}]",
        f"  [{c('surface2')}]3.[/{c('surface2')}]  [{c('accent_blue')}]python async await[/{c('accent_blue')}]",
        "",
        f"[{c('yellow')}][bold]Tip:[/bold][/{c('yellow')}]  Supports English, French, and Arabic",
    ]
    ex_content = "\n".join(ex_lines)
    ex_panel = Panel(
        Text(ex_content),
        border_style=c("surface2"),
        box=rich_box.ROUNDED,
        width=ex_width,
        style=c("bg"),
    )
    console.print(Align.center(ex_panel))

    used_height = 6 + 6 + 6 + 1 + 7 + 3
    remaining = term_height - used_height - 6

    if remaining > 0:
        for _ in range(max(1, remaining // 2)):
            console.print()

    controls = f"[{c('green')}][bold]Enter[/bold][/{c('green')}] Start   │   [{c('red')}][bold]Ctrl+C[/bold][/{c('red')}] Quit"
    console.print(Align.center(controls))
    console.print()

    sys_info = get_system_info()
    footer = (
        f"[bold {c('mauve')}]v{VERSION}[/bold {c('mauve')}]   │   "
        f"[{c('green')}]CPU: {sys_info['cpu_percent']:.1f}%[/{c('green')}]   "
        f"[{c('yellow')}]RAM: {sys_info['memory_mb']:.0f}MB[/{c('yellow')}]"
    )
    console.print(Align.center(footer))
    console.print()


def format_relevance(relevance_score: float) -> tuple:
    if relevance_score > 70:
        return c(
            "green"
        ), f"[bold {c('green')}]Relevance: {relevance_score:.0f}%[/bold {c('green')}]"
    elif relevance_score >= 40:
        return c(
            "yellow"
        ), f"[bold {c('yellow')}]Relevance: {relevance_score:.0f}%[/bold {c('yellow')}]"
    else:
        return c("red"), f"[bold {c('red')}]⚠ {relevance_score:.0f}%[/bold {c('red')}]"


def get_rtl_text(text: str) -> str:
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display

        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except ImportError:
        return text


def is_rtl_text(text: str) -> bool:
    if not text:
        return False
    arabic_chars = sum(1 for ch in text if "\u0600" <= ch <= "\u06ff")
    total = len(text)
    return arabic_chars / total > 0.15 if total > 0 else False


def highlight_summary_keywords(text: str, theme_color: str = "accent_blue") -> str:
    if not text:
        return text
    highlighted = text
    highlighted = re.sub(
        r"\*\*([^*]+)\*\*", f"[bold {c('yellow')}]\\1[/bold {c('yellow')}]", highlighted
    )
    highlighted = re.sub(
        r"`([^`]+)`",
        f"[bold {c('accent_blue')}]\\1[/bold {c('accent_blue')}]",
        highlighted,
    )
    highlighted = re.sub(
        r"(Step\s+\d+[\.:]?)",
        f"[bold {c('teal')}]\\1[/bold {c('teal')}]",
        highlighted,
        flags=re.IGNORECASE,
    )
    highlighted = re.sub(
        r"^(#{1,3}\s+.+)$",
        f"[bold {c('mauve')}]\\1[/bold {c('mauve')}]",
        highlighted,
        flags=re.MULTILINE,
    )
    highlighted = re.sub(
        r"^(\d+[\.\)]\s)",
        f"[bold {c('teal')}]\\1[/bold {c('teal')}]",
        highlighted,
        flags=re.MULTILINE,
    )
    highlighted = re.sub(
        r"^(\-\s)",
        f"[{c('overlay0')}]\\1[/{c('overlay0')}]",
        highlighted,
        flags=re.MULTILINE,
    )
    return highlighted


def print_unified_result(
    articles: List[dict],
    keywords: List[str],
    unified_summary: str = None,
    theme: Dict = None,
    mode: str = "local",
    source_count: int = None,
):
    if not articles:
        return

    best_article = max(articles, key=lambda a: a.get("relevance_score", 0))
    best_title = best_article.get("title", "Unknown")
    best_relevance = best_article.get("relevance_score", 0)
    rel_color, rel_text = format_relevance(best_relevance)

    kw_text = ""
    if keywords:
        kw_text = "  ".join(
            [f"[{c('accent_blue')}]{kw}[/{c('accent_blue')}]" for kw in keywords[:8]]
        )

    mode_badge = (
        f"[bold {c('green')}]{mode.upper()}[/bold {c('green')}]"
        if mode in ("hf", "groq", "gemini", "openrouter", "ollama")
        else f"[bold {c('yellow')}]{mode.upper()}[/bold {c('yellow')}]"
    )

    count_display = source_count if source_count is not None else len(articles)

    result_lines = []
    result_lines.append(f"[bold {c('pink')}]{best_title}[/bold {c('pink')}] {rel_text}")
    result_lines.append(
        f"[{c('overlay0')}]└── {count_display} sources • {mode_badge}[/{c('overlay0')}]"
    )
    if kw_text:
        result_lines.append(f"[{c('overlay0')}]└── Topics: {kw_text}[/{c('overlay0')}]")

    if unified_summary:
        result_lines.append("")
        if is_rtl_text(unified_summary):
            display_summary = get_rtl_text(unified_summary)
        else:
            display_summary = highlight_summary_keywords(unified_summary, "accent_blue")
        result_lines.append(display_summary)

    console.print()
    for line in result_lines:
        console.print(line)
    console.print()
    for line in result_lines:
        console.print(line)
    console.print()


def get_footer(cpu: float, ram: float, cache_stats: dict = None) -> Table:
    cache_str = ""
    if cache_stats:
        hits = cache_stats.get("hits", 0)
        misses = cache_stats.get("misses", 0)
        if hits + misses > 0:
            cache_str = f"  [{c('accent_blue')}]Cache: {hits}/{hits + misses}[/{c('accent_blue')}]"
    version_text = f"[bold {c('mauve')}]v{VERSION}[/bold {c('mauve')}]"
    stats_text = (
        f"[{c('green')}]CPU: {cpu:.1f}%[/{c('green')}]  "
        f"[{c('yellow')}]RAM: {ram:.0f}MB[/{c('yellow')}]{cache_str}"
    )
    footer_table = Table(
        show_header=False,
        show_edge=False,
        pad_edge=False,
        padding=(0, 1, 0, 0),
        min_width=80,
    )
    footer_table.add_column(justify="center", width=80)
    footer_table.add_row(f"{version_text}   │   {stats_text}")
    return footer_table


def get_system_info() -> dict:
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_mb": memory_info.rss / 1024 / 1024,
    }


def get_interactive_input() -> Optional[str]:
    try:
        from prompt_toolkit import Prompt
        from prompt_toolkit.styles import Style
        from prompt_toolkit.key_binding import KeyBindings

        bindings = KeyBindings()

        @bindings.add("c-c")
        def _(event):
            event.app.exit(result=None)

        @bindings.add("escape")
        def _(event):
            event.app.exit(result=None)

        style = Style(
            [
                ("prompt", f"fg:{c('accent_blue')} bold"),
                ("input", f"fg:{c('text')}"),
                ("placeholder", f"fg:{c('overlay0')}"),
            ]
        )
        prompt_text = [("class:prompt", "❯ ")]
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

        return Prompt.ask(f"[{c('accent_blue')}]❯[/{c('accent_blue')}]")
