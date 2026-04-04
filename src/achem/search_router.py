from typing import List, Tuple
from enum import Enum


class SearchSource(Enum):
    """Available search sources."""

    WIKIPEDIA = "wikipedia"
    DUCKDUCKGO = "duckduckgo"
    BOTH = "both"


class SearchRouter:
    """Router to select appropriate search source based on query."""

    @staticmethod
    def detect_source(query: str) -> SearchSource:
        """Detect best search source based on query.

        Deep-Web Research Mode: DuckDuckGo is ALWAYS primary.
        Wikipedia is only secondary/backup.
        """
        return SearchSource.BOTH

    @staticmethod
    def get_sources_config(query: str) -> Tuple[bool, bool]:
        """Get configuration for which sources to use.

        Returns:
            Tuple of (use_wikipedia, use_duckduckgo)
            Deep Research: DDG is primary (True, True)
            Wikipedia is secondary/backup only
        """
        return True, True

    @staticmethod
    def suggest_sources(query: str) -> str:
        """Suggest which sources to use based on query."""
        return "DuckDuckGo (Primary) + Wikipedia (Secondary)"


def detect_search_sources(query: str) -> Tuple[bool, bool]:
    """Convenience function to detect search sources.

    Deep-Web Research Mode: Always uses both, DDG is primary.
    """
    return True, True


def get_source_priority() -> dict:
    """Return source priority for deep research mode.

    Returns:
        Dict with priority order: ddg=primary, wiki=secondary
    """
    return {
        "primary": "duckduckgo",
        "secondary": "wikipedia",
        "scraping_targets": 5,
        "total_results": 50,
    }
