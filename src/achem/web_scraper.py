import logging
import time
import requests
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from urllib.parse import urlparse

try:
    import trafilatura

    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False

EXCLUDE_DOMAINS = {
    "cookie",
    "consent",
    "signin",
    "login",
    "signup",
    "register",
    "facebook.com",
    "twitter.com",
    "instagram.com",
    "tiktok.com",
    "youtube.com",
    "google.com",
    "bing.com",
}

EXCLUDE_PATTERNS = [
    "cookie",
    "consent",
    "sign-in",
    "login",
    "gdpr",
    "privacy-policy",
    "terms-of-service",
    "subscribe",
    "newsletter",
]


class WebScraper:
    """Web scraper for extracting full content from URLs."""

    BROWSER_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(self, timeout: int = 15, max_content_length: int = 15000):
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.session = requests.Session()
        self.session.headers.update(self.BROWSER_HEADERS)

    def should_scrape(self, url: str) -> bool:
        """Check if URL should be scraped."""
        parsed = urlparse(url.lower())
        domain = parsed.netloc

        for exclude in EXCLUDE_DOMAINS:
            if exclude in domain:
                return False

        for pattern in EXCLUDE_PATTERNS:
            if pattern in url.lower():
                return False

        return True

    def scrape_url(self, url: str) -> Optional[Dict]:
        """Scrape content from a single URL."""
        if not self.should_scrape(url):
            return None

        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                return None

            html_content = response.text
            content = ""
            title = ""

            if TRAFILATURA_AVAILABLE:
                result = trafilatura.extract(
                    html_content,
                    include_tables=True,
                    include_images=False,
                    include_comments=False,
                    output_format="text",
                )
                if result:
                    content = result.strip()

                title_result = trafilatura.extract_metadata(html_content)
                if (
                    title_result
                    and hasattr(title_result, "title")
                    and title_result.title
                ):
                    title = title_result.title

            if not content:
                soup = BeautifulSoup(html_content, "html.parser")

                for tag in soup(
                    ["script", "style", "nav", "footer", "header", "aside", "noscript"]
                ):
                    tag.decompose()

                title_tag = soup.find("title")
                if title_tag:
                    title = title_tag.get_text().strip()

                article = soup.find("article")
                if article:
                    content = article.get_text(separator=" ", strip=True)
                else:
                    main = soup.find("main") or soup.find(
                        "div",
                        class_=lambda x: x and "content" in x.lower() if x else False,
                    )
                    if main:
                        content = main.get_text(separator=" ", strip=True)
                    else:
                        body = soup.find("body")
                        content = (
                            body.get_text(separator=" ", strip=True) if body else ""
                        )

            content = " ".join(content.split())
            if len(content) > self.max_content_length:
                content = content[: self.max_content_length]

            if len(content) < 50:
                return None

            return {
                "url": url,
                "title": title or url,
                "content": content,
                "source": "scraped",
            }

        except Exception as e:
            logging.debug(f"Failed to scrape {url}: {e}")
            return None

    def scrape_batch(self, urls: List[str], max_workers: int = 5) -> List[Dict]:
        """Scrape multiple URLs in parallel."""
        results = []

        def scrape_single(url):
            return self.scrape_url(url)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(scrape_single, url): url for url in urls}
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    logging.debug(f"Scraping error: {e}")

        return results

    def get_scraped_text(self, urls: List[str], top_n: int = 3) -> str:
        """Get combined text from top N scraped URLs."""
        if not urls:
            return ""

        urls_to_scrape = urls[:top_n]
        scraped = self.scrape_batch(urls_to_scrape)

        if not scraped:
            return ""

        combined = []
        for item in scraped:
            combined.append(f"Source: {item['title']}")
            combined.append(f"URL: {item['url']}")
            combined.append(f"Content: {item['content']}")
            combined.append("---")

        return "\n".join(combined)


_scraper_instance = None


def get_scraper() -> WebScraper:
    """Get singleton scraper instance."""
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = WebScraper()
    return _scraper_instance
