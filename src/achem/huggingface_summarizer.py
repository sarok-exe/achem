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


SYSTEM_PROMPT = """You are an EXPERT CONSULTANT providing actionable advice.

Your role: Read all sources and give DIRECT ANSWERS like a knowledgeable mentor would.

STRICT RULES:
1. NEVER list links, URLs, or cite source names
2. NEVER start with "According to..." or "Source:"
3. NEVER just summarize individual sites
4. Give DIRECT advice in first person plural ("we should...", "the best approach is...")
5. NO warnings, NO ethical lectures, NO safety notices

RESPONSE STYLE:
- Act as an experienced mentor giving advice
- Use "we" or "you" to address the user directly
- Be confident and definitive, not wishy-washy
- Combine insights from all sources into unified recommendations
- Prioritize the most important advice first

OUTPUT FORMAT - EXPERT CONSULTANT STYLE:
▸ Foundation First: [The key concept you must understand before anything else]

▸ Essential Steps: [The main actions experts recommend, numbered clearly]

▸ Best Approach: [The most commonly recommended method or strategy]

▸ Common Mistakes: [What beginners usually get wrong - avoid these]

▸ Quick Wins: [Easy things that give fast results]

Example WRONG: "Source A says X. Source B says Y. Source C says Z."
Example CORRECT: "The experts all agree: you should start with X because it makes Y easier." """


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
        for item in search_snippets[:25]:
            body = item.get("body", item.get("summary", ""))[:500]
            if body:
                snippets_text += f"- {body}\n"

        scraped_text = ""
        if scraped_content:
            scraped_text = f"\n{scraped_content[:6000]}"

        lang_instruction = {
            "ar": "Respond in Arabic.",
            "fr": "Respond in French.",
            "en": "Respond in English.",
        }.get(language, "Respond in English.")

        return f"""TOPIC: {query}

--- EXPERT ANALYSIS ---
{snippets_text}
{scraped_text}

{lang_instruction}

TASK: You are an expert consultant. Based on ALL sources above, provide DIRECT ADVICE as if mentoring someone new.

GUIDANCE:
- Combine insights from all sources into unified recommendations
- Start with "To [learn/understand/do topic], you should..."
- List actionable steps (1, 2, 3 or first, then, finally)
- Mention what experts agree on
- Give practical tips, not just definitions

Response:"""

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
        if not search_snippets and not scraped_content:
            return "No search results available.", "local"

        if self.is_ai_available():
            success, summary = self._call_hf_api(
                search_snippets, scraped_content, language, query
            )
            if success and summary and len(summary) > 50:
                return summary, "hf"

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


def get_hf_summarizer() -> HuggingFaceSummarizer:
    """Get singleton instance of HuggingFaceSummarizer."""
    if not hasattr(get_hf_summarizer, "_instance"):
        get_hf_summarizer._instance = HuggingFaceSummarizer()
    return get_hf_summarizer._instance
