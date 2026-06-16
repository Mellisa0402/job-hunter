# 宝宝AI星露谷风格视频模板

版本：2026-06-09

用途：把任意宝宝AI教程、工具介绍、项目展示，稳定做成“像星露谷实机画面”的竖版视频。

这份文件是单文件模板。以后迁移到别的项目时，先读这份文件，再按里面的配置生成视频。

## 一句话目标

先像一段真实像素农场游戏画面，再把教程内容挂进木牌、任务板、背包格子、对话框这些游戏 UI 里。

不要做成普通像素海报，不要做成 PPT 卡片，不要做成黑底字幕视频。

## 输出规格

| 项目 | 固定值 |
|---|---|
| 视频比例 | 9:16 |
| 分辨率 | 1080x1920 |
| 帧率 | 30fps |
| 默认时长 | 60 秒 |
| 视频编码 | H.264 MP4 |
| 音频 | AAC |
| 字体 | Zpix.ttf |
| 字幕样式 | 8 方向硬边黑色描边，中心米黄色文字 |
| 视觉母版 | 星露谷式像素农场实机风 |

## 必须保留的风格

| 必须有 | 说明 |
|---|---|
| 游戏实机感 | 画面先像游戏截图，再承载内容 |
| 俯视农场场景 | 草地、路径、农田、木屋、水域、围栏要有空间关系 |
| 木质像素 UI | 标题、章节、提示、按钮都优先放在木牌或任务板里 |
| 浅米色内容底 | 文字不要直接压在复杂背景上 |
| 硬边像素文字 | 禁止模糊、羽化、柔光阴影 |
| 模块化元素 | 木牌、背包格子、状态条、作物、动物、工具可以复用 |

## 明确禁止

| 禁止项 | 原因 |
|---|---|
| 黑色大背景 | 不像星露谷，也不适合宝宝AI的温暖感 |
| 普通科技风 UI | 会跑偏成企业宣传片 |
| 纯文字卡片堆叠 | 没有游戏实机感 |
| 只有木框没有农场场景 | 只是像素海报，不是游戏画面 |
| 直接整张复制完整游戏截图当模板 | 完整场景只提取语法，单独元素和 UI 组件才可复用 |
| 把真实软件界面重画成像素画 | 教程主体要能看懂，风格服务于理解 |

## 可复用模块

| 模块 | 用法 | 可替换内容 |
|---|---|---|
| 封面木牌 | 视频前 0-7 秒，打痛点和结果 | 主标题、副标题、核心收益 |
| 任务公告板 | 分章节讲解 | 章节名、任务说明、步骤状态 |
| 对话框 | 放口播重点句 | 用户痛点、提醒、转折句 |
| 背包格子 | 放流程步骤 | 收集、筛选、匹配、手册、开源 |
| 状态条 | 展示进度和分数 | 匹配分、完成度、通关感 |
| 技能解锁框 | 展示新功能出现 | 自动抓取、AI匹配、导出手册 |
| 收获结算页 | 视频结尾总结 | 结果、项目名、行动引导 |
| 像素提示音 | 章节切换和模块出现 | page、item、score、harvest、success |

## 标准视频结构

| 时间 | 画面 | 文字目标 | 音频 |
|---|---|---|---|
| 0-7 秒 | 大封面木牌弹出 | 讲清最大痛点和这条视频干什么 | 封面提示音 + 口播进入 |
| 7-15 秒 | 农场场景 + 任务板 | 说清用户现在卡在哪里 | 轻提示音 |
| 15-26 秒 | 背包/输入槽位 | 说清把什么交给工具 | 物品放入音 |
| 26-38 秒 | 分数条/技能解锁 | 说清工具怎么筛和排 | 打分音 |
| 38-50 秒 | 手册/收获页 | 说清最后拿到什么 | 收获音 |
| 50-60 秒 | 结尾木牌 | 项目名、开源、行动引导 | 成功音 |

## 推荐默认文案骨架

| 位置 | 写法 |
|---|---|
| 封面标题 | 先写痛点，不写工具名 |
| 封面副标题 | 写“这条视频帮你做什么” |
| 章节标题 | 一句话说人话，不写术语 |
| 口播 | 像朋友解释，短句，不装 |
| 结尾 | 不喊口号，给一个实际动作 |

示例：

```text
封面标题：刷岗位刷到头大？
封面副标题：先别硬扛
正文钩子：这条视频帮你把一堆岗位，整理成能直接投的求职手册。
结尾引导：想少走点弯路，可以先把它当成你的求职任务板。
```

## 单文件配置模板

未来换一个主题时，只改这个配置里的文字、素材路径和章节即可。

