"""
Generic YAML-driven crawler.
Implements BaseCrawler using a site config dict loaded from YAML.
Covers ~80% of job sites with no custom code needed.
"""

import json
import os
from urllib.parse import urlencode
from playwright.sync_api import Page
from hunter.crawler.base import BaseCrawler


class GenericCrawler(BaseCrawler):
    """Crawler driven entirely by a site config dict (loaded from YAML).
    Supports query-param pagination, CSS-selector-based extraction,
    and marker-based detail page parsing.
    """

    def _build_list_url(self, job_type: str, city_code: str, page: int) -> str:
        list_cfg = self.site_config.get('list', {})
        paths = list_cfg.get('paths', {})
        path = paths.get(job_type, paths.get('full_time', '/'))
        params = list_cfg.get('params', {})

        filled = {}
        for k, v in params.items():
            v = v.replace('{city_code}', city_code or '')
            v = v.replace('{page}', str(page))
            v = v.replace('{token}', self.token)
            filled[k] = v

        base = f"https://{self.domain}"
        qs = urlencode(filled)
        return f"{base}{path}?{qs}"

    def _get_city_code(self, city: str) -> str:
        city_codes = self.site_config.get('list', {}).get('city_codes', {})
        return city_codes.get(city, city)  # fallback: use city name directly

    def _should_stop(self, page_text: str, stop_conditions: list[dict]) -> bool:
        for cond in stop_conditions:
            if cond.get('type') == 'text_contains':
                if cond.get('value', '') in page_text:
                    return True
            elif cond.get('type') == 'marker_count_is_zero':
                marker = cond.get('marker', '')
                if marker and page_text.count(marker) == 0:
                    return True
        return False

    def _has_next_page(self, page_text: str, current_page: int) -> bool:
        """Default: if there are fewer than 10 job markers, assume last page."""
        stop_conditions = self.site_config.get('list', {}).get('stop_conditions', [])
        for cond in stop_conditions:
            if cond.get('type') == 'marker_count_is_zero':
                marker = cond.get('marker', '')
                if marker:
                    return page_text.count(marker) >= 10
        return True

    def _extract_job_links(self, page: Page) -> list[dict]:
        selectors = self.site_config.get('list', {}).get('selectors', {})
        link_selector = selectors.get('job_link', 'a[href*="/position/"]')
        card_selector = selectors.get('job_card', 'li')

        return page.evaluate("""({linkSelector, cardSelector}) => {
            var results = [];
            var seen = new Set();
            var anchors = document.querySelectorAll(linkSelector);
            anchors.forEach(function(a) {
                var href = a.href;
                if (seen.has(href)) return;
                seen.add(href);
                var item = a.closest(cardSelector);
                results.push({
                    href: href,
                    text: item ? item.innerText.substring(0, 1500) : a.innerText.substring(0, 300)
                });
            });
            return results;
        }""", {'linkSelector': link_selector, 'cardSelector': card_selector})

    def _build_detail_url(self, job: dict) -> str:
        detail_cfg = self.site_config.get('detail', {})
        template = detail_cfg.get('path_template', '')
        # Extract position ID from job URL
        href = job.get('href', '')
        # Default: last segment of path is the ID
        parts = href.rstrip('/').split('/')
        pos_id = parts[-1] if parts else ''
        base = f"https://{self.domain}"
        url = template.replace('{id}', pos_id)
        url = url.replace('{type}', 'pc')
        # Append token if present
        if self.token:
            sep = '&' if '?' in url else '?'
            token_param = self.site_config.get('auth', {}).get('token_param', 'token')
            url += f"{sep}{token_param}={self.token}"
        return url if url.startswith('http') else f"{base}{url}"

    def _parse_detail_page(self, text: str, job: dict) -> dict:
        extraction = self.site_config.get('detail', {}).get('extraction', {})
        info = {
            'url': job.get('href', ''),
            'city': job.get('city', ''),
            'source': job.get('source', ''),
            'raw_text': text,
        }

        lines = text.split('\n')

        # Title extraction
        title_cfg = extraction.get('title', {})
        if title_cfg.get('strategy') == 'first_line_excluding':
            excludes = title_cfg.get('exclude_prefixes', [])
            for line in lines:
                ls = line.strip()
                if ls and len(ls) > 3 and not any(ls.startswith(p) for p in excludes):
                    info['title'] = ls
                    break

        # Job ID extraction
        id_cfg = extraction.get('job_id', {})
        if id_cfg.get('strategy') == 'line_containing':
            markers = id_cfg.get('markers', [])
            sep = id_cfg.get('separator', ':')
            fallback_sep = id_cfg.get('fallback_separator', sep)
            for line in lines:
                for m in markers:
                    if m in line:
                        for s in [sep, fallback_sep]:
                            if s in line:
                                info['job_id'] = line.split(s)[-1].strip()
                                break
                        if 'job_id' in info:
                            break
                if 'job_id' in info:
                    break

        # Description extraction
        desc_cfg = extraction.get('description', {})
        desc_start = req_start = -1
        if desc_cfg.get('strategy') == 'between_markers':
            start_markers = desc_cfg.get('start_markers', [])
            end_markers = desc_cfg.get('end_markers', [])
            max_lines = desc_cfg.get('max_lines', 30)
            for li, line in enumerate(lines):
                if any(m in line for m in start_markers):
                    desc_start = li
                if any(m in line for m in end_markers):
                    req_start = li
                    if desc_start >= 0:
                        break
            if desc_start >= 0:
                end = req_start if req_start > desc_start else min(desc_start + max_lines, len(lines))
                info['description'] = ' '.join(
                    l.strip() for l in lines[desc_start + 1:end] if l.strip())[:2000]

        # Requirements extraction
        req_cfg = extraction.get('requirements', {})
        if req_cfg.get('strategy') == 'after_marker':
            markers = req_cfg.get('markers', [])
            max_lines = req_cfg.get('max_lines', 25)
            for li, line in enumerate(lines):
                if any(m in line for m in markers):
                    info['requirements'] = ' '.join(
                        l.strip() for l in lines[li + 1:li + 1 + max_lines] if l.strip())[:1500]
                    break

        return info

    def _fetch_details(self, page: Page, checkpoint_every: int = 50):
        detailed_jobs = []
        for i, job in enumerate(self.jobs):
            try:
                detail_url = self._build_detail_url(job)
                page.goto(detail_url, wait_until="domcontentloaded", timeout=10000)
                page.wait_for_timeout(600)
                text = page.inner_text('body')
                detailed = self._parse_detail_page(text, job)
                detailed_jobs.append(detailed)
            except Exception as e:
                print(f"  [{i + 1}] error: {str(e)[:80]}")
                detailed_jobs.append({**job, 'error': str(e)[:200]})

            if (i + 1) % 20 == 0:
                pct = (i + 1) * 100 // len(self.jobs)
                print(f"  [{i + 1}/{len(self.jobs)}] {pct}%")

            if (i + 1) % checkpoint_every == 0:
                ckpt_path = os.path.join(self.output_dir, f'jobs_raw_ckpt_{i + 1}.json')
                with open(ckpt_path, 'w', encoding='utf-8') as f:
                    json.dump(detailed_jobs, f, ensure_ascii=False, indent=2)

        self.jobs = detailed_jobs
