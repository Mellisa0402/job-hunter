"""
Claude API semantic matcher.
Analyzes a resume with Claude, then batch-scores jobs for semantic match quality.
"""

import json
import os
import re


class AIMatcher:
    """Uses Claude API to analyze resume + batch-score jobs semantically."""

    def __init__(self, user_config: dict):
        import anthropic
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"
        self.user_config = user_config
        self.resume_analysis: dict = {}
        self.resume_summary: str = ''

    def analyze_resume(self, resume_text: str) -> dict:
        """Analyze resume with Claude to extract structured profile."""
        target_roles = self.user_config.get('preferences', {}).get('target_roles', [])
        roles_hint = f"Target roles: {', '.join(target_roles)}" if target_roles else ""

        prompt = f"""Analyze this resume and extract key information. Return ONLY JSON, no other text.

Resume:
{resume_text[:8000]}

Return format:
{{
  "skills": ["skill1", "skill2"],
  "experience_summary": "one-sentence summary of work/internship experience",
  "education": "education summary",
  "suitable_roles": ["role direction 1", "role direction 2"],
  "unsuitable_roles": ["role type where experience is clearly insufficient"],
  "seniority": "junior or mid or senior"
}}

Requirements:
- skills: list all hard skills (languages, tools, frameworks, domain knowledge), be thorough
- suitable_roles: 3-5 suitable role directions, use common job title terms
- unsuitable_roles: roles where experience is clearly lacking, empty array if none
- seniority: 0-2 years→junior, 3-5 years→mid, 6+→senior
{roles_hint}"""

        print("[Matcher] Analyzing resume (Claude API)...")
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        result_text = response.content[0].text
        result = self._parse_json(result_text, "resume analysis")
        self.resume_analysis = result
        self.resume_summary = self._build_summary(result)

        print(f"[Matcher] Resume analyzed → seniority={result.get('seniority')}, "
              f"skills={len(result.get('skills', []))}, "
              f"suitable={result.get('suitable_roles', [])}")
        return result

    def _build_summary(self, analysis: dict) -> str:
        parts = []
        skills = analysis.get('skills', [])
        if skills:
            parts.append(f"Skills: {', '.join(skills[:15])}")
        exp = analysis.get('experience_summary', '')
        if exp:
            parts.append(f"Experience: {exp}")
        edu = analysis.get('education', '')
        if edu:
            parts.append(f"Education: {edu}")
        roles = analysis.get('suitable_roles', [])
        if roles:
            parts.append(f"Suitable: {', '.join(roles)}")
        seniority = analysis.get('seniority', '')
        if seniority:
            parts.append(f"Level: {seniority}")
        return ' | '.join(parts)

    def batch_score(self, job_batch: list[dict], target_cities: list[str] | None = None) -> list[dict]:
        """Score a batch of up to 10 jobs in one Claude API call."""
        # Build job summaries
        parts = []
        for i, job in enumerate(job_batch):
            title = job.get('title', 'N/A')
            desc = job.get('description', '') or ''
            reqs = job.get('requirements', '') or ''
            raw = job.get('raw_text', '') or ''
            jd_text = f"{desc} {reqs} {raw}"[:600]
            parts.append(f"Job{i + 1}: {title} | {jd_text}")

        jobs_block = '\n'.join(parts)

        city_hint = ''
        if target_cities:
            city_hint = f' City preference: {", ".join(target_cities)} (bonus for jobs in these cities).'

        prompt = f"""I am a job seeker. My resume summary:
{self.resume_summary}

Score each job for match quality (0-100). Return ONLY a JSON array:
{jobs_block}

Return format: [{{"index": 1, "score": 85, "reasons": ["skill A matches", "experience B relevant"]}}, ...]

Scoring:
- 90-100: excellent match — skills/direction/experience perfectly aligned
- 75-89: good match — most requirements met, small gaps
- 60-74: partial match — some foundation but needs learning curve
- 40-59: marginal — only a few skill overlaps
- 0-39: not relevant — direction or skills mismatch
{city_hint}
Factors (importance descending):
1. Role direction alignment (highest weight)
2. Skill overlap
3. Experience/seniority fit
4. City preference"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        result_text = response.content[0].text
        result = self._parse_json(result_text, "batch scoring")
        return result if isinstance(result, list) else result.get('results', [])

    def _parse_json(self, text: str, label: str) -> dict | list:
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            pass
        for pattern in [r'\[.*\]', r'\{.*\}']:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except (json.JSONDecodeError, TypeError):
                    pass
        print(f"[Matcher] {label} JSON parse failed, raw: {text[:300]}")
        return {}