```json
{
  "template_name": "baobao-ai-stardew-video",
  "version": "2026-06-09",
  "output": {
    "width": 1080,
    "height": 1920,
    "fps": 30,
    "duration_seconds": 60,
    "final_path": "output/final_stardew_promo.mp4"
  },
  "style": {
    "visual_world": "Stardew-like pixel farming game screenshot",
    "camera": "top-down or slight top-down farming game view",
    "ui": "wooden pixel panels, cream content area, inventory slots, task board",
    "font": "Zpix.ttf",
    "subtitle_fill": "#FFFDF0",
    "subtitle_stroke": "#000000",
    "subtitle_stroke_width": 3,
    "subtitle_stroke_directions": [
      "up",
      "down",
      "left",
      "right",
      "left_up",
      "right_up",
      "left_down",
      "right_down"
    ]
  },
  "assets": {
    "reference_material_dir": "/Users/mellisa/Desktop/星露谷元素素材",
    "base_scene": "/Users/mellisa/Desktop/星露谷元素素材/IMG_3791.jpg",
    "font": "Zpix.ttf",
    "optional_bgm": "assets/audio/stardew_overture.mp3",
    "generated_bgm": "output/audio/generated_pixel_farm_bgm.wav",
    "sfx_dir": "output/audio/sfx"
  },
  "audio": {
    "voice_engine": "gTTS",
    "language": "zh-CN",
    "target_voice_note": "如果 Edge-TTS 可用，优先 zh-CN-YunxiNeural，rate +5%。如果连不上，使用 gTTS 生成自然中文口播。",
    "bgm_volume": 0.15,
    "voice_volume": 1.0,
    "sfx_volume": 0.35
  },
  "segments": [
    {
      "id": 1,
      "time_start_ms": 0,
      "time_end_ms": 7000,
      "scene_type": "cover_board",
      "title": "刷岗位刷到头大？",
      "subtitle": "先别硬扛",
      "body": "这条视频帮你把一堆岗位，整理成能直接投的求职手册。",
      "voiceover_script": "刷岗位刷到头大？先别硬扛。这条视频帮你把一堆岗位，整理成能直接投的求职手册。",
      "sfx": "cover"
    },
    {
      "id": 2,
      "time_start_ms": 7000,
      "time_end_ms": 15000,
      "scene_type": "task_board",
      "title": "岗位名字都差不多",
      "body": "城市、要求、链接散得到处都是，人眼看久了就会乱。",
      "voiceover_script": "岗位名字看着都差不多，城市、要求、链接散得到处都是。人眼看久了，真的会乱。",
      "sfx": "page"
    },
    {
      "id": 3,
      "time_start_ms": 15000,
      "time_end_ms": 26000,
      "scene_type": "inventory_input",
      "title": "把简历和网址丢进去",
      "body": "不用来回开十几个页面，它会先帮你收好，再按你的条件筛。",
      "voiceover_script": "把简历和招聘网址丢进去，不用来回开十几个页面。AI 会先帮你收好，再按条件慢慢筛。",
      "sfx": "item"
    },
    {
      "id": 4,
      "time_start_ms": 26000,
      "time_end_ms": 38000,
      "scene_type": "score_unlock",
      "title": "自动匹配打分",
      "body": "合适的留下，不合适的先放下。投递顺序一下就清楚了。",
      "voiceover_script": "接下来自动匹配打分。合适的留下，不合适的先放下，投递顺序一下就清楚了。",
      "sfx": "score"
    },
    {
      "id": 5,
      "time_start_ms": 38000,
      "time_end_ms": 50000,
      "scene_type": "harvest_manual",
      "title": "最后直接看手册",
      "body": "哪个岗位更适合你，投递入口在哪，打开就能看明白。",
      "voiceover_script": "最后直接看手册。哪个岗位更适合你，投递入口在哪，打开就能看明白。",
      "sfx": "harvest"
    },
    {
      "id": 6,
      "time_start_ms": 50000,
      "time_end_ms": 60000,
      "scene_type": "ending_board",
      "title": "job-hunter 已开源",
      "body": "如果你也找工作找得头大，可以直接拿去用。",
      "voiceover_script": "这个 job-hunter 已经开源。如果你也找工作找得头大，可以直接拿去用。",
      "sfx": "success"
    }
  ]
}
```

## 生成流程

| 顺序 | 做什么 | 输入 | 输出 |
|---|---|---|---|
| 1 | 读取配置 | `video_pipeline_config.json` 或上面的配置块 | 章节、口播、时间轴 |
| 2 | 生成口播 | `segments[].voiceover_script` | `output/audio/vo_1.mp3` 到 `vo_6.mp3` |
| 3 | 生成提示音 | `segments[].sfx` | `output/audio/sfx/*.wav` |
| 4 | 准备背景音 | 本地 BGM 或生成像素轻背景音 | 混音素材 |
| 5 | 生成画面帧 | 星露谷场景 + 模块化 UI + 文案 | `output/real_stardew_frames/frame_00000.png` |
| 6 | 混合音频 | 口播 + BGM + SFX | `output/mixed_voiceover.m4a` |
| 7 | 导出视频 | 画面帧 + 混音 | `output/final_stardew_promo.mp4` |
| 8 | 抽帧检查 | 成片 | 1 秒、31 秒、54 秒预览图 |

