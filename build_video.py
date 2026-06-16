#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
宝宝AI job-hunter 星露谷实机风视频一键合成脚本。

流程：
1. 读取 video_pipeline_config.json 的时间轴和口播。
2. 用 Edge-TTS 生成 6 段旁白。
3. 用桌面星露谷素材生成 60 秒、30fps 的实机风画面帧。
4. 用 FFmpeg h264_videotoolbox 导出最终 MP4。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import shutil
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont

try:
    from moviepy import AudioFileClip, CompositeAudioClip, concatenate_audioclips
except ModuleNotFoundError:
    from moviepy.editor import AudioFileClip, CompositeAudioClip, concatenate_audioclips


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = Path("/Users/mellisa/Desktop/video_pipeline_config.json")
LOCAL_CONFIG_PATH = PROJECT_ROOT / "video_pipeline_config.json"
MATERIAL_DIR = Path("/Users/mellisa/Desktop/星露谷元素素材")
SCENE_PATH = MATERIAL_DIR / "IMG_3791.jpg"
BGM_PATH = PROJECT_ROOT / "assets" / "audio" / "stardew_overture.mp3"
FONT_PATH = PROJECT_ROOT / "Zpix.ttf"

OUTPUT_DIR = PROJECT_ROOT / "output"
AUDIO_DIR = OUTPUT_DIR / "audio"
SFX_DIR = AUDIO_DIR / "sfx"
FRAME_DIR = OUTPUT_DIR / "real_stardew_frames"
FINAL_VIDEO_PATH = OUTPUT_DIR / "final_stardew_promo.mp4"
MIXED_AUDIO_PATH = OUTPUT_DIR / "mixed_voiceover.m4a"
GENERATED_BGM_PATH = AUDIO_DIR / "generated_pixel_farm_bgm.wav"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION_SECONDS = 60
TOTAL_FRAMES = FPS * DURATION_SECONDS

VOICE = "zh-CN-YunxiNeural"
VOICE_RATE = "+5%"
SAMPLE_RATE = 44100

SYNCED_VOICEOVER = {
    1: "刷岗位刷到头大？先别硬扛。这条视频帮你把一堆岗位，整理成能直接投的求职手册。",
    2: "岗位名字看着都差不多，城市、要求、链接散得到处都是。人眼看久了，真的会乱。",
    3: "把简历和招聘网址丢进去，不用来回开十几个页面。AI 会先帮你收好，再按条件慢慢筛。",
    4: "接下来自动匹配打分。合适的留下，不合适的先放下，投递顺序一下就清楚了。",
    5: "最后直接看手册。哪个岗位更适合你，投递入口在哪，打开就能看明白。",
    6: "这个 job-hunter 已经开源。如果你也找工作找得头大，可以直接拿去用。",
}


class BuildVideoError(Exception):
    """视频生成失败时抛出的可读错误。"""


@dataclass(frozen=True)
class Segment:
    id: int
    start_ms: int
    end_ms: int
    voiceover_script: str

    @property
    def start_seconds(self) -> float:
        return self.start_ms / 1000


