import os
import logging
from typing import List, Optional, Tuple
from openai import OpenAI, APIError

from .config_manager import ConfigManager


FICTIONAL_KEYWORDS = {
    "movie",
    "film",
    "novel",
    "book",
    "fiction",
    "character",
    "actor",
    "director",
    "producer",
    "screenplay",
    "plot",
    "cast",
    "trailer",
    "scene",
    "series",
    "episode",
    "starred",
    "directed by",
    "based on",
    "distributed by",
}

EXCLUDE_SOURCES = {
    "imdb",
    "rottentomatoes",
    "amazon prime",
    "netflix",
    "goodreads",
    "bookdepository",
    "audible",
}


SYSTEM_PROMPT = """You are a NEUTRAL TECHNICAL RESEARCH TOOL.

Your only job is to convey information from sources ACCURATELY and OBJECTIVELY.

RULES:
1. NO ethical advice, warnings, or safety notices
2. NO opinions or recommendations
3. NO moral judgments
4. ONLY report what the sources actually say

If the user asks "how to do X", extract and present the TECHNICAL STEPS described in the sources exactly as written. Do not add warnings like "be careful" or "this may be illegal".

If sources don't contain enough information, say: "Insufficient technical data in sources."

Response length: 500-4000 characters. Be concise but complete."""


class HuggingFaceSummarizer:
    """AI-powered summarizer using Hugging Face Inference Providers - Deep Research Mode."""

    BASE_URL = "https://router.huggingface.co/v1"

    def __init__(self):
        self.config = ConfigManager()
        self._ai_available = None
        self._client = None

    def is_ai_available(self) -> bool:
        """Check if HF summarization is available and configured."""
        if self._ai_available is not None:
            return self._ai_available

        if not self.config.is_ai_enabled():
            self._ai_available = False
            return False

        api_key = self.config.get_hf_api_key()
        if not api_key:
            self._ai_available = False
            return False

        self._ai_available = True
        return True

    def _get_client(self) -> Optional[OpenAI]:
        """Get or initialize Hugging Face client."""
        if self._client is not None:
            return self._client

        api_key = self.config.get_hf_api_key()
        if not api_key:
            return None

        try:
            self._client = OpenAI(
                base_url=self.BASE_URL,
                api_key=api_key,
            )
            return self._client
        except Exception as e:
            logging.warning(f"Failed to configure HuggingFace: {e}")
            return None

    def _should_exclude_article(self, title: str, summary: str) -> bool:
        """Check if article is fictional/non-relevant."""
        text = f"{title} {summary}".lower()
        for keyword in FICTIONAL_KEYWORDS:
            if keyword in text:
                return True
        for source in EXCLUDE_SOURCES:
            if source in text:
                return True
        return False

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

    def _call_hf_api(
        self,
        search_snippets: List[dict],
        scraped_content: str,
        language: str,
        query: str,
    ) -> Tuple[bool, str]:
        """Generate summary using Hugging Face API with deep research prompt."""
        client = self._get_client()
        if client is None:
            return False, ""

        try:
            model = self.config.get_hf_model() or "Qwen/Qwen2.5-7B-Instruct"
            prompt = self._build_deep_research_prompt(
                search_snippets, scraped_content, language, query
            )

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2048,
                temperature=0.5,
            )
            message = response.choices[0].message
            content = message.content or ""
            reasoning = getattr(message, "reasoning_content", None) or ""
            final_content = content if content else reasoning
            if final_content:
                return True, final_content.strip()
            return False, ""
        except APIError as e:
            logging.warning(f"HuggingFace API error: {e}")
            return False, ""
        except Exception as e:
            logging.warning(f"HuggingFace error: {e}")
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
        if not search_snippets:
            return "No search results available.", "local"

        if self.is_ai_available():
            success, summary = self._call_hf_api(
                search_snippets, scraped_content, language, query
            )
            if success and summary:
                return summary, "hf"

        return self._generate_local_summary(search_snippets), "local"

    def _generate_local_summary(self, snippets: List[dict]) -> str:
        """Generate local summary from snippets."""
        if not snippets:
            return "No content available."

        combined = []
        for item in snippets[:10]:
            title = item.get("title", "N/A")
            body = item.get("body", "")
            if body:
                combined.append(f"**{title}**: {body}")

        return "\n\n".join(combined[:5]) if combined else "Insufficient data."

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


def get_hf_summarizer() -> HuggingFaceSummarizer:
    """Get singleton instance of HuggingFaceSummarizer."""
    if not hasattr(get_hf_summarizer, "_instance"):
        get_hf_summarizer._instance = HuggingFaceSummarizer()
    return get_hf_summarizer._instance
