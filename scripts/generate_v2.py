#!/usr/bin/env python3
"""
6-card Xiaohongshu carousel — Stardew bg, minimal text, no CTA
Just: "我开源了一个 XXX"
"""
from PIL import Image, ImageDraw, ImageFont
import os, math

FRAMES_DIR = '/sessions/determined-awesome-brown/mnt/job-hunter/output/real_stardew_frames'
OUT = '/sessions/determined-awesome-brown/mnt/job-hunter/output/carousel_v2'
os.makedirs(OUT, exist_ok=True)

FONT = '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
F72 = ImageFont.truetype(FONT, 72)
F48 = ImageFont.truetype(FONT, 48)
F36 = ImageFont.truetype(FONT, 36)
F28 = ImageFont.truetype(FONT, 28)
F22 = ImageFont.truetype(FONT, 22)

W, H = 1080, 1440

def frame(index):
    frames = sorted(os.listdir(FRAMES_DIR))
    idx = min(index * 200, len(frames) - 1)
    img = Image.open(os.path.join(FRAMES_DIR, frames[idx])).convert('RGB')
    h_off = (img.height - H) // 2
    return img.crop((0, h_off, W, h_off + H))

def dim(img, strength=0.35):
    """Just a simple dark overlay, nothing fancy."""
    over = Image.new('RGB', img.size, (0, 0, 0))
    return Image.blend(img, over, strength)

def txt(d, text, y, font=F48, color=(250, 246, 238), max_w=960, center=True):
    """Draw text, auto-wrap by CJK chars."""
    fs = font.size
    if font.size == 72:
        fs = 72
    elif font.size == 48:
        fs = 48
    elif font.size == 36:
        fs = 36
    elif font.size == 28:
        fs = 28
    else:
        fs = 22

    cpl = int(max_w / (fs * 0.65))
    lines = []
    for i in range(0, len(text), max(1, cpl)):
        lines.append(text[i:i+cpl])

    total_h = len(lines) * int(fs * 1.6)
    sy = y - total_h // 2

    for line in lines:
        bb = d.textbbox((0, 0), line, font=font)
        lw = bb[2] - bb[0]
        if center:
            x = (W - lw) // 2
        else:
            x = 80
        d.text((x, sy), line, fill=color, font=font)
        sy += int(fs * 1.6)

# ---------- Card 1: Cover ----------
print("1/6")
bg = dim(frame(0))
d = ImageDraw.Draw(bg)

txt(d, "我开源了一个", 480, F36, (196, 168, 122))
txt(d, "job-hunter", 560, F72, (240, 192, 80))
txt(d, "skill 投简历像种地一样简单", 660, F36)

# bottom: @宝宝AI
bb = d.textbbox((0, 0), "@ 宝宝AI", font=F28)
x = (W - (bb[2]-bb[0])) // 2
d.text((x, H-120), "@ 宝宝AI", fill=(240, 192, 80), font=F28)

bg.save(f"{OUT}/01_cover.png")

# ---------- Card 2: Problem ----------
print("2/6")
bg = dim(frame(1))
d = ImageDraw.Draw(bg)

txt(d, "传统投递流程", 200, F48, (240, 192, 80))

lines = [
    "打开招聘网站 → 搜索关键词",
    "复制岗位信息 → 打开简历文件",
    "调整投递格式 → 发送简历",
    "换下一个网站 → 重复以上步骤",
]
y = 360
for l in lines:
    txt(d, l, y, F28, (200, 200, 200), max_w=900, center=False)
    y += 80

txt(d, "投完了也记不清投了哪些", 900, F28, (200, 180, 180))

bg.save(f"{OUT}/02_problem.png")

# ---------- Card 3: Solution ----------
print("3/6")
bg = dim(frame(2), 0.3)
d = ImageDraw.Draw(bg)

txt(d, "一条命令跑完整条流水线", 180, F48, (240, 192, 80))

# Three steps
steps = [("Crawl", "自动爬取\n任意招聘网站岗位"), ("Match", "AI 匹配简历\n按条件打分排序"), ("Report", "生成投递手册\nPDF 一键导出")]
bw, bh, gap = 300, 260, 20
sx = (W - (bw*3 + gap*2)) // 2

