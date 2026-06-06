#!/usr/bin/env python3
"""
DEPRECATED: Thin wrapper for backward compatibility.
Use 'python3 run.py' instead, or import from hunter.crawler directly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hunter.config import load_user_config
from hunter.crawler.registry import load_crawler

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Job crawler (legacy wrapper)')
    parser.add_argument('--url', required=True)
    parser.add_argument('--cities', default='')
    parser.add_argument('--types', default='full_time')
    parser.add_argument('--output', default='/tmp/jobs_raw.json')
    parser.add_argument('--session', default='storage_state.json')
    parser.add_argument('--config', default=None)
    args = parser.parse_args()

    config = load_user_config()
    if args.cities:
        config.setdefault('preferences', {})['cities'] = [
            c.strip() for c in args.cities.split(',')
        ]
    if args.types:
        config.setdefault('preferences', {})['job_types'] = [
            t.strip() for t in args.types.split(',')
        ]

    crawler = load_crawler(args.url, config, args.session)
    crawler.output_dir = os.path.dirname(args.output) or '.'
    jobs = crawler.run(session_path=args.session)

    # Save to requested path
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    import json
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(jobs)} jobs to {args.output}")
