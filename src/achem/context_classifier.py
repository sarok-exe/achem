import re
from typing import List, Dict, Set


TECHNICAL_TERMS = {
    "graphql",
    "react",
    "angular",
    "vue",
    "javascript",
    "typescript",
    "python",
    "java",
    "golang",
    "rust",
    "c++",
    "csharp",
    "ruby",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "linux",
    "unix",
    "api",
    "rest",
    "http",
    "database",
    "sql",
    "nosql",
    "mongodb",
    "postgresql",
    "mysql",
    "redis",
    "nginx",
    "apache",
    "git",
    "github",
    "stackoverflow",
    "stack overflow",
    "syntax",
    "compile",
    "runtime",
    "debug",
    "error",
    "exception",
    "function",
    "class",
    "method",
    "variable",
    "array",
    "object",
    "framework",
    "library",
    "package",
    "module",
    "async",
    "promise",
    "callback",
    "thread",
    "server",
    "client",
    "frontend",
    "backend",
    "devops",
    "algorithm",
    "node",
    "hack",
    "exploit",
    "vulnerability",
    "injection",
    "bug",
    "patch",
}

MUSIC_NOISE = {
    "song",
    "lyrics",
    "album",
    "released",
    "singer",
    "recorded",
    "track",
    "chart",
    "billboard",
    "spotify",
    "itunes",
    "streaming",
    "melody",
    "tune",
    "band",
    "concert",
    "tour",
    "studio",
    "single",
    "debut",
    "feat",
    "featuring",
    "verse",
    "chorus",
    "bridge",
    "elvis",
    "presley",
    "beatles",
    "taylor swift",
    "beyonce",
    "drake",
    "weeknd",
    "kanye",
    "rihanna",
    "bruno mars",
    "adele",
}

MOVIE_NOISE = {
    "film",
    "movie",
    "cinema",
    "director",
    "actor",
    "actress",
    "cast",
    "trailer",
    "premiere",
    "box office",
    "screenplay",
    "hollywood",
    "netflix",
    "hulu",
    "disney",
    "marvel",
    "dc comics",
}

ADVICE_INDICATORS = {
    "how to",
    "tips",
    "guide",
    "ways",
    "advice",
    "steps",
    "method",
    "strategy",
    "techniques",
    "best practices",
}

SURVIVAL_CONTEXT = {
    "survive",
    "survival",
    "escape",
    "attack",
    "bite",
    "bite",
    "snake",
    "python",
    "reptile",
    "wildlife",
    "animal",
    "dangerous",
    "prey",
    "neck",
    "constrict",
    "coil",
    "tail",
    "head",
    "fireman",
    "rescue",
}

PROGRAMMING_CONTEXT = {
    "python",
    "script",
    "code",
    "coding",
    "programming",
    "tutorial",
    "install",
    "pip",
    "package",
    "module",
    "function",
    "class",
    "variable",
    "syntax",
    "run",
    "execute",
    "file",
    "import",
    "github",
    "stackoverflow",
    "beginner",
    "advanced",
    "project",
}

TECHNICAL_ATTACK = {
    "ddos",
    "cyber",
    "security",
    "malware",
    "virus",
    "hack",
    "firewall",
    "network",
    "server",
    "dos",
    "botnet",
    "exploit",
    "vulnerability",
    "injection",
    "breach",
    "threat",
    "protect",
}

MOVIE_NOISE = {
    "film",
    "movie",
    "cinema",
    "director",
    "actor",
    "actress",
    "cast",
    "trailer",
    "premiere",
    "box office",
    "screenplay",
    "hollywood",
    "netflix",
    "hulu",
    "disney",
    "marvel",
    "dc comics",
}

ADVICE_INDICATORS = {
    "how to",
    "tips",
    "guide",
    "ways",
    "advice",
    "steps",
    "method",
    "strategy",
    "techniques",
    "best practices",
}


