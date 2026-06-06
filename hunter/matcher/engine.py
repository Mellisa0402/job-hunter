"""
Match engine — orchestrates resume parsing, pre-screening, and scoring.
Supports two modes: 'ai' (Claude API) and 'keyword' (offline).
"""

import json
import os
import pdfplumber

from hunter.matcher.keyword_matcher import KeywordMatcher
from hunter.matcher.ai_matcher import AIMatcher


class MatchEngine:
    """Orchestrates the full match pipeline: parse resume → pre-screen → score."""

    def __init__(self, user_config: dict):
        self.user_config = user_config
        matching = user_config.get('matching', {})
        self.mode = matching.get('mode', 'ai')
        self.preferences = user_config.get('preferences', {})

        # Check API availability for AI mode
        self._api_available = bool(os.environ.get('ANTHROPIC_API_KEY'))
        if self.mode == 'ai' and not self._api_available:
            print("[Matcher] ANTHROPIC_API_KEY not set, falling back to keyword mode")
            self.mode = 'keyword'

        # Instantiate matchers
        self.keyword_matcher = KeywordMatcher(user_config)

        self.ai_matcher = None
        if self.mode == 'ai':
            self.ai_matcher = AIMatcher(user_config)

        # Pre-screen exclusions (from keyword matcher, shared across modes)
        matching_cfg = user_config.get('matching', {})
        kw_cfg = matching_cfg.get('keywords', {})
        self.exclude_titles = kw_cfg.get('exclude_titles', [])
        self.seniority_filters = matching_cfg.get('seniority_filters', {})

    # ---- Resume parsing ----

    def parse_resume(self, resume_path: str | None) -> str:
        """Extract full text from a resume file (PDF or text)."""
        if not resume_path:
            return ""

        if resume_path.lower().endswith('.pdf'):
            try:
                text = ""
                with pdfplumber.open(resume_path) as pdf:
                    for page in pdf.pages:
                        t = page.extract_text()
                        if t:
                            text += t + '\n'
                return text
            except Exception as e:
                print(f"[Matcher] PDF parse failed: {e}")
                return ""

        if resume_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            print("[Matcher] Image resumes not supported, use PDF or text")
            return ""

        with open(resume_path, 'r', encoding='utf-8') as f:
            return f.read()

    # ---- Pre-screening ----

    def _pre_screen(self, job: dict) -> bool:
        """Filter out jobs with excluded titles or too-senior roles."""
        title = job.get('title', '')

        for ex in self.exclude_titles:
            if ex.lower() in title.lower():
                return False

        if self.mode == 'ai' and self.ai_matcher and self.ai_matcher.resume_analysis:
            seniority = self.ai_matcher.resume_analysis.get('seniority', 'mid')
        else:
            seniority = self.preferences.get('seniority', 'mid')

        for kw in self.seniority_filters.get(seniority, []):
            if kw.lower() in title.lower():
                return False

        return True

    # ---- Main match flow ----

    def match(self, jobs: list[dict], resume_path: str | None = None,
              target_cities: list[str] | None = None) -> list[dict]:
        """Run full match pipeline on a list of jobs. Returns scored jobs sorted desc."""

        # Step 1: Parse & analyze resume (AI mode only)
        if resume_path and self.mode == 'ai' and self.ai_matcher:
            resume_text = self.parse_resume(resume_path)
            if resume_text:
                self.ai_matcher.analyze_resume(resume_text)

        if not target_cities:
            target_cities = self.preferences.get('cities', [])

        # Step 2: Pre-screen
        passed = []
        excluded = 0
        for job in jobs:
            if self._pre_screen(job):
                passed.append(job)
            else:
                excluded += 1

        print(f"[Matcher] Pre-screen: {len(jobs)} → {len(passed)} passed, {excluded} excluded")

        # Step 3: Score
        scored = []

        if self.mode == 'ai' and self.ai_matcher:
            BATCH_SIZE = 10
            total_batches = (len(passed) + BATCH_SIZE - 1) // BATCH_SIZE

            for bi in range(0, len(passed), BATCH_SIZE):
                batch = passed[bi:bi + BATCH_SIZE]
                batch_num = bi // BATCH_SIZE + 1
                print(f"[Matcher] Scoring batch {batch_num}/{total_batches} ({len(batch)} jobs)...")

                results = self.ai_matcher.batch_score(batch, target_cities)

                for r in results:
                    idx = r.get('index', 0) - 1
                    if 0 <= idx < len(batch):
                        job = batch[idx]
                        scored.append({
                            **job,
                            'score': self._normalize_score(r.get('score', 50)),
                            'match_reason': r.get('reasons', []),
                        })
        else:
            for job in passed:
                score, reasons = self.keyword_matcher.score_job(job, target_cities)
                scored.append({
                    **job,
                    'score': self._normalize_score(score),
                    'match_reason': reasons,
                })

        # Sort by score descending
        scored.sort(key=lambda x: x['score'], reverse=True)

        # Summary
        print(f"\n[Matcher] Total: {len(jobs)} → excluded {excluded} → scored {len(scored)}")
        if scored:
            print(f"[Matcher] Score range: {scored[-1]['score']} ~ {scored[0]['score']}")
            high = sum(1 for j in scored if j['score'] >= 80)
            med = sum(1 for j in scored if 50 <= j['score'] < 80)
            low = sum(1 for j in scored if j['score'] < 50)
            print(f"[Matcher] High(≥80): {high}, Mid(50-79): {med}, Low(<50): {low}")

        # Filter by min_score
        min_score = self.preferences.get('min_score', 0)
        if min_score > 0:
            scored = [j for j in scored if j['score'] >= min_score]
            print(f"[Matcher] After min_score filter (≥{min_score}): {len(scored)} jobs")

        return scored

    def _normalize_score(self, score: int | float) -> int:
        try:
            numeric = int(round(score))
        except (TypeError, ValueError):
            return 0
        return max(0, min(100, numeric))
