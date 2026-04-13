import logging
from typing import List, Optional, Tuple

from .config_manager import ConfigManager


SYSTEM_PROMPT = """You are a WRITER who creates NEW content based on multiple sources.

CRITICAL - NEVER DO THIS:
- DO NOT copy sentences from sources
- DO NOT list URLs or titles
- DO NOT say "According to..." or "Source:"
- DO NOT output the raw text from any source

WHAT YOU MUST DO:
- Read ALL sources and UNDERSTAND them
- Write COMPLETELY NEW sentences in YOUR own words
- COMBINE information from multiple sources into unified paragraphs
- Think: "What would an expert say about this topic?"

RESPONSE FORMAT - Write as ONE flowing piece of text:
- No bullet points unless explicitly asked
- No citations or references
- Pure synthesized writing in your own voice

Think of yourself as a journalist who read many articles and is now writing a summary article."""


class GroqSummarizer:
    """AI-powered summarizer using Groq API."""

    def __init__(self):
        self.config = ConfigManager()
        self._ai_available = None
        self._client = None

    def is_ai_available(self) -> bool:
        """Check if Groq summarization is available and configured."""
        if self._ai_available is not None:
            return self._ai_available

        if not self.config.is_ai_enabled():
            self._ai_available = False
            return False

        api_key = self.config.get_groq_api_key()
        if not api_key:
            self._ai_available = False
            return False

        self._ai_available = True
        return True

    def _get_client(self):
        """Get or initialize Groq client."""
        if self._client is not None:
            return self._client

        api_key = self.config.get_groq_api_key()
        if not api_key:
            return None

        try:
            from groq import Groq

            self._client = Groq(api_key=api_key)
            return self._client
        except Exception as e:
            logging.warning(f"Failed to configure Groq: {e}")
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
        for item in search_snippets[:25]:
            body = item.get("body", item.get("summary", ""))[:500]
            if body:
                snippets_text += f"[Info: {body}]\n"

        scraped_text = ""
        if scraped_content:
            scraped_text = f"\n[Additional: {scraped_content[:5000]}]"

        lang_instruction = {
            "ar": "Respond in Arabic.",
            "fr": "Respond in French.",
            "en": "Respond in English.",
        }.get(language, "Respond in English.")

        return f"""QUESTION: {query}

Read the following information and write a RESPONSE in your OWN WORDS:

{snippets_text}
{scraped_text}

{lang_instruction}

WRITE YOUR RESPONSE NOW:
- Use YOUR OWN words, not the words from above
- Combine everything into ONE cohesive answer
- NO copying, NO citations, NO references
- Just pure synthesized writing:"""

    def _call_groq_api(
        self,
        search_snippets: List[dict],
        scraped_content: str,
        language: str,
        query: str,
    ) -> Tuple[bool, str]:
        """Generate summary using Groq API with deep research prompt."""
        client = self._get_client()
        if client is None:
            return False, ""

        try:
            model = self.config.get_groq_model() or "llama-3.3-70b-versatile"
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
            if content:
                return True, content.strip()
            return False, ""
        except Exception as e:
            logging.warning(f"Groq API error: {e}")
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
            success, summary = self._call_groq_api(
                search_snippets, scraped_content, language, query
            )
            if success and summary and len(summary) > 50:
                return summary, "groq"

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
            return "No content available for summarization."

        parts = []

        if scraped_content:
            cleaned = self._strip_urls(scraped_content)
            if len(cleaned) > 100:
                parts.append(f"## From Scraped Sources:\n{cleaned[:3000]}...")

        if snippets:
            combined = []
            for item in snippets[:10]:
                title = item.get("title", "N/A")
                body = self._strip_urls(item.get("body", "") or item.get("summary", ""))
                if body and len(body) > 20:
                    combined.append(f"**{title}**: {body[:400]}")

            if combined:
                parts.append("## Key Findings:\n" + "\n\n".join(combined))

        if not parts:
            combined = []
            for item in snippets[:5]:
                title = item.get("title", "N/A")
                combined.append(f"**{title}**")
            if combined:
                return "## Sources Found:\n" + "\n".join(combined)

        return (
            "\n\n".join(parts)
            if parts
            else f"Found {len(snippets)} sources. Content extraction incomplete."
        )

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


def get_groq_summarizer() -> GroqSummarizer:
    """Get singleton instance of GroqSummarizer."""
    if not hasattr(get_groq_summarizer, "_instance"):
        get_groq_summarizer._instance = GroqSummarizer()
    return get_groq_summarizer._instance
