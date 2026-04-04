import logging
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
    "forum",
    "community",
    "tutorial",
}


class DuckDuckGoClient:
    """DuckDuckGo search client for fast web results - Deep Research Mode."""

    def __init__(self, max_results: int = 30):
        self.max_results = max_results
        self._ddgs = None

    def _get_client(self):
        """Get or create DuckDuckGo client."""
        if not DDGS_AVAILABLE:
            return None
        if self._ddgs is None:
            self._ddgs = DDGS()
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

            for r in client.text(query, max_results=max_results * 2):
                url = r.get("href", "")
                if url and url not in seen_urls and not self._should_exclude(url):
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
        self, query: str, max_results: int = 30, scrape_top: int = 3
    ) -> tuple[List[dict], str]:
        """Search and also scrape top results for deep content.

        Returns:
            Tuple of (search_results, scraped_content)
        """
        from .web_scraper import get_scraper

        results = self.search(query, max_results)

        if not results:
            return [], ""

        urls_to_scrape = [r["url"] for r in results[:scrape_top] if r.get("url")]

        scraper = get_scraper()
        scraped_text = scraper.get_scraped_text(urls_to_scrape, top_n=scrape_top)

        return results, scraped_text

    def search_batch(self, queries: List[str], max_per_query: int = 10) -> List[dict]:
        """Search multiple queries in parallel."""
        all_results = []

        def search_single(q):
            return self.search(q, max_results=max_per_query)

        with ThreadPoolExecutor(max_workers=5) as executor:
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
