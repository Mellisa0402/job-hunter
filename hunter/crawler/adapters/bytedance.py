"""
ByteDance adapter — reference implementation for sites needing Python-level customization.
Extends GenericCrawler to handle ByteDance-specific detail URL construction.
"""

from urllib.parse import urlparse, parse_qs
from hunter.crawler.generic import GenericCrawler


class ByteDanceCrawler(GenericCrawler):
    """ByteDance-specific crawler. Most logic is in the YAML config;
    this adapter only handles detail URL construction differences."""

    def _build_detail_url(self, job: dict) -> str:
        href = job.get('href', '')
        # ByteDance detail URLs are full URLs already in the list page
        # Just append token if needed
        if self.token:
            sep = '&' if '?' in href else '?'
            return f"{href}{sep}token={self.token}"
        return href
