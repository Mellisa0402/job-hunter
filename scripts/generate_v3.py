#!/usr/bin/env python3
"""
6-card Xiaohongshu carousel — clean solid backgrounds with Stardew palette
No video frames, no UI, no CTA. Just: 我开源了一个 XXX
"""
from PIL import Image, ImageDraw, ImageFont
import os, math, random

OUT = '/sessions/determined-awesome-brown/mnt/job-hunter/output/carousel_v3'
os.makedirs(OUT, exist_ok=True)

FONT = '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
F72 = ImageFont.truetype(FONT, 72)
F48 = ImageFont.truetype(FONT, 48)
F36 = ImageFont.truetype(FONT, 36)
F28 = ImageFont.truetype(FONT, 28)
F22 = ImageFont.truetype(FONT, 22)

W, H = 1080, 1440

# Stardew-inspired palette
BG_COLORS = [
    (162, 189, 135),  # soft grass green
    (186, 170, 126),  # warm sand
    (235, 208, 148),  # golden cream
    (140, 175, 140),  # sage green
    (215, 185, 135),  # warm wheat
    (170, 155, 120),  # muted earth
]

def make_bg(color, stars=0):
    """Clean solid background with optional subtle star dots."""
    img = Image.new('RGB', (W, H), color)
    if stars:
        d = ImageDraw.Draw(img)
        for _ in range(stars):
            x = random.randint(0, W)
            y = random.randint(0, H)
            r = random.choice([2, 3, 4])
            alpha = random.randint(40, 120)
            c = (255, 255, 255)
            d.ellipse([x-r, y-r, x+r, y+r], fill=(255, 255, 255, alpha))
    return img

def txt(d, text, y, font=F36, color=(250, 246, 238), max_w=960, center=True):
    fs = font.size
    cpl = int(max_w / (fs * 0.65))
    lines = [text[i:i+max(1,cpl)] for i in range(0, len(text), max(1,cpl))]
    total_h = len(lines) * int(fs * 1.6)
    sy = y - total_h // 2
    for line in lines:
        bb = d.textbbox((0, 0), line, font=font)
        lw = bb[2] - bb[0]
        x = (W - lw) // 2 if center else 80
        d.text((x, sy), line, fill=color, font=font)
        sy += int(fs * 1.6)

# ---------- Card 1: Cover ----------
print("1/6")
img = make_bg(BG_COLORS[0], stars=80)
d = ImageDraw.Draw(img)

txt(d, "我开源了", 560, F36, (42, 30, 16))
txt(d, "job-hunter", 640, F72, (240, 192, 80))
txt(d, "投简历像种地一样简单", 740, F36, (42, 30, 16))

bb = d.textbbox((0, 0), "@ 宝宝AI", font=F28)
x = (W - (bb[2]-bb[0])) // 2
d.text((x, H-100), "@ 宝宝AI", fill=(42, 30, 16), font=F28)

img.save(f"{OUT}/01_cover.png")

# ---------- Card 2: What it does ----------
print("2/6")
img = make_bg(BG_COLORS[1], stars=40)
d = ImageDraw.Draw(img)

txt(d, "我开源了一个", 240, F36, (42, 30, 16))
txt(d, "求职岗位自动爬取+匹配+出报告", 320, F48, (240, 192, 80))
txt(d, "的三阶段流水线工具", 400, F48, (240, 192, 80))

txt(d, "输入招聘网站链接 + 你的简历", 600, F28, (42, 30, 16))
txt(d, "就能拿到一份带链接的投递手册", 660, F28, (42, 30, 16))
txt(d, "支持内推链接 / 任意招聘网站", 740, F28, (42, 30, 16))
txt(d, "AI 匹配 / 关键词匹配 双模式", 800, F28, (42, 30, 16))

img.save(f"{OUT}/02_what.png")

# ---------- Card 3: 3 steps ----------
print("3/6")
img = make_bg(BG_COLORS[2], stars=30)
d = ImageDraw.Draw(img)

txt(d, "三条命令就是全部操作", 180, F36, (42, 30, 16))

