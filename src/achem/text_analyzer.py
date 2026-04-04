import math
import re
from collections import Counter
from typing import List


class TextAnalyzer:
    """Analyze text using logarithmic TF-IDF for keyword extraction."""

    NEGATIVE_INDICATORS = {
        "directed by",
        "starring",
        "cast:",
        "produced by",
        "released",
        "box office",
        "runtime",
        "plot:",
        "album review",
        "track listing",
        "personnel",
    }

    def __init__(self, min_keyword_length: int = 4):
        self.min_keyword_length = min_keyword_length
        self.stop_words = self._load_stop_words()

    def _load_stop_words(self) -> set:
        """Load common English stop words."""
        return {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "is",
            "was",
            "are",
            "were",
            "been",
            "be",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "shall",
            "can",
            "need",
            "this",
            "that",
            "these",
            "those",
            "it",
            "its",
            "they",
            "them",
            "their",
            "we",
            "our",
            "you",
            "your",
            "he",
            "she",
            "him",
            "her",
            "his",
            "her",
            "what",
            "which",
            "who",
            "whom",
            "whose",
            "where",
            "when",
            "why",
            "how",
            "all",
            "each",
            "every",
            "both",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "nor",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "just",
            "also",
            "now",
            "here",
            "there",
            "then",
            "once",
            "about",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "under",
            "again",
            "further",
            "then",
            "once",
            "being",
            "because",
            "while",
            "although",
            "however",
            "upon",
            "within",
            "without",
            "according",
            "including",
        }

    def tokenize(self, text: str) -> list[str]:
        """Tokenize text into words."""
        text = text.lower()
        words = re.findall(r"\b[a-z]+\b", text)
        return [
            w
            for w in words
            if len(w) >= self.min_keyword_length and w not in self.stop_words
        ]

    def calculate_tf(self, tokens: list[str]) -> dict[str, int]:
        """Calculate term frequency."""
        return dict(Counter(tokens))

    def calculate_log_tf(self, tf: dict[str, int]) -> dict[str, float]:
        """Apply logarithmic scaling to TF: log(tf + 1)"""
        return {term: math.log(count + 1) for term, count in tf.items()}

    def calculate_idf(self, documents: list[list[str]]) -> dict[str, float]:
        """Calculate inverse document frequency: log(N / df)"""
        n_docs = len(documents)
        df = Counter()

        for doc in documents:
            unique_terms = set(doc)
            for term in unique_terms:
                df[term] += 1

        return {term: math.log(n_docs / doc_freq) for term, doc_freq in df.items()}

    def calculate_tfidf(self, articles: list[dict]) -> list[list[tuple[str, float]]]:
        """Calculate TF-IDF scores for all articles."""
        if not articles:
            return []

        documents = []
        for article in articles:
            tokens = self.tokenize(
                article.get("summary", "") + " " + " ".join(article.get("sections", []))
            )
            documents.append(tokens)

        idf = self.calculate_idf(documents)
        tfidf_results = []

        for tokens in documents:
            tf = self.calculate_tf(tokens)
            log_tf = self.calculate_log_tf(tf)

            tfidf = {
                term: log_tf_val * idf.get(term, 0)
                for term, log_tf_val in log_tf.items()
            }

            sorted_tfidf = sorted(tfidf.items(), key=lambda x: x[1], reverse=True)
            tfidf_results.append(sorted_tfidf[:20])

        return tfidf_results

    def find_recurring_keywords(
        self, articles: list[dict], top_n: int = 15
    ) -> list[tuple[str, float]]:
        """Find keywords that appear across multiple articles."""
        if not articles:
            return []

        term_doc_freq = Counter()
        term_total_score = Counter()
        n_articles = len(articles)

        tfidf_results = self.calculate_tfidf(articles)

        for tfidf_list in tfidf_results:
            for term, score in tfidf_list:
                term_doc_freq[term] += 1
                term_total_score[term] += score

        recurring = []
        for term in term_doc_freq:
            if term_doc_freq[term] >= 1:
                avg_score = term_total_score[term] / term_doc_freq[term]
                doc_ratio = term_doc_freq[term] / n_articles
                combined_score = avg_score * math.log(1 + doc_ratio)
                recurring.append((term, combined_score))

        recurring.sort(key=lambda x: x[1], reverse=True)
        return recurring[:top_n]

    def detect_negative_content(self, article: dict) -> list[str]:
        """Detect if article contains non-informational content indicators."""
        warnings = []
        summary = article.get("summary", "").lower()
        title = article.get("title", "").lower()

        combined = f"{title} {summary}"

        for indicator in self.NEGATIVE_INDICATORS:
            if indicator in combined:
                warnings.append(f"Contains '{indicator}': may be a film/music result")

        return warnings

    def filter_articles(self, articles: list[dict]) -> tuple[list[dict], list[str]]:
        """Filter out low-quality articles and return filtered list with warnings."""
        filtered = []
        warnings = []

        for article in articles:
            article_warnings = self.detect_negative_content(article)
            if article_warnings:
                warnings.extend(article_warnings)
            filtered.append(article)

        return filtered, warnings

    def calculate_relevance_scores(
        self, articles: list[dict], search_terms: list[str]
    ) -> dict[str, float]:
        """Calculate relevance score for each article based on search term match."""
        scores = {}
        search_terms_set = set(t.lower() for t in search_terms)
        search_query = " ".join(search_terms).lower()

        for article in articles:
            title = article.get("title", "").lower()
            summary = article.get("summary", "").lower()
            sections = " ".join(article.get("sections", [])).lower()

            article_text = f"{title} {summary} {sections}"
            article_words = set(re.findall(r"\b[a-z]+\b", article_text))

            matches = 0
            for term in search_terms_set:
                term_words = term.split()
                for tw in term_words:
                    if tw in article_words:
                        matches += 1
                    if tw in title:
                        matches += 2

            title_match = any(term in title for term in search_terms_set)
            title_exact = search_query in title
            title_start = title.startswith(search_query)

            tfidf_keywords = self.find_recurring_keywords([article], top_n=10)
            tfidf_matches = sum(
                1 for kw, _ in tfidf_keywords if any(t in kw for t in search_terms_set)
            )

            score = (matches * 8) + (30 if title_match else 0) + (tfidf_matches * 3)
            score += 25 if title_exact else 0
            score += 15 if title_start else 0
            score = min(100, max(0, score))

            scores[article["title"]] = score

        return scores

    def score_articles_with_relevance(
        self, articles: list[dict], search_terms: list[str]
    ) -> list[dict]:
        """Add relevance scores to articles and sort by relevance."""
        scores = self.calculate_relevance_scores(articles, search_terms)

        for article in articles:
            article["relevance_score"] = scores.get(article["title"], 0)

        return sorted(articles, key=lambda x: x["relevance_score"], reverse=True)

    def filter_by_relevance(
        self, articles: list[dict], min_score: float = 60.0
    ) -> tuple[list[dict], list[dict]]:
        """Filter articles by minimum relevance score.

        Returns:
            Tuple of (filtered_articles, removed_articles)
        """
        filtered = []
        removed = []

        for article in articles:
            score = article.get("relevance_score", 0)
            if score >= min_score:
                filtered.append(article)
            else:
                removed.append(article)

        return filtered, removed
