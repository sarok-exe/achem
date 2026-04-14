"""
Topic Classifier - Automatically classifies queries and prioritizes relevant sources.
"""

from typing import Dict, List, Tuple, Optional


TOPIC_CATEGORIES = {
    "anime_manga": {
        "keywords": [
            "anime",
            "manga",
            "chapter",
            "episode",
            "naruto",
            "one piece",
            "dragon ball",
            "attack on titan",
            "jujutsu kaisen",
            "demon slayer",
            "my hero academia",
            "aot",
            "opm",
            "toei",
            "studio ghibli",
            "cosplay",
            "otaku",
            "japan",
            "anime",
        ],
        "priority_sites": [
            "myanimelist.net",
            "animedaily.com",
            "crunchyroll.com",
            "animenewsnetwork.com",
            "kitsu.io",
            "anilist.co",
        ],
        "weight": 10,
    },
    "football_soccer": {
        "keywords": [
            "football",
            "soccer",
            "match",
            "champions league",
            "premier league",
            "la liga",
            "bundesliga",
            "serie a",
            "ligue 1",
            "messi",
            "ronaldo",
            "mbappe",
            "transfer",
            "goal",
            "score",
            "bayern",
            "real madrid",
            "manchester",
            "liverpool",
            "arsenal",
            "chelsea",
            "barcelona",
        ],
        "priority_sites": [
            "theanalyst.com",
            "espn.com/soccer",
            "bbc.com/sport",
            "skysports.com",
            "goal.com",
            "transfermarkt.com",
            "fotmob.com",
            "whoscored.com",
            "uefa.com",
        ],
        "weight": 10,
    },
    "general_sports": {
        "keywords": [
            "sport",
            "basketball",
            "nba",
            "tennis",
            "golf",
            "nfl",
            "baseball",
            "mlb",
            "hockey",
            "nhl",
            "olympics",
            "ufc",
            "boxing",
            "mma",
        ],
        "priority_sites": [
            "espn.com",
            "bbc.com/sport",
            "skysports.com",
            "sports.yahoo.com",
            "cbssports.com",
            "si.com",
        ],
        "weight": 8,
    },
    "mma_fighting": {
        "keywords": [
            "mma",
            "ufc",
            "boxing",
            "wwe",
            "wrestling",
            "fight",
            "fighter",
            "tapology",
            "sherdog",
            "mmafighting",
            "bellator",
        ],
        "priority_sites": [
            "tapology.com",
            "sherdog.com",
            "mmajunkie.usatoday.com",
            "mmafighting.com",
            "espn.com/mma",
        ],
        "weight": 10,
    },
    "gaming": {
        "keywords": [
            "game",
            "gaming",
            "steam",
            "playstation",
            "xbox",
            "nintendo",
            "pc gaming",
            "esports",
            "twitch",
            "console",
            "rpg",
            "fps",
            "moba",
            "league of legends",
            "valorant",
            "fortnite",
            "minecraft",
        ],
        "priority_sites": [
            "ign.com",
            "gamespot.com",
            "metacritic.com",
            "howlongtobeat.com",
            "steamcommunity.com",
            "pcgamer.com",
        ],
        "weight": 9,
    },
    "movies_series": {
        "keywords": [
            "movie",
            "film",
            "series",
            "tv show",
            "netflix",
            "hbo",
            "disney+",
            "actor",
            "actress",
            "director",
            "hollywood",
            "cinema",
            "imdb",
            " Rotten Tomatoes",
        ],
        "priority_sites": [
            "imdb.com",
            "rottentomatoes.com",
            "metacritic.com",
            "letterboxd.com",
            "tvguide.com",
        ],
        "weight": 9,
    },
    "health_medicine": {
        "keywords": [
            "health",
            "medical",
            "medicine",
            "disease",
            "treatment",
            "symptom",
            "doctor",
            "hospital",
            "diagnosis",
            "cancer",
            "diabetes",
            "heart",
            "cancer",
            "vaccine",
            "mental health",
            "therapy",
            "pharmaceutical",
            "drug",
            "surgery",
            "hospital",
            "clinic",
        ],
        "priority_sites": [
            "mayoclinic.org",
            "webmd.com",
            "who.int",
            "nih.gov",
            "medlineplus.gov",
            "healthline.com",
            "medicalnewstoday.com",
        ],
        "weight": 10,
    },
    "science_physics": {
        "keywords": [
            "science",
            "physics",
            "biology",
            "chemistry",
            "research",
            "experiment",
            "quantum",
            "space",
            "nasa",
            "scientific",
            "laboratory",
            "study",
            "discovery",
            "gene",
            "dna",
            "evolution",
            "ecology",
        ],
        "priority_sites": [
            "scientificamerican.com",
            "nature.com",
            "sciencemag.org",
            "nationalgeographic.com",
            "livescience.com",
            "space.com",
        ],
        "weight": 10,
    },
    "history": {
        "keywords": [
            "history",
            "war",
            "ancient",
            "civilization",
            "world war",
            "medieval",
            "empire",
            "historical",
            "archaeology",
            "museum",
            "dynasty",
            "colonial",
        ],
        "priority_sites": [
            "britannica.com",
            "history.com",
            "livescience.com",
            "nationalgeographic.com",
            "worldhistory.org",
        ],
        "weight": 9,
    },
    "technology": {
        "keywords": [
            "technology",
            "programming",
            "coding",
            "software",
            "hardware",
            "ai",
            "artificial intelligence",
            "machine learning",
            "python",
            "javascript",
            "developer",
            "tech",
            "computer",
            "cyber",
            "security",
            "hack",
            "data",
            "cloud",
        ],
        "priority_sites": [
            "stackoverflow.com",
            "github.com",
            "techcrunch.com",
            "wired.com",
            "arstechnica.com",
            "theverge.com",
        ],
        "weight": 9,
    },
    "music": {
        "keywords": [
            "music",
            "song",
            "album",
            "artist",
            "band",
            "concert",
            "spotify",
            "lyrics",
            "rapper",
            "singer",
            "pop",
            "rock",
            "hip hop",
            "jazz",
            "playlist",
        ],
        "priority_sites": [
            "genius.com",
            "spotify.com",
            "billboard.com",
            " rollingstone.com",
            " Pitchfork.com",
        ],
        "weight": 8,
    },
    "finance_crypto": {
        "keywords": [
            "finance",
            "stock",
            "crypto",
            "bitcoin",
            "trading",
            "investment",
            "market",
            "economy",
            "forex",
            "trading",
            "shares",
            "bonds",
            "banking",
            "fintech",
        ],
        "priority_sites": [
            "bloomberg.com",
            "reuters.com/finance",
            "cnbc.com",
            "coindesk.com",
            "investopedia.com",
        ],
        "weight": 8,
    },
    "food_recipes": {
        "keywords": [
            "recipe",
            "food",
            "cooking",
            "chef",
            "restaurant",
            "meal",
            "dish",
            "baking",
            "ingredient",
            "cuisine",
            "kitchen",
        ],
        "priority_sites": [
            "allrecipes.com",
            "foodnetwork.com",
            "epicurious.com",
            "seriouseats.com",
            "bonappetit.com",
        ],
        "weight": 8,
    },
}


