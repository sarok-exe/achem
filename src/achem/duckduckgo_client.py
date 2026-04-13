import logging
import re
import time
from typing import List, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

try:
    from ddgs import DDGS

    DDGS_AVAILABLE = True
except ImportError:
    try:
        from duckduckgo_search import DDGS

        DDGS_AVAILABLE = True
    except ImportError:
        DDGS_AVAILABLE = False


EXCLUDE_DOMAINS = {
    "cookie",
    "consent",
    "signin",
    "login",
    "signup",
    "register",
    "account",
    "facebook.com",
    "twitter.com",
    "instagram.com",
    "tiktok.com",
    "youtube.com",
    "google.com",
    "bing.com",
    "yahoo.com",
}

TECHNICAL_PRIORITY_DOMAINS = {
    "github.com",
    "stackoverflow.com",
    "medium.com",
    "dev.to",
    "reddit.com",
    "forum",
    "blog",
    "docs",
    "documentation",
    "wiki",
    "community",
    "tutorial",
}

MUSIC_DOMAINS = {
    "spotify.com",
    "genius.com",
    "azlyrics.com",
    "lyrics.com",
    "songfacts.com",
}
MUSIC_KEYWORDS = {
    "song",
    "lyrics",
    "album",
    "released",
    "singer",
    "recorded",
    "track",
    "chart",
    "elvis",
    "presley",
    "beatles",
    "taylor swift",
    "beyonce",
    "drake",
    "spotify",
    "itunes",
}

MOVIE_KEYWORDS = {
    "film",
    "movie",
    "cinema",
    "director",
    "actor",
    "trailer",
    "premiere",
    "box office",
    "netflix",
    "hulu",
    "disney",
    "marvel",
    "hollywood",
}

ADVICE_KEYWORDS = {
    "how to",
    "tips",
    "guide",
    "ways",
    "advice",
    "steps",
    "learn",
    "best",
}


