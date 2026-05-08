"""Academic search client — ArXiv + Semantic Scholar async search via aiohttp."""

import asyncio
import logging
import re
from typing import List, Dict, Optional
from xml.etree import ElementTree

try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False


ARXIV_API_URL = "http://export.arxiv.org/api/query"
SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

ARXIV_NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


async def search_arxiv(query: str, max_results: int = 10) -> List[Dict]:
    """Search ArXiv via its public OAI-PMH API.

    Args:
        query: Search query
        max_results: Max papers to return (API limit: 50)

    Returns:
        List of dicts with keys: title, authors, summary, url, published, source
    """
    if not AIOHTTP_AVAILABLE:
        logging.warning("aiohttp not available for ArXiv search")
        return []

    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": min(max_results, 50),
        "sortBy": "relevance",
        "sortOrder": "descending",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                ARXIV_API_URL,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"User-Agent": "ACHEM/2.0"},
            ) as resp:
                if resp.status != 200:
                    logging.warning(f"ArXiv API error {resp.status}")
                    return []
                text = await resp.text()

        root = ElementTree.fromstring(text)
        entries = root.findall("atom:entry", ARXIV_NAMESPACES)

        results = []
        for entry in entries:
            title_el = entry.find("atom:title", ARXIV_NAMESPACES)
            summary_el = entry.find("atom:summary", ARXIV_NAMESPACES)
            published_el = entry.find("atom:published", ARXIV_NAMESPACES)
            link_el = entry.find("atom:id", ARXIV_NAMESPACES)

            authors = []
            for author_el in entry.findall("atom:author", ARXIV_NAMESPACES):
                name_el = author_el.find("atom:name", ARXIV_NAMESPACES)
                if name_el is not None and name_el.text:
                    authors.append(name_el.text.strip())

            title = (title_el.text or "").strip() if title_el is not None else ""
            title = re.sub(r"\s+", " ", title)

            summary = (summary_el.text or "").strip() if summary_el is not None else ""
            summary = re.sub(r"\s+", " ", summary)

            url = link_el.text.strip() if link_el is not None else ""
            published = published_el.text[:10] if published_el is not None else ""

            if title:
                results.append({
                    "title": title,
                    "authors": authors,
                    "body": summary[:2000],
                    "summary": summary[:500],
                    "url": url,
                    "published": published,
                    "source": "arxiv",
                })

        return results[:max_results]

    except asyncio.TimeoutError:
        logging.warning("ArXiv API timeout")
        return []
    except Exception as e:
        logging.warning(f"ArXiv search error: {e}")
        return []


async def search_semantic_scholar(query: str, max_results: int = 10) -> List[Dict]:
    """Search Semantic Scholar via its free public API.

    Args:
        query: Search query
        max_results: Max papers to return

    Returns:
        List of dicts with keys: title, authors, summary, url, published, source
    """
    if not AIOHTTP_AVAILABLE:
        logging.warning("aiohttp not available for Semantic Scholar search")
        return []

    await asyncio.sleep(1)

    params = {
        "query": query,
        "limit": min(max_results, 50),
        "fields": "title,authors,url,abstract,publicationDate,externalIds",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                SEMANTIC_SCHOLAR_API_URL,
                params=params,
                timeout=aiohttp.ClientTimeout(total=15),
                headers={"User-Agent": "ACHEM/2.0"},
            ) as resp:
                if resp.status != 200:
                    logging.warning(f"Semantic Scholar API error {resp.status}")
                    return []
                data = await resp.json()

        papers = data.get("data", []) if isinstance(data, dict) else []
        results = []

        for paper in papers:
            title = (paper.get("title") or "").strip()
            if not title:
                continue

            authors = [
                a.get("name", "") for a in (paper.get("authors") or []) if a.get("name")
            ]
            abstract = (paper.get("abstract") or "").strip()
            url = paper.get("url") or ""
            ext_ids = paper.get("externalIds") or {}
            if not url:
                url = ext_ids.get("ArXiv", "")
                if url:
                    url = f"https://arxiv.org/abs/{url}"

            published = (paper.get("publicationDate") or "")[:10]

            results.append({
                "title": title,
                "authors": authors,
                "body": abstract[:2000] if abstract else "",
                "summary": abstract[:500] if abstract else "",
                "url": url,
                "published": published,
                "source": "semantic_scholar",
            })

        return results[:max_results]

    except asyncio.TimeoutError:
        logging.warning("Semantic Scholar API timeout")
        return []
    except Exception as e:
        logging.warning(f"Semantic Scholar search error: {e}")
        return []


async def search_academic(
    query: str, max_results: int = 10, sources: Optional[List[str]] = None
) -> List[Dict]:
    """Search all enabled academic sources in parallel.

    Args:
        query: Search query
        max_results: Max results per source
        sources: List of sources ["arxiv", "semantic_scholar"]. Default: both.

    Returns:
        Combined list of academic results
    """
    if sources is None:
        sources = ["arxiv", "semantic_scholar"]

    tasks = []
    if "arxiv" in sources:
        tasks.append(search_arxiv(query, max_results=max_results))
    if "semantic_scholar" in sources:
        tasks.append(search_semantic_scholar(query, max_results=max_results))

    if not tasks:
        return []

    results = await asyncio.gather(*tasks, return_exceptions=True)

    combined = []
    seen_urls = set()

    for r in results:
        if isinstance(r, list):
            for item in r:
                url = item.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    combined.append(item)

    return combined
