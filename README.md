# ACHEM - Deep Web Research Tool

![ACHEM Banner](https://img.shields.io/badge/ACHEM-v1.2.0-blue?style=for-the-badge)

> **ACHEM** (Arabic: آشم) is an intelligent research tool that automatically classifies your query, finds relevant specialized sources, and generates comprehensive 300+ word AI conclusions.

## Features

### Smart Topic Classification
Automatically detects your query type and prioritizes relevant sources:

| Topic | Priority Sites |
|-------|----------------|
| Anime & Manga | MyAnimeList, Crunchyroll, Anime News Network |
| Football/Soccer | The Analyst, ESPN, Sky Sports, Goal.com |
| MMA/Fighting | Tapology, Sherdog, MMA Junkie |
| Gaming | IGN, GameSpot, Metacritic, Steam |
| Movies/TV | IMDb, Rotten Tomatoes, Metacritic |
| Health/Medicine | Mayo Clinic, WebMD, WHO |
| Science | Scientific American, Nature, NASA |
| Technology | Stack Overflow, GitHub, TechCrunch |
| History | Britannica, History.com |

### Comprehensive Research
- **100+ Sources**: Searches DuckDuckGo with topic-prioritized results
- **Full Content Extraction**: Scrapes complete articles from specialized sites
- **Smart Filtering**: Removes ads/boilerplate, keeps relevant content
- **300+ Word Conclusions**: Detailed AI-generated analysis

### How Results Are Sorted
Results are sorted by relevance:
1. Most relevant sources for your topic first
2. Specialized sites for your query type
3. General sources last

## Installation

```bash
git clone https://github.com/sarok-exe/achem.git
cd achem
uv venv .venv && source .venv/bin/activate
uv pip install -e .
```

### API Configuration

Create `~/.ACHEM/api.env`:

```bash
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_MODEL=google/gemma-4-31b-it:free
```

Get API key: https://openrouter.ai/settings

## Usage

```bash
achem "What are the health risks of smoking?" --ddg-limit 50
achem "Who will win Bayern vs Real Madrid?" --ddg-limit 100
achem "Latest One Piece chapter summary" --ddg-limit 50
```

### Options

```bash
--ddg-limit N     Number of sources (default: 100)
--mode ai         AI conclusions (default)
--mode local      Local TF-IDF (no API)
--lang en/fr/ar   Response language
```

## How It Works

```
┌──────────────────────────────────────────────────────┐
│ 1. CLASSIFY                                          │
│    Detects topic: anime, football, health, etc.       │
│    Identifies priority sites for your topic           │
├──────────────────────────────────────────────────────┤
│ 2. SEARCH (100+ sources)                             │
│    Prioritizes specialized sites                      │
│    Sorts by topic relevance                          │
├──────────────────────────────────────────────────────┤
│ 3. SCRAPE                                            │
│    Extracts full article text                        │
│    Removes ads and boilerplate                       │
├──────────────────────────────────────────────────────┤
│ 4. ANALYZE & CONCLUDE                                │
│    Generates 300+ word comprehensive analysis        │
│    Synthesizes all sources into detailed paragraphs  │
└──────────────────────────────────────────────────────┘
```

## Output

Reports saved to `~/Documents/ACHEM/`:
- **AI Conclusion**: 300+ word detailed analysis
- **All Articles**: Full extracted content
- **Topic Classification**: Shows detected category

## License

MIT License

## Acknowledgments

- [OpenRouter](https://openrouter.ai/) - Free AI models
- [DuckDuckGo](https://duckduckgo.com/) - Web search
- [Trafilatura](https://trafilatura.readthedocs.io/) - Content extraction
