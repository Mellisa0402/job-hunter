"""
Site registry: resolves a target URL domain to the best crawler.
Priority: Python adapter > YAML site config > auto-detect heuristic.
"""

from urllib.parse import urlparse
from pathlib import Path
from hunter.crawler.base import BaseCrawler
from hunter.crawler.generic import GenericCrawler
from hunter.config import PROJECT_ROOT


# Python adapter classes keyed by (domain,)
ADAPTERS: dict[str, type[BaseCrawler]] = {}

# Eager-load Python adapters
try:
    from hunter.crawler.adapters.bytedance import ByteDanceCrawler
    ADAPTERS['jobs.bytedance.com'] = ByteDanceCrawler
except ImportError:
    pass


def load_crawler(url: str, user_config: dict, session_path: str | None = None) -> BaseCrawler:
    """Resolve a URL to the appropriate crawler instance."""
    domain = urlparse(url).netloc
    site_config = None

    # 1. Python adapters (exact domain match)
    for key, cls in ADAPTERS.items():
        if key in domain:
            cfg_path = PROJECT_ROOT / 'config' / 'sites' / f'{key.split(".")[0]}.yaml'
            if cfg_path.exists():
                from hunter.config import load_site_config
                site_config = load_site_config(cfg_path)
            else:
                site_config = {'name': key, 'domains': [key]}
            return cls(url, user_config, site_config)

    # 2. YAML site configs
    from hunter.config import load_all_site_configs, load_site_config
    all_configs = load_all_site_configs()
    for cfg in all_configs:
        cfg_domains = cfg.get('domains', [])
        if any(d in domain for d in cfg_domains):
            return GenericCrawler(url, user_config, cfg)

    # 3. Fallback: auto-detect heuristic
    print(f"[Registry] No site config found for {domain}, using generic auto-detect")
    generic_cfg = {
        'name': domain,
        'domains': [domain],
        'locale': 'en-US',
        'list': {
            'paths': {'full_time': '/'},
            'params': {},
            'pagination': {'strategy': 'query_param', 'param': 'page', 'max_pages': 50},
            'stop_conditions': [{'type': 'text_contains', 'value': 'No results'}],
            'selectors': {'job_link': 'a[href*="/job/"]', 'job_card': 'li'},
        },
        'detail': {
            'path_template': '',
            'extraction': {
                'title': {'strategy': 'first_line_excluding', 'exclude_prefixes': []},
                'description': {'strategy': 'between_markers', 'start_markers': ['Description'], 'end_markers': ['Requirements'], 'max_lines': 30},
                'requirements': {'strategy': 'after_marker', 'markers': ['Requirements'], 'max_lines': 25},
            },
        },
        'auth': {'type': 'none'},
    }
    return GenericCrawler(url, user_config, generic_cfg)
