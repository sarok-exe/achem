import os
import json
from pathlib import Path


class ConfigManager:
    """Manage application configuration from config files."""

    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Load configuration from .env and config.json files."""
        self._config = self._load_env()
        self._config.update(self._load_json_config())

    def _load_env(self) -> dict:
        """Load configuration from .env or api.env file."""
        env_config = {}

        current_dir = Path.cwd()
        home_dir = Path.home()

        try:
            package_dir = Path(__file__).parent.parent.parent
        except Exception:
            package_dir = None

        search_paths = [
            home_dir / ".achem" / "api.env",
            current_dir / ".env",
            current_dir / "api.env",
            home_dir / ".achem.env",
            home_dir / ".ACHEM" / "api.env",
            home_dir / ".config" / "achem" / "api.env",
            home_dir / "Documents" / "ACHEM" / "api.env",
        ]

        if package_dir:
            search_paths.extend(
                [
                    package_dir / ".env",
                    package_dir / "api.env",
                    package_dir / "config.json",
                ]
            )

        env_path = None
        for path in search_paths:
            if path.exists():
                env_path = path
                break

        if env_path:
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_config[key.strip().lower()] = value.strip()

        for key, value in os.environ.items():
            if key.startswith("RESEARCH_"):
                env_key = key.replace("RESEARCH_", "").lower()
                env_config[env_key] = value
            elif key.startswith("OLLAMA_"):
                env_key = key.replace("OLLAMA_", "").lower()
                env_config[env_key] = value

        return env_config

    def _load_json_config(self) -> dict:
        """Load configuration from config.json file."""
        config_path = Path(__file__).parent.parent / "config.json"

        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        return {}

    def get(self, key: str, default=None):
        """Get configuration value by key."""
        return self._config.get(key, default)

    def get_api_key(self) -> str | None:
        """Get Gemini API key from configuration."""
        return self.get("gemini_api_key") or self.get("api_key")

    def get_hf_api_key(self) -> str | None:
        """Get HuggingFace API key from configuration."""
        return self.get("hf_api_key") or self.get("hf_token")

    def get_hf_model(self) -> str | None:
        """Get HuggingFace model name."""
        return self.get("hf_model")

    def get_groq_api_key(self) -> str | None:
        """Get Groq API key from configuration."""
        return self.get("groq_api_key") or self.get("groq_key")

    def get_groq_model(self) -> str | None:
        """Get Groq model name."""
        return self.get("groq_model")

    def get_gemini_api_key(self) -> str | None:
        """Get Gemini API key from configuration."""
        return (
            self.get("gemini_api_key")
            or self.get("gemini_key")
            or os.environ.get("GEMINI_API_KEY")
        )

    def get_gemini_model(self) -> str | None:
        """Get Gemini model name."""
        return self.get("gemini_model")

    def get_openrouter_api_key(self) -> str | None:
        """Get OpenRouter API key from configuration."""
        return self.get("openrouter_api_key") or self.get("openrouter_key")

    def get_openrouter_model(self) -> str | None:
        """Get OpenRouter model name."""
        return self.get("openrouter_model")

    def is_ai_enabled(self) -> bool:
        """Check if AI summarization is enabled."""
        enabled = self.get("ai_enabled", "true")
        if isinstance(enabled, str):
            return enabled.lower() in ("true", "1", "yes")
        return bool(enabled)

    def get_model_name(self) -> str:
        """Get the Gemini model name to use."""
        return self.get("gemini_model", "gemini-2.0-flash")

    def get_max_tokens(self) -> int:
        """Get maximum tokens for AI response."""
        return int(self.get("max_tokens", "2048"))

    def get_temperature(self) -> float:
        """Get temperature for AI generation."""
        return float(self.get("temperature", "0.7"))

    def get_ollama_base_url(self) -> str:
        """Get Ollama base URL."""
        return self.get("ollama_base_url", "http://localhost:11434")

    def get_ollama_model(self) -> str:
        """Get Ollama model name."""
        return self.get("ollama_model", "llama3.2")

    def is_ollama_primary(self) -> bool:
        """Check if Ollama should be used as primary AI."""
        primary = self.get("ollama_primary", "true")
        if isinstance(primary, str):
            return primary.lower() in ("true", "1", "yes")
        return bool(primary)
