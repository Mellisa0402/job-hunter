#!/usr/bin/env python3
"""
DEPRECATED: Thin wrapper for backward compatibility.
Use 'python3 run.py' instead, or import from hunter.reporter directly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hunter.config import load_user_config
from hunter.reporter.generator import ReportGenerator

if __name__ == '__main__':
    import argparse, json
    parser = argparse.ArgumentParser(description='Report generator (legacy wrapper)')
    parser.add_argument('--jobs', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--highlights', default='')
    parser.add_argument('--search-keywords', default='')
    parser.add_argument('--cities', default='')
    parser.add_argument('--output', default='handbook.pdf')
    args = parser.parse_args()

    with open(args.jobs, 'r', encoding='utf-8') as f:
        jobs = json.load(f)

    config = load_user_config()
    config.setdefault('profile', {})['name'] = args.name
    if args.cities:
        config.setdefault('preferences', {})['cities'] = [
            c.strip() for c in args.cities.split(',')
        ]

    reporter = ReportGenerator(config)
    pdf_path = reporter.generate(
        jobs,
        highlights=args.highlights,
        search_keywords=args.search_keywords,
        output_filename=os.path.basename(args.output)
    )

    import subprocess
    subprocess.run(['open', pdf_path])
