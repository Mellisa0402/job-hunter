"""
Keyword matcher — config-driven, no hardcoded keywords.
All skill categories, city bonuses, and filters come from user_config.
"""


class KeywordMatcher:
    """Scores jobs based on keyword overlap with user-defined skill categories."""

    def __init__(self, user_config: dict):
        matching = user_config.get('matching', {})
        kw_cfg = matching.get('keywords', {})
        self.exclude_titles = kw_cfg.get('exclude_titles', [])
        self.skill_categories = kw_cfg.get('skill_categories', {})
        self.seniority_filters = matching.get('seniority_filters', {})
        self.city_bonus = matching.get('city_bonus', {})
        self.source_bonus = matching.get('source_bonus', {})
        self.preferences = user_config.get('preferences', {})

    def pre_screen(self, job: dict) -> bool:
        """Check if a job should be excluded based on title keywords."""
        title = job.get('title', '')

        for ex in self.exclude_titles:
            if ex.lower() in title.lower():
                return False

        seniority = self.preferences.get('seniority', 'mid')
        for kw in self.seniority_filters.get(seniority, []):
            if kw.lower() in title.lower():
                return False

        return True

    def score_job(self, job: dict, target_cities: list[str] | None = None) -> tuple[int, list[str]]:
        """Score a single job. Returns (score, reasons)."""
        text = ' '.join([
            job.get('description', ''),
            job.get('requirements', ''),
            job.get('raw_text', ''),
        ])
        city = job.get('city', '')
        source = job.get('source', '')

        score = 0
        reasons = []

        # Skill keyword matching
        for cat_name, rules in self.skill_categories.items():
            must = rules.get('must', [])
            nice = rules.get('nice', [])

            for kw in must:
                if kw.lower() in text.lower():
                    score += 10
                    reasons.append(f'skill:{kw}')

            for kw in nice:
                if kw.lower() in text.lower():
                    score += 5

        # City bonus
        if target_cities is None:
            target_cities = list(self.city_bonus.keys())
        for c, bonus in self.city_bonus.items():
            if c in str(city) and c in target_cities:
                score += bonus
                reasons.append(f'city:{c}')
                break

        # Source bonus
        for s, bonus in self.source_bonus.items():
            if s in source.lower():
                score += bonus
                reasons.append(s)
                break

        return score, reasons
