"""
Report generator — produces HTML and PDF job application handbooks.
Config-driven: cities, strategy text, and content all come from user_config.
"""

import os
import html
from pathlib import Path
from playwright.sync_api import sync_playwright


class ReportGenerator:
    """Generates HTML and PDF reports from scored jobs."""

    def __init__(self, user_config: dict):
        self.user_config = user_config
        profile = user_config.get('profile', {})
        self.name = profile.get('name', 'Job Seeker')
        self.preferences = user_config.get('preferences', {})
        self.target_cities = self.preferences.get('cities', [])
        self.output_cfg = user_config.get('output', {})
        self.output_dir = self.output_cfg.get('dir', './output')

    def generate(self, jobs: list[dict], highlights: str = '',
                 search_keywords: str = '', output_filename: str | None = None) -> str:
        """Generate PDF report from scored jobs. Returns path to PDF."""
        os.makedirs(self.output_dir, exist_ok=True)

        if output_filename is None:
            output_filename = 'handbook.pdf'
        pdf_path = os.path.join(self.output_dir, output_filename)
        html_path = pdf_path.replace('.pdf', '.html')

        html = self._build_html(jobs, highlights, search_keywords)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[Report] HTML saved: {html_path} ({len(html)} chars)")

        # Generate PDF
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f'file://{html_path}', wait_until='load')
            page.pdf(
                path=pdf_path,
                format='A4',
                margin={'top': '15mm', 'bottom': '15mm', 'left': '12mm', 'right': '12mm'},
                print_background=True,
            )
            browser.close()

        size_kb = os.path.getsize(pdf_path) / 1024
        print(f"[Report] PDF saved: {pdf_path} ({size_kb:.0f} KB)")
        return pdf_path

    def _build_html(self, jobs: list[dict], highlights: str = '',
                    search_keywords: str = '') -> str:
        """Build the full HTML report."""
        min_score = self.preferences.get('min_score', 50)
        high = [j for j in jobs if j.get('score', 0) >= max(min_score, 50)]
        if not high:
            high = jobs

        # Group by city
        cities: dict[str, list] = {c: [] for c in self.target_cities}
        cities['Other'] = []
        for j in high:
            city_str = str(j.get('city', ''))
            placed = False
            for c in self.target_cities:
                if c.lower() in city_str.lower():
                    cities[c].append(j)
                    placed = True
                    break
            if not placed:
                cities['Other'].append(j)

        for c in cities:
            cities[c].sort(key=lambda x: x.get('score', 0), reverse=True)

        # Campus jobs
        campus = [j for j in high if 'campus' in j.get('source', '').lower()]

        # Load CSS
        css_path = Path(__file__).resolve().parent.parent.parent / 'templates' / 'style.css'
        style = ''
        if css_path.exists():
            style = css_path.read_text(encoding='utf-8')

        total = sum(len(v) for v in cities.values())
        average_score = int(sum(job.get('score', 0) for job in high) / len(high)) if high else 0
        strong_matches = sum(1 for job in high if job.get('score', 0) >= 80)
        campus_count = len(campus)
        active_cities = [city_name for city_name, city_jobs in cities.items() if city_jobs]
        top_jobs = high[:3]

        strategy_entries = self._get_strategy()
        flow_steps = [
            ('01', '收集岗位', '从招聘官网批量抓取岗位列表和详情。'),
            ('02', '筛选匹配', '按城市、岗位类型和简历特征做优先级排序。'),
            ('03', '生成手册', '把值得投递的岗位整理成可直接点击的清单。'),
        ]

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8">
<title>{self.name} · 求职投递手册</title>
<style>{style}</style></head>
<body>

