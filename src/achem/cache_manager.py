import os
import json
import time
import hashlib
from pathlib import Path
from typing import Optional


class CacheManager:
    def __init__(self, cache_dir: str = None, ttl_seconds: int = 86400):
        if cache_dir is None:
            cache_dir = os.path.join(
                os.path.expanduser("~"), ".wiki-summarizer", "cache"
            )

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds

    def _get_cache_key(self, query: str) -> str:
        """Generate a unique cache key for a query."""
        query_normalized = query.lower().strip()
        return hashlib.md5(query_normalized.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{cache_key}.json"

    def get(self, query: str) -> Optional[dict]:
        """Retrieve cached data for a query."""
        cache_key = self._get_cache_key(query)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            cached_time = cache_data.get("timestamp", 0)
            if time.time() - cached_time > self.ttl_seconds:
                cache_path.unlink()
                return None

            return cache_data.get("data")
        except (json.JSONDecodeError, IOError):
            return None

    def set(self, query: str, data: dict) -> None:
        """Store data in cache for a query."""
        cache_key = self._get_cache_key(query)
        cache_path = self._get_cache_path(cache_key)

        cache_data = {"query": query, "timestamp": time.time(), "data": data}

        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except IOError:
            pass

    def invalidate(self, query: str = None) -> None:
        """Invalidate cache for a specific query or all queries."""
        if query:
            cache_key = self._get_cache_key(query)
            cache_path = self._get_cache_path(cache_key)
            if cache_path.exists():
                cache_path.unlink()
        else:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_size = 0
        file_count = 0
        expired_count = 0
        current_time = time.time()

        for cache_file in self.cache_dir.glob("*.json"):
            file_count += 1
            total_size += cache_file.stat().st_size

            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                cached_time = cache_data.get("timestamp", 0)
                if current_time - cached_time > self.ttl_seconds:
                    expired_count += 1
            except (json.JSONDecodeError, IOError):
                pass

        return {
            "total_files": file_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "expired_files": expired_count,
        }
