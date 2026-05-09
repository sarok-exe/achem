# achem

Deep web research tool. Searches DuckDuckGo + Wikipedia + academic sources, scrapes pages, generates AI summaries via OpenRouter/Groq/Gemini/Ollama.

### How to use

```
git clone https://github.com/sarok-exe/achem.git
cd achem
pip install .
```

Set API keys in `~/.ACHEM/api.env`:

```
OPENROUTER_API_KEY=your_key
```

Run:

```
achem "<your query>"
```

Prefix with `l:` for local (TF-IDF) mode, `o:` for Ollama.

```
achem l:python async
achem o:machine learning
```