<section class="hero">
  <div class="hero-kicker">JOB HUNTER PLAYBOOK</div>
  <h1>{self.name} · 求职投递手册</h1>
  <div class="subtitle">把分散岗位整理成一份能直接投、能直接讲、也能直接展示的清单。</div>

  <div class="hero-grid">
    <div class="hero-card accent">
      <div class="hero-label">优先投递</div>
      <div class="hero-value">{strong_matches}</div>
      <div class="hero-note">分数 80 以上的岗位数量</div>
    </div>
    <div class="hero-card">
      <div class="hero-label">纳入手册</div>
      <div class="hero-value">{total}</div>
      <div class="hero-note">达到展示标准的岗位数量</div>
    </div>
    <div class="hero-card">
      <div class="hero-label">平均匹配度</div>
      <div class="hero-value">{average_score}</div>
      <div class="hero-note">已经压到 100 分制内</div>
    </div>
    <div class="hero-card">
      <div class="hero-label">目标城市</div>
      <div class="hero-value">{len(active_cities)}</div>
      <div class="hero-note">当前覆盖的城市分组</div>
    </div>
  </div>
</section>

<section class="summary-panel">
  <div class="panel-title">这份手册怎么看</div>
  <div class="flow-grid">
"""
        for step_no, step_title, step_desc in flow_steps:
            html += f"""
    <div class="flow-card">
      <div class="flow-no">{step_no}</div>
      <div class="flow-title">{step_title}</div>
      <div class="flow-desc">{step_desc}</div>
    </div>
"""

        html += """
  </div>
</section>

<section class="summary-panel">
  <div class="panel-title">概览</div>
  <div class="summary-grid">
"""
        for city_name in self.target_cities:
            count = len(cities.get(city_name, []))
            if not count:
                continue
            html += f"""
    <div class="summary-item">
      <div class="summary-city">📍 {html_escape(city_name)}</div>
      <div class="summary-num">{count}</div>
      <div class="summary-label">可优先关注</div>
    </div>
"""

        if cities.get('Other'):
            html += f"""
    <div class="summary-item">
      <div class="summary-city">🌐 其他城市</div>
      <div class="summary-num">{len(cities['Other'])}</div>
      <div class="summary-label">补充选择</div>
    </div>
"""

        html += f"""
    <div class="summary-item">
      <div class="summary-city">🎓 校招岗位</div>
      <div class="summary-num">{campus_count}</div>
      <div class="summary-label">适合新人或转向</div>
    </div>
  </div>
</section>
"""

        if highlights or search_keywords:
            html += '<section class="notes-panel">\n'
            html += '  <div class="panel-title">定位提示</div>\n'
            if highlights:
                html += f'  <div class="note-row"><span class="note-key">你的亮点</span><span class="note-value">{html_escape(highlights)}</span></div>\n'
            if search_keywords:
                html += f'  <div class="note-row"><span class="note-key">建议关键词</span><span class="note-value">{html_escape(search_keywords)}</span></div>\n'
            html += '</section>\n'

        if top_jobs:
            html += '<section class="summary-panel">\n'
            html += '  <div class="panel-title">最值得先看</div>\n'
            html += '  <div class="top-picks">\n'
            for rank, job in enumerate(top_jobs, 1):
                title = html_escape(job.get('title') or '岗位标题待补齐')
                city_name = html_escape(job.get('city') or '城市待确认')
                source = html_escape(job.get('source') or '来源待确认')
                reasons = self._format_reasons(job.get('match_reason', []))[:2]
                reason_text = ' / '.join(html_escape(item) for item in reasons) if reasons else '匹配原因待补充'
                html += f"""
    <div class="pick-card">
      <div class="pick-rank">Top {rank}</div>
      <div class="pick-title">{title}</div>
      <div class="pick-meta">{city_name} · {source}</div>
      <div class="pick-reason">{reason_text}</div>
    </div>
