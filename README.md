# ACHEM - Deep Web Research Tool

![ACHEM Banner](https://img.shields.io/badge/ACHEM-v1.1.0-blue?style=for-the-badge)

> **ACHEM** (Arabic: آشم) is a powerful deep web research tool that extracts content from 100+ sources, scrapes full article text, filters relevant content, and generates AI-powered conclusions.

## Features

- **100+ Sources**: Searches DuckDuckGo for up to 100 results
- **Full Content Extraction**: Scrapes full article text using Trafilatura
- **Smart Content Filtering**: Removes ads/boilerplate, keeps only relevant sentences
- **AI Conclusions**: Generates synthesized final verdicts with probability predictions
- **Multi-AI Providers**: OpenRouter (free), Groq, Gemini, Ollama
- **Markdown Export**: Saves complete reports with all sources to `~/Documents/ACHEM/`
- **Multi-language**: Supports English, French, and Arabic
- **Rate Limit Retry**: Automatic retry on 429 errors

## Installation

### Prerequisites

- Python 3.10 or higher
- uv package manager (recommended)

### Quick Install

```bash
git clone https://github.com/sarok-exe/achem.git
cd achem
uv venv .venv && source .venv/bin/activate
uv pip install -e .
```

### API Configuration

Create config at `~/.ACHEM/api.env` or `~/Documents/ACHEM/api.env`:

```bash
# OpenRouter (free, recommended)
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_MODEL=google/gemma-4-31b-it:free

# Ollama (local AI)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_PRIMARY=false
```

Get OpenRouter API key: https://openrouter.ai/settings

## Usage

### Command Line

```bash
achem "your research query" --ddg-limit 100
```

### Options

```bash
--ddg-limit N        Number of DuckDuckGo results (default: 100)
--mode ai           Use AI for conclusions (default)
--mode local        Use local TF-IDF (no API needed)
--lang en/fr/ar     Response language
--no-wikipedia      Skip Wikipedia sources
--no-cache         Skip cache
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│ 1. SEARCH (100+ sources)                           │
│    • DuckDuckGo web search                         │
│    • Prioritizes relevant content                 │
├─────────────────────────────────────────────────────┤
│ 2. SCRAPE (Full article text)                      │
│    • Extracts full content from URLs               │
│    • Uses Trafilatura for clean text               │
│    • Scrapes up to 100 pages concurrently         │
├─────────────────────────────────────────────────────┤
│ 3. FILTER (Relevant content only)                    │
│    • Removes boilerplate and ads                   │
│    • Keeps sentences matching keywords              │
│    • Deduplicates similar content                  │
├─────────────────────────────────────────────────────┤
│ 4. AI CONCLUSION                                   │
│    • Analyzes all content                          │
│    • Generates final prediction                    │
│    • Includes probability percentages               │
│    • Provides key reasons                          │
└─────────────────────────────────────────────────────┘
```

## Output

Reports saved to `~/Documents/ACHEM/` include:
- **AI Conclusion**: Synthesized final prediction
- **All Articles**: Full extracted content from each source
- **Keywords**: Identified topics
- **Extracted Web Content**: Combined filtered content

## License

MIT License - see [LICENSE](LICENSE) file

## Acknowledgments

- [OpenRouter](https://openrouter.ai/) - Free AI models
- [DuckDuckGo](https://duckduckgo.com/) - Privacy-focused search
- [Trafilatura](https://trafilatura.readthedocs.io/) - Web content extraction
- [Sumy](https://miso-belka.github.io/sumy/) - Text summarization