for i, (title, desc) in enumerate(steps):
    x = sx + i*(bw+gap)
    d.rounded_rectangle([x, 360, x+bw, 360+bh], radius=12, fill=(250, 246, 238), outline=(42, 30, 16), width=3)
    txt(d, title, 400, F36, (92, 138, 75), max_w=bw-40)
    txt(d, desc, 470, F22, (122, 106, 90), max_w=bw-40)
    if i < 2:
        ax = x + bw + 5
        d.text((ax, 360+bh//2-20), "→", fill=(92, 138, 75), font=F48)

# Features
txt(d, "支持内推链接 / AI+关键词双模式 / YAML 配置新网站", 760, F22, (196, 196, 196))

bg.save(f"{OUT}/03_solution.png")

# ---------- Card 4: Demo ----------
print("4/6")
bg = dim(frame(3))
d = ImageDraw.Draw(bg)

txt(d, "实机演示", 150, F48, (240, 192, 80))

# Terminal
tx, ty, tw, th = 60, 280, 960, 500
d.rounded_rectangle([tx, ty, tx+tw, ty+th], radius=12, fill=(26, 26, 46), outline=(42, 30, 16), width=4)

demo = [
    ((136,136,136), "# 一条命令跑完全流程"),
    ((255,204,0),   "$ python3 run.py \\"),
    ((136,136,136), "  --url \"<招聘网站URL>\" \\"),
    ((136,136,136), "  --resume ./resume.pdf \\"),
    ((136,136,136), "  --cities \"杭州,上海\" --mode ai"),
    (None, ""),
    ((0,255,136),   "╔══════════════════════════════╗"),
    ((0,255,136),   "║ Crawl → Match → Report       ║"),
    ((0,255,136),   "║ 199 个岗位 / 最高匹配 140 分  ║"),
    ((0,255,136),   "╚══════════════════════════════╝"),
    (None, ""),
    ((176,176,255), "[OK] 投递手册已生成"),
]
for i, (c, t) in enumerate(demo):
    if c:
        d.text((tx+20, ty+15+i*38), t, fill=c, font=F22)

# Stats
stats = [("199", "抓取"), ("140", "最高分"), ("3步", "全流程")]
for i, (n, l) in enumerate(stats):
    bx = 80 + i*340
    d.rounded_rectangle([bx, 850, bx+280, 940], radius=10, fill=(250, 246, 238), outline=(42, 30, 16), width=3)
    txt(d, n, 888, F36, (92, 138, 75))
    txt(d, l, 925, F22, (122, 106, 90))

bg.save(f"{OUT}/04_demo.png")

# ---------- Card 5: Output ----------
print("5/6")
bg = dim(frame(4), 0.3)
d = ImageDraw.Draw(bg)

txt(d, "输出效果", 150, F48, (240, 192, 80))

# PDF mock
px, py, pw, ph = 80, 300, 920, 520
d.rounded_rectangle([px, py, px+pw, py+ph], radius=12, fill=(250, 246, 238), outline=(42, 30, 16), width=3)

# Header
d.rounded_rectangle([px+15, py+15, px+pw-15, py+50], radius=6, fill=(42, 30, 16))
d.text((px+30, py+25), "求职投递手册 · job-hunter output", fill=(245, 237, 214), font=F22)

# Job rows
jobs = [
    ("AI 产品运营实习生", "杭州 · 字节跳动 · 140 分"),
    ("Prompt 工程实习生", "杭州 · 字节跳动 · 138 分"),
    ("数据运营实习生", "杭州 · 字节跳动 · 126 分"),
    ("AIGC 内容运营", "上海 · 字节跳动 · 101 分"),
]
for i, (title, meta) in enumerate(jobs):
    jy = py + 80 + i * 100
    d.text((px+30, jy), title, fill=(42, 30, 16), font=F28)
    d.text((px+30, jy+42), meta, fill=(122, 106, 90), font=F22)
    if i < len(jobs)-1:
        d.line([(px+30, jy+90), (px+pw-30, jy+90)], fill=(232, 220, 196), width=2)

txt(d, "每条岗位含可点击投递链接", 900, F22, (196, 196, 196))
txt(d, "按城市分组 / AI 标注匹配原因", 950, F22, (196, 196, 196))

bg.save(f"{OUT}/05_output.png")

# ---------- Card 6: End ----------
print("6/6")
bg = dim(frame(5))
d = ImageDraw.Draw(bg)

txt(d, "我开源了", 500, F36, (196, 168, 122))
txt(d, "job-hunter", 580, F72, (240, 192, 80))
txt(d, "一个求职岗位爬取+匹配+投递手册生成工具", 700, F36)

txt(d, "GitHub: github.com/baobaoai/job-hunter", 900, F28, (220, 220, 220))

bb = d.textbbox((0, 0), "@ 宝宝AI", font=F28)
x = (W - (bb[2]-bb[0])) // 2
d.text((x, H-120), "@ 宝宝AI", fill=(240, 192, 80), font=F28)

bg.save(f"{OUT}/06_end.png")

print(f"\nDone → {OUT}/")
print("6 cards, 1080x1440 each")