## 一键运行入口

在项目根目录运行：

```bash
.venv/bin/pip install -r requirements.txt
.venv/bin/python build_video.py
```

如果只想重新合成画面和视频，不重新生成语音：

```bash
.venv/bin/python build_video.py --skip-tts
```

## 迁移到新项目时需要带走什么

| 文件或目录 | 必须 | 说明 |
|---|---|---|
| 这份模板文件 | 是 | 未来 Codex 先读它 |
| `build_video.py` | 是 | 一键生成脚本 |
| `video_pipeline_config.json` | 是 | 每条视频的时间轴和口播 |
| `Zpix.ttf` | 是 | 像素字体 |
| `requirements.txt` | 是 | Python 依赖 |
| `assets/audio/stardew_overture.mp3` | 否 | 有就用作 BGM，没有就生成像素轻背景音 |
| 星露谷元素素材目录 | 是 | 提供实机参考和可复用模块 |

## 生成前检查

| 检查项 | 通过标准 |
|---|---|
| 封面 | 第一眼能看懂痛点，不用读正文 |
| 风格 | 像游戏实机，不像海报 |
| 字幕 | 大、清楚、硬边、不发虚 |
| 内容 | 人话、短句、少术语 |
| 画面 | 每个板块都有变化，不是静态卡片 |
| 音频 | 口播跟字幕同步，章节切换有提示音 |
| 成片 | 60 秒、1080x1920、30fps、H.264、AAC |

## Codex 调用提示词

以后要让 Codex 使用这个模板，可以直接发：

```text
请读取 /Users/mellisa/Desktop/codex-work1/宝宝AI星露谷视频模板.md，
并按里面的规则生成一条宝宝AI星露谷实机风视频。
要求先生成 3 张关键预览帧给我看，再完整生成最终 MP4。
风格必须像游戏实机画面，不要普通像素海报，不要黑色背景。
```

如果是新的主题，把最后再补一句：

```text
这次主题是：这里写主题。
目标用户是：这里写用户。
我想表达的是：这里写核心内容。
```

## 和宝宝AI skill 链接的方法

推荐做法：把这份文件软链接到宝宝AI skill 的 references 目录，让宝宝AI skill 以后能直接读到它。

链接命令：

```bash
mkdir -p /Users/mellisa/.codex/skills/baobao-ai/references
ln -sf /Users/mellisa/Desktop/codex-work1/宝宝AI星露谷视频模板.md /Users/mellisa/.codex/skills/baobao-ai/references/stardew-video-template.md
```

然后在 `/Users/mellisa/.codex/skills/baobao-ai/SKILL.md` 的“固定视觉母版”附近补一句：

```text
如果任务涉及星露谷风格视频模板，请先读取 references/stardew-video-template.md。
```

以后只要说“按宝宝AI星露谷视频模板生成”，Codex 就能从这个文件开始，不用重新解释一遍。

## 最小质量线

只要生成结果出现下面任意一种情况，就要返工：

| 问题 | 处理 |
|---|---|
| 看起来像普通像素海报 | 回到真实农场场景，减少平面卡片 |
| 文字太小 | 放大标题，减少句子数量 |
| 画面太空 | 增加任务板、背包格子、状态条、作物和路径 |
| 内容太像广告 | 改成朋友说话，不喊口号 |
| 只有字幕没有画面变化 | 每个章节加 UI 弹出、提示音和状态变化 |
| 干货看不懂 | 保留真实界面或真实流程，不重画核心操作 |

## 当前项目实测结论

本模板已经在 `job-hunter` 项目里跑通过。

| 项目 | 结果 |
|---|---|
| 成片路径 | `output/final_stardew_promo.mp4` |
| 成片时长 | 60 秒 |
| 画面 | 1080x1920，30fps |
| 编码 | H.264 |
| 音频 | AAC |
| 预览帧 | `output/final_check_01s.png`、`output/final_check_31s.png`、`output/final_check_54s.png` |

已知决定：

- Edge-TTS 在本机连不上微软语音服务时，不要卡死流程，可以改用 gTTS。
- Mac M 系列硬件编码如果创建会话失败，直接用稳定的 H.264 软件编码出片。
- 星露谷风格不能只靠字幕和木框，必须先有真实农场场景。
