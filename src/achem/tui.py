from textual.app import App, ComposeResult
from textual.widgets import Static, Input
from textual.binding import Binding
from textual.reactive import reactive


LOGO = """[bold #89B4FA]
 █████╗  ██████╗██╗  ██╗███████╗███╗   ███╗
██╔══██╗██╔════╝██║  ██║██╔════╝████╗ ████║
███████║██║     ███████║█████╗  ██╔████╔██║
██╔══██║██║     ██╔══██║██╔══╝  ██║╚██╔╝██║
██║  ██║╚██████╗██║  ██║███████╗██║ ╚═╝ ██║
╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝[/bold #89B4FA]"""

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class ACHEMApp(App):
    CSS = """
    Screen {
        background: #1E1E2E;
    }
    
    #container {
        width: 100%;
        height: 100%;
        align: center middle;
    }
    
    #content {
        width: 70;
        height: auto;
        align: center top;
    }
    
    #logo {
        width: 100%;
        align: center top;
    }
    
    #description {
        width: 100%;
        align: center top;
        margin-top: 1;
        color: #BAC2DE;
    }
    
    #search-box {
        width: 100%;
        height: 3;
        border: double #89B4FA;
        background: #1E1E2E;
        margin-top: 3;
    }
    
    #search {
        width: 100%;
        height: 100%;
        background: transparent;
        color: #CDD6F4;
        border: none;
    }
    
    #search:focus {
        border: none;
    }
    
    #loading-container {
        width: 100%;
        align: center top;
        margin-top: 2;
    }
    
    #loading-box {
        width: 100%;
        border: solid #585B70;
        background: #1E1E2E;
        padding: 1 2;
    }
    
    #loading-title {
        color: #F9E2AF;
    }
    
    #loading-spinner {
        color: #89B4FA;
    }
    
    #loading-status {
        color: #89B4FA;
    }
    
    #loading-sources {
        color: #6C7086;
    }
    
    #results-container {
        width: 100%;
        height: auto;
        align: center top;
    }
    
    #results-title {
        color: #F5C2E7;
    }
    
    #results-meta {
        color: #6C7086;
    }
    
    #results-summary {
        color: #CDD6F4;
    }
    
    #results-keywords {
        color: #89B4FA;
    }
    
    .hidden {
        display: none;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
    ]

    spinner_frame = reactive(0)
    _spinner_timer = None

    def __init__(self):
        super().__init__()
        self.query_result = None
        self.is_loading = False
        self.loading_status = ""
        self.loading_sources = []
        self.search_results = None

    def compose(self) -> ComposeResult:
        with Static(id="container"):
            with Static(id="content"):
                yield Static(LOGO, id="logo")
                yield Static(
                    "Aggregates 100+ sources, scrapes content, generates AI summaries.",
                    id="description",
                )

                yield Static(
                    "[#A6E3A1]l:[/#A6E3A1] TF-IDF  |  [#89B4FA]ai:[/#89B4FA] Cloud  |  [#CBA6F7]o:[/#CBA6F7] Ollama  |  Default: AI",
                    id="mode-help",
                )

                with Static(id="search-box"):
                    yield Input(
                        placeholder="ai:python or o:machine learning", id="search"
                    )

                with Static(id="loading-container"):
                    with Static(id="loading-box"):
                        yield Static("[#89B4FA]⠋[/]", id="loading-spinner")
                        yield Static(
                            "[#F9E2AF][bold]Searching...[/]", id="loading-title"
                        )
                        yield Static("[#89B4FA]Initializing...[/]", id="loading-status")
                        yield Static("", id="loading-sources")

                with Static(id="results-container"):
                    yield Static("", id="results-title")
                    yield Static("", id="results-meta")
                    yield Static("", id="results-summary")
                    yield Static("", id="results-keywords")

                yield Static(
                    "[#A6E3A1][bold]Enter[/] Start    |    [#F38BA8][bold]Ctrl+C[/] Quit",
                    id="controls",
                )
                yield Static("[#CBA6F7][bold]v1.0.4[/]", id="footer")

    def on_mount(self) -> None:
        self.title = "ACHEM"
        self.set_focus(self.query_one("#search"))
        self.query_one("#loading-container").display = False
        self.query_one("#results-container").display = False
        self._start_spinner()

    def _start_spinner(self):
        self._spinner_timer = self.set_interval(0.1, self._update_spinner)

    def _update_spinner(self):
        if self.is_loading:
            self.spinner_frame = (self.spinner_frame + 1) % len(SPINNER_FRAMES)
            spinner = self.query_one("#loading-spinner")
            if spinner:
                spinner.update(f"[#89B4FA]{SPINNER_FRAMES[self.spinner_frame]}[/]")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        raw = event.value.strip()
        if not raw:
            return

        mode = "ai"
        query = raw

        if raw.lower().startswith("l:"):
            mode = "local"
            query = raw[2:].strip()
        elif raw.lower().startswith("local:"):
            mode = "local"
            query = raw[6:].strip()
        elif raw.lower().startswith("o:"):
            mode = "ollama"
            query = raw[2:].strip()
        elif raw.lower().startswith("ollama:"):
            mode = "ollama"
            query = raw[7:].strip()
        elif raw.lower().startswith("ai:"):
            query = raw[3:].strip()

        if query:
            self.query_result = (query, mode)
            self.exit(self.query_result)

    def show_loading(self, status: str = "Searching...", sources: list = None):
        """Show loading screen."""
        self.is_loading = True
        self.loading_status = status
        self.loading_sources = sources or []

        self.query_one("#search-box").display = False
        self.query_one("#results-container").display = False
        loading = self.query_one("#loading-container")
        loading.display = True

        title = self.query_one("#loading-title")
        title.update(f"[#F9E2AF][bold]{status}[/]")

        status_widget = self.query_one("#loading-status")
        if sources:
            sources_text = "\n".join(
                [f"[#6C7086]• {s}[/#6C7086]" for s in sources[:10]]
            )
            status_widget.update(sources_text)
        else:
            status_widget.update("[#89B4FA]Gathering sources...[/]")

    def show_results(
        self, title_text: str, meta_text: str, summary_text: str, keywords_text: str
    ):
        """Show results screen."""
        self.is_loading = False
        self.query_one("#loading-container").display = False
        self.query_one("#search-box").display = False

        results = self.query_one("#results-container")
        results.display = True

        self.query_one("#results-title").update(f"[#F5C2E7][bold]{title_text}[/]")
        self.query_one("#results-meta").update(f"[#6C7086]{meta_text}[/]")
        self.query_one("#results-summary").update(f"[#CDD6F4]{summary_text}[/]")
        self.query_one("#results-keywords").update(
            f"[#89B4FA]Topics: {keywords_text}[/]"
        )

    def reset_to_search(self):
        """Reset UI to search state."""
        self.is_loading = False
        self.query_result = None
        self.search_results = None
        self.query_one("#loading-container").display = False
        self.query_one("#results-container").display = False
        self.query_one("#search-box").display = True
        self.query_one("#search").value = ""
        self.set_focus(self.query_one("#search"))

    def action_quit(self) -> None:
        self.exit(None)


def run_tui() -> str | None:
    """Run full-screen TUI. Returns query string or None."""
    app = ACHEMApp()
    return app.run()
