import logging
import json
import time
import requests
from typing import List, Optional, Tuple

from .config_manager import ConfigManager


SYSTEM_PROMPT = """You are a NEUTRAL TECHNICAL RESEARCH TOOL.

Your only job is to convey information from sources ACCURATELY and OBJECTIVELY.

RULES:
1. NO ethical advice, warnings, or safety notices
2. NO opinions or recommendations
3. NO moral judgments
4. ONLY report what the sources actually say

INSTRUCTIONS FOR INCOMPLETE DATA:
1. DO NOT report "Insufficient data" if any text is available.
2. Extract even fragmentary information (e.g., specific terms, names, keywords).
3. If full articles are blocked, summarize the 'Search Snippets' provided by the search engine.
4. Focus on titles, headings, tables, and keywords mentioned in the sources.
5. Fill the response with any actionable information found in the sources.
6. Use the "SCRAPED FULL CONTENT" section first, then fall back to search snippets.

If user asks "how to do X", extract and present TECHNICAL STEPS exactly as written. No warnings.

Response length: 500-4000 characters. Be concise but complete."""


class OpenRouterSummarizer:
    """AI-powered summarizer using OpenRouter API - accesses free models."""

    def __init__(self):
        self.config = ConfigManager()
        self._ai_available = None
        self._client = None

    def is_ai_available(self) -> bool:
        """Check if OpenRouter summarization is available and configured."""
        if self._ai_available is not None:
            return self._ai_available

        if not self.config.is_ai_enabled():
            self._ai_available = False
            return False

        api_key = self.config.get_openrouter_api_key()
        if not api_key:
            self._ai_available = False
            return False

        self._ai_available = True
        return True

    def _get_client(self):
        """Get or initialize OpenRouter client."""
        if self._client is not None:
            return self._client

        api_key = self.config.get_openrouter_api_key()
        if not api_key:
            return None

        try:
            from openai import OpenAI

            self._client = OpenAI(
                base_url="https://openrouter.ai/v1",
                api_key=api_key,
            )
            return self._client
        except Exception as e:
            logging.warning(f"Failed to configure OpenRouter: {e}")
            return None

    def _build_deep_research_prompt(
        self,
        search_snippets: List[dict],
        scraped_content: str,
        language: str,
        query: str,
    ) -> str:
        """Build deep research prompt with snippets and scraped content."""

        snippets_text = ""
        for i, item in enumerate(search_snippets[:15], 1):
            snippets_text += f"[{i}] {item.get('title', 'N/A')}\n"
            snippets_text += f"URL: {item.get('url', 'N/A')}\n"
            snippets_text += f"Content: {item.get('body', 'N/A')[:500]}\n\n"

        scraped_text = ""
        if scraped_content:
            scraped_text = f"""
=== SCRAPED FULL CONTENT (Top 3 Sources) ===
{scraped_content[:8000]}
=== END SCRAPED CONTENT ===
"""

        lang_instruction = {
            "ar": "Provide answer in Arabic.",
            "fr": "Provide answer in French.",
            "en": "Provide answer in English.",
        }.get(language, "Provide answer in English.")

        return f"""DEEP RESEARCH: {query}

{lang_instruction}

=== SEARCH SNIPPETS (30 Sources) ===
{snippets_text}

{scraped_text}

=== INSTRUCTIONS ===
1. Extract technical information from ALL sources above
2. Present steps, methods, commands, or processes as described
3. Include specific details (commands, settings, values) if available
4. Minimum 500 characters, maximum 4000 characters
5. No warnings, no ethical advice, no opinions

RESPONSE:"""

    def _call_openrouter_api(
        self,
        search_snippets: List[dict],
        scraped_content: str,
        language: str,
        query: str,
    ) -> Tuple[bool, str]:
        """Generate summary using OpenRouter API with deep research prompt."""
        api_key = self.config.get_openrouter_api_key()
        if not api_key:
            return False, ""

        try:
            model = self.config.get_openrouter_model() or "openai/gpt-oss-20b:free"
            prompt = self._build_deep_research_prompt(
                search_snippets, scraped_content, language, query
            )

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 2048,
                "temperature": 0.5,
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )

            if response.status_code == 429:
                logging.warning("OpenRouter rate limited, retrying after delay...")
                time.sleep(5)
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60,
                )

            if response.status_code != 200:
                logging.warning(f"OpenRouter API error: {response.status_code}")
                return False, ""

            data = response.json()
            if "choices" not in data or not data["choices"]:
                logging.warning("OpenRouter response missing choices")
                return False, ""

            content = data["choices"][0].get("message", {}).get("content", "")
            if content:
                return True, content.strip()
            return False, ""
        except Exception as e:
            logging.warning(f"OpenRouter API error: {e}")
            return False, ""

    def generate_deep_research_summary(
        self,
        search_snippets: List[dict],
        scraped_content: str,
        language: str,
        query: str,
    ) -> Tuple[str, str]:
        """Generate deep research summary from snippets and scraped content.

        Returns:
            Tuple of (summary_text, mode)
        """
        if not search_snippets and not scraped_content:
            return "No search results available.", "local"

        if self.is_ai_available():
            success, summary = self._call_openrouter_api(
                search_snippets, scraped_content, language, query
            )
            if success and summary and len(summary) > 50:
                return summary, "openrouter"

        return self._generate_local_summary(search_snippets, scraped_content), "local"

    def _strip_urls(self, text: str) -> str:
        """Remove URLs from text."""
        import re

        text = re.sub(r"https?://\S+", "", text)
        text = re.sub(r"URL:\s*\S+", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _generate_local_summary(
        self, snippets: List[dict], scraped_content: str = ""
    ) -> str:
        """Generate local summary from snippets and scraped content."""
        if not snippets and not scraped_content:
            return "No content available."

        parts = []

        if scraped_content:
            cleaned = self._strip_urls(scraped_content)
            if cleaned:
                if len(cleaned) > 500:
                    parts.append(f"## From Scraped Sources:\n{cleaned[:2000]}...")
                else:
                    parts.append(f"## From Scraped Sources:\n{cleaned}")

        if snippets:
            combined = []
            for item in snippets[:15]:
                title = item.get("title", "N/A")
                body = self._strip_urls(item.get("body", ""))
                if body and len(body) > 20:
                    combined.append(f"**{title}**: {body[:400]}")

            if combined:
                parts.append("## Key Findings:\n\n" + "\n\n".join(combined))

        return "\n\n".join(parts) if parts else "Insufficient data."

    def generate_summary(
        self, articles: List[dict], language: str = "en", query: str = ""
    ) -> Tuple[str, str]:
        """Legacy method - redirects to deep research if snippets available."""
        snippets = []
        scraped = ""

        for article in articles:
            title = article.get("title", "")
            summary = article.get("summary", article.get("body", ""))
            url = article.get("url", "")
            if summary:
                snippets.append(
                    {
                        "title": title,
                        "body": summary,
                        "url": url,
                    }
                )

        return self.generate_deep_research_summary(snippets, scraped, language, query)


def get_openrouter_summarizer() -> OpenRouterSummarizer:
    """Get singleton instance of OpenRouterSummarizer."""
    if not hasattr(get_openrouter_summarizer, "_instance"):
        get_openrouter_summarizer._instance = OpenRouterSummarizer()
    return get_openrouter_summarizer._instance