class DuckDuckGoClient:
    """DuckDuckGo search client for fast web results - Deep Research Mode."""

    def __init__(self, max_results: int = 50):
        self.max_results = max_results
        self._ddgs = None

    def _get_client(self):
        """Get or create DuckDuckGo client."""
        if not DDGS_AVAILABLE:
            return None
        if self._ddgs is None:
            self._ddgs = DDGS(proxy=None, timeout=20)
        return self._ddgs

    def _should_exclude(self, url: str) -> bool:
        """Check if URL should be excluded."""
        if not url:
            return True
        parsed = urlparse(url.lower())
        domain = parsed.netloc

        for exclude in EXCLUDE_DOMAINS:
            if exclude in domain:
                return True
        return False

    def _detect_query_context(self, query: str) -> str:
        """Detect query context (survival, technical, advice, general)."""
        query_lower = query.lower()

        if "survive" in query_lower or "survival" in query_lower:
            return "survival"

        for kw in ADVICE_KEYWORDS:
            if kw in query_lower:
                return "advice"
        return "general"

    def _is_context_mismatch(self, query: str, title: str, url: str) -> bool:
        """Check if result is a context mismatch."""
        query_context = self._detect_query_context(query)

        title_lower = title.lower()
        url_lower = url.lower()
        combined = title_lower + " " + url_lower

        programming_terms = {
            "script",
            "code",
            "programming",
            "tutorial",
            "install",
            "pip",
            "github",
            "beginner",
            "project",
            "function",
            "class",
            "file",
            "import",
            "run",
            "execute",
            "package",
        }
        survival_terms = {
            "snake",
            "reptile",
            "wildlife",
            "fireman",
            "neck",
            "constrict",
            "bite",
            "escape",
            "prey",
            "animal",
            "dangerous",
        }

        if query_context == "survival":
            prog_count = sum(1 for t in programming_terms if t in combined)
            if prog_count >= 3:
                return True

        if query_context == "advice":
            music_count = sum(
                1 for kw in MUSIC_KEYWORDS if kw in title_lower or kw in url_lower
            )
            if (
                music_count >= 2
                and "music" not in query.lower()
                and "song" not in query.lower()
            ):
                return True

            movie_count = sum(1 for kw in MOVIE_KEYWORDS if kw in title_lower)
            if (
                movie_count >= 2
                and "movie" not in query.lower()
                and "film" not in query.lower()
            ):
                return True

        return False

    def _get_priority_score(self, url: str) -> int:
        """Get priority score for URL (higher = more technical)."""
        parsed = urlparse(url.lower())
        domain = parsed.netloc

        score = 0
        for tech_domain in TECHNICAL_PRIORITY_DOMAINS:
            if tech_domain in domain:
                score += 10

        if "stackoverflow" in domain:
            score += 20
        if "github" in domain:
            score += 15
        if "forum" in domain:
            score += 10

        return score

    def search(self, query: str, max_results: int = None) -> List[dict]:
        """Search DuckDuckGo and return prioritized results."""
        if max_results is None:
            max_results = self.max_results

        client = self._get_client()
        if client is None:
            return []

        try:
            all_results = []
            seen_urls = set()
            filtered_count = 0

            for r in client.text(query, max_results=max_results * 2):
                url = r.get("href", "")
                title = r.get("title", "")

                if url and url not in seen_urls and not self._should_exclude(url):
                    if self._is_context_mismatch(query, title, url):
                        filtered_count += 1
                        continue

                    seen_urls.add(url)
                    all_results.append(
                        {
                            "title": title,
                            "body": r.get("body", ""),
                            "url": url,
                            "source": "duckduckgo",
                            "priority_score": self._get_priority_score(url),
                        }
                    )

            if filtered_count > 0:
                logging.info(f"Filtered {filtered_count} context-mismatched results")

            if not all_results:
                for r in client.text(query, max_results=max_results):
                    url = r.get("href", "")
                    if url and url not in seen_urls and "yahoo" not in url.lower():
                        seen_urls.add(url)
                        all_results.append(
                            {
                                "title": r.get("title", ""),
                                "body": r.get("body", ""),
                                "url": url,
                                "source": "duckduckgo",
                                "priority_score": self._get_priority_score(url),
                            }
                        )

            all_results.sort(key=lambda x: x["priority_score"], reverse=True)

            return all_results[:max_results]

        except Exception as e:
            logging.warning(f"DuckDuckGo search error: {e}")
            return []

    def search_with_scrape(
        self,
        query: str,
        max_results: int = 30,
        scrape_top: int = 3,
        trusted_only: bool = False,
    ) -> tuple[List[dict], str]:
        """Search and also scrape top results for deep content.

        Args:
            trusted_only: If True, only return results from trusted sources
        """
        from .web_scraper import get_scraper

        results = self.search(query, max_results)

        if not results:
            return [], ""

        if trusted_only:
            trusted_sources = [
                "wikipedia.org",
                "wikimedia.org",
                "cnn.com",
                "bbc.com",
                "reuters.com",
                "apnews.com",
                "nytimes.com",
                "theguardian.com",
                "nasa.gov",
                "nih.gov",
                ".edu",
                ".gov",
            ]
            results = [
                r
                for r in results
                if any(s in r.get("url", "").lower() for s in trusted_sources)
            ]

        urls_to_scrape = [r["url"] for r in results[:scrape_top] if r.get("url")]

        scraper = get_scraper()
        scraped_text = scraper.get_scraped_text(urls_to_scrape, top_n=scrape_top)

        return results, scraped_text

    def search_batch(self, queries: List[str], max_per_query: int = 10) -> List[dict]:
        """Search multiple queries in parallel."""
        all_results = []

        def search_single(q):
            return self.search(q, max_results=max_per_query)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(search_single, q): q for q in queries}
            for future in as_completed(futures):
                try:
                    results = future.result()
                    all_results.extend(results)
                except Exception as e:
                    logging.warning(f"Query failed: {futures[future]} - {e}")

        return all_results


def get_ddg_client(max_results: int = 30) -> DuckDuckGoClient:
    """Get DuckDuckGo client instance for deep research."""
    return DuckDuckGoClient(max_results=max_results)
