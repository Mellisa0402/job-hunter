#!/usr/bin/env python3
"""
job-hunter: Crawl + Match + Report — all in one pipeline.

Usage:
  python3 run.py --url "https://jobs.example.com/..." --resume ./resume.pdf

All personal preferences (cities, keywords, seniority, etc.) are read from
config/user.yaml (create it from config/user.example.yaml first).

CLI arguments override config file values.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from hunter.config import load_user_config, PROJECT_ROOT
from hunter.crawler.registry import load_crawler
from hunter.matcher.engine import MatchEngine
from hunter.reporter.generator import ReportGenerator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='job-hunter — Crawl jobs, match against resume, generate PDF handbook'
    )
    parser.add_argument('--url', help='Job site URL (with token if required)')
    parser.add_argument('--resume', help='Path to resume file (PDF or text)')
    parser.add_argument('--config', default=None,
                        help='Path to user config YAML (default: config/user.yaml)')
    parser.add_argument('--name', help='Your name (overrides config)')
    parser.add_argument('--cities', help='Target cities, comma-separated (overrides config)')
    parser.add_argument('--types', help='Job types: full_time,campus,intern (overrides config)')
    parser.add_argument('--min-score', type=int, help='Minimum match score (overrides config)')
    parser.add_argument('--mode', choices=['ai', 'keyword'],
                        help='Matching mode: ai or keyword (overrides config)')
    parser.add_argument('--highlights', default='',
                        help='Resume highlights for the report')
    parser.add_argument('--search-keywords', default='',
                        help='Suggested search keywords for the report')
    parser.add_argument('--output', default=None,
                        help='Output PDF path (default: output/handbook.pdf)')
    parser.add_argument('--session', default='storage_state.json',
                        help='Playwright session file for authenticated crawling')
    parser.add_argument('--output-dir', default=None,
                        help='Output directory (overrides config)')

    return parser.parse_args()


def main():
    args = parse_args()

    # Load user config
    if args.config:
        from hunter.config import USER_CONFIG_PATH
        import hunter.config as cfg_mod
        cfg_mod.USER_CONFIG_PATH = Path(args.config)
    user_config = load_user_config()

    # Apply CLI overrides
    if args.name:
        user_config.setdefault('profile', {})['name'] = args.name
    if args.cities:
        user_config.setdefault('preferences', {})['cities'] = [
            c.strip() for c in args.cities.split(',')
        ]
    if args.types:
        user_config.setdefault('preferences', {})['job_types'] = [
            t.strip() for t in args.types.split(',')
        ]
    if args.min_score is not None:
        user_config.setdefault('preferences', {})['min_score'] = args.min_score
    if args.mode:
        user_config.setdefault('matching', {})['mode'] = args.mode
    if args.output_dir:
        user_config.setdefault('output', {})['dir'] = args.output_dir

    output_dir = user_config.get('output', {}).get('dir', './output')
    os.makedirs(output_dir, exist_ok=True)

    resume_path = args.resume or user_config.get('profile', {}).get('resume', '')
    name = user_config.get('profile', {}).get('name', 'Job Seeker')
    cities = user_config.get('preferences', {}).get('cities', [])

    print(f"{'='*60}")
    print(f"  job-hunter · Crawl → Match → Report")
    print(f"  Profile: {name}")
    print(f"  Cities: {cities}")
    print(f"{'='*60}")

    # ---- Stage 1: Crawl ----
    if args.url:
        print("\n--- Stage 1: Crawl ---")
        session_path = args.session
        if not os.path.isabs(session_path):
            session_path = str(PROJECT_ROOT / session_path)
        if not os.path.exists(session_path):
            session_path = None

        crawler = load_crawler(args.url, user_config, session_path)
        jobs = crawler.run(session_path=session_path)
    else:
        # Try to load existing jobs_raw.json
        raw_path = os.path.join(output_dir, 'jobs_raw.json')
        if os.path.exists(raw_path):
            print(f"\n[Stage 1] Using existing {raw_path}")
            with open(raw_path, 'r', encoding='utf-8') as f:
                jobs = json.load(f)
        else:
            print("Error: --url is required for crawling, and no jobs_raw.json found.")
            sys.exit(1)

    # ---- Stage 2: Match ----
    print("\n--- Stage 2: Match ---")
    engine = MatchEngine(user_config)
    scored = engine.match(jobs, resume_path=resume_path if resume_path else None,
                          target_cities=cities)

    scored_path = os.path.join(output_dir, 'jobs_scored.json')
    with open(scored_path, 'w', encoding='utf-8') as f:
        json.dump(scored, f, ensure_ascii=False, indent=2)
    print(f"[Stage 2] Saved {len(scored)} scored jobs to {scored_path}")

    # ---- Stage 3: Report ----
    print("\n--- Stage 3: Report ---")
    reporter = ReportGenerator(user_config)
    output = args.output or os.path.join(output_dir, 'handbook.pdf')
    pdf_path = reporter.generate(
        scored,
        highlights=args.highlights,
        search_keywords=args.search_keywords,
        output_filename=os.path.basename(output)
    )

    print(f"\n{'='*60}")
    print(f"  Done! PDF handbook: {pdf_path}")
    print(f"{'='*60}")

    # Auto-open on macOS
    if sys.platform == 'darwin':
        subprocess.run(['open', pdf_path])


if __name__ == '__main__':
    main()
