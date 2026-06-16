#!/usr/bin/env python3
"""
6 cards — custom pixel-art Stardew-style backgrounds (code-generated, no external images)
+ minimal text per the original template format
"""
from PIL import Image, ImageDraw, ImageFont
import os, math

OUT = '/sessions/determined-awesome-brown/mnt/job-hunter/output/carousel_v4'
os.makedirs(OUT, exist_ok=True)

FONT = '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
F72 = ImageFont.truetype(FONT, 72)
F48 = ImageFont.truetype(FONT, 48)
F36 = ImageFont.truetype(FONT, 36)
F28 = ImageFont.truetype(FONT, 28)
F22 = ImageFont.truetype(FONT, 22)

W, H = 1080, 1440

# ---- Stardew Pixel Color Palette ----
SKY_TOP    = (120, 184, 224)
SKY_BOT    = (180, 220, 240)
GRASS_MAIN = (92, 138, 75)
GRASS_LT   = (120, 168, 100)
GRASS_DK   = (72, 110, 58)
DIRT       = (162, 132, 82)
DIRT_DK    = (130, 105, 65)
BROWN      = (139, 107, 74)
BROWN_LT   = (196, 168, 122)
CREAM      = (245, 237, 214)
INK        = (42, 30, 16)
GOLD       = (240, 192, 80)
WHITE      = (250, 246, 238)
DARK_GREEN = (56, 90, 48)

def draw_sky(draw):
    """Simple gradient sky."""
    for y in range(420):
        r = int(SKY_TOP[0] + (SKY_BOT[0]-SKY_TOP[0]) * y/420)
        g = int(SKY_TOP[1] + (SKY_BOT[1]-SKY_TOP[1]) * y/420)
        b = int(SKY_TOP[2] + (SKY_BOT[2]-SKY_TOP[2]) * y/420)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

