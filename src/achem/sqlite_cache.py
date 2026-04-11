import os
import json
import time
import sqlite3
import hashlib
from pathlib import Path
from typing import Optional, List, Dict
from contextlib import contextmanager


class SQLiteCache:
    """SQLite-based cache for search results."""

    def __init__(self, cache_dir: str = None, ttl_seconds: int = 86400):
        if cache_dir is None:
            cache_dir = os.path.join(os.path.expanduser("~"), ".wiki-summarizer")

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / "cache.db"
        self.ttl_seconds = ttl_seconds
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    query_hash TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    articles_json TEXT NOT NULL,
                    full_content TEXT,
                    summary TEXT,
                    summary_mode TEXT,
                    relevance_scores_json TEXT,
                    keywords_json TEXT,
                    timestamp REAL NOT NULL,
                    expires_at REAL NOT NULL
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires 
                ON cache(expires_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_query 
                ON cache(query)
            """)
            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _get_cache_key(self, query: str) -> str:
        """Generate a unique cache key for a query."""
        query_normalized = query.lower().strip()
        return hashlib.sha256(query_normalized.encode()).hexdigest()

    def get(self, query: str) -> Optional[Dict]:
        """Retrieve cached data for a query."""
        cache_key = self._get_cache_key(query)
        current_time = time.time()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM cache WHERE query_hash = ? AND expires_at > ?""",
                (cache_key, current_time),
            )
            row = cursor.fetchone()

            if row:
                return {
                    "articles": json.loads(row["articles_json"]),
                    "full_content": row["full_content"] or "",
                    "summary": row["summary"],
                    "summary_mode": row["summary_mode"],
                    "relevance_scores": json.loads(row["relevance_scores_json"])
                    if row["relevance_scores_json"]
                    else {},
                    "keywords": json.loads(row["keywords_json"])
                    if row["keywords_json"]
                    else [],
                    "timestamp": row["timestamp"],
                    "cached": True,
                }

            cursor.execute("""DELETE FROM cache WHERE query_hash = ?""", (cache_key,))
            conn.commit()

        return None

    def set(
        self,
        query: str,
        articles: List[Dict],
        summary: str,
        summary_mode: str = "local",
        relevance_scores: Dict = None,
        keywords: List = None,
        full_content: str = None,
    ) -> None:
        """Store data in cache for a query."""
        cache_key = self._get_cache_key(query)
        current_time = time.time()
        expires_at = current_time + self.ttl_seconds

        articles_json = json.dumps(articles, ensure_ascii=False)
        relevance_json = json.dumps(relevance_scores or {}, ensure_ascii=False)
        keywords_json = json.dumps(keywords or [], ensure_ascii=False)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO cache 
                (query_hash, query, articles_json, full_content, summary, summary_mode, 
                relevance_scores_json, keywords_json, timestamp, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    cache_key,
                    query,
                    articles_json,
                    full_content or "",
                    summary,
                    summary_mode,
                    relevance_json,
                    keywords_json,
                    current_time,
                    expires_at,
                ),
            )
            conn.commit()

    def invalidate(self, query: str = None) -> int:
        """Invalidate cache for a specific query or all queries."""
        count = 0
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if query:
                cache_key = self._get_cache_key(query)
                cursor.execute(
                    """DELETE FROM cache WHERE query_hash = ?""", (cache_key,)
                )
                count = cursor.rowcount
            else:
                cursor.execute("""DELETE FROM cache""")
                count = cursor.rowcount
            conn.commit()
        return count

    def cleanup_expired(self) -> int:
        """Remove expired cache entries."""
        current_time = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """DELETE FROM cache WHERE expires_at < ?""", (current_time,)
            )
            count = cursor.rowcount
            conn.commit()
        return count

    def get_stats(self) -> Dict:
        """Get cache statistics."""
        total_size = self.db_path.stat().st_size if self.db_path.exists() else 0
        current_time = time.time()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT COUNT(*) as total FROM cache""")
            total = cursor.fetchone()["total"]

            cursor.execute(
                """SELECT COUNT(*) as expired FROM cache WHERE expires_at < ?""",
                (current_time,),
            )
            expired = cursor.fetchone()["expired"]

        return {
            "total_entries": total,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "expired_entries": expired,
        }


_cache_instance = None


def get_sqlite_cache(ttl_seconds: int = 86400) -> SQLiteCache:
    """Get singleton SQLite cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = SQLiteCache(ttl_seconds=ttl_seconds)
    return _cache_instance