VISUAL_STATES = [
    {
        "start": 0,
        "end": 7,
        "kind": "cover",
        "title1": "刷岗位刷到头大？",
        "title2": "先别硬扛",
        "body": "这条视频帮你做一件事：\n把一堆岗位，整理成\n能直接投的求职手册",
        "caption": "如果你也刷岗位刷到烦，先看这个。",
        "active_slot": 0,
        "sfx": "cover",
    },
    {
        "start": 7,
        "end": 15,
        "kind": "normal",
        "title": "岗位名字都差不多",
        "body": "城市、要求、链接散得到处都是，\n人眼看久了就会乱。",
        "caption": "先把乱七八糟的岗位收进一个篮子。",
        "active_slot": 0,
        "active_tile": 2,
        "sfx": "page",
    },
    {
        "start": 15,
        "end": 26,
        "kind": "normal",
        "title": "把简历和网址丢进去",
        "body": "不用来回开十几个页面，\n它会先帮你收好，\n再按你的条件慢慢筛。",
        "caption": "把重复的整理工作交给 AI。",
        "active_slot": 1,
        "active_tile": 1,
        "sfx": "item",
    },
    {
        "start": 26,
        "end": 38,
        "kind": "normal",
        "title": "自动匹配打分",
        "body": "合适的留下，\n不合适的先放下。\n投递顺序一下就清楚了。",
        "caption": "不是替你做决定，是先排个顺序。",
        "active_slot": 3,
        "active_tile": 3,
        "sfx": "score",
    },
    {
        "start": 38,
        "end": 50,
        "kind": "normal",
        "title": "最后直接看手册",
        "body": "哪个更适合你，\n投递入口在哪，\n打开就能看明白。",
        "caption": "不用乱翻，照着手册投就行。",
        "active_slot": 4,
        "active_tile": 5,
        "sfx": "harvest",
    },
    {
        "start": 50,
        "end": 60,
        "kind": "normal",
        "title": "job-hunter 已开源",
        "body": "如果你也找工作找得头大，\n可以直接拿去用。\n祝你早日通关求职季。",
        "caption": "开源社区搜索 job-hunter。",
        "active_slot": 4,
        "active_tile": 5,
        "sfx": "success",
    },
]


def load_config(config_path: Path) -> dict[str, Any]:
    if config_path == DEFAULT_CONFIG_PATH and not config_path.exists() and LOCAL_CONFIG_PATH.exists():
        config_path = LOCAL_CONFIG_PATH

    if not config_path.exists():
        raise BuildVideoError(f"找不到配置文件：{config_path}")

    return json.loads(config_path.read_text(encoding="utf-8"))


def extract_segments(config: dict[str, Any]) -> list[Segment]:
    raw_segments = config.get("segments") or config.get("timeline_tracks")
    if not isinstance(raw_segments, list) or not raw_segments:
        raise BuildVideoError("配置里没有找到 segments 或 timeline_tracks。")

    segments: list[Segment] = []
    for item in raw_segments:
        for key in ("id", "time_start_ms", "time_end_ms", "voiceover_script"):
            if key not in item:
                raise BuildVideoError(f"时间轴片段缺少字段：{key}")

        text = str(item["voiceover_script"]).strip()
        if not text:
            raise BuildVideoError(f"片段 {item['id']} 的口播为空。")

        segments.append(
            Segment(
                id=int(item["id"]),
                start_ms=int(item["time_start_ms"]),
                end_ms=int(item["time_end_ms"]),
                voiceover_script=text,
            )
        )

    segments.sort(key=lambda segment: segment.id)
    return segments


def ensure_inputs() -> None:
    required = [SCENE_PATH, FONT_PATH]
    missing = [path for path in required if not path.exists()]
    if missing:
        raise BuildVideoError("缺少必要素材：\n" + "\n".join(str(path) for path in missing))

    if shutil.which("ffmpeg") is None:
        raise BuildVideoError("未检测到 FFmpeg，请先安装：brew install ffmpeg")

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def synthesize_voiceover(segments: list[Segment]) -> None:
    for segment in segments:
        output_path = AUDIO_DIR / f"vo_{segment.id}.mp3"
        gTTS(
            SYNCED_VOICEOVER.get(segment.id, segment.voiceover_script),
            lang="zh-CN",
            slow=False,
        ).save(output_path)
        fit_audio_to_slot(output_path, (segment.end_ms - segment.start_ms) / 1000 - 0.35)
        print(f"[完成] 旁白：{output_path.relative_to(PROJECT_ROOT)}")


