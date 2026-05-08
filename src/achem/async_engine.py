"""ACHEM Async Research Engine — async search + scrape orchestrator with Rich progress."""

import asyncio
import time
import logging
from typing import List, Dict, Optional, Callable

from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
)
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box as rich_box

from .duckduckgo_client import DuckDuckGoClient
from .web_scraper import WebScraper
from .planner import generate_search_queries
from .reasoning_engine import synthesize_findings
from .output_formatter import c


class ProgressTracker:
    """Manages Rich progress display for the async research pipeline."""

    def __init__(self, console: Console = None):
        self.console = console or Console()
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console,
            transient=False,
        )
        self.plan_task = None
        self.search_task = None
        self.scrape_task = None
        self.process_task = None
        self.reasoning_task = None

    def start_planning(self):
        self.plan_task = self.progress.add_task(
            "[#CBA6F7]Planning research strategy...[/]", total=1
        )

    def complete_planning(self):
        if self.plan_task is not None:
            self.progress.update(self.plan_task, completed=1)

    def start_search(self, total: int = 100, label: str = "Searching DuckDuckGo"):
        self.search_task = self.progress.add_task(
            f"[#89B4FA]{label}[/]", total=total
        )

    def update_search(self, completed: int):
        if self.search_task is not None:
            self.progress.update(self.search_task, completed=completed)

    def complete_search(self):
        if self.search_task is not None:
            t = self.progress.tasks[self.search_task]
            self.progress.update(self.search_task, completed=t.total or 100)

    def start_scrape(self, total: int):
        self.scrape_task = self.progress.add_task(
            "[#A6E3A1]Scraping pages...[/]", total=total
        )

    def update_scrape(self, completed: int, total: int):
        if self.scrape_task is not None:
            self.progress.update(
                self.scrape_task,
                completed=completed,
                total=total,
                description=f"[#A6E3A1]Scraping {completed}/{total} pages...[/]",
            )

    def complete_scrape(self):
        if self.scrape_task is not None:
            t = self.progress.tasks[self.scrape_task]
            self.progress.update(self.scrape_task, completed=t.total or 1)

    def start_processing(self):
        self.process_task = self.progress.add_task(
            "[#F9E2AF]Processing content...[/]", total=1
        )

    def complete_processing(self):
        if self.process_task is not None:
            self.progress.update(self.process_task, completed=1)

    def start_reasoning(self):
        self.reasoning_task = self.progress.add_task(
            "[#F5C2E7]Synthesizing findings...[/]", total=1
        )

    def complete_reasoning(self):
        if self.reasoning_task is not None:
            self.progress.update(self.reasoning_task, completed=1)

    def __enter__(self):
        self.progress.__enter__()
        return self

    def __exit__(self, *args):
        self.progress.__exit__(*args)


