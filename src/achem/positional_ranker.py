import re
import math
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass


@dataclass
class OrdinalPattern:
    """Represents the ordinal structure of a text."""

    words: List[str]
    positions: Dict[str, List[int]]
    length: int
    target_word: str
    target_position: int


class OrdinalDistanceCalculator:
    """
    ═══════════════════════════════════════════════════════════════════════
    ORDINAL DISTANCE ALGORITHM - The Magical Ranking System
    ═══════════════════════════════════════════════════════════════════════

    This algorithm calculates the "ordinal distance" between a user's query
    and search result titles. Unlike traditional similarity that checks word
    overlap, this measures STRUCTURAL alignment.

    Key Insight: When a writer titles an article with the same "mindset" as
    your question, the ordinal pattern of key terms will match.

    Example:
      Query: "what is usogui manga"
                    └───┬──┘
                    This pattern: [question, verb, ..., noun, noun]

      Title: "usogui manga review"
             └───┬──┘
             Same ordinal pattern!

    The closer the ordinal distance, the more semantically aligned.

    ═══════════════════════════════════════════════════════════════════════
    """

    STOP_WORDS = {
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

    QUESTION_WORDS = {"what", "who", "which", "where", "when", "why", "how", "?"}
    ACTION_WORDS = {
        "do",
        "make",
        "cook",
        "bake",
        "fry",
        "boil",
        "grill",
        "create",
        "build",
        "write",
        "use",
        "install",
        "set",
        "start",
        "run",
        "play",
        "watch",
        "see",
        "find",
        "get",
        "become",
    }

    def __init__(self):
        pass

    def _tokenize(self, text: str) -> List[str]:
        """Extract all words, lowercase, no punctuation."""
        return re.findall(r"\b[a-z0-9]+\b", text.lower())

    def _tokenize_meaningful(self, text: str) -> List[str]:
        """Extract meaningful words only (no stop words)."""
        words = self._tokenize(text)
        return [w for w in words if w not in self.STOP_WORDS and len(w) > 2]

    def extract_target_word(self, query: str) -> str:
        """Extract the main topic/target word from query."""
        words = self._tokenize(query.lower())

        if "is" in words or "are" in words:
            for i, w in enumerate(words):
                if w in ("is", "are") and i + 1 < len(words):
                    return words[i + 1]

        if "how" in words:
            try:
                how_idx = words.index("how")
                for w in words[how_idx + 1 :]:
                    if w in self.ACTION_WORDS:
                        action_idx = words.index(w)
                        if action_idx + 1 < len(words):
                            return words[action_idx + 1]
            except ValueError:
                pass

        meaningful = self._tokenize_meaningful(query)
        return meaningful[-1] if meaningful else (words[-1] if words else "")

    def extract_key_terms(self, query: str) -> List[str]:
        """Extract all key terms from query (not just target)."""
        return self._tokenize_meaningful(query)

    def calculate_ordinal_pattern(self, text: str, target_word: str) -> OrdinalPattern:
        """Calculate the ordinal pattern of a text."""
        words = self._tokenize(text.lower())
        positions = {}

        for i, word in enumerate(words):
            if word not in positions:
                positions[word] = []
            positions[word].append(i)

        target_lower = target_word.lower()
        target_pos = 0
        for word, poss in positions.items():
            if target_lower in word or word in target_lower:
                target_pos = poss[0]
                break
        else:
            target_pos = len(words)

        return OrdinalPattern(
            words=words,
            positions=positions,
            length=len(words),
            target_word=target_word,
            target_position=target_pos,
        )

    def calculate_ordinal_distance(
        self, query_pattern: OrdinalPattern, title_pattern: OrdinalPattern
    ) -> float:
        """
        Calculate the ordinal distance between query and title.

        Lower distance = more aligned = higher rank

        Distance Components:
        1. Target Position Distance (primary)
        2. Relative Position Distance (secondary)
        3. Length Penalty (slight)
        4. SEO Spam Penalty
        """
        target_dist = abs(query_pattern.target_position - title_pattern.target_position)

        key_terms = [t for t in query_pattern.words if t not in self.QUESTION_WORDS]
        key_terms = [t for t in key_terms if t not in ("is", "are", "the", "a", "an")]

        relative_dists = []
        for term in key_terms[:3]:
            if term in title_pattern.positions:
                title_pos = title_pattern.positions[term][0]
                query_pos = query_pattern.positions.get(term, [0])[0]
                relative_dists.append(abs(query_pos - title_pos))

        avg_relative_dist = (
            sum(relative_dists) / len(relative_dists) if relative_dists else 0
        )

        target_distance_score = target_dist * 15

        relative_distance_score = avg_relative_dist * 10

        length_diff = abs(query_pattern.length - title_pattern.length)
        length_penalty = length_diff * 2

        seo_penalty = 50 if title_pattern.target_position == 0 else 0

        total_distance = (
            target_distance_score
            + relative_distance_score
            + length_penalty
            + seo_penalty
        )

        return max(0, total_distance)

    def calculate_relevance_score(
        self, ordinal_distance: float, max_distance: float = 100
    ) -> float:
        """Convert ordinal distance to a 0-100 relevance score."""
        normalized = 1 - min(ordinal_distance / max_distance, 1)
        return normalized * 100

    def rank_by_ordinal_distance(self, results: List[dict], query: str) -> List[dict]:
        """
        Rank results by ordinal distance - THE MAGICAL SORTING.

        This is the main entry point. It:
        1. Extracts query pattern
        2. Calculates ordinal distance for each title
        3. Sorts by smallest distance (most aligned first)
        4. Adds diagnostic metadata
        """
        target_word = self.extract_target_word(query)
        key_terms = self.extract_key_terms(query)

        query_pattern = self.calculate_ordinal_pattern(query, target_word)

        distances = []
        for result in results:
            title = result.get("title", "")
            title_pattern = self.calculate_ordinal_pattern(title, target_word)

            distance = self.calculate_ordinal_distance(query_pattern, title_pattern)

            result["ordinal_distance"] = distance
            result["target_word"] = target_word
            result["query_target_pos"] = query_pattern.target_position
            result["title_target_pos"] = title_pattern.target_position
            result["relevance_score"] = self.calculate_relevance_score(distance)

            distances.append((result, distance))

        distances.sort(key=lambda x: x[1])
        return [r for r, _ in distances]


class PositionalRanker:
    """
    Legacy wrapper for backward compatibility.
    Now uses the more powerful OrdinalDistanceCalculator internally.
    """

    def __init__(self, tolerance: int = 2):
        self.tolerance = tolerance
        self.ordinal_calc = OrdinalDistanceCalculator()

    def extract_target_word(self, query: str) -> Optional[str]:
        return self.ordinal_calc.extract_target_word(query)

    def get_word_position(self, text: str, target: str) -> Optional[int]:
        words = self.ordinal_calc._tokenize(text.lower())
        target_lower = target.lower()

        for i, word in enumerate(words):
            if word == target_lower or target_lower in word:
                return i + 1
        return None

    def calculate_position_score(
        self, title: str, query_position: int, target_word: str
    ) -> Tuple[float, int]:
        title_pos = self.get_word_position(title, target_word)
        if title_pos is None:
            return 0.0, 0

        distance = abs(title_pos - query_position)

        if distance == 0:
            base_score = 100.0
        elif distance == 1:
            base_score = 85.0
        elif distance == 2:
            base_score = 70.0
        else:
            base_score = max(50.0 - (distance * 5), 20.0)

        if title_pos == 1:
            base_score -= 50

        if title_pos >= 4:
            base_score += 15

        if query_position >= 4 and title_pos >= 4:
            base_score += 10

        return max(0.0, base_score), title_pos

    def rank_results(self, results: List[dict], query: str) -> List[dict]:
        return self.ordinal_calc.rank_by_ordinal_distance(results, query)

    def extract_target_word(self, query: str) -> Optional[str]:
        """Extract the main target word from a query.

        Detects the "noun" or "topic" being asked about.

        Logic:
        - "what is X" → X
        - "who is X" → X
        - "how to X Y" → Y (the object/topic, not the action)
        - "best X Y Z" → Z (the main topic)
        - Default → last significant word
        """
        words = re.findall(r"\b[a-z0-9]+\b", query.lower())

        question_words = {"what", "who", "which", "where", "when", "why", "how", "?"}
        stop = {"a", "an", "the", "to", "for", "of", "in", "on", "at", "by"}
        filtered = [
            w for w in words if w not in question_words and w not in stop and len(w) > 2
        ]

        if not filtered:
            return None

        if "is" in words or "are" in words:
            for i, w in enumerate(words):
                if w in ("is", "are") and i + 1 < len(words):
                    return words[i + 1]

        if "how" in words:
            how_idx = words.index("how")
            after_how = words[how_idx + 1 :] if how_idx + 1 < len(words) else []
            actionable = {
                "do",
                "make",
                "cook",
                "bake",
                "fry",
                "boil",
                "grill",
                "create",
                "build",
                "write",
                "use",
                "install",
                "set",
                "start",
                "run",
                "play",
                "watch",
                "see",
                "find",
                "get",
                "become",
            }
            for w in after_how:
                if w in actionable and words.index(w) + 1 < len(words):
                    return words[words.index(w) + 1]

        return filtered[-1]

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words, excluding punctuation."""
        words = re.findall(r"\b[a-z0-9]+\b", text.lower())
        return [w for w in words if w not in self.STOP_WORDS or w in ("is", "are")]

    def _tokenize_all(self, text: str) -> List[str]:
        """Tokenize ALL words including stop words (for position tracking)."""
        return re.findall(r"\b[a-z0-9]+\b", text.lower())

    def get_word_position(self, text: str, target: str) -> Optional[int]:
        """Get 1-based position of target word in text."""
        words = self._tokenize_all(text.lower())
        target_lower = target.lower()

        for i, word in enumerate(words):
            if word == target_lower:
                return i + 1
            if target_lower in word:
                return i + 1

        return None

    def calculate_position_score(
        self, title: str, query_position: int, target_word: str
    ) -> Tuple[float, int]:
        """
        Calculate positional score for a title.

        Returns:
            Tuple of (score, detected_position)

        Scoring logic:
        - Exact match (same position): 100 points
        - Within tolerance (±2): score decreases linearly
        - Position 1 (SEO spam): -50 penalty
        - Position 2-3 (short phrase): moderate bonus
        - Position 4+: higher bonus (contextual discussion)
        """
        if not target_word:
            return 0.0, 0

        title_position = self.get_word_position(title, target_word)
        if title_position is None:
            return 0.0, 0

        distance = abs(title_position - query_position)

        if distance == 0:
            base_score = 100.0
        elif distance == 1:
            base_score = 85.0
        elif distance == 2:
            base_score = 70.0
        else:
            base_score = max(50.0 - (distance * 5), 20.0)

        if title_position == 1:
            base_score -= 50

        if title_position >= 4:
            base_score += 15

        if query_position >= 4 and title_position >= 4:
            base_score += 10

        return max(0.0, base_score), title_position

    def rank_results(self, results: List[dict], query: str) -> List[dict]:
        """
        Rank search results using structural positional analysis.

        Adds 'positional_score' and 'target_position' to each result.
        """
        target_word = self.extract_target_word(query)
        if not target_word:
            return results

        query_position = self.get_word_position(query, target_word)
        if query_position is None:
            query_position = self._get_fallback_position(query, target_word)

        for result in results:
            title = result.get("title", "")
            pos_score, pos = self.calculate_position_score(
                title, query_position, target_word
            )

            result["target_word"] = target_word
            result["query_position"] = query_position
            result["title_position"] = pos
            result["positional_score"] = pos_score

            base_score = result.get("relevance_score", 50)
            result["relevance_score"] = (base_score * 0.4) + (pos_score * 0.6)

        return sorted(results, key=lambda x: x["relevance_score"], reverse=True)

    def _get_fallback_position(self, query: str, target: str) -> int:
        """Fallback position detection using keyword extraction."""
        words = self._tokenize_all(query.lower())
        target_lower = target.lower()

        for i, word in enumerate(words):
            if target_lower in word:
                return i + 1

        return len(words)

    def filter_by_position(
        self, results: List[dict], min_position: int = 1, max_position: int = 99
    ) -> List[dict]:
        """Filter results by target word position in title."""
        return [
            r
            for r in results
            if min_position <= r.get("title_position", 0) <= max_position
        ]

    def get_position_stats(self, results: List[dict]) -> dict:
        """Get statistics about position distribution."""
        positions = [
            r.get("title_position", 0)
            for r in results
            if r.get("title_position", 0) > 0
        ]

        if not positions:
            return {"count": 0, "avg": 0, "seo_spam": 0, "contextual": 0}

        return {
            "count": len(positions),
            "avg": round(sum(positions) / len(positions), 1),
            "seo_spam": sum(1 for p in positions if p == 1),
            "early": sum(1 for p in positions if 2 <= p <= 3),
            "contextual": sum(1 for p in positions if p >= 4),
            "positions": sorted(set(positions)),
        }


def rank_by_structure(results: List[dict], query: str) -> List[dict]:
    """Convenience function to rank results using positional analysis."""
    ranker = PositionalRanker()
    return ranker.rank_results(results, query)
