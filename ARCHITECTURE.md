当前目标：这个项目把招聘官网岗位抓下来，按简历做匹配，再生成一份能直接投递和展示的手册。

模块职责

- `run.py`：总入口，串起抓取、匹配、出手册三步。
- `hunter/config.py`：读取用户配置和站点配置，顺手把相对路径变成可用路径。
- `hunter/crawler/base.py`：定义抓取流程骨架，统一分页、列表提取和详情抓取。
- `hunter/crawler/generic.py`：按 YAML 配置抓大多数招聘站，不用单独写代码。
- `hunter/crawler/registry.py`：根据网址决定该用哪个抓取器。
- `hunter/crawler/adapters/bytedance.py`：处理字节这类少量需要单独规则的网站。
- `hunter/matcher/engine.py`：统一做预筛选、打分和分数整理。
- `hunter/matcher/ai_matcher.py`：用 AI 理解简历和岗位内容。
- `hunter/matcher/keyword_matcher.py`：离线关键词打分，不依赖外部接口。
- `hunter/reporter/generator.py`：把结果整理成更适合展示的 HTML 和 PDF 手册。
- `templates/style.css`：控制手册的视觉样式和信息层级。
- `assets/overview.svg`：仓库首页用的总览横幅。
- `docs/showcase-plan.md`：记录展示包装下一步要补什么。
- `docs/demo-script.md`：对外介绍项目时可直接复用的短讲稿。
- `config/sites/*.yaml`：每个招聘网站的抓取规则。
- `config/user.example.yaml`：用户自己的配置模板。
- `scripts/*.py`：兼容旧用法的脚本入口。
- `scripts/build_alina_job_manual.py`：一次性生成阿离岗位投递手册，抓智联公开岗位，按简历画像筛选，输出 HTML/PDF、岗位 JSON 和平台反爬策略 JSON。

调用关系

- `run.py` 先读配置，再调用 `registry.py` 选抓取器。
- 抓取器输出岗位原始数据后，`engine.py` 负责打分。
- 打分结果最后交给 `generator.py` 生成展示手册。

关键设计决定

- 抓取优先走 YAML 配置，是为了扩站快，少改代码。
- 匹配保留 AI 和关键词两条路，是为了同时兼顾效果和离线可用。
- 报告先出 HTML 再转 PDF，是为了更容易把展示效果做漂亮，也方便后面继续做公开演示页。
- 分数统一压到 100 分制，是为了让展示结果更直观，也更适合对外说明。
- 多平台投递链接不能默认都可抓；未验证能读取岗位卡片的平台只作为备用入口，最终清单只放可验证岗位，并输出 `platform_access_policy.json` 留痕。
- 岗位筛选只看岗位本身信息，不把搜索关键词并入匹配文本，避免假命中。