async def async_search_pipeline(
    query: str,
    ddg_limit: int = 100,
    scrape_concurrent: int = 20,
    progress_tracker: ProgressTracker = None,
) -> Dict:
    """Run the full async search + scrape pipeline.

    Args:
        query: The search query
        ddg_limit: Max DuckDuckGo results
        scrape_concurrent: Max concurrent scrape connections
        progress_tracker: Optional ProgressTracker for Rich UI

    Returns:
        Dict with keys: 'results' (DDG results), 'scraped' (scraped content),
                        'stats' (timing stats)
    """
    tracker = progress_tracker or ProgressTracker()
    own_tracker = progress_tracker is None

    ddg = DuckDuckGoClient(max_results=ddg_limit)
    scraper = WebScraper()

    stats = {"search_time": 0, "scrape_time": 0, "total_sources": 0, "scraped_count": 0}

    try:
        if own_tracker:
            tracker = tracker.__enter__()

        # ---- Phase 1: Async Search ----
        tracker.start_search(total=ddg_limit)
        search_start = time.time()

        results = await ddg.search_async(query, max_results=ddg_limit)

        search_elapsed = time.time() - search_start
        stats["search_time"] = round(search_elapsed, 2)
        stats["total_sources"] = len(results)
        tracker.complete_search()

        if not results:
            tracker.console.print("[yellow]No search results found.[/yellow]")
            if own_tracker:
                tracker.__exit__(None, None, None)
            return {"results": [], "scraped": [], "stats": stats}

        # ---- Phase 2: Async Scraping ----
        urls = [r["url"] for r in results if r.get("url")]
        valid_urls = [u for u in urls if scraper.should_scrape(u)]

        tracker.start_scrape(total=len(valid_urls))
        scrape_start = time.time()

        async def update_progress(completed: int, total: int):
            tracker.update_scrape(completed, total)

        scraped = await scraper.scrape_batch_async(
            valid_urls,
            max_concurrent=scrape_concurrent,
            progress_callback=update_progress,
        )

        scrape_elapsed = time.time() - scrape_start
        stats["scrape_time"] = round(scrape_elapsed, 2)
        stats["scraped_count"] = len(scraped)
        tracker.complete_scrape()

        # ---- Phase 3: Processing ----
        tracker.start_processing()

        scraped_by_url = {item["url"]: item["content"] for item in scraped}

        articles = []
        for r in results:
            url = r.get("url", "")
            scraped_text = scraped_by_url.get(url, "")
            articles.append({
                "title": r.get("title", "Unknown"),
                "summary": r.get("body", "") or scraped_text[:2000],
                "body": scraped_text if scraped_text else r.get("body", ""),
                "url": url,
                "source": "duckduckgo",
            })

        tracker.complete_processing()

        if own_tracker:
            tracker.__exit__(None, None, None)

        return {
            "results": results,
            "articles": articles,
            "scraped": scraped,
            "stats": stats,
        }

    except Exception as e:
        logging.error(f"Async pipeline failed: {e}")
        if own_tracker:
            tracker.__exit__(None, None, None)
        return {"results": [], "scraped": [], "articles": [], "stats": stats, "error": str(e)}


async def async_search_batch(
    queries: List[str],
    ddg_limit: int = 50,
    max_concurrent_queries: int = 5,
) -> List[Dict]:
    """Search multiple queries in parallel, each with its own pipeline.

    Args:
        queries: List of search queries
        ddg_limit: Results per query
        max_concurrent_queries: Max concurrent searches

    Returns:
        List of result dicts from async_search_pipeline
    """
    sem = asyncio.Semaphore(max_concurrent_queries)

    async def search_one(query: str) -> Dict:
        async with sem:
            return await async_search_pipeline(query, ddg_limit=ddg_limit)

    tasks = [search_one(q) for q in queries]
    return await asyncio.gather(*tasks, return_exceptions=True)


