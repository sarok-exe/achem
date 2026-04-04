# ACHEM - Deep Web Research Tool

![ACHEM Banner](https://img.shields.io/badge/ACHEM-v1.0.0-blue?style=for-the-badge)

> **ACHEM** (Arabic: آشم) is a powerful deep web research tool that aggregates information from 30+ sources, scrapes full content from top results, and generates concise summaries using AI.

## Features

- **Deep Web Research**: Gathers results from 30+ sources via DuckDuckGo
- **Web Scraping**: Extracts full content from top 3 most relevant links
- **Two-Pass Search**: Prioritizes technical content (StackOverflow, GitHub, forums)
- **AI Summarization**: Uses Hugging Face Inference Providers (free tier)
- **Syntax Highlighting**: Color-coded output for easy scanning
- **SQLite Cache**: Instant recall for repeated searches
- **Export**: Save summaries to Markdown files
- **Multi-language**: Supports English, French, and Arabic

## Screenshots

```
╔══════════════════════════════════════════════════════════════════╗
║                    ACHEM - Deep Web Research                      ║
╚══════════════════════════════════════════════════════════════════╝

🔍 Deep Research: how to learn python
==================================================
PASS 1: Gathering 30 sources from DuckDuckGo...
✓ Found 30 sources
PASS 2: Scraped full content from top 3 links
→ Analyzing 35 total sources...
→ Generating deep summary...

╭──────────────────────────────────────────────────────────────────╮
│ UNIFIED RESEARCH SUMMARY                                          │
├──────────────────────────────────────────────────────────────────┤
│ 1. Start with the official Python tutorial:                     │
│    - Visit docs.python.org/3/tutorial                           │
│                                                                  │
│ 2. Use free online tutorials:                                   │
│    - LearnPython.org, pythonbasics.org                         │
╰──────────────────────────────────────────────────────────────────╯
```

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Quick Install (PyPI)

```bash
pipx install achem
```

> **Note**: `pipx` is recommended as it manages virtual environments automatically. If you prefer pip, use `pip install achem --break-system-packages`.

### Or Install from Source

1. **Clone the repository**
```bash
git clone https://github.com/achem/achem.git
cd achem
```

2. **Install in editable mode**
```bash
pip install -e .
```

3. **Configure API keys**
```bash
cp .env.example .env
```

Then edit `.env` and add your Hugging Face API token:
```env
HF_API_KEY=hf_your_token_here
HF_MODEL=Qwen/Qwen2.5-7B-Instruct
```

### Getting a Hugging Face API Token

1. Go to [Hugging Face](https://huggingface.co/)
2. Create an account (free)
3. Go to Settings → Access Tokens
4. Create a new token with "Read" permissions
5. Copy the token to your `.env` file

## Usage

### Interactive Mode

```bash
python src/main.py
```

### Command Line Mode

```bash
python src/main.py "your search query"
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-l, --limit` | Wikipedia results per query | 10 |
| `--lang` | Language (en/fr/ar/auto) | auto |
| `--ddg-limit` | DuckDuckGo results | 30 |
| `--min-relevance` | Minimum relevance % | 0 |
| `--no-cache` | Skip cache | False |
| `--no-wikipedia` | Skip Wikipedia | False |
| `--clear-cache` | Clear SQLite cache | False |

### Commands (Interactive Mode)

| Command | Description |
|---------|-------------|
| `clear` / `cls` | Clear screen |
| `export` / `save` | Export last summary |
| `help` / `?` | Show help |
| `version` / `v` | Show version |
| `exit` / `quit` / `q` | Exit program |

## Project Structure

```
ACHEM/
├── src/
│   └── achem/              # Main package
│       ├── __init__.py
│       ├── main.py        # Entry point
│       ├── commands.py    # Command handler
│       ├── config_manager.py    # Config loader
│       ├── duckduckgo_client.py # DDG search
│       ├── export_manager.py    # Export to Documents/ACHEM/
│       ├── huggingface_summarizer.py # AI summarization
│       ├── output_formatter.py # Terminal UI
│       ├── search_router.py    # Source priority
│       ├── sqlite_cache.py     # SQLite cache
│       ├── spell_checker.py    # Typo correction
│       ├── text_analyzer.py    # TF-IDF analysis
│       ├── user_input.py       # Input handler
│       ├── web_scraper.py      # BeautifulSoup scraper
│       └── wikipedia_client.py  # Wikipedia API
├── .env.example            # Config template
├── .gitignore
├── LICENSE
├── README.md
└── pyproject.toml         # Package metadata
```

## How It Works

### Two-Pass Search System

```
┌─────────────────────────────────────────────────────┐
│ PASS 1: DuckDuckGo Search (30 results)              │
│ • Prioritizes technical sites                        │
│ • Filters out cookie/login/consent pages            │
│ • Ranks by domain authority                         │
├─────────────────────────────────────────────────────┤
│ PASS 2: Web Scraping (Top 3)                        │
│ • BeautifulSoup extracts full article text           │
│ • Removes navigation/footer/scripts                 │
│ • Combines up to 10,000 chars per article           │
├─────────────────────────────────────────────────────┤
│ PASS 3: AI Summarization                            │
│ • Neutral technical prompt                           │
│ • No ethical warnings or opinions                   │
│ • 500-4000 character output                        │
│ • Syntax highlighting for steps/commands             │
└─────────────────────────────────────────────────────┘
```

### Source Priority

1. **DuckDuckGo** (Primary) - Real-time web results
2. **Wikipedia** (Secondary) - Background concepts only
3. **Web Scraping** - Full content from top 3

## Export Location

Summaries are saved to:
- **Linux/macOS**: `~/Documents/ACHEM/`
- **Windows**: `C:\Users\<username>\Documents\ACHEM\`

## Disclaimer

**ACHEM is for educational and research purposes only.**

The tool aggregates publicly available information from the web. Any actions taken based on the information provided are the sole responsibility of the user. The developer is not responsible for any misuse of this tool.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Acknowledgments

- [Hugging Face](https://huggingface.co/) - Free inference API
- [DuckDuckGo](https://duckduckgo.com/) - Privacy-focused search
- [Wikipedia](https://www.wikipedia.org/) - Free encyclopedia
- [Qwen](https://huggingface.co/Qwen) - Open source AI models