def draw_ground(draw, y_base):
    """Grass + dirt stripes."""
    # Main grass
    draw.rectangle([0, y_base, W, H], fill=GRASS_MAIN)
    # Grass texture stripes
    for y in range(y_base, H, 8):
        shade = GRASS_LT if (y//8) % 2 == 0 else GRASS_DK
        draw.line([(0, y), (W, y)], fill=shade, width=3)

def draw_tree(draw, cx, cy, scale=1.0):
    """Pixel tree: brown trunk + green triangle top."""
    tw = int(16 * scale)
    th = int(50 * scale)
    # Trunk
    draw.rectangle([cx-tw//2, cy-th, cx+tw//2, cy], fill=BROWN)
    # Top (triangle layers)
    for i in range(4):
        layer_y = cy - th - i * int(24*scale)
        layer_w = int((40 + i*20) * scale)
        draw.polygon([(cx-layer_w//2, layer_y+int(24*scale)),
                       (cx+layer_w//2, layer_y+int(24*scale)),
                       (cx, layer_y)], fill=DARK_GREEN)

def draw_grass_patches(draw, y_base):
    """Small grass detail tufts."""
    for x in range(40, W, 60):
        y = y_base + 20 + (x * 7 % 60)
        draw.ellipse([x-6, y-4, x+6, y+4], fill=GRASS_LT)

def draw_sun(draw):
    """Pixel sun."""
    cx, cy = 880, 100
    r = 40
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=GOLD)
    # glow
    draw.ellipse([cx-r-10, cy-r-10, cx+r+10, cy+r+10], fill=(240, 192, 80, 60))

def draw_fence(draw, y):
    """Simple fence line."""
    for x in range(20, W-20, 50):
        draw.rectangle([x-3, y-20, x+3, y], fill=BROWN)
        draw.rectangle([x-15, y-8, x+15, y-4], fill=BROWN_LT)

def draw_farmer(draw, x, y):
    """Simple farmer character (pixel style)."""
    # body
    draw.rectangle([x-12, y-30, x+12, y], fill=INK)
    # head
    draw.ellipse([x-10, y-50, x+10, y-30], fill=(255, 220, 180))
    # hat
    draw.ellipse([x-14, y-56, x+14, y-44], fill=GOLD)

def txt(d, text, y, font=F36, color=WHITE, max_w=960, center=True):
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

# ==================== BUILD SCENE ====================
def stardew_scene():
    img = Image.new('RGB', (W, H), SKY_TOP)
    d = ImageDraw.Draw(img)
    draw_sky(d)
    draw_sun(d)
    draw_ground(d, 380)
    draw_grass_patches(d, 380)
    draw_fence(d, 800)
    draw_farmer(d, 220, 780)
    draw_tree(d, 60, 360, 1.2)
    draw_tree(d, 980, 340, 1.0)
    draw_tree(d, 520, 350, 1.4)
    return img

def darken(img, strength=0.35):
    over = Image.new('RGB', img.size, (0, 0, 0))
    return Image.blend(img, over, strength)

# ============================================================
print("1/6 Cover")
img = darken(stardew_scene(), 0.4)
d = ImageDraw.Draw(img)

txt(d, "我做了个 job-hunter skill", 600, F48, GOLD)
txt(d, "投简历像种地一样简单", 700, F36)

bb = d.textbbox((0, 0), "@ 宝宝AI", font=F28)
x = (W - (bb[2]-bb[0])) // 2
d.text((x, H-100), "@ 宝宝AI", fill=GOLD, font=F28)

img.save(f"{OUT}/01_cover.png")

# ============================================================
print("2/6 Problem")
img = darken(stardew_scene(), 0.45)
d = ImageDraw.Draw(img)

txt(d, "我做了个 job-hunter", 500, F48, GOLD)
txt(d, "求职岗位爬取+简历匹配+PDF投递手册", 600, F36)
txt(d, "一条命令跑完三阶段", 690, F28)

img.save(f"{OUT}/02_intro.png")

# ============================================================
print("3/6 How it works")
img = stardew_scene()
d = ImageDraw.Draw(img)

# Semi-transparent overlay for text area
d.rectangle([0, 300, W, 720], fill=(250, 246, 238, 220))

txt(d, "Crawl → Match → Report", 400, F48, INK)
txt(d, "爬招聘网站 → AI匹配简历 → 生成PDF", 500, F36, INK)
txt(d, "支持内推链接 · AI/关键词双模式", 600, F28, BROWN)

img.save(f"{OUT}/03_flow.png")

# ============================================================
print("4/6 Demo")
img = darken(stardew_scene(), 0.4)
d = ImageDraw.Draw(img)

txt(d, "用法", 200, F48, GOLD)

# Terminal
tx, ty, tw, th = 100, 320, 880, 500
d.rounded_rectangle([tx, ty, tx+tw, ty+th], radius=12, fill=(26,26,46), outline=INK, width=3)

lines = [
    ((136,136,136), "# 一条命令"),
    ((255,204,0),   "$ python3 run.py \\"),
    ((136,136,136), "  --url \"<招聘网站URL>\" \\"),
    ((136,136,136), "  --resume ./resume.pdf \\"),
    ((136,136,136), "  --cities \"杭州,上海\""),
    (None, ""),
    ((0,255,136),   "[Crawl]  ✅ 岗位抓取完成"),
    ((0,255,136),   "[Match]  ✅ AI匹配完成"),
    ((176,176,255), "[Report] ✅ PDF已生成"),
]
for i, (c, t) in enumerate(lines):
    if c:
        d.text((tx+25, ty+20+i*42), t, fill=c, font=F22)

img.save(f"{OUT}/04_demo.png")

# ============================================================
print("5/6 Output")
img = stardew_scene()
d = ImageDraw.Draw(img)

d.rectangle([0, 250, W, 680], fill=(250, 246, 238, 220))

txt(d, "投递手册示例", 320, F48, INK)

jobs = [
    "AI产品运营实习生 · 杭州 · 字节 · 140分",
    "Prompt工程实习生 · 杭州 · 字节 · 138分",
    "数据运营实习生 · 杭州 · 字节 · 126分",
    "AIGC内容运营 · 上海 · 字节 · 101分",
]
for i, j in enumerate(jobs):
    txt(d, j, 430 + i*55, F28, INK)

img.save(f"{OUT}/05_output.png")

# ============================================================
print("6/6 End")
img = darken(stardew_scene(), 0.4)
d = ImageDraw.Draw(img)

txt(d, "我做了个 job-hunter", 580, F48, GOLD)
txt(d, "开源 · 直接可用", 680, F36)

bb = d.textbbox((0, 0), "@ 宝宝AI", font=F28)
x = (W - (bb[2]-bb[0])) // 2
d.text((x, H-100), "@ 宝宝AI", fill=GOLD, font=F28)

img.save(f"{OUT}/06_end.png")

print(f"\nDone → {OUT}/")
print("1080x1440 x 6 cards, code-generated Stardew scenes + simple text")
