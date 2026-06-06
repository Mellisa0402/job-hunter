#!/usr/bin/env python3
"""
DEPRECATED: Thin wrapper for backward compatibility.
Use 'python3 run.py' instead, or import from hunter.matcher directly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hunter.config import load_user_config
from hunter.matcher.engine import MatchEngine

if __name__ == '__main__':
    import argparse, json
    parser = argparse.ArgumentParser(description='Job matcher (legacy wrapper)')
    parser.add_argument('--jobs', required=True)
    parser.add_argument('--resume')
    parser.add_argument('--cities')
    parser.add_argument('--output', default='/tmp/jobs_scored.json')
    parser.add_argument('--min-score', type=int, default=0)
    parser.add_argument('--mode', default='ai', choices=['ai', 'keyword'])
    args = parser.parse_args()

    with open(args.jobs, 'r', encoding='utf-8') as f:
        jobs = json.load(f)

    config = load_user_config()
    config.setdefault('matching', {})['mode'] = args.mode
    if args.min_score > 0:
        config.setdefault('preferences', {})['min_score'] = args.min_score

    cities = [c.strip() for c in args.cities.split(',')] if args.cities else None

    engine = MatchEngine(config)
    scored = engine.match(jobs, args.resume, cities)

    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(scored, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(scored)} scored jobs to {args.output}")
