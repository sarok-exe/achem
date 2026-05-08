"""Query Planner — decomposes a topic into sub-queries using OpenRouter AI."""

import json
import logging
from typing import List, Optional

from .config_manager import ConfigManager

RESEARCH_PLANNER_SYSTEM_PROMPT = """You are an Intelligence Analyst responsible for breaking down complex research topics into precise search queries.

Your task is to analyze the user's topic and generate exactly 5 search queries that cover different angles of the topic.

RULES:
1. Each query must be self-contained and searchable on the web
2. Cover different perspectives: technical, historical, comparative, future-looking, and practical
3. Queries should be specific, not generic
4. Output ONLY valid JSON — no explanations, no markdown
5. Use the SAME LANGUAGE as the user's topic

OUTPUT FORMAT (strict JSON):
{
  "queries": [
    "specific search query 1",
    "specific search query 2",
    "specific search query 3",
    "specific search query 4",
    "specific search query 5"
  ],
  "rationale": "Brief 1-sentence explanation of the decomposition strategy"
}"""


async def generate_search_queries(
    topic: str,
    language: str = "en",
    model: Optional[str] = None,
) -> List[str]:
    """Decompose a research topic into 5 search queries using OpenRouter.

    Args:
        topic: The user's research topic
        language: Output language (en, fr, ar)
        model: OpenRouter model override

    Returns:
        List of 5 search query strings. Falls back to [topic] if API fails.
    """
    config = ConfigManager()
    api_key = config.get_openrouter_api_key()
    if not api_key or len(api_key) < 10:
        logging.warning("No OpenRouter API key for planner — using topic as-is")
        return [topic]

    try:
        import aiohttp

        model_name = model or config.get_openrouter_model() or "google/gemma-4-31b-it:free"

        lang_instruction = {
            "ar": "Respond in Arabic.",
            "fr": "Respond in French.",
            "en": "Respond in English.",
        }.get(language[:2], "Respond in English.")

        user_prompt = f"""Topic: {topic}

{lang_instruction}

Generate 5 search queries that comprehensively cover this topic from different angles."""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://achem.github.io",
            "X-Title": "ACHEM Research Planner",
        }

        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": RESEARCH_PLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 1024,
            "temperature": 0.3,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    logging.error(f"Planner API error {response.status}: {text[:200]}")
                    return [topic]

                data = await response.json()

        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        if not content:
            return [topic]

        queries = _parse_queries(content)
        return queries if queries else [topic]

    except ImportError:
        logging.warning("aiohttp not available for planner — using topic as-is")
        return [topic]
    except Exception as e:
        logging.error(f"Planner error: {e}")
        return [topic]


def _parse_queries(raw: str) -> Optional[List[str]]:
    """Parse JSON from AI response, trying multiple extraction strategies."""
    json_candidates = []

    # Strategy 1: Try parsing the entire response as JSON
    cleaned = raw.strip()
    if cleaned.startswith("{"):
        json_candidates.append(cleaned)

    # Strategy 2: Extract JSON from markdown code block
    import re

    code_blocks = re.findall(r"```(?:json)?\s*\n?(.*?)\n?```", raw, re.DOTALL)
    json_candidates.extend(code_blocks)

    # Strategy 3: Find anything between { and } that looks like JSON
    braces_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if braces_match:
        json_candidates.append(braces_match.group(0))

    for candidate in json_candidates:
        try:
            parsed = json.loads(candidate)
            queries = parsed.get("queries", [])
            if queries and len(queries) >= 1:
                return queries[:10]
        except (json.JSONDecodeError, TypeError):
            continue

    # Strategy 4: Fallback — extract numbered lines as queries
    lines = raw.strip().split("\n")
    queries = []
    for line in lines:
        line = line.strip().strip('"').strip("-").strip()
        if line and not line.startswith("{") and not line.startswith("}"):
            cleaned_line = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
            if cleaned_line and len(cleaned_line) > 5:
                queries.append(cleaned_line)

    return queries[:10] if queries else None
