#!/usr/bin/env python3
"""
Generate 6-card Xiaohongshu carousel: Stardew Valley backgrounds + job-hunter demo
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import os, json, math

FRAMES_DIR = '/sessions/determined-awesome-brown/mnt/job-hunter/output/real_stardew_frames'
OUTPUT_DIR = '/sessions/determined-awesome-brown/mnt/job-hunter/output/carousel'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===== Load fonts =====
FONT_HUGE = None
FONT_LARGE = None
FONT_MED = None
FONT_SMALL = None
FONT_TINY = None

# Known CJK font on this system
DROID_FONT = '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'

def find_font(size):
    """Load Droid Sans Fallback (CJK-capable)."""
    try:
        return ImageFont.truetype(DROID_FONT, size)
    except:
        try:
            return ImageFont.load_default()
        except:
            return None

# ===== Color Palette =====
SD_GOLD = (240, 192, 80)
SD_GREEN = (92, 138, 75)
SD_BROWN = (139, 107, 74)
SD_BROWN_LIGHT = (196, 168, 122)
SD_CREAM = (245, 237, 214)
SD_CREAM_DARK = (232, 220, 196)
SD_INK = (42, 30, 16)
SD_MUTED = (122, 106, 90)
SD_WHITE = (250, 246, 238)
SD_RED = (192, 64, 64)
SD_SKY = (122, 184, 224)

W, H = 1080, 1440

FONT_HUGE = find_font(72)
FONT_LARGE = find_font(48)
FONT_MED = find_font(32)
FONT_SMALL = find_font(24)
FONT_TINY = find_font(18)

def load_bg(index):
    frames = sorted(os.listdir(FRAMES_DIR))
    idx = min(index * 250, len(frames) - 1)
    path = os.path.join(FRAMES_DIR, frames[idx])
    img = Image.open(path).convert('RGB')
    h_off = (img.height - H) // 2
    return img.crop((0, h_off, W, h_off + H))

def prepare_bg(img, dark=0.4):
    overlay = Image.new('RGB', img.size, (0, 0, 0))
    img = Image.blend(img, overlay, dark)
    # Vignette
    w, h = img.size
    mask = Image.new('L', (w, h), 255)
    md = ImageDraw.Draw(mask)
    cx, cy = w//2, int(h*0.35)
    max_r = math.sqrt(cx*cx + cy*cy) * 1.1
    for y in range(h):
        for x in range(w):
            dx, dy = x - cx, y - cy
            d = math.sqrt(dx*dx + dy*dy)
            v = int(255 * (1 - min(d / max_r, 1.0) * 0.35))
            md.point((x, y), v)
    dark_img = Image.new('RGB', (w, h), (0, 0, 0))
    return Image.composite(img, dark_img, mask)

def center_text(draw, text, y, font, color=SD_WHITE, max_w=920):
    # Get font size, handling ImageFont.FreeTypeFont vs default font
    try:
        fs = font.size
    except AttributeError:
        fs = 32  # default fallback
    lines = []
    cpl = int(max_w / (fs * 0.65))
    for i in range(0, len(text), max(1, cpl)):
        lines.append(text[i:i+cpl])
    total = len(lines) * int(fs * 1.5)
    sy = y - total // 2
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=font)
        x = (W - (bb[2]-bb[0])) // 2
        draw.text((x, sy), line, fill=color, font=font)
        sy += int(fs * 1.5)

def left_text(draw, text, x, y, font, color=SD_WHITE, max_w=900):
    try:
        fs = font.size
    except AttributeError:
        fs = 32
    cpl = int(max_w / (fs * 0.65))
    for i in range(0, len(text), max(1, cpl)):
        draw.text((x, y + i*int(fs*1.5)), text[i:i+cpl], fill=color, font=font)

# ==================== CARD 1: COVER ====================
print("Card 1/6: Cover...")
bg = prepare_bg(load_bg(0))
d = ImageDraw.Draw(bg)

# Badge
d.rounded_rectangle([W//2-180, 100, W//2+180, 160], radius=10, fill=SD_INK, outline=SD_GOLD, width=4)
center_text(d, "✦  NEW SKILL  ✦", 130, FONT_SMALL, SD_GOLD)

center_text(d, "我做了个", 360, FONT_MED, SD_CREAM)
center_text(d, "job-hunter", 460, FONT_HUGE, SD_GOLD)
center_text(d, "skill", 540, FONT_MED, SD_CREAM)

# Divider
for i in range(8):
    x = W//2 - 160 + i * 40
    d.rectangle([x, 610, x+24, 618], fill=SD_GOLD if i%2==0 else SD_BROWN)

center_text(d, "投简历像种地一样简单", 700, FONT_LARGE, SD_CREAM)
center_text(d, "💻  🔍  📄  🌾", 820, FONT_MED, SD_CREAM)

# Account
d.rounded_rectangle([W//2-140, H-140, W//2+140, H-70], radius=10, fill=SD_GOLD, outline=SD_INK, width=4)
center_text(d, "@ 宝宝AI", H-108, FONT_MED, SD_INK)

bg.save(f'{OUTPUT_DIR}/01_cover.png')

# ==================== CARD 2: PAIN ====================
print("Card 2/6: Pain...")
bg = prepare_bg(load_bg(1), 0.45)
d = ImageDraw.Draw(bg)

d.text((60, 60), "⚡", fill=SD_GOLD, font=FONT_HUGE)
left_text(d, "找工作比种地还累？", 60, 170, FONT_LARGE, SD_GOLD)

# Terminal
tx, ty, tw, th = 60, 320, 960, 480
d.rounded_rectangle([tx, ty, tx+tw, ty+th], radius=14, fill=(26,26,46), outline=SD_INK, width=4)
lines = [
    ((136,136,136), "# 传统求职流程"),
    ((200,200,255), "❌ 打开 5 个招聘网站 → 手动搜"),
    ((200,200,255), "❌ 复制岗位 → 打开简历 → 投递"),
    ((200,200,255), "❌ 换下一个网站 → 重复"),
    (None, ""),
    ((255,68,68),   "✖ 今天有效投递：3 个"),
    ((255,68,68),   "✖ 哪个岗位投过了？记不清了"),
]
for i, (c, t) in enumerate(lines):
    if c:
        d.text((tx+25, ty+25+i*48), t, fill=c, font=FONT_SMALL)

left_text(d, "一季种完了，offer 还没发芽 🌱", 60, 860, FONT_MED, SD_CREAM)
center_text(d, "👇  试试自动收割", 1100, FONT_SMALL, SD_GOLD)

bg.save(f'{OUTPUT_DIR}/02_pain.png')

# ==================== CARD 3: SOLUTION ====================
print("Card 3/6: Solution...")
bg = prepare_bg(load_bg(2))
d = ImageDraw.Draw(bg)

d.text((60, 60), "🛠️", fill=SD_GOLD, font=FONT_HUGE)
left_text(d, "一条命令 · 全自动流水线", 60, 170, FONT_LARGE, SD_GOLD)

# 3-step pipeline
bw, bh = 280, 280
gap = 30
tw = bw*3 + gap*2
sx = (W - tw)//2
by = 340

steps = [
    ("01", "🌾 播种", "任意招聘网站\nPlaywright 自动\n爬取全部岗位"),
    ("02", "🌱 筛选", "AI 语义匹配简历\n按城市/类型\n自动打分排序"),
    ("03", "🧺 收获", "一键生成 PDF\n含可点击链接\n直接投递"),
]

for i, (num, title, desc) in enumerate(steps):
    x = sx + i*(bw+gap)
    d.rounded_rectangle([x, by, x+bw, by+bh], radius=14, fill=SD_WHITE, outline=SD_INK, width=4)
    d.text((x+20, by+15), num, fill=SD_GOLD, font=FONT_LARGE)
    d.text((x+20, by+85), title, fill=SD_INK, font=FONT_MED)
    left_text(d, desc, x+20, by+145, FONT_SMALL, SD_MUTED, max_w=240)
    if i < 2:
        ax = x+bw+5
        d.text((ax, by+bh//2-25), "→", fill=SD_GREEN, font=FONT_LARGE)

# Features
bullets = [
    "✅ 支持内推链接带 token 爬取",
    "✅ AI / 关键词双匹配模式",
    "✅ 新网站 YAML 配置即用",
]
for i, b in enumerate(bullets):
    left_text(d, b, 60, 700+i*50, FONT_SMALL, SD_CREAM)

bg.save(f'{OUTPUT_DIR}/03_solution.png')

# ==================== CARD 4: REAL DEMO ====================
print("Card 4/6: Real demo...")
bg = prepare_bg(load_bg(3), 0.45)
d = ImageDraw.Draw(bg)

d.text((60, 60), "💻", fill=SD_GOLD, font=FONT_HUGE)
left_text(d, "实机演示 · 一条命令跑完", 60, 170, FONT_LARGE, SD_GOLD)

# Terminal
tx, ty, tw, th = 40, 300, 1000, 560
d.rounded_rectangle([tx, ty, tx+tw, ty+th], radius=14, fill=(26,26,46), outline=SD_INK, width=4)
demo = [
    ((136,136,136), "# 一条命令跑完全流程"),
    ((255,204,0),   "$ python3 run.py \\"),
    ((136,136,136), "  --url \"https://jobs.bytedance.com/...\" \\"),
    ((136,136,136), "  --resume ./resume.pdf \\"),
    ((136,136,136), "  --cities \"杭州,上海\" --mode ai"),
    (None,          ""),
    ((0,255,136),   "╔══════════════════════════════╗"),
    ((0,255,136),   "║ job-hunter · Crawl→Match→Report ║"),
    ((0,255,136),   "║ 🎯 杭州 · 195 个岗位            ║"),
    ((0,255,136),   "║ 🎯 上海 · 4 个岗位             ║"),
    ((0,255,136),   "╚══════════════════════════════╝"),
    (None,          ""),
    ((176,176,255), "[Crawl] ✅ 抓取完成：199 个岗位"),
    ((176,176,255), "[Match] ✅ AI 匹配完成，最高 140 分"),
    ((176,176,255), "[Report] ✅ PDF 投递手册已生成"),
]
for i, (c, t) in enumerate(demo):
    if c:
        d.text((tx+20, ty+15+i*34), t, fill=c, font=FONT_TINY)

# Bottom stats
stats = [("199", "抓取岗位"), ("140分", "最高匹配"), ("📄", "PDF手册")]
for i, (n, l) in enumerate(stats):
    bx = 80 + i*340
    d.rounded_rectangle([bx, 920, bx+280, 1020], radius=12, fill=SD_WHITE, outline=SD_INK, width=3)
    center_text(d, n, 955, FONT_MED, SD_GREEN)
    center_text(d, l, 1010, FONT_TINY, SD_MUTED)

bg.save(f'{OUTPUT_DIR}/04_demo.png')

# ==================== CARD 5: PDF PREVIEW ====================
print("Card 5/6: PDF preview...")
bg = prepare_bg(load_bg(4))
d = ImageDraw.Draw(bg)

d.text((60, 60), "📄", fill=SD_GOLD, font=FONT_HUGE)
left_text(d, "输出效果 · 直接投递", 60, 170, FONT_LARGE, SD_GOLD)

# PDF mock
px, py, pw, ph = 60, 310, 960, 760
d.rounded_rectangle([px, py, px+pw, py+ph], radius=14, fill=SD_WHITE, outline=SD_INK, width=4)

# Header
d.rounded_rectangle([px+16, py+16, px+pw-16, py+56], radius=8, fill=SD_INK)
d.text((px+35, py+28), "JOB HUNTER PLAYBOOK · 求职投递手册", fill=SD_CREAM, font=FONT_TINY)

# Chips
chips = [("优先投递 183", SD_GREEN), ("平均匹配 92分", SD_BROWN), ("城市 3", SD_GOLD)]
cx = px + 30
for label, color in chips:
    d.rounded_rectangle([cx, py+76, cx+170, py+108], radius=8, fill=color)
    d.text((cx+14, py+84), label, fill=SD_WHITE, font=FONT_TINY)
    cx += 190

# Jobs
jobs = [
    ("#1  AI 产品运营实习生", "杭州 · 字节跳动", "★★★★  140分"),
    ("#2  Prompt 工程实习生", "杭州 · 字节跳动", "★★★★  138分"),
    ("#3  数据运营实习生", "杭州 · 字节跳动", "★★★  126分"),
    ("#4  AIGC 内容运营", "上海 · 字节跳动", "★★★  101分"),
    ("#5  AI 训练数据实习生", "杭州 · 字节跳动", "★★★   98分"),
]
for i, (title, meta, score) in enumerate(jobs):
    jy = py + 140 + i * 106
    d.text((px+30, jy), title, fill=SD_INK, font=FONT_SMALL)
    d.text((px+30, jy+42), meta, fill=SD_MUTED, font=FONT_TINY)
    d.rounded_rectangle([px+680, jy+4, px+920, jy+36], radius=8, fill=SD_GREEN)
    d.text((px+695, jy+10), score, fill=SD_WHITE, font=FONT_TINY)
    if i < len(jobs)-1:
        d.line([(px+30, jy+100), (px+pw-30, jy+100)], fill=SD_CREAM_DARK, width=2)

# Bottom features
left_text(d, "📌 每条岗位含可点击投递链接", 60, 1140, FONT_SMALL, SD_CREAM)
left_text(d, "📌 AI 分析匹配原因 + 按城市/分数分组", 60, 1190, FONT_SMALL, SD_CREAM)
left_text(d, "📌 附带投递节奏建议", 60, 1240, FONT_SMALL, SD_CREAM)

bg.save(f'{OUTPUT_DIR}/05_pdf.png')

# ==================== CARD 6: CTA ====================
print("Card 6/6: CTA...")
bg = prepare_bg(load_bg(5), 0.5)
d = ImageDraw.Draw(bg)

center_text(d, "🎁", 180, FONT_HUGE)
center_text(d, "GET JOB-HUNTER", 350, FONT_LARGE, SD_GOLD)

# Divider
for i in range(10):
    x = W//2 - 200 + i*40
    d.rectangle([x, 410, x+24, 418], fill=SD_GOLD if i%2==0 else SD_BROWN)

# CTA box
d.rounded_rectangle([W//2-420, 470, W//2+420, 640], radius=14, fill=SD_INK, outline=SD_GOLD, width=4)
center_text(d, "复制这行字", 510, FONT_MED, SD_GOLD)
center_text(d, "打开【小红书】就能看 skill", 575, FONT_MED, SD_CREAM)

# Copy box
d.rounded_rectangle([W//2-440, 700, W//2+440, 900], radius=12, fill=SD_WHITE, outline=SD_INK, width=4)
center_text(d, "我做了个 job-hunter skill", 748, FONT_MED, SD_INK)
center_text(d, "投简历像种地一样简单", 810, FONT_MED, SD_INK)
center_text(d, "复制 → 打开小红书 → 查看", 875, FONT_SMALL, SD_MUTED)

# Comment prompt
center_text(d, "💬 评论 \"求 skill\" 自动发送", 1060, FONT_SMALL, SD_GOLD)

# Account
d.rounded_rectangle([W//2-160, H-150, W//2+160, H-70], radius=10, fill=SD_GOLD, outline=SD_INK, width=4)
center_text(d, "@ 宝宝AI", H-113, FONT_MED, SD_INK)

bg.save(f'{OUTPUT_DIR}/06_cta.png')

print(f"\n✅ Done! 6 cards saved to {OUTPUT_DIR}/")
print("1080x1440 each, ready for Xiaohongshu carousel upload.")
