# job-hunter · Crawl + Match + Report

One command to crawl job listings from any career site, match them against your resume, and generate an HTML/PDF application handbook with clickable apply links.

![Project overview](./assets/overview.svg)

## Why This Exists

Job sites are noisy. This project turns a long list of openings into a short, ranked handbook you can actually act on.

It helps you:

- collect jobs from a target career site
- score them against your resume or keyword profile
- output a cleaner handbook for applying, reviewing, or sharing

## Showcase

The current outward-facing result is a visual handbook instead of a plain raw export.

What it already shows:

- a clear 3-step flow: collect → match → report
- a ranked city-by-city shortlist
- a stronger visual cover and summary area
- HTML output that is easier to demo before exporting to PDF

What is still being polished:

- cleaner public sample data
- screenshot assets for GitHub
- a dedicated demo page for sharing

## Demo Pitch

`job-hunter` turns a messy careers page into a short, ranked application handbook.

Instead of reading hundreds of listings by hand, you can:

- pull jobs from a target site
- score them against your resume
- review a cleaner shortlist by city and priority

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Create your config
cp config/user.example.yaml config/user.yaml
# Edit config/user.yaml — fill in your name, resume path, target cities, skills, etc.

# 3. Run the pipeline
python3 run.py --url "https://jobs.example.com/..." --resume ./resume.pdf
```

That's it. `run.py` will:
1. **Crawl** — scrape all job listings (list pages + detail pages) from the target site
2. **Match** — analyze your resume and score every job for fit
3. **Report** — generate a visual handbook with high-match jobs grouped by city, plus clickable apply links and a clearer decision flow

## How It Works

```
run.py --url <job-site-url> --resume <resume.pdf>
       │
       ├─ Stage 1: Crawler (hunter/crawler/)
       │   Reads site config YAML → paginates list pages → extracts job details
       │   Output: jobs_raw.json
       │
       ├─ Stage 2: Matcher (hunter/matcher/)
       │   Analyzes resume (Claude API or keyword mode) → scores each job 0-100
       │   Output: jobs_scored.json
       │
       └─ Stage 3: Reporter (hunter/reporter/)
           Groups high-match jobs by city → generates visual HTML → renders PDF
           Output: handbook.html + handbook.pdf
```

## Configuration

All personal settings live in `config/user.yaml` (gitignored). Copy `config/user.example.yaml` to get started:

| Section | What you configure |
|---------|-------------------|
| `profile` | Your name, resume file path |
| `preferences` | Target cities, job types, seniority level, target roles, minimum score |
| `matching` | AI or keyword mode, skill keywords, city bonuses, title exclusions |
| `output` | Output directory, format, custom strategy text |

## Adding a New Job Site

Most sites work with zero code — just create a YAML config:

```bash
cp config/sites/generic.yaml config/sites/my-site.yaml
# Edit the YAML: set domains, list paths, CSS selectors, pagination, extraction markers
```

The `GenericCrawler` reads this config and handles everything: URL construction, pagination, link extraction, detail page parsing.

For complex sites (API-driven, infinite scroll, iframes), write a Python adapter in `hunter/crawler/adapters/`. See `hunter/crawler/adapters/bytedance.py` for the reference implementation.

### Verified Sites

| Site | Config | Status |
|------|--------|--------|
| ByteDance (jobs.bytedance.com) | `config/sites/bytedance.yaml` | Verified |
| TikTok (lifeattiktok.com) | `config/sites/tiktok.yaml` | Verified |

### Contributing Site Configs

Found a site that works with a YAML config? PRs welcome for new `config/sites/*.yaml` files.

## Matching Modes

| Mode | Flag | Description |
|------|------|-------------|
| AI (default) | `--mode ai` | Claude API analyzes resume + batch-scores jobs. Requires `ANTHROPIC_API_KEY`. |
| Keyword | `--mode keyword` | Offline keyword matching based on your `config/user.yaml` skill categories. No API needed. |

All scores are normalized to a 0-100 range before report generation, so the ranking and report visuals stay consistent.

## Login / Authentication

Many job sites require login. job-hunter supports four approaches:

1. **Session file (recommended)**: Run `scripts/save_session.py` once to log in manually, then pass `--session storage_state.json` to `run.py`.
2. **Cookie injection**: Set cookies directly in the site's YAML config or a Python adapter.
3. **Bookmarklet export**: Use a browser bookmarklet to export job links from an already-logged-in page. Feed the JSON to `run.py` (skip crawling).
4. **URL token**: For sites that use referral tokens in the URL, just pass the full URL to `--url`.

## CLI Reference

```
python3 run.py [options]

Required:
  --url URL              Job site URL (with token if required)

Options:
  --resume PATH          Path to resume PDF/text (default: from config)
  --name NAME            Your name (default: from config)
  --cities CITY1,CITY2   Target cities, comma-separated (default: from config)
  --types TYPE1,TYPE2    Job types: full_time,campus,intern (default: from config)
  --min-score N          Minimum match score for report (default: from config)
  --mode ai|keyword      Matching mode (default: from config)
  --highlights TEXT      Resume highlights for report header
  --search-keywords TEXT Suggested search keywords for report
  --session PATH         Playwright auth session file
  --output PATH          Output PDF path (default: output/handbook.pdf)
  --output-dir PATH      Output directory (default: from config)
```

## Project Structure

```
job-hunter/
  run.py                          # Main entry point
  hunter/                         # Python package
    config.py                     # Config loading + validation
    crawler/
      base.py                     # BaseCrawler abstract class
      generic.py                  # YAML-driven generic crawler
      registry.py                 # Domain → crawler resolution
      adapters/                   # Python adapters for complex sites
        bytedance.py              # ByteDance reference adapter
    matcher/
      engine.py                   # MatchEngine orchestrator
      ai_matcher.py               # Claude API semantic matcher
      keyword_matcher.py          # Config-driven keyword matcher
    reporter/
      generator.py                # Visual handbook generator for HTML+PDF output
  config/
    user.example.yaml             # User config template
    user.yaml                     # Your config (gitignored)
    sites/                        # Site YAML configs
      bytedance.yaml              # ByteDance
      tiktok.yaml                 # TikTok
      generic.yaml                # Template for new sites
  templates/
    report.html.j2                # Legacy report template
    style.css                     # Visual handbook styles
  scripts/                        # Legacy wrappers (backward compat)
    crawler.py
    matcher.py
    report_generator.py
    save_session.py
```

## Requirements

- Python 3.10+
- Playwright Chromium
- pdfplumber (resume PDF parsing)
- anthropic (Claude API, optional — for AI matching mode)
- pyyaml (optional — falls back to built-in parser)

## License

MIT
