# ACHEM - Deep Web Research Tool

![ACHEM Banner](https://img.shields.io/badge/ACHEM-v1.0.5-blue?style=for-the-badge)

> **ACHEM** (Arabic: آشم) is a powerful deep web research tool that aggregates information from 100+ sources, scrapes full content from top results using anti-bot bypass techniques, and generates AI-powered summaries.

## Features

- **Deep Web Research**: Gathers results from 100+ sources via DuckDuckGo
- **Advanced Web Scraping**: Uses Trafilatura + browser headers to bypass bot protection
- **Multi-AI Providers**: OpenRouter (free), Groq, Gemini, and HuggingFace as fallbacks
- **Two-Pass Search**: Prioritizes technical content (StackOverflow, GitHub, forums)
- **SQLite Cache**: Instant recall for repeated searches
- **Markdown Export**: Auto-saves reports to `~/Documents/ACHEM/`
- **Multi-language**: Supports English, French, and Arabic
- **Rate Limit Retry**: Automatic retry on 429 errors
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

```bash
git clone https://github.com/sarok-exe/achem.git
cd achem
pip install -e .
```

### API Configuration

Create `~/.ACHEM/api.env` or `~/Documents/ACHEM/api.env`:

```bash
# OpenRouter (free, recommended)
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_MODEL=qwen/qwen3.6-plus:free
AI_ENABLED=true

# Or use other providers:
# GROQ_API_KEY=your_groq_key
# GEMINI_API_KEY=your_gemini_key
# HF_API_KEY=your_huggingface_key
```

#### Getting an API Key

- **OpenRouter** (free): https://openrouter.ai/settings
- **Groq**: https://console.groq.com/keys
- **Gemini**: https://aistudio.google.com/app/apikey
- **HuggingFace**: https://huggingface.co/settings/access-tokens

## Usage

### Interactive Mode

```bash
python src/main.py
```

### Command Line Mode

```bash
python src/main.py "your search query"
```
## How It Works

### Two-Pass Search System

```
┌─────────────────────────────────────────────────────┐
│ PASS 1: DuckDuckGo Search (100 sources)             │
│ • Prioritizes technical sites                        │
│ • Filters out cookie/login/consent pages            │
│ • Ranks by relevance score                         │
├─────────────────────────────────────────────────────┤
│ PASS 2: Web Scraping (Top 15)                       │
│ • Uses browser headers to bypass bot detection      │
│ • Trafilatura extracts main content                │
│ • Falls back to BeautifulSoup if needed            │
│ • Combines up to 15,000 chars per article          │
├─────────────────────────────────────────────────────┤
│ PASS 3: AI Summarization                            │
│ • Priority: OpenRouter → Groq → Gemini → HF         │
│ • Neutral technical prompt                         │
│ • No ethical warnings or opinions                   │
│ • 500-4000 character output                        │
│ • Retry on rate limit (429)                        │
└─────────────────────────────────────────────────────┘
```

### Source Priority

1. **OpenRouter** (free models like Qwen, GPT-oss)
2. **Groq** (fast inference)
3. **Gemini** (Google AI)
4. **HuggingFace** (fallback)
5. **Local** (if all APIs fail)

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

- [OpenRouter](https://openrouter.ai/) - Free AI models
- [Groq](https://groq.com/) - Fast AI inference
- [Google Gemini](https://gemini.google.com/) - AI powered by Google
- [HuggingFace](https://huggingface.co/) - AI models & inference
- [DuckDuckGo](https://duckduckgo.com/) - Privacy-focused search
- [Wikipedia](https://www.wikipedia.org/) - Free encyclopedia
- [Trafilatura](https://trafilatura.readthedocs.io/) - Web content extraction