class ContextClassifier:
    """Classify and filter sources based on query context."""

    def __init__(self, query: str):
        self.query = query.lower()
        self.query_words = set(re.findall(r"\w+", self.query))
        self.is_advice_query = self._is_advice_query()
        self.query_context = self._detect_context()

    def _is_advice_query(self) -> bool:
        """Check if query is asking for advice/how-to."""
        for indicator in ADVICE_INDICATORS:
            if indicator in self.query:
                return True
        return False

    def _detect_context(self) -> str:
        """Detect the general context/topic of the query."""
        query_str = self.query.lower()

        for topic in MUSIC_NOISE:
            if topic in query_str:
                return "music"
        for topic in MOVIE_NOISE:
            if topic in query_str:
                return "movie"

        survival_count = sum(1 for t in SURVIVAL_CONTEXT if t in query_str)
        programming_count = sum(1 for t in PROGRAMMING_CONTEXT if t in query_str)

        if "survive" in query_str or "survival" in query_str:
            if programming_count > survival_count:
                return "technical"
            return "survival"

        if survival_count >= 2 and programming_count <= 1:
            return "survival"
        if programming_count >= 2 and survival_count <= 1:
            return "technical"

        technical_indicators = TECHNICAL_TERMS
        tech_count = sum(1 for t in technical_indicators if t in query_str)
        if tech_count >= 2:
            return "technical"

        return "general"

    def _count_music_terms(self, text: str) -> int:
        """Count how many music-related terms are in text."""
        text_lower = text.lower()
        return sum(1 for term in MUSIC_NOISE if term in text_lower)

    def _count_movie_terms(self, text: str) -> int:
        """Count how many movie-related terms are in text."""
        text_lower = text.lower()
        return sum(1 for term in MOVIE_NOISE if term in text_lower)

    def _is_music_content(self, text: str) -> bool:
        """Check if text is primarily about music."""
        return self._count_music_terms(text) >= 2

    def _is_movie_content(self, text: str) -> bool:
        """Check if text is primarily about movies."""
        return self._count_movie_terms(text) >= 2

    def _count_survival_terms(self, text: str) -> int:
        """Count survival-related terms."""
        text_lower = text.lower()
        return sum(1 for t in SURVIVAL_CONTEXT if t in text_lower)

    def _count_programming_terms(self, text: str) -> int:
        """Count programming-related terms."""
        text_lower = text.lower()
        return sum(1 for t in PROGRAMMING_CONTEXT if t in text_lower)

    def _is_survival_content(self, text: str) -> bool:
        """Check if text is about survival/wildlife."""
        return self._count_survival_terms(text) >= 3

    def _is_programming_content(self, text: str) -> bool:
        """Check if text is about programming."""
        return self._count_programming_terms(text) >= 3

    def has_exclude_pattern(self, url: str, title: str) -> bool:
        """Check if URL or title matches exclude patterns."""
        exclude_patterns = [
            "stackoverflow.com/questions",
            "stackoverflow.com/answer",
            "github.com/",
            ".git",
            "/issues",
            "/pull/",
        ]
        combined = (url + " " + title).lower()
        return any(p in combined for p in exclude_patterns)

    def relevance_score(self, title: str, body: str, url: str) -> float:
        """Calculate relevance score (0-100) based on query context."""
        title_lower = title.lower()
        body_lower = body.lower()
        url_lower = url.lower()
        combined = title_lower + " " + body_lower + " " + url_lower

        score = 50

        for word in self.query_words:
            if len(word) < 3:
                continue
            if word in title_lower:
                score += 15
            elif word in body_lower:
                score += 5

        if self.query_context == "survival":
            if self._count_programming_terms(title) >= 3:
                score -= 60
            if self._count_programming_terms(body) >= 5:
                score -= 40

        if self.is_advice_query:
            if self._count_music_terms(title) >= 3:
                score -= 50
            if self._count_movie_terms(title) >= 3:
                score -= 50

        if self.has_exclude_pattern(url, title):
            score -= 30

        return max(20, min(100, score))

    def is_relevant(self, title: str, body: str, url: str, threshold: int = 30) -> bool:
        """Check if article is relevant to the query."""
        score = self.relevance_score(title, body, url)
        return score >= threshold

    def filter_articles(self, articles: List[Dict], threshold: int = 25) -> tuple:
        """Filter articles by relevance. Returns (kept, removed)."""
        kept = []
        removed = []

        for article in articles:
            title = article.get("title", "")
            body = article.get("body", article.get("summary", ""))
            url = article.get("url", "")

            score = self.relevance_score(title, body, url)

            if score >= threshold:
                article["relevance_score"] = max(
                    article.get("relevance_score", 50), score
                )
                kept.append(article)
            else:
                removed.append(article)

        return kept, removed


def classify_and_filter(articles: List[Dict], query: str, threshold: int = 25) -> tuple:
    """Main function to classify and filter articles."""
    classifier = ContextClassifier(query)
    return classifier.filter_articles(articles, threshold)