def classify_query(query: str) -> Tuple[str, List[str], Dict]:
    """
    Classify a query and return the topic category, priority sites, and metadata.

    Returns:
        Tuple of (category_name, priority_sites_list, category_metadata)
    """
    query_lower = query.lower()
    query_words = set(query_lower.split())

    best_category = "general"
    best_score = 0
    best_meta = {}

    for category, meta in TOPIC_CATEGORIES.items():
        score = 0
        keywords = meta.get("keywords", [])

        for kw in keywords:
            if kw.lower() in query_lower:
                score += 2
            if kw.lower() in query_words:
                score += 1

        if score > best_score:
            best_score = score
            best_category = category
            best_meta = meta

    priority_sites = best_meta.get("priority_sites", [])

    return best_category, priority_sites, best_meta


def get_search_boosters(query: str) -> Dict[str, int]:
    """
    Get domain boosters for search results based on query classification.
    Returns dict of domain -> boost_score
    """
    _, priority_sites, meta = classify_query(query)

    boosters = {}
    base_weight = meta.get("weight", 5)

    for site in priority_sites:
        boosters[site] = base_weight

    return boosters


def sort_by_topic_relevance(results: List[dict], query: str) -> List[dict]:
    """
    Sort search results by topic relevance.
    Prioritizes results from specialized sites for the query type.
    """
    boosters = get_search_boosters(query)

    for result in results:
        url = result.get("url", "").lower()
        score = result.get("priority_score", 0)

        for domain, boost in boosters.items():
            if domain in url:
                score += boost
                break

        priority_sites = []
        _, priority_sites, _ = classify_query(query)

        for i, site in enumerate(priority_sites):
            if site in url:
                score += (len(priority_sites) - i) * 2
                break

        result["topic_relevance_score"] = score

    sorted_results = sorted(
        results,
        key=lambda x: (
            x.get("topic_relevance_score", 0),
            x.get("relevance_score", 0),
            x.get("priority_score", 0),
        ),
        reverse=True,
    )

    return sorted_results


def get_topic_description(category: str) -> str:
    """Get a human-readable description of the topic category."""
    descriptions = {
        "anime_manga": "Anime & Manga",
        "football_soccer": "Football & Soccer",
        "general_sports": "Sports",
        "mma_fighting": "MMA & Fighting",
        "gaming": "Gaming",
        "movies_series": "Movies & TV Series",
        "health_medicine": "Health & Medicine",
        "science_physics": "Science & Physics",
        "history": "History",
        "technology": "Technology & Programming",
        "music": "Music",
        "finance_crypto": "Finance & Crypto",
        "food_recipes": "Food & Recipes",
        "general": "General Topic",
    }
    return descriptions.get(category, "General Topic")


def build_topic_search_query(query: str) -> str:
    """
    Build optimized search query with topic-specific terms.
    """
    category, priority_sites, _ = classify_query(query)

    if category == "general":
        return query

    category_terms = {
        "anime_manga": ["anime", "manga"],
        "football_soccer": ["football prediction", "soccer prediction"],
        "health_medicine": ["medical", "health information"],
        "technology": ["technology news"],
        "science_physics": ["science", "research"],
    }

    additional_terms = category_terms.get(category, [])

    if additional_terms:
        return f"{query} {' '.join(additional_terms)}"

    return query
