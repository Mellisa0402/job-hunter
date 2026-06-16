# job-hunter 项目完整说明

这个文件用于给任何新的 AI 对话快速理解整个项目。把它单独发给 AI，对方也应该能知道项目目标、目录结构、运行方法、当前状态和注意事项。

## 一句话介绍

`job-hunter` 是一个求职岗位筛选工具：它把招聘官网上一大堆岗位抓下来，按用户简历和偏好打分，最后生成一份可阅读、可投递、可展示的岗位手册。

## 项目目标

这个项目解决的是“招聘网站岗位太多、筛选太慢、结果不好展示”的问题。

用户输入：

- 一个招聘网站链接，可以是普通招聘页，也可以是带 token 的内推链接
- 一份简历，支持 PDF 或文本
- 求职偏好，比如城市、岗位类型、最低分数、关键词

项目输出：

- `jobs_raw.json`：抓下来的岗位原始数据
- `jobs_scored.json`：按简历和偏好打完分的岗位列表
- `handbook.html` / `handbook.pdf`：最终投递手册
- 展示用网页、视频脚本和宣传素材

## 当前项目状态

截至 2026-06-08，这个项目有两条主线：

| 主线 | 状态 | 说明 |
|---|---|---|
| 求职工具本体 | 已有基础闭环 | 已有抓取、匹配、报告生成三阶段代码 |
| 对外展示包装 | 正在补素材 | 已做 README 展示、公开 demo、宣传文案、宝宝AI风格视频 |

最近一次上下文记录显示：当前重点是给 `job-hunter` 补一条宝宝AI星露谷风展示视频，成片在 `output/宝宝AI_jobhunter_星露谷风展示视频.webm`。

## 核心流程

| 阶段 | 做什么 | 主要代码 | 主要产物 |
|---|---|---|---|
| 1. 抓取岗位 | 打开招聘网站，读取岗位列表和详情 | `hunter/crawler/` | `jobs_raw.json` |
| 2. 匹配打分 | 用简历、关键词、城市偏好给岗位评分 | `hunter/matcher/` | `jobs_scored.json` |
| 3. 生成手册 | 把岗位结果做成 HTML/PDF 手册 | `hunter/reporter/` | `handbook.html`、`handbook.pdf` |

总入口是 `run.py`。它会按顺序执行抓取、匹配、生成报告。

## 本地运行方法

推荐先准备虚拟环境。当前项目已有 `.venv`，在 macOS 或 Linux 中优先使用：

```bash
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m playwright install chromium
cp config/user.example.yaml config/user.yaml
./.venv/bin/python run.py --url "https://jobs.example.com/..." --resume "./resume.pdf"
```

如果不用 AI 匹配，可以改成关键词模式：

```bash
./.venv/bin/python run.py --url "https://jobs.example.com/..." --resume "./resume.pdf" --mode keyword
```

AI 匹配模式需要设置 `ANTHROPIC_API_KEY`。没有这个环境变量时，不要强行跑 AI 模式，直接用 `--mode keyword`。

## 常用参数

| 参数 | 作用 |
|---|---|
| `--url` | 招聘网站地址 |
| `--resume` | 简历文件路径 |
| `--config` | 指定用户配置文件 |
| `--name` | 覆盖配置里的姓名 |
| `--cities` | 覆盖目标城市，逗号分隔 |
| `--types` | 覆盖岗位类型，如 `full_time,campus,intern` |
| `--min-score` | 覆盖最低匹配分 |
| `--mode` | 匹配模式，`ai` 或 `keyword` |
| `--output-dir` | 输出目录 |
| `--output` | 输出 PDF 文件路径 |
| `--session` | Playwright 登录状态文件 |

## 主要目录和文件

| 路径 | 作用 |
|---|---|
| `run.py` | 项目主入口，串起抓取、匹配、报告生成 |
| `hunter/config.py` | 读取用户配置和网站配置 |
| `hunter/crawler/base.py` | 抓取流程骨架 |
| `hunter/crawler/generic.py` | YAML 驱动的通用招聘站抓取器 |
| `hunter/crawler/registry.py` | 按网址选择抓取器 |
| `hunter/crawler/adapters/bytedance.py` | 字节跳动招聘站专用适配器 |
| `hunter/matcher/engine.py` | 匹配总控，负责预筛选、打分和整理 |
| `hunter/matcher/ai_matcher.py` | Claude API 语义匹配 |
| `hunter/matcher/keyword_matcher.py` | 离线关键词匹配 |
| `hunter/reporter/generator.py` | 生成 HTML/PDF 投递手册 |
| `templates/report.html.j2` | 报告 HTML 模板 |
| `templates/style.css` | 报告视觉样式 |
| `config/user.example.yaml` | 用户配置模板 |
| `config/sites/*.yaml` | 招聘网站抓取规则 |
| `scripts/*.py` | 旧版或辅助入口 |
| `docs/` | 展示、视频、发布、项目包装文档 |
| `examples/public-demo.html` | 公开演示页面 |
| `site/` | 对外展示站点 |
| `promo/` | 宣传页面、封面、字幕和发布文案 |
| `output/` | 本地生成结果 |
| `public-export/` | 可对外发布的项目副本 |
| `assets/` | README 和展示图 |

## 配置体系

个人配置从 `config/user.example.yaml` 复制为 `config/user.yaml`。`config/user.yaml` 不应该提交到 git。

用户配置主要包括：