steps = [
    ("Crawl", "爬取招聘网站岗位"),
    ("Match", "简历匹配打分"),
    ("Report", "生成 PDF 投递手册"),
]
by = 340
for i, (title, desc) in enumerate(steps):
    d.rounded_rectangle([140, by+i*220, 940, by+180+i*220], radius=12, fill=(250,246,238), outline=(42,30,16), width=3)
    txt(d, title, by+45+i*220, F36, (92, 138, 75))
    txt(d, desc, by+100+i*220, F28, (122, 106, 90))

img.save(f"{OUT}/03_steps.png")

# ---------- Card 4: Demo terminal ----------
print("4/6")
img = make_bg(BG_COLORS[3], stars=0)
d = ImageDraw.Draw(img)

txt(d, "使用方式", 160, F36, (42, 30, 16))

# Terminal
tx, ty = 100, 300
tw, th = 880, 500
d.rounded_rectangle([tx, ty, tx+tw, ty+th], radius=12, fill=(26,26,46), outline=(42,30,16), width=4)

lines = [
    ((136,136,136), "# 一条命令跑完"),
    ((255,204,0),   "$ python3 run.py \\"),
    ((136,136,136), "  --url \"<招聘网站URL>\" \\"),
    ((136,136,136), "  --resume ./resume.pdf \\"),
    ((136,136,136), "  --cities \"杭州,上海\""),
    (None, ""),
    ((0, 255, 136),  "[Crawl]  ✅ 199 个岗位抓取完成"),
    ((0, 255, 136),  "[Match]  ✅ AI 匹配完成"),
    ((176,176,255),  "[Report] ✅ PDF 投递手册已生成"),
]
for i, (c, t) in enumerate(lines):
    if c:
        d.text((tx+25, ty+20+i*42), t, fill=c, font=F22)

txt(d, "Python 实现，开源 MIT 协议", 900, F28, (42, 30, 16))

img.save(f"{OUT}/04_demo.png")

# ---------- Card 5: Output ----------
print("5/6")
img = make_bg(BG_COLORS[4], stars=0)
d = ImageDraw.Draw(img)

txt(d, "生成效果", 180, F36, (42, 30, 16))

# PDF mock
px, py = 100, 300
pw, ph = 880, 480
d.rounded_rectangle([px, py, px+pw, py+ph], radius=12, fill=(250,246,238), outline=(42,30,16), width=3)
d.rounded_rectangle([px+15, py+15, px+pw-15, py+50], radius=6, fill=(42,30,16))
d.text((px+30, py+27), "求职投递手册", fill=(245,237,214), font=F22)

jobs = [
    ("AI 产品运营实习生 · 杭州 · 字节 · 140 分"),
    ("Prompt 工程实习生 · 杭州 · 字节 · 138 分"),
    ("数据运营实习生 · 杭州 · 字节 · 126 分"),
    ("AIGC 内容运营 · 上海 · 字节 · 101 分"),
]
for i, j in enumerate(jobs):
    d.text((px+30, py+80+i*95), j, fill=(42,30,16), font=F22)
    if i < len(jobs)-1:
        d.line([(px+30, py+80+(i+1)*95-20), (px+pw-30, py+80+(i+1)*95-20)], fill=(232,220,196), width=2)

txt(d, "每条岗位含可点击投递链接，按城市分组", 860, F28, (42, 30, 16))

img.save(f"{OUT}/05_output.png")

# ---------- Card 6: End ----------
print("6/6")
img = make_bg(BG_COLORS[5], stars=60)
d = ImageDraw.Draw(img)

txt(d, "我开源了", 520, F36, (42, 30, 16))
txt(d, "job-hunter", 600, F72, (240, 192, 80))
txt(d, "求职爬取+匹配+PDF 生成工具", 710, F36, (42, 30, 16))

txt(d, "开源 MIT · github.com/baobaoai/job-hunter", 880, F28, (42, 30, 16))

bb = d.textbbox((0, 0), "@ 宝宝AI", font=F28)
x = (W - (bb[2]-bb[0])) // 2
d.text((x, H-100), "@ 宝宝AI", fill=(42, 30, 16), font=F28)

img.save(f"{OUT}/06_end.png")

print(f"\nDone → {OUT}/")
print("1080x1440 x 6 cards")
