import logging
import json
import time
import requests
from typing import List, Tuple

from .config_manager import ConfigManager


SYSTEM_PROMPT = """You are an expert research analyst. Provide COMPREHENSIVE, DETAILED analysis of at least 300 words.

Requirements:
- Write at least 300 words (detailed paragraphs)
- Cover multiple aspects of the topic
- Synthesize information from ALL sources
- Provide deep insights and analysis
- Use your OWN words, never copy sentences
- Structure your response with clear sections

Output Format:
## Overview
[General understanding of the topic]

## Key Findings
[Detailed analysis with specific facts from sources]

## Important Details
[Supporting evidence and statistics]

## Conclusions
[Your comprehensive conclusions]"""


class OpenRouterSummarizer:
    """AI-powered summarizer using OpenRouter API."""

    def __init__(self):
        self.config = ConfigManager()
        self._ai_available = None

    def is_ai_available(self) -> bool:
        """Check if OpenRouter API is configured."""
        if self._ai_available is not None:
            return self._ai_available

        if not self.config.is_ai_enabled():
            self._ai_available = False
            return False

        api_key = self.config.get_openrouter_api_key()
        if not api_key or len(api_key) < 10:
            logging.warning("OpenRouter API key not found")
            self._ai_available = False
            return False

        self._ai_available = True
        return True

    def _call_api(self, prompt: str) -> str:
        """Call OpenRouter API directly with requests."""
        api_key = self.config.get_openrouter_api_key()
        model = self.config.get_openrouter_model() or "google/gemma-4-31b-it:free"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://achem.github.io",
            "X-Title": "ACHEM Research Tool",
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 4000,
            "temperature": 0.4,
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=90,
            )

            if response.status_code == 429:
                logging.warning("Rate limited, retrying...")
                time.sleep(3)
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=90,
                )

            if response.status_code != 200:
                logging.error(
                    f"OpenRouter error {response.status_code}: {response.text[:200]}"
                )
                return ""

            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return content.strip() if content else ""

        except requests.exceptions.Timeout:
            logging.error("OpenRouter request timed out")
            return ""
        except Exception as e:
            logging.error(f"OpenRouter error: {e}")
            return ""

    def generate_deep_research_summary(
        self,
        search_snippets: List[dict],
        scraped_content: str = "",
        language: str = "en",
        query: str = "",
    ) -> Tuple[str, str]:
        """Generate summary from search results."""

        if not self.is_ai_available():
            return self._fallback_summary(search_snippets), "local"

        lang_instruction = {
            "ar": "Respond in Arabic.",
            "fr": "Respond in French.",
            "en": "Respond in English.",
        }.get(language[:2], "Respond in English.")

        if scraped_content and len(scraped_content) > 100:
            prompt = f"""QUESTION: {query}

Read ALL articles below carefully and write a COMPREHENSIVE analysis of at least 300 words.

=== ARTICLES ===
{scraped_content[:15000]}
===

{lang_instruction}

Your comprehensive analysis (at least 300 words):"""
        else:
            sources = []
            for i, item in enumerate(search_snippets[:50], 1):
                body = item.get("body", item.get("summary", ""))
                if body:
                    sources.append(f"[{i}] {body}")

            sources_text = "\n".join(sources)

            prompt = f"""QUESTION: {query}

Based on {len(search_snippets)} sources, write a COMPREHENSIVE analysis of at least 300 words.

=== SOURCES ===
{sources_text}
===

{lang_instruction}

Your comprehensive analysis (at least 300 words):"""

        result = self._call_api(prompt)

        if result and len(result) > 30:
            return result, "openrouter"

        return self._fallback_summary(search_snippets), "local"

    def _fallback_summary(self, snippets: List[dict]) -> str:
        """Simple fallback when API fails."""
        if not snippets:
            return "No results found."

        bodies = []
        for item in snippets[:10]:
            body = item.get("body", item.get("summary", ""))
            if body:
                bodies.append(body)

        return " ".join(bodies[:3]) if bodies else "Analysis unavailable."


_singleton = None


def get_openrouter_summarizer() -> OpenRouterSummarizer:
    """Get singleton instance."""
    global _singleton
    if _singleton is None:
        _singleton = OpenRouterSummarizer()
    return _singleton