| 配置块 | 内容 |
|---|---|
| `profile` | 姓名和简历路径 |
| `preferences` | 城市、岗位类型、资历、目标方向、最低分 |
| `matching` | 匹配模式、关键词、资历过滤、城市加分、来源加分 |
| `output` | 输出目录、输出格式、投递策略文案 |

网站配置在 `config/sites/`：

| 文件 | 作用 |
|---|---|
| `generic.yaml` | 通用招聘网站配置模板 |
| `bytedance.yaml` | 字节跳动招聘站配置 |
| `tiktok.yaml` | TikTok 招聘站配置 |

## 支持的网站方式

项目按这个顺序选择抓取器：

| 优先级 | 方式 | 说明 |
|---|---|---|
| 1 | Python 专用适配器 | 复杂网站用代码单独处理，比如 `bytedance.py` |
| 2 | YAML 网站配置 | 大多数网站用选择器配置即可 |
| 3 | 通用自动识别 | 没有配置时，尝试用默认规则抓取 |

添加新招聘站时，优先复制 `config/sites/generic.yaml`，改成新站点配置。只有 YAML 配不动时，才新增 Python 适配器。

## 匹配逻辑

项目有两种匹配模式：

| 模式 | 适合场景 | 依赖 |
|---|---|---|
| `ai` | 想让模型理解简历和岗位语义 | 需要 `ANTHROPIC_API_KEY` |
| `keyword` | 想离线、稳定、无外部接口运行 | 只依赖本地关键词配置 |

分数统一整理为 `0-100`，方便报告展示和人工判断。

匹配会参考：

- 岗位标题
- 岗位描述
- 岗位要求
- 用户简历
- 目标城市
- 招聘类型
- 资历过滤规则
- 用户配置的关键词

## 报告与展示

核心报告由 `hunter/reporter/generator.py` 生成，视觉由 `templates/` 控制。

展示相关资料集中在：

| 路径 | 内容 |
|---|---|
| `README.md` | GitHub 首页介绍 |
| `examples/public-demo.html` | 公开 demo |
| `docs/demo-script.md` | 对外介绍短讲稿 |
| `docs/showcase-plan.md` | 展示包装计划 |
| `docs/jobhunter-video-project-brief.md` | 视频项目说明 |
| `docs/workbench-*.md` | 通用视频工作台相关说明 |
| `promo/` | 宣传页、字幕、发布文案 |
| `output/宝宝AI_jobhunter_星露谷风展示视频.webm` | 当前宝宝AI星露谷风展示视频成片 |

## 已完成内容

| 内容 | 状态 |
|---|---|
| 三阶段流水线：抓取、匹配、报告 | 已完成基础版 |
| YAML 驱动通用抓取 | 已完成 |
| 字节跳动站点适配 | 已完成 |
| TikTok 站点配置 | 已完成 |
| AI 匹配和关键词匹配双模式 | 已完成 |
| HTML/PDF 投递手册 | 已完成基础版 |
| GitHub README 展示包装 | 已完成 |
| 公开 demo 页面 | 已完成 |
| 宣传脚本和视频物料 | 已有多版 |
| 宝宝AI星露谷风展示视频 | 已生成 WebM 成片 |

## 待继续事项

| 事项 | 说明 |
|---|---|
| 继续补公开展示素材 | 当前上下文里的进行中事项 |
| 根据真实用户场景打磨配置 | 尤其是不同岗位方向的关键词和报告表达 |
| 验证更多招聘网站 | 当前已记录 ByteDance 和 TikTok，其他站点要逐个验证 |

## 重要约束

| 约束 | 说明 |
|---|---|
| 不要提交个人配置 | `config/user.yaml`、简历、cookie、登录状态不应入库 |
| 不要伪造岗位数据 | 生产逻辑必须来自真实抓取或真实输入 |
| 不要把 mock 混进生产代码 | mock 只能本地调试，并且要排除在 git 外 |
| 文件读写使用 UTF-8 | 项目里有中文文档和中文文件名 |
| Python 优先用项目虚拟环境 | macOS/Linux 用 `./.venv/bin/python` |
| 数据库或文件删除前必须确认 | 当前项目主要是文件产物，删除也要谨慎 |
| 不要擅自创建分支或 worktree | 需要用户明确同意 |

## 给下一个 AI 的建议

先读这几个文件：

1. `PROJECT_OVERVIEW_FOR_AI.md`：完整项目说明，也就是当前文件
2. `CONTEXT.md`：最近一次工作停在哪里
3. `README.md`：对外展示口径
4. `ARCHITECTURE.md`：模块职责和调用关系
5. `CLAUDE.md`：项目内 AI 协作规则

如果任务是改代码，优先看 `run.py` 和 `hunter/`。

如果任务是继续做展示包装，优先看 `docs/`、`promo/`、`site/` 和 `output/`。

如果任务是继续做宝宝AI风格视频，优先看：

- `docs/baby-ai-jobhunter-stardew-film.html`
- `docs/baby-ai-stardew-subtitles.srt`
- `scripts/render_baby_ai_stardew_video.js`
- `scripts/record_stardew_frames_to_media.js`
- `output/宝宝AI_jobhunter_星露谷风展示视频.webm`

## 快速判断这个项目是什么

不要把它只理解成“爬虫项目”。更准确地说，它是一个“求职行动手册生成器”：

- 爬虫只是第一步
- 匹配是核心价值
- 报告和展示决定它能不能被用户理解、被公开演示、被传播

当前项目已经从纯工具开发，进入“产品展示和内容包装”阶段。
