# job-hunter｜求职岗位投递手册生成器

`job-hunter` 可以把一堆杂乱的招聘链接，整理成一份能直接查看、筛选和投递的岗位手册。

它适合这样的场景：你手里有很长的招聘官网、岗位搜索页、城市关键词或投递入口，不想一条条手动判断哪些适合自己。项目会先抓取岗位，再按简历和偏好做匹配，最后生成 HTML / PDF 手册。

`job-hunter` turns long, noisy career pages and job-search links into a ranked application handbook.

It is useful when you have many company career pages, city-specific search links, or application entrances and want a clean shortlist instead of manual sorting. The project crawls jobs, matches them against a resume or keyword profile, and outputs an HTML / PDF handbook.

![Project overview](./assets/overview.svg)

## 它能做什么｜What It Does

中文：

- 抓取目标招聘网站或岗位搜索入口。
- 按简历、城市、岗位方向和关键词做匹配。
- 排除明显不适合的岗位，比如销售、客服、地推、过度资深或重开发岗位。
- 生成可点击的 HTML 手册和适合查看的 PDF 手册。
- HTML 手册可按城市、薪资高低、实习/全职筛选；投递链接会新开页面，不覆盖手册。
- 对反爬严重的平台做分层处理：能公开读取才入库，不能验证就只作为备用入口。

English:

- Crawl target career pages or job-search entrances.
- Match jobs against resume signals, cities, target roles, and keywords.
- Filter out clearly unsuitable jobs such as sales-heavy, customer-service, field-promotion, overly senior, or heavy engineering roles.
- Generate a clickable HTML handbook and a readable PDF handbook.
- Filter the HTML handbook by city, salary order, and internship/full-time type; application links open separately so the handbook stays in place.
- Handle anti-crawl platforms conservatively: only verified readable jobs enter the final list; unverified platforms stay as backup entrances.

![Flow map](./assets/flow-map.svg)

## 你会看到什么｜What People See

中文：

输出结果不是一堆原始链接，而是一份可以直接执行的投递清单。它会显示城市分布、岗位标题、公司、薪资、地点要求、匹配原因和投递链接；HTML 里还能按城市、薪资和实习/全职快速切换。

English:

The output is not a dump of raw links. It is an actionable shortlist showing city distribution, job title, company, salary, location requirements, match reasons, and application links, with city, salary, and internship/full-time controls in the HTML version.

![Handbook preview](./assets/handbook-preview.svg)

公开示例 / Public sample:

- `examples/public-demo.html`

## 一句话介绍｜Quick Demo Line

中文：`job-hunter` 把杂乱岗位页变成一份按匹配度排序的投递手册。

English: `job-hunter` turns noisy job pages into a ranked application handbook.

## 快速开始｜Quick Start

```bash
pip install -r requirements.txt
playwright install chromium
cp config/user.example.yaml config/user.yaml
python3 run.py --url "https://jobs.example.com/..." --resume ./resume.pdf
```

中文：把自己的简历路径、目标城市、岗位方向和关键词填进 `config/user.yaml`，再运行命令。

English: Fill your resume path, target cities, role directions, and keywords in `config/user.yaml`, then run the command.

## 流程｜How It Flows

| 步骤 | 中文说明 | English | Output |
|---|---|---|---|
| 1 | 抓取岗位列表和详情 | Crawl job listings and details | `jobs_raw.json` |
| 2 | 按简历和关键词打分 | Score jobs against resume and keywords | `jobs_scored.json` |
| 3 | 生成投递手册 | Generate the application handbook | `handbook.html` / `handbook.pdf` |

## 适合谁｜Who It Fits

| 场景 | 中文说明 | English |
|---|---|---|
| 校招/实习 | 快速从大量岗位中筛出值得投的机会 | Quickly shortlist roles from large campus or internship pools |
| 多城市求职 | 对比不同城市的机会和薪资 | Compare opportunities across cities |
| 简历定向投递 | 根据个人经历和关键词排序岗位 | Rank jobs by resume fit and target keywords |
| 项目展示 | 展示“抓取 → 匹配 → 手册”的完整流程 | Demonstrate a clear crawl → match → report workflow |

## 配置｜Configuration

个人配置放在 `config/user.yaml`。

Personal settings live in `config/user.yaml`.

| Section | 中文 | English |
|---|---|---|
| `profile` | 姓名和简历路径 | Name and resume path |
| `preferences` | 城市、岗位类型、方向、最低分 | Cities, job types, target direction, minimum score |
| `matching` | AI 或关键词模式、加分项、排除项 | AI or keyword mode, boosts, exclusions |
| `output` | 输出目录、格式、摘要文案 | Output folder, format, summary text |

