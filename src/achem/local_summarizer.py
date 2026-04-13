import logging
import json
from typing import List, Tuple, Optional


class LocalSummarizer:
    """Local AI summarizer using Ollama API."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2",
        config_base_url: Optional[str] = None,
        config_model: Optional[str] = None,
    ):
        self.base_url = (config_base_url or base_url).rstrip("/")
        self.model = config_model or model
        self._available = None

    def is_ai_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        if self._available is not None:
            return self._available

        try:
            import requests

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
            import requests

            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 500,
                    "top_p": 0.9,
                },
            }
            response = requests.post(
                f"{self.base_url}/api/generate", json=payload, timeout=600
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
        """Generate synthesis using local AI - combines sources into conclusions."""

        sources_text = []
        for i, item in enumerate(search_snippets[:10]):
            body = item.get("body", item.get("summary", ""))
            if body:
                sources_text.append(f"[{i + 1}] {body[:500]}")

        scraped_text = ""
        if scraped_content:
            scraped_text = f"\n\nSCRAPED CONTENT:\n{scraped_content[:3000]}"

        user_prompt = f"""Query: "{query}"

Sources ({len(sources_text)} articles):
{"".join(sources_text)}
{scraped_text}

Task: Summarize the key findings into 2-3 clear paragraphs. Be concise and informative.

Summary:"""

        summary = self._generate(user_prompt)

        if summary and len(summary) > 50:
            return summary, "ollama"
        return "Local AI generation failed. Is Ollama running?", "ollama"

    def generate_summary(
        self,
        articles: List[dict],
        scraped_content: str = "",
        language: str = "en",
        query: str = "",
    ) -> Tuple[str, str]:
        """Generate summary using local AI."""
        return self.generate_deep_research_summary(
            search_snippets=articles,
            scraped_content=scraped_content,
            language=language,
            query=query,
        )


def get_local_summarizer(config_manager=None) -> LocalSummarizer:
    """Get local summarizer instance with optional config."""
    if config_manager:
        return LocalSummarizer(
            config_base_url=config_manager.get_ollama_base_url(),
            config_model=config_manager.get_ollama_model(),
        )
    return LocalSummarizer()
