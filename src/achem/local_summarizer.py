import logging
import requests
from typing import List, Tuple


class LocalSummarizer:
    """Local AI summarizer using Ollama API."""

    def __init__(
        self, base_url: str = "http://localhost:11434", model: str = "llama3.2"
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._available = None

    def is_ai_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        if self._available is not None:
            return self._available

        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                if self.model in model_names or any(
                    self.model in m for m in model_names
                ):
                    self._available = True
                    return True
            self._available = False
            return False
        except Exception:
            self._available = False
            return False

    def _generate(self, prompt: str) -> str:
        """Generate response from local model."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 2048,
                },
            }

            response = requests.post(
                f"{self.base_url}/api/generate", json=payload, timeout=180
            )

            if response.status_code == 200:
                return response.json().get("response", "")
            return ""
        except Exception as e:
            logging.warning(f"Local AI error: {e}")
            return ""

    def generate_deep_research_summary(
        self,
        search_snippets: List[dict],
        scraped_content: str = "",
        language: str = "en",
        query: str = "",
    ) -> Tuple[str, str]:
        """Generate synthesis using local AI - combines all sources into unified conclusions."""

        snippets_text = ""
        for item in search_snippets[:25]:
            body = item.get("body", item.get("summary", ""))[:500]
            if body:
                snippets_text += f"- {body}\n"

        scraped_text = ""
        if scraped_content:
            scraped_text = f"\n{scraped_content[:5000]}"

        system_prompt = """You are an EXPERT WRITER who synthesizes information into ONE coherent piece.

Your job: Read ALL sources and write NEW content in your own words. DO NOT copy sentences."""

        user_prompt = f"""TASK: Read all information below about "{query}" and write a SYNTHESIZED response.

SOURCES:
{snippets_text}
{scraped_text}

REQUIREMENTS:
1. Write in YOUR OWN WORDS - NEVER copy from sources
2. NEVER mention URLs, titles, or "According to..."
3. Combine everything into ONE unified answer
4. Be direct and practical

Write now:"""

        summary = self._generate(user_prompt)

        if summary and len(summary) > 50:
            return summary, "ollama"
        return "Local AI generation failed. Is Ollama running?", "ollama"

    def generate_summary(
        self, articles: List[dict], language: str = "en", query: str = ""
    ) -> Tuple[str, str]:
        """Generate summary using local AI."""
        return self.generate_deep_research_summary(
            search_snippets=articles,
            scraped_content="",
            language=language,
            query=query,
        )


def get_local_summarizer() -> LocalSummarizer:
    """Get local summarizer instance."""
    return LocalSummarizer()
