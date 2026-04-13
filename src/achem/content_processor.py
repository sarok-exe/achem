import re
import hashlib
import json
import time
import difflib
from typing import List, Dict, Set, Tuple
from pathlib import Path
from datetime import datetime, timedelta


class ContentCache:
    """Smart cache for scraped content with TTL."""

    def __init__(self, cache_dir: str = None, ttl_hours: int = 24):
        if cache_dir is None:
            cache_dir = Path.home() / ".achem" / "cache"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

    def _url_hash(self, url: str) -> str:
        """Generate hash for URL."""
        return hashlib.md5(url.encode()).hexdigest()

    def get(self, url: str) -> str | None:
        """Get cached content if not expired."""
        cache_file = self.cache_dir / f"{self._url_hash(url)}.json"
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            cached_time = datetime.fromisoformat(data["cached_at"])
            if datetime.now() - cached_time > self.ttl:
                cache_file.unlink()
                return None

            return data["content"]
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def set(self, url: str, content: str) -> None:
        """Cache content."""
        cache_file = self.cache_dir / f"{self._url_hash(url)}.json"
        data = {
            "url": url,
            "content": content,
            "cached_at": datetime.now().isoformat(),
        }
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception:
            pass

    def clear(self) -> int:
        """Clear all cache. Returns number of files removed."""
        count = 0
        for f in self.cache_dir.glob("*.json"):
            f.unlink()
            count += 1
        return count


class TextDeduplicator:
    """Remove duplicate sentences using difflib."""

    def __init__(self, similarity_threshold: float = 0.85):
        self.threshold = similarity_threshold

    def deduplicate(self, sentences: List[str]) -> List[str]:
        """Remove near-duplicate sentences."""
        if not sentences:
            return []

        unique = []
        for sent in sentences:
            is_duplicate = False
            sent_normalized = self._normalize(sent)

            for existing in unique:
                existing_normalized = self._normalize(existing)
                ratio = difflib.SequenceMatcher(
                    None, sent_normalized, existing_normalized
                ).ratio()
                if ratio > self.threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique.append(sent)

        return unique

    def _normalize(self, text: str) -> str:
        """Normalize text for comparison."""
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text


class KeywordFilter:
    """Filter sentences by keywords."""

    def __init__(self, keywords: List[str]):
        self.keywords = {kw.lower() for kw in keywords if len(kw) > 2}
        self.required_matches = max(1, len(self.keywords) // 4)

    def filter(self, sentences: List[str]) -> List[str]:
        """Keep sentences matching at least required keywords."""
        if not self.keywords:
            return sentences

        filtered = []
        for sent in sentences:
            sent_lower = sent.lower()
            matches = sum(1 for kw in self.keywords if kw in sent_lower)
            if matches >= self.required_matches:
                filtered.append(sent)

        return filtered if filtered else sentences


class TextCompressor:
    """Compress text using sumy extractive summarization."""

    def __init__(self):
        self._nltk_downloaded = False

    def _ensure_nltk(self):
        """Download required NLTK data."""
        if not self._nltk_downloaded:
            try:
                import nltk

                nltk.download("punkt", quiet=True)
                nltk.download("punkt_tab", quiet=True)
                nltk.download("stopwords", quiet=True)
                self._nltk_downloaded = True
            except Exception:
                pass

    def compress(self, text: str, target_sentences: int = 5) -> str:
        """Compress text to target number of sentences using sumy."""
        if not text or len(text) < 200:
            return text

        self._ensure_nltk()

        try:
            from sumy.parsers.plaintext import PlaintextParser
            from sumy.nlp.tokenizers import Tokenizer
            from sumy.summarizers.lsa import LsaSummarizer
            from sumy.nlp.stemmers import Stemmer
            from sumy.utils import get_stop_words

            parser = PlaintextParser.from_string(text, Tokenizer("english"))
            stemmer = Stemmer("english")
            summarizer = LsaSummarizer(stemmer)
            summarizer.stop_words = get_stop_words("english")

            sentences = []
            for sentence in summarizer(parser.document, target_sentences):
                sentences.append(str(sentence))

            return " ".join(sentences) if sentences else text[:3000]

        except Exception:
            return self._fallback_compress(text, target_sentences)

    def _fallback_compress(self, text: str, target_sentences: int = 5) -> str:
        """Fallback compression using simple scoring."""
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 30]

        if len(sentences) <= target_sentences:
            return " ".join(sentences)

        scores = {}
        words = set(w.lower() for w in re.findall(r"\w+", text.lower()) if len(w) > 4)

        for i, sent in enumerate(sentences):
            sent_words = set(w.lower() for w in re.findall(r"\w+", sent) if len(w) > 4)
            score = len(sent_words & words)
            scores[i] = score

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, _ in ranked[:target_sentences]]
        top_indices.sort()

        return " ".join(sentences[i] for i in top_indices)


class ContentProcessor:
    """Process scraped content: dedupe, filter, compress."""

    def __init__(self, keywords: List[str] = None):
        self.cache = ContentCache()
        self.deduplicator = TextDeduplicator()
        self.filter = KeywordFilter(keywords or [])
        self.compressor = TextCompressor()

    def process(
        self,
        urls: List[str],
        contents: List[str],
        titles: List[str],
        keywords: List[str],
        compress: bool = True,
        max_pages: int = 50,
    ) -> str:
        """Process scraped content from multiple pages."""
        if not urls or not contents:
            return ""

        self.filter = KeywordFilter(keywords)
        all_sentences = []
        source_map = {}

        for i, (url, content, title) in enumerate(zip(urls, contents, titles)):
            if i >= max_pages:
                break

            if len(content) < 100:
                continue

            sentences = re.split(r"[.!?\n]+", content)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 40]

            for sent in sentences:
                sent_id = hashlib.md5(sent.encode()).hexdigest()[:16]
                source_map[sent_id] = {
                    "url": url,
                    "title": title[:80],
                    "text": sent[:200],
                }
                all_sentences.append(sent)

        all_sentences = self.deduplicator.deduplicate(all_sentences)

        all_sentences = self.filter.filter(all_sentences)

        if compress and all_sentences:
            compressed = []
            for sent in all_sentences:
                if len(compressed) >= 100:
                    break
                compressed.append(sent)

            if len(compressed) > 10:
                combined = ". ".join(compressed)
                combined = self.compressor.compress(combined, target_sentences=15)
                return combined

            return ". ".join(compressed)
        else:
            return ". ".join(all_sentences[:50])

    def process_single(
        self,
        url: str,
        content: str,
        title: str,
        keywords: List[str],
        use_cache: bool = True,
    ) -> str:
        """Process single page content."""
        if use_cache:
            cached = self.cache.get(url)
            if cached:
                return cached

        if len(content) < 100:
            return content

        sentences = re.split(r"[.!?\n]+", content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 40]

        sentences = self.deduplicator.deduplicate(sentences)

        self.filter = KeywordFilter(keywords)
        sentences = self.filter.filter(sentences)

        result = ". ".join(sentences[:30])

        if use_cache and len(result) > 200:
            self.cache.set(url, result)

        return result


def process_content(
    scraped_results: List[dict],
    keywords: List[str],
    compress: bool = True,
) -> str:
    """Convenience function to process scraped results."""
    processor = ContentProcessor(keywords)

    urls = [r.get("url", "") for r in scraped_results]
    contents = [r.get("content", "") for r in scraped_results]
    titles = [r.get("title", "") for r in scraped_results]

    return processor.process(urls, contents, titles, keywords, compress=compress)