## 支持的网站类型｜Supported Site Styles

中文：多数普通招聘官网可以通过 YAML 配置接入。

English: Most regular career pages can be supported with YAML configuration.

```bash
cp config/sites/generic.yaml config/sites/my-site.yaml
```

如果网站更复杂，可以在 `hunter/crawler/adapters/` 里添加专门适配器。

If a site is more complex, add a custom adapter under `hunter/crawler/adapters/`.

| Site | Config | Status |
|---|---|---|
| ByteDance | `config/sites/bytedance.yaml` | Verified |
| TikTok | `config/sites/tiktok.yaml` | Verified |

## 反爬处理原则｜Anti-Crawl Handling

中文：

项目不绕过平台风控，不伪造岗位数据。只有已经能看到、能解析、能打开的岗位才进入最终手册。对 BOSS、拉勾、前程无忧、猎聘这类动态加载或登录态依赖较强的平台，默认只作为备用入口；必须先通过登录态浏览器验证能读到岗位卡片，才允许入库。

English:

The project does not bypass platform protections or fabricate job data. Only jobs that are visible, parseable, and openable enter the final handbook. Platforms such as BOSS Zhipin, Lagou, 51job, and Liepin are treated as backup entrances by default because they often depend on dynamic rendering or login state. They can enter the pipeline only after a logged-in browser session verifies readable job cards.

## 匹配模式｜Matching Modes

| Mode | 中文 | English |
|---|---|---|
| AI | 用 AI 更语义化地理解简历和岗位 | Use AI to understand resume and job content semantically |
| Keyword | 离线关键词打分，不依赖外部接口 | Run offline keyword scoring without external APIs |

所有分数都会压到 `0-100`，方便展示和比较。

All scores are normalized to `0-100` for easier display and comparison.

## 常用命令｜Common Commands

```bash
python3 run.py --url <job-site-url> --resume <resume.pdf>
python3 run.py --url <job-site-url> --mode keyword
python3 scripts/save_session.py
```

2026-06-16 阿离岗位投递手册专用流程：

Special workflow for the 2026-06-16 Alina application handbook:

```bash
/Users/mellisa/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/build_alina_job_manual.py
```

中文：详细流程见 `docs/alina-job-manual-runbook.md`。它使用已验证可公开读取的智联招聘页面，缓存原始页面，生成 `platform_access_policy.json` 记录平台反爬策略，并输出 HTML + PDF 手册。

English: See `docs/alina-job-manual-runbook.md` for details. It uses verified public Zhilian pages, caches raw pages, writes `platform_access_policy.json` for platform anti-crawl strategy, and outputs HTML + PDF handbooks.

## 项目结构｜Project Shape

| Path | 中文职责 | English Responsibility |
|---|---|---|
| `run.py` | 总入口，串起抓取、匹配、报告 | Main pipeline entry |
| `hunter/crawler/` | 抓取岗位列表和详情 | Job crawling |
| `hunter/matcher/` | 岗位匹配和打分 | Job matching and scoring |
| `hunter/reporter/` | 生成 HTML / PDF 手册 | HTML / PDF handbook generation |
| `config/` | 用户配置和站点配置 | User and site configs |
| `templates/` | 报告样式 | Report styles |
| `scripts/` | 辅助脚本和专项流程 | Helper scripts and special workflows |
| `lessons.md` | 项目踩坑和正确路径记录 | Project lessons and proven paths |
| `docs/alina-job-manual-runbook.md` | 阿离岗位手册复用流程 | Repeatable Alina handbook workflow |

## 依赖｜Requirements

- Python 3.10+
- Playwright Chromium
- `pdfplumber`
- `anthropic` for AI mode

## 搜索记录｜Search Notes

| Source | Conclusion |
|---|---|
| `skills.sh` | 本轮没有新增功能模块，不需要额外搜索 |
| GitHub | 本轮重点是展示包装和专项投递手册流程，不重复搜索 |

## 已完成 / 待办｜Done / Next

| Status | 中文 | English |
|---|---|---|
| Done | 更清晰的手册首页样式 | Clearer handbook cover style |
| Done | 更稳定的 100 分制匹配分数 | More stable 100-point scoring |
| Done | GitHub 首页横幅和展示文案 | GitHub showcase assets and copy |
| Done | 阿离岗位投递手册：221 个已筛选岗位，输出 PDF + HTML | Alina handbook: 221 filtered jobs, PDF + HTML output |
| Done | HTML 手册支持城市、薪资、实习/全职筛选，投递链接不覆盖手册 | HTML handbook supports city, salary, internship/full-time filters, with non-overwriting links |
| Doing | 继续补公开展示素材 | Continue polishing public showcase assets |

## License

MIT