def get_audio_duration(audio_path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(audio_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def build_atempo_filter(speed: float) -> str:
    filters: list[str] = []
    remaining = speed
    while remaining > 2.0:
        filters.append("atempo=2.0")
        remaining /= 2.0
    while remaining < 0.5:
        filters.append("atempo=0.5")
        remaining /= 0.5
    filters.append(f"atempo={remaining:.4f}")
    return ",".join(filters)


def fit_audio_to_slot(audio_path: Path, target_duration: float) -> None:
    duration = get_audio_duration(audio_path)
    if duration <= target_duration:
        return

    speed = duration / target_duration
    temp_path = audio_path.with_name(f"{audio_path.stem}_fit.mp3")
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(audio_path),
        "-filter:a",
        build_atempo_filter(speed),
        "-codec:a",
        "libmp3lame",
        "-q:a",
        "2",
        str(temp_path),
    ]
    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    if result.returncode != 0:
        raise BuildVideoError(f"口播压缩失败：{audio_path.name}")
    temp_path.replace(audio_path)


def crop_no_black(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    pixels = rgb.load()
    width, height = rgb.size
    rows: list[int] = []
    step = max(1, width // 40)

    for y in range(height):
        sample = [pixels[x, y] for x in range(0, width, step)]
        average = sum(sum(color) for color in sample) / (len(sample) * 3)
        if average > 16:
            rows.append(y)

    if not rows:
        return rgb

    return rgb.crop((0, min(rows), width, max(rows) + 1))


def make_scene_background(source_scene: Image.Image, pan: float) -> Image.Image:
    base = crop_no_black(source_scene)
    scale = max(WIDTH / base.width, HEIGHT / base.height)
    resized = base.resize(
        (int(base.width * scale), int(base.height * scale)),
        Image.Resampling.NEAREST,
    )

    max_x = max(0, resized.width - WIDTH)
    max_y = max(0, resized.height - HEIGHT)
    x = int(max_x * (0.44 + 0.06 * math.sin(pan * math.tau)))
    y = int(max_y * (0.50 + 0.06 * math.cos(pan * math.tau)))
    return resized.crop((x, y, x + WIDTH, y + HEIGHT)).convert("RGBA")


def text_outline(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str = "#fff8dd",
    stroke: str = "#55230f",
    width: int = 4,
) -> None:
    x, y = xy
    offsets = (
        (0, -width),
        (0, width),
        (-width, 0),
        (width, 0),
        (-width, -width),
        (width, -width),
        (-width, width),
        (width, width),
    )
    for dx, dy in offsets:
        draw.text((x + dx, y + dy), text, font=font, fill=stroke)
    draw.text((x, y), text, font=font, fill=fill)


def center_outline(
    draw: ImageDraw.ImageDraw,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str = "#fff8dd",
    stroke: str = "#55230f",
    width: int = 4,
) -> None:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_width = right - left
    text_outline(draw, ((WIDTH - text_width) // 2, y), text, font, fill, stroke, width)


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        if char == "\n":
            if current:
                lines.append(current)
                current = ""
            continue

        candidate = current + char
        width = draw.textbbox((0, 0), candidate, font=font)[2]
        if width <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = char

    if current:
        lines.append(current)
    return lines


def draw_brand(draw: ImageDraw.ImageDraw, font_small: ImageFont.FreeTypeFont) -> None:
    draw.rectangle([52, 50, 480, 126], fill="#fff2bf", outline="#5a260f", width=7)
    draw.text((82, 72), "宝宝AI 求职农场", font=font_small, fill="#4b1f0e")


def draw_cover(
    draw: ImageDraw.ImageDraw,
    state: dict[str, Any],
    fonts: dict[str, ImageFont.FreeTypeFont],
) -> None:
    x, y, width, height = 58, 245, 964, 620
    draw.rectangle([x, y, x + width, y + height], fill="#9b4f22", outline="#5a260f", width=10)
    draw.rectangle(
        [x + 15, y + 15, x + width - 15, y + height - 15],
        fill="#efa758",
        outline="#7c3517",
        width=6,
    )
    draw.rectangle(
        [x + 34, y + 34, x + width - 34, y + 248],
        fill="#ffd98f",
        outline="#9a421b",
        width=5,
    )
    center_outline(draw, y + 62, state["title1"], fonts["huge"])
    center_outline(draw, y + 156, state["title2"], fonts["huge"])

    body_lines = state["body"].split("\n")
    draw.text((x + 70, y + 305), body_lines[0], font=fonts["big"], fill="#4b1f0e")
    draw.text((x + 70, y + 382), body_lines[1], font=fonts["big"], fill="#4b1f0e")
    text_outline(draw, (x + 70, y + 460), body_lines[2], fonts["big"], width=3)

    labels = ["岗位收集", "简历匹配", "投递手册"]
    for index, label in enumerate(labels):
        bx = 112 + index * 310
        by = 1125
        draw.rectangle([bx, by, bx + 250, by + 96], fill="#b8612a", outline="#5a260f", width=7)
        draw.rectangle(
            [bx + 12, by + 12, bx + 238, by + 84],
            fill="#fff2bf",
            outline="#8b421d",
            width=4,
        )
        text_width = draw.textbbox((0, 0), label, font=fonts["mid"])[2]
        draw.text((bx + (250 - text_width) // 2, by + 25), label, font=fonts["mid"], fill="#4b1f0e")


def draw_panel(
    draw: ImageDraw.ImageDraw,
    state: dict[str, Any],
    fonts: dict[str, ImageFont.FreeTypeFont],
) -> None:
    x, y, width, height = 70, 245, 940, 365
    draw.rectangle([x, y, x + width, y + height], fill="#9b4f22", outline="#5a260f", width=9)
    draw.rectangle(
        [x + 12, y + 12, x + width - 12, y + height - 12],
        fill="#f1a14a",
        outline="#7c3517",
        width=5,
    )
    draw.rectangle(
        [x + 26, y + 26, x + width - 26, y + 122],
        fill="#ffd083",
        outline="#8a3918",
        width=4,
    )
    text_outline(draw, (x + 48, y + 38), state["title"], fonts["panel_title"], width=3)

    text_y = y + 154
    for line in wrap_text(draw, state["body"], fonts["body"], width - 96):
        draw.text((x + 50, text_y), line, font=fonts["body"], fill="#4b1f0e")
        text_y += 63


def draw_info_tiles(
    draw: ImageDraw.ImageDraw,
    active_tile: int,
    font: ImageFont.FreeTypeFont,
) -> None:
    labels = ["招聘页", "简历", "城市", "匹配分", "投递口", "手册"]
    for index, label in enumerate(labels):
        x = 92 + (index % 3) * 318
        y = 650 + (index // 3) * 120
        fill = "#fff2bf" if index == active_tile else "#ffd083"
        draw.rectangle([x, y, x + 270, y + 86], fill="#b8612a", outline="#5a260f", width=7)
        draw.rectangle([x + 12, y + 12, x + 258, y + 74], fill=fill, outline="#8b421d", width=4)
        draw.text((x + 34, y + 27), label, font=font, fill="#4b1f0e")


def draw_caption(
    draw: ImageDraw.ImageDraw,
    caption: str,
    font: ImageFont.FreeTypeFont,
) -> None:
    draw.rectangle([70, 1544, 1010, 1640], fill="#fff2bf", outline="#5a260f", width=8)
    draw.text((118, 1572), caption, font=font, fill="#4b1f0e")


def draw_slots(
    draw: ImageDraw.ImageDraw,
    active_slot: int,
    font: ImageFont.FreeTypeFont,
) -> None:
    labels = ["岗位", "简历", "城市", "分数", "手册"]
    x0, y, slot_width, slot_height, gap = 70, 1710, 190, 106, 12
    for index, label in enumerate(labels):
        x = x0 + index * (slot_width + gap)
        draw.rectangle(
            [x, y, x + slot_width, y + slot_height],
            fill="#b8612a",
            outline="#5a260f",
            width=7,
        )
        draw.rectangle(
            [x + 12, y + 12, x + slot_width - 12, y + slot_height - 12],
            fill="#fff2bf" if index == active_slot else "#f2bd68",
            outline="#8b421d",
            width=4,
        )
        text_width = draw.textbbox((0, 0), label, font=font)[2]
        draw.text((x + (slot_width - text_width) // 2, y + 34), label, font=font, fill="#4b1f0e")


def get_visual_state(seconds: float) -> dict[str, Any]:
    for state in VISUAL_STATES:
        if state["start"] <= seconds < state["end"]:
            return state
    return VISUAL_STATES[-1]


def render_frames() -> None:
    source_scene = Image.open(SCENE_PATH).convert("RGB")
    fonts = {
        "huge": ImageFont.truetype(str(FONT_PATH), 80),
        "big": ImageFont.truetype(str(FONT_PATH), 54),
        "mid": ImageFont.truetype(str(FONT_PATH), 42),
        "panel_title": ImageFont.truetype(str(FONT_PATH), 64),
        "body": ImageFont.truetype(str(FONT_PATH), 48),
        "small": ImageFont.truetype(str(FONT_PATH), 36),
    }

    for old_frame in FRAME_DIR.glob("frame_*.png"):
        old_frame.unlink()

    for frame_index in range(TOTAL_FRAMES):
        seconds = frame_index / FPS
        state = get_visual_state(seconds)
        pan = seconds / DURATION_SECONDS
        image = make_scene_background(source_scene, pan)
        draw = ImageDraw.Draw(image)

        draw_brand(draw, fonts["small"])
        if state["kind"] == "cover":
            draw_cover(draw, state, fonts)
        else:
            draw_panel(draw, state, fonts)
            draw_info_tiles(draw, int(state["active_tile"]), fonts["small"])

        draw_caption(draw, state["caption"], fonts["small"])
        draw_slots(draw, int(state["active_slot"]), fonts["small"])

        frame_path = FRAME_DIR / f"frame_{frame_index:05d}.png"
        image.convert("RGB").save(frame_path, quality=95)

        if (frame_index + 1) % 300 == 0 or frame_index + 1 == TOTAL_FRAMES:
            print(f"[完成] 画面帧：{frame_index + 1}/{TOTAL_FRAMES}")


def set_start(clip: AudioFileClip, seconds: float):
    if hasattr(clip, "with_start"):
        return clip.with_start(seconds)
    return clip.set_start(seconds)


def set_duration(clip, seconds: float):
    if hasattr(clip, "with_duration"):
        return clip.with_duration(seconds)
    return clip.set_duration(seconds)


def set_volume(clip, volume: float):
    if hasattr(clip, "with_volume_scaled"):
        return clip.with_volume_scaled(volume)
    return clip.volumex(volume)


def loop_audio(clip: AudioFileClip, duration: float):
    if clip.duration is None or clip.duration <= 0:
        raise BuildVideoError("背景音乐时长无效，无法循环。")
    repeat_count = math.ceil(duration / clip.duration)
    return set_duration(concatenate_audioclips([clip] * repeat_count), duration)


def write_mono_wav(path: Path, samples: list[int]) -> None:
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(b"".join(sample.to_bytes(2, "little", signed=True) for sample in samples))


def synth_note(frequency: float, duration: float, volume: float) -> list[int]:
    total_samples = int(duration * SAMPLE_RATE)
    samples: list[int] = []
    for index in range(total_samples):
        progress = index / max(1, total_samples - 1)
        attack = min(1.0, progress / 0.08)
        release = min(1.0, (1.0 - progress) / 0.22)
        envelope = max(0.0, min(attack, release))
        sine = math.sin(math.tau * frequency * index / SAMPLE_RATE)
        square = 1.0 if sine >= 0 else -1.0
        value = (sine * 0.72 + square * 0.28) * envelope * volume
        samples.append(int(max(-1.0, min(1.0, value)) * 32767))
    return samples


def generate_sfx_assets() -> dict[str, Path]:
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    recipes = {
        "cover": [(523, 0.055), (659, 0.06), (784, 0.11)],
        "page": [(392, 0.045), (523, 0.055)],
        "item": [(659, 0.05), (880, 0.07)],
        "score": [(523, 0.05), (659, 0.05), (784, 0.08)],
        "harvest": [(659, 0.06), (880, 0.07), (1175, 0.12)],
        "success": [(523, 0.055), (659, 0.06), (784, 0.07), (1046, 0.14)],
    }
    silence = [0] * int(0.025 * SAMPLE_RATE)
    paths: dict[str, Path] = {}
    for name, notes in recipes.items():
        samples: list[int] = []
        for frequency, duration in notes:
            samples.extend(synth_note(frequency, duration, 0.28))
            samples.extend(silence)
        path = SFX_DIR / f"{name}.wav"
        write_mono_wav(path, samples)
        paths[name] = path
    return paths


def generate_pixel_bgm() -> Path:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    if GENERATED_BGM_PATH.exists():
        return GENERATED_BGM_PATH

    notes = [196, 247, 294, 247, 220, 262, 330, 262]
    total_samples = DURATION_SECONDS * SAMPLE_RATE
    chunk_size = SAMPLE_RATE
    with wave.open(str(GENERATED_BGM_PATH), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)

        for chunk_start in range(0, total_samples, chunk_size):
            chunk: list[int] = []
            chunk_end = min(chunk_start + chunk_size, total_samples)
            for index in range(chunk_start, chunk_end):
                seconds = index / SAMPLE_RATE
                note = notes[int(seconds * 2) % len(notes)]
                pad = math.sin(math.tau * 98 * seconds) * 0.055
                melody = math.sin(math.tau * note * seconds) * 0.035
                upper = math.sin(math.tau * (note * 2) * seconds) * 0.018
                # 轻微起伏，让背景音有生命感，但不抢旁白。
                envelope = 0.78 + 0.22 * math.sin(math.tau * seconds / 4)
                value = (pad + melody + upper) * envelope
                chunk.append(int(max(-1.0, min(1.0, value)) * 32767))
            wav_file.writeframes(
                b"".join(sample.to_bytes(2, "little", signed=True) for sample in chunk)
            )
    return GENERATED_BGM_PATH


def build_audio(segments: list[Segment]) -> None:
    sfx_paths = generate_sfx_assets()
    voice_clips = []
    for segment in segments:
        audio_path = AUDIO_DIR / f"vo_{segment.id}.mp3"
        if not audio_path.exists():
            raise BuildVideoError(f"缺少旁白音频：{audio_path}")
        voice_clips.append(set_start(AudioFileClip(str(audio_path)), segment.start_seconds))

    audio_layers = []
    if BGM_PATH.exists():
        bgm_source = BGM_PATH
    else:
        bgm_source = generate_pixel_bgm()

    bgm = set_volume(loop_audio(AudioFileClip(str(bgm_source)), DURATION_SECONDS), 0.12)
    audio_layers.append(bgm)

    for state in VISUAL_STATES:
        sfx_name = state.get("sfx")
        if not sfx_name:
            continue
        sfx_path = sfx_paths[str(sfx_name)]
        sfx_clip = set_start(AudioFileClip(str(sfx_path)), float(state["start"]))
        audio_layers.append(set_volume(sfx_clip, 0.9))

    audio_layers.extend(voice_clips)
    mixed_audio = CompositeAudioClip(audio_layers)
    mixed_audio = set_duration(mixed_audio, DURATION_SECONDS)
    mixed_audio.write_audiofile(str(MIXED_AUDIO_PATH), fps=44100, codec="aac")
    mixed_audio.close()
    for clip in audio_layers:
        clip.close()


def encode_video() -> None:
    command = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(FPS),
        "-i",
        str(FRAME_DIR / "frame_%05d.png"),
        "-i",
        str(MIXED_AUDIO_PATH),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        "-shortest",
        str(FINAL_VIDEO_PATH),
    ]
    result = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    if result.returncode != 0:
        raise BuildVideoError("FFmpeg 导出视频失败。")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="一键生成宝宝AI星露谷实机风求职视频。")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--skip-tts", action="store_true")
    parser.add_argument("--skip-frames", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        ensure_inputs()
        config = load_config(args.config)
        segments = extract_segments(config)

        if not args.skip_tts:
            asyncio.run(synthesize_voiceover(segments))

        if not args.skip_frames:
            render_frames()

        build_audio(segments)
        encode_video()
    except BuildVideoError as exc:
        print(f"[错误] {exc}")
        return 1
    except KeyboardInterrupt:
        print("[错误] 已手动中断。")
        return 130

    print(f"[完成] 最终视频：{FINAL_VIDEO_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