async def async_deep_research(
    topic: str,
    language: str = "en",
    ddg_limit: int = 100,
    scrape_concurrent: int = 20,
    planner_model: Optional[str] = None,
    progress_tracker: ProgressTracker = None,
) -> Dict:
    """Full deep research pipeline: planner → batch search → merge results.

    Stage 0: Decompose topic into sub-queries via OpenRouter
    Stage 1: Search all sub-queries in parallel
    Stage 2: Scrape all found URLs
    Stage 3: Merge and deduplicate results

    Args:
        topic: The user's research topic
        language: Response language
        ddg_limit: Results per sub-query
        scrape_concurrent: Max concurrent scrape connections
        planner_model: Optional model override for the planner
        progress_tracker: Optional ProgressTracker

    Returns:
        Dict with keys: 'results', 'articles', 'scraped', 'stats', 'sub_queries'
    """
    tracker = progress_tracker or ProgressTracker()
    own_tracker = progress_tracker is None

    stats = {"plan_time": 0, "search_time": 0, "scrape_time": 0,
             "total_sources": 0, "scraped_count": 0, "sub_queries": 0,
             "reasoning_time": 0}
    sub_queries = [topic]

    try:
        if own_tracker:
            tracker = tracker.__enter__()

        # ---- Stage 0: Planning ----
        tracker.start_planning()
        plan_start = time.time()

        generated = await generate_search_queries(
            topic=topic,
            language=language,
            model=planner_model,
        )

        if generated and len(generated) >= 1 and generated != [topic]:
            sub_queries = generated

        stats["plan_time"] = round(time.time() - plan_start, 2)
        stats["sub_queries"] = len(sub_queries)
        tracker.complete_planning()

        # ---- Display AI Research Plan ----
        panel_lines = [f"[bold {c('accent_blue')}]Topic:[/bold {c('accent_blue')}] {topic}\n"]
        panel_lines.append(f"[{c('overlay0')}]Decomposed into {len(sub_queries)} sub-queries:[/{c('overlay0')}]\n")
        for i, q in enumerate(sub_queries, 1):
            panel_lines.append(f"  [{c('green')}]{i}.[/{c('green')}] [{c('text')}]{q}[/{c('text')}]")

        plan_panel = Panel(
            Text("\n".join(panel_lines)),
            title=f" [{c('mauve')}][bold]AI Research Plan[/bold][/{c('mauve')}] ",
            border_style=c('mauve'),
            box=rich_box.ROUNDED,
            width=80,
        )
        tracker.console.print()
        tracker.console.print(plan_panel)
        tracker.console.print()

        # ---- Stage 1+2: Batch Search + Scrape ----
        per_query_limit = max(10, ddg_limit // max(len(sub_queries), 1))
        results_list = await async_search_batch(
            queries=sub_queries,
            ddg_limit=per_query_limit,
        )

        # ---- Stage 3: Merge Results ----
        all_results = []
        all_scraped = []
        seen_urls = set()
        seen_titles = set()
        seen_scraped_urls = set()

        for res in results_list:
            if isinstance(res, dict) and not res.get("error"):
                for r in res.get("results", []):
                    url = r.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_results.append(r)

                for s in res.get("scraped", []):
                    url = s.get("url", "")
                    if url and url not in seen_scraped_urls:
                        seen_scraped_urls.add(url)
                        all_scraped.append(s)

                sub_stats = res.get("stats", {})
                stats["search_time"] += sub_stats.get("search_time", 0)
                stats["scrape_time"] += sub_stats.get("scrape_time", 0)

        scraped_by_url = {item["url"]: item["content"] for item in all_scraped}

        articles = []
        references = []
        ref_counter = 1
        for r in all_results:
            url = r.get("url", "")
            title = r.get("title", "")
            if title and title not in seen_titles:
                seen_titles.add(title)
                scraped_text = scraped_by_url.get(url, "")
                articles.append({
                    "ref_id": ref_counter,
                    "title": title,
                    "summary": r.get("body", "") or scraped_text[:2000],
                    "body": scraped_text if scraped_text else r.get("body", ""),
                    "url": url,
                    "source": "duckduckgo",
                })
                references.append({
                    "ref_id": ref_counter,
                    "title": title,
                    "url": url,
                })
                ref_counter += 1

        stats["total_sources"] = len(articles)
        stats["scraped_count"] = len(all_scraped)

        tracker.start_processing()
        tracker.complete_processing()

        # ---- Stage 4: Reasoning / Synthesis ----
        tracker.start_reasoning()
        reason_start = time.time()

        reasoning = await synthesize_findings(
            articles=articles,
            scraped=all_scraped,
            references=references,
            topic=topic,
            language=language,
        )

        stats["reasoning_time"] = round(time.time() - reason_start, 2)
        tracker.complete_reasoning()

        if own_tracker:
            tracker.__exit__(None, None, None)

        return {
            "results": all_results,
            "articles": articles,
            "scraped": all_scraped,
            "stats": stats,
            "sub_queries": sub_queries,
            "reasoning": reasoning,
            "references": references,
        }

    except Exception as e:
        logging.error(f"Deep research pipeline failed: {e}")
        if own_tracker:
            tracker.__exit__(None, None, None)
        return {
            "results": [], "articles": [], "scraped": [],
            "stats": stats, "sub_queries": sub_queries, "error": str(e),
            "reasoning": None, "references": [],
        }


def run_async_search(
    query: str,
    ddg_limit: int = 100,
    scrape_concurrent: int = 20,
) -> Dict:
    """Synchronous entry point that runs the async pipeline with asyncio.run().

    Use this from existing sync code (like main.py).
    """
    return asyncio.run(
        async_search_pipeline(
            query=query,
            ddg_limit=ddg_limit,
            scrape_concurrent=scrape_concurrent,
        )
    )


def run_deep_research(
    topic: str,
    language: str = "en",
    ddg_limit: int = 100,
    scrape_concurrent: int = 20,
) -> Dict:
    """Synchronous entry point for the full deep research pipeline.

    Calls the planner, then batch searches all sub-queries, merges results.
    """
    return asyncio.run(
        async_deep_research(
            topic=topic,
            language=language,
            ddg_limit=ddg_limit,
            scrape_concurrent=scrape_concurrent,
        )
    )
