"""
Base crawler abstract class.
Defines the standard pipeline: paginate → extract list → fetch details.
"""

from abc import ABC, abstractmethod
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright, Page, BrowserContext
import json
import os
import time


class BaseCrawler(ABC):
    """Abstract base for all site crawlers.
    Subclasses implement site-specific URL construction and DOM parsing.
    """

    def __init__(self, url: str, user_config: dict, site_config: dict):
        self.url = url
        self.domain = urlparse(url).netloc
        self.token = self._extract_token(url)
        self.user_config = user_config
        self.site_config = site_config
        self.cities = user_config.get('preferences', {}).get('cities', [])
        self.job_types = user_config.get('preferences', {}).get('job_types', ['full_time'])
        self.output_dir = user_config.get('output', {}).get('dir', './output')
        self.jobs: list[dict] = []
        self.seen_urls: set[str] = set()

    def _extract_token(self, url: str) -> str:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        token_param = self.site_config.get('auth', {}).get('token_param', 'token')
        return params.get(token_param, [None])[0] or ''

    # ---- Template method: the standard crawl pipeline ----

    def run(self, session_path: str | None = None) -> list[dict]:
        """Execute the full crawl pipeline."""
        name = self.site_config.get('name', self.domain)
        print(f"[Crawler] Target: {name}")
        print(f"[Crawler] Cities: {self.cities}")
        print(f"[Crawler] Types: {self.job_types}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            locale = self.site_config.get('locale', 'en-US')

            if session_path and os.path.exists(session_path):
                print(f'[Crawler] Using saved session: {session_path}')
                context = browser.new_context(locale=locale, storage_state=session_path)
            else:
                print('[Crawler] No session file found, running unauthenticated')
                context = browser.new_context(locale=locale)

            page = context.new_page()

            for jt in self.job_types:
                for city in self.cities:
                    self._crawl_list_pages(page, jt, city)

            # Fetch detail pages
            print(f"\n[Crawler] {len(self.jobs)} jobs found, fetching details...")
            self._fetch_details(page)

            browser.close()

        # Save results
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, 'jobs_raw.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.jobs, f, ensure_ascii=False, indent=2)

        print(f"\n[Crawler] Done! {len(self.jobs)} jobs saved to {output_path}")
        return self.jobs

    def _crawl_list_pages(self, page: Page, job_type: str, city: str):
        """Paginate through list pages for a given job type and city."""
        city_code = self._get_city_code(city)
        name = self.site_config.get('name', '')
        stop_conditions = self.site_config.get('list', {}).get('stop_conditions', [])
        max_pages = self.site_config.get('list', {}).get('pagination', {}).get('max_pages', 300)

        for pg in range(1, max_pages + 1):
            url = self._build_list_url(job_type, city_code, pg)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(2000)
            except Exception as e:
                print(f"  Page {pg}: timeout ({e})")
                break

            text = page.inner_text('body')

            # Check stop conditions
            if self._should_stop(text, stop_conditions):
                print(f"  Page {pg}: no more jobs")
                break

            # Extract job links
            links = self._extract_job_links(page)
            new_count = 0
            for link in links:
                href = link.get('href', '')
                if href not in self.seen_urls:
                    self.seen_urls.add(href)
                    link['city'] = city
                    link['source'] = f"{name}_{job_type}"
                    link['page_in_list'] = pg
                    self.jobs.append(link)
                    new_count += 1

            print(f"  Page {pg}: {len(links)} raw, {new_count} new (total: {len(self.jobs)})")

            if not self._has_next_page(text, pg):
                break

    # ---- Abstract methods (implemented by generic or adapter) ----

    @abstractmethod
    def _build_list_url(self, job_type: str, city_code: str, page: int) -> str:
        """Build the list page URL for the given parameters."""
        ...

    @abstractmethod
    def _get_city_code(self, city: str) -> str:
        """Map a user-facing city name to the site's internal city code."""
        ...

    @abstractmethod
    def _should_stop(self, page_text: str, stop_conditions: list[dict]) -> bool:
        """Check whether pagination should stop based on page text."""
        ...

    @abstractmethod
    def _has_next_page(self, page_text: str, current_page: int) -> bool:
        """Check if there is a next page."""
        ...

    @abstractmethod
    def _extract_job_links(self, page: Page) -> list[dict]:
        """Extract job link URLs and summaries from a list page."""
        ...

    @abstractmethod
    def _build_detail_url(self, job: dict) -> str:
        """Build the detail page URL for a job."""
        ...

    @abstractmethod
    def _parse_detail_page(self, text: str, job: dict) -> dict:
        """Parse a detail page's text into structured job info."""
        ...

    @abstractmethod
    def _fetch_details(self, page: Page, checkpoint_every: int = 50):
        """Visit each job's detail page and extract full JD."""
        ...