"""
            html += '  </div>\n'
            html += '</section>\n'

        for city_name in self.target_cities + ['Other']:
            city_jobs = cities.get(city_name, [])
            if not city_jobs:
                continue
            emoji = '📍' if city_name != 'Other' else '🌐'
            city_avg = int(sum(job.get('score', 0) for job in city_jobs) / len(city_jobs))
            html += f'<div class="section-title">{emoji} {html_escape(city_name)} · 推荐岗位 {len(city_jobs)} 个</div>\n'
            html += f'<div class="section-subtitle">这一组平均匹配度 {city_avg} 分，按优先级从高到低排列。</div>\n'
            for rank, j in enumerate(city_jobs, 1):
                html += self._job_card(j, rank)

        if campus:
            html += f'<div class="section-title">🎓 校招 / 应届生岗位 {len(campus)} 个</div>\n'
            html += '<div class="section-subtitle">适合想先拿机会、再逐步挑方向的投递顺序。</div>\n'
            for rank, j in enumerate(campus[:50], 1):
                html += self._job_card(j, rank)

        html += '<div class="page-break"></div>\n'
        html += '<div class="section-title">📋 投递节奏建议</div>\n'
        for entry in strategy_entries:
            html += f'<div class="strategy-card">{entry}</div>\n'

        html += '<div class="footer"><p>Generated by job-hunter · HTML 与 PDF 都可直接展示</p></div>\n'
        html += '</body></html>'
        return html

    def _job_card(self, j: dict, rank: int) -> str:
        title = html_escape(j.get('title') or '岗位标题待补齐')
        score = int(j.get('score', 0))
        url = html_escape(j.get('url', ''))
        source = html_escape(j.get('source') or '来源待确认')
        job_id = html_escape(j.get('job_id') or '未提供')
        city = html_escape(j.get('city') or '城市待确认')
        reasons = self._format_reasons(j.get('match_reason', []))
        score_width = max(0, min(score, 100))
        score_label = self._score_label(score)

        card = f"""<div class="job-card">
  <div class="job-rank">#{rank}</div>
  <div class="job-header">
    <div class="job-title">{title}</div>
    <div class="job-score">{score}分</div>
  </div>
  <div class="job-meta">
    <span>{city}</span><span>{source}</span><span>岗位编号 {job_id}</span>
  </div>
  <div class="score-track"><div class="score-fill" style="width: {score_width}%"></div></div>
  <div class="score-caption">{score_label}</div>
  <div class="job-tags">"""
        for r in reasons:
            card += f'<span class="job-tag">{html_escape(r)}</span>'
        card += """  </div>
"""
        if url:
            card += f'  <div class="job-link"><a href="{url}" target="_blank">打开岗位链接</a></div>\n'
        else:
            card += '  <div class="job-link muted">这个岗位暂时没有可用链接，建议回到原站补抓详情页。</div>\n'
        card += """</div>
"""
        return card

    def _format_reasons(self, reasons: list[str]) -> list[str]:
        formatted = []
        for reason in reasons:
            if not reason:
                continue
            if reason.startswith('skill:'):
                formatted.append(reason.replace('skill:', '技能命中：', 1))
            elif reason.startswith('city:'):
                formatted.append(reason.replace('city:', '城市匹配：', 1))
            elif reason == 'campus':
                formatted.append('校招通道')
            elif reason == 'intern':
                formatted.append('实习通道')
            else:
                formatted.append(reason)
        return formatted[:4]

    def _score_label(self, score: int) -> str:
        if score >= 85:
            return '建议立刻投递'
        if score >= 70:
            return '建议本周优先处理'
        if score >= 50:
            return '可以作为补充选择'
        return '仅建议留档观察'

    def _get_strategy(self) -> list[str]:
        """Get strategy text from config or use generic defaults."""
        custom = self.output_cfg.get('strategy_text', '')
        if custom:
            return [html_escape(line.strip()) for line in custom.split('\n') if line.strip()]

        return [
            '<b>第 1 步：</b>先投高分岗位，尽快拿到反馈。',
            '<b>第 2 步：</b>把同城同类岗位放在同一天处理，节省切换成本。',
            '<b>第 3 步：</b>每次投递后记录状态，三天内没有回音就跟进。',
            '<b>提醒：</b>链接缺失或标题缺失的岗位，不建议直接对外展示。',
        ]


def html_escape(value: str) -> str:
    return html.escape(str(value), quote=True)
