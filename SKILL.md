---
name: job-hunter
description: 求职岗位爬取与投递手册生成工具。当用户要求爬取招聘网站岗位、筛选匹配职位、生成投递清单PDF、分析内推链接岗位时使用。支持任意招聘网站的岗位爬取、简历匹配打分、生成带可点击投递链接的PDF手册。
argument-hint: <操作> [选项]
allowed-tools: [Bash, Read, Write, Edit, WebFetch, WebSearch]
---

# 求职岗位爬取 + 匹配 + PDF投递手册

三阶段流水线工具，帮助求职者从任意招聘官网高效筛选岗位并生成投递手册。

## 触发条件

当用户提到以下任一场景时使用此技能：
- "帮我爬取/抓取这个招聘网站的岗位"
- "筛选适合我的岗位"
- "生成投递手册/投递清单PDF"
- "分析这个内推链接的岗位"
- "匹配我的简历和这些岗位"

## 工作流程

### 阶段1: 爬取岗位

使用 `hunter/crawler/` 子系统从招聘网站爬取岗位列表+详情。

**输入：**
- 招聘网站URL（支持带token的内推链接）
- 目标城市列表（任意城市名）
- 招聘类型（full_time/campus/intern）

**输出：** `jobs_raw.json`

**使用方式：**
```bash
python3 run.py --url "https://jobs.bytedance.com/referral/pc/position?token=XXX" --resume ~/Desktop/简历.pdf
```

**支持的网站：**
- 内置YAML配置：字节跳动 (jobs.bytedance.com)、TikTok (lifeattiktok.com)
- 通用模式：大部分招聘网站可通过添加 `config/sites/<site>.yaml` 配置文件支持
- 复杂网站：可在 `hunter/crawler/adapters/` 中编写Python适配器

### 阶段2: 匹配打分

使用 `hunter/matcher/` 子系统将岗位与简历进行匹配打分。

**输入：**
- `jobs_raw.json`（阶段1输出）
- 简历文件（PDF/文本）

**输出：** `jobs_scored.json`

**打分维度：**
- AI模式：Claude API语义分析简历 + 批量打分
- 关键词模式：基于 `config/user.yaml` 中用户自定义的技能关键词
- 城市偏好加分、招聘类型加分
- 基于资历的标题关键词排除

### 阶段3: 生成PDF投递手册

使用 `hunter/reporter/` 子系统生成带可点击投递链接的PDF。

**输入：**
- `jobs_scored.json`（阶段2输出）
- 用户配置中的姓名、卖点、搜索关键词

**输出：** PDF投递手册

## 配置参考

用户配置文件：`config/user.yaml`（从 `config/user.example.yaml` 复制）

关键配置项：
- `profile.name`, `profile.resume` — 个人信息与简历路径
- `preferences.cities`, `preferences.job_types`, `preferences.seniority` — 求职偏好
- `matching.mode` — ai 或 keyword
- `matching.keywords.skill_categories` — 自定义技能分类（仅keyword模式）
- `matching.city_bonus` — 城市加分权重
- `output.dir` — 输出目录

## 添加新网站

1. 复制 `config/sites/generic.yaml` 为 `config/sites/your-site.yaml`
2. 填入域名、列表页路径、CSS选择器、分页策略、详情页提取规则
3. 无需编写代码

## 快捷使用

如果用户已经提供了简历和链接，可以直接运行：

```bash
python3 run.py --url "<招聘网站URL>" --resume "<简历路径>"
```

## 已知限制

1. **需要Playwright**: `pip install -r requirements.txt && python3 -m playwright install chromium`
2. **SPA页面需等待渲染**: 列表页需要3-8秒加载，详情页需要1-2秒
3. **大站全量爬取耗时**: 600+岗位详情页约需10-15分钟
4. **AI模式需要ANTHROPIC_API_KEY**: 未设置时请改用关键词模式
