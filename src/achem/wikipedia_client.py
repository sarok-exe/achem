import wikipediaapi
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
import re

from .cache_manager import CacheManager


class WikipediaClient:
    def __init__(
        self,
        user_agent: str = "ACHEM/1.0 (research tool)",
        max_workers: int = 5,
        use_cache: bool = True,
        cache_ttl: int = 86400,
    ):
        self.api = wikipediaapi.Wikipedia(user_agent)
        self.max_workers = max_workers
        self.cache = CacheManager(ttl_seconds=cache_ttl) if use_cache else None
        self.cache_hits = 0
        self.cache_misses = 0

    def search(self, query: str, limit: int = 10) -> list[dict]:
        if self.cache:
            cached = self.cache.get(query)
            if cached is not None:
                self.cache_hits += 1
                return cached

        self.cache_misses += 1

        results = self.api.search(query, limit=limit)

        titles = list(results.pages.keys())

        articles = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._get_article, title): title for title in titles
            }

            for future in as_completed(futures):
                title = futures[future]
                try:
                    result = future.result()
                    if result:
                        articles.append(result)
                except Exception as e:
                    print(f"  Error processing '{title}': {e}")

        if self.cache and articles:
            self.cache.set(query, articles)

        return articles

    def _get_article(self, title: str) -> Optional[dict]:
        page = self.api.page(title)

        if not page.exists():
            return None

        return self._build_article(page)

    def _get_categories_fast(self, page) -> list[str]:
        categories = []
        if hasattr(page, "categories"):
            for cat in page.categories.keys():
                cat_name = cat.split(":")[-1].lower().strip()
                categories.append(cat_name)
        return categories

    def _build_article(self, page) -> dict:
        return {
            "title": page.title,
            "summary": self._clean_text(page.summary),
            "sections": self._extract_sections(page),
            "categories": self._get_categories_fast(page),
            "url": page.fullurl,
        }

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _extract_sections(self, page) -> list[str]:
        sections = []
        for section in page.sections:
            sections.append(section.title)
        return sections

    def get_articles_for_queries(
        self, queries: list[str], limit_per_query: int = 3
    ) -> list[dict]:
        all_articles = []
        seen_titles = set()

        for query in queries:
            try:
                articles = self.search(query, limit=limit_per_query)
                for article in articles:
                    if article["title"] not in seen_titles:
                        all_articles.append(article)
                        seen_titles.add(article["title"])
            except Exception as e:
                print(f"Warning: Failed to search '{query}': {e}")

        return all_articles

    def get_cache_stats(self) -> dict:
        if self.cache:
            stats = self.cache.get_stats()
            stats["hits"] = self.cache_hits
            stats["misses"] = self.cache_misses
            if self.cache_misses > 0:
                stats["hit_rate"] = round(self.cache_hits / self.cache_misses * 100, 1)
            else:
                stats["hit_rate"] = 0
            return stats
        return {"cache_enabled": False}

    def clear_cache(self) -> None:
        if self.cache:
            self.cache.invalidate()
