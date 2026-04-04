import re
from typing import Optional


class SpellChecker:
    """Simple spell checker with common corrections and optional transformer-based correction."""

    COMMON_CORRECTIONS = {
        "artifical": "artificial",
        "inteligence": "intelligence",
        "inteligent": "intelligent",
        "machin lerning": "machine learning",
        "machne": "machine",
        "cumputer": "computer",
        "sciene": "science",
        "achem": "achem",
        "developmnt": "development",
        "devoloping": "developing",
        "swiming": "swimming",
        "programing": "programming",
        "algoritm": "algorithm",
        "neural": "neural",
        "depp": "deep",
        "leraning": "learning",
        "netwrk": "network",
        "data": "data",
        "analtics": "analytics",
        "robottics": "robotics",
        "autonomus": "autonomous",
        "predictve": "predictive",
        "automtion": "automation",
        "quantm": "quantum",
        "blockchan": "blockchain",
        "cybersecurity": "cybersecurity",
        "clouds": "cloud",
        "bigdata": "big data",
        "internet of things": "internet of things",
        "machinelearning": "machine learning",
        "artificialintelligence": "artificial intelligence",
        "deeplearning": "deep learning",
        "naturallanguage": "natural language",
        "computervision": "computer vision",
        "reinforcementlearning": "reinforcement learning",
        "supervisedlearning": "supervised learning",
        "unsupervisedlearning": "unsupervised learning",
        "howto": "how to",
        "howto make": "how to make",
        "howto do": "how to do",
        "howto create": "how to create",
        "whats": "what's",
        "whos": "who's",
        "wheres": "where's",
        "dont": "don't",
        "cant": "can't",
        "wont": "won't",
        "didnt": "didn't",
        "isnt": "isn't",
        "arent": "aren't",
        "wasnt": "wasn't",
        "werent": "weren't",
        "hasnt": "hasn't",
        "hadnt": "hadn't",
        "hasnt": "hasn't",
        "havent": "haven't",
        "shouldnt": "shouldn't",
        "wouldnt": "wouldn't",
        "couldnt": "couldn't",
        "mustnt": "mustn't",
        "youre": "you're",
        "theyre": "they're",
        "were": "we're",
        "thats": "that's",
        "whats": "what's",
        "whos": "who's",
        "theres": "there's",
        "heres": "here's",
        "lets": "let's",
        "im": "I'm",
        "ive": "I've",
        "id": "I'd",
        "youd": "you'd",
        "hed": "he'd",
        "shed": "she'd",
        "theyd": "they'd",
        "wed": "we'd",
        "itd": "it'd",
        "aint": "isn't",
        "gonna": "going to",
        "wanna": "want to",
        "gotta": "got to",
        "kinda": "kind of",
        "sorta": "sort of",
        "outta": "out of",
        "dunno": "don't know",
    }

    def __init__(self, use_transformer: bool = False):
        self.use_transformer = use_transformer
        self._transformer_pipeline = None

    def correct(self, query: str) -> tuple[str, list[str]]:
        """Correct spelling in query and return (corrected, suggestions)."""
        suggestions = []
        corrected = query

        corrected_lower = corrected.lower()
        if corrected_lower in self.COMMON_CORRECTIONS:
            correct = self.COMMON_CORRECTIONS[corrected_lower]
            if correct != corrected_lower:
                suggestions.append(f"'{query}' → '{correct}'")
                corrected = correct

        words = re.findall(r"\b\w+\b", corrected)
        for word in words:
            word_lower = word.lower()
            if word_lower in self.COMMON_CORRECTIONS:
                correct = self.COMMON_CORRECTIONS[word_lower]
                if correct != word_lower:
                    suggestions.append(f"'{word}' → '{correct}'")
                    corrected = corrected.replace(word, correct, 1)

        return corrected, suggestions

    def suggest_corrections(self, query: str) -> list[str]:
        """Get spelling correction suggestions for a query."""
        _, suggestions = self.correct(query)
        return suggestions

    def has_corrections(self, query: str) -> bool:
        """Check if query has any spelling corrections."""
        corrected, _ = self.correct(query)
        return corrected.lower() != query.lower()
