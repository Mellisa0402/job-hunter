#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
job-hunter 视频营销流水线本地环境初始化脚本。

功能：
1. 创建音频、字幕帧、背景音乐目录。
2. 检查系统 FFmpeg 是否可用。
3. 使用项目本地 .venv 安装多媒体依赖。
4. 提醒手动放置中文像素字体 Zpix.ttf。
"""

from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / ".venv"
VENV_PIP = VENV_DIR / "bin" / "pip"
REQUIRED_DIRS = (
    PROJECT_ROOT / "output" / "audio",
    PROJECT_ROOT / "output" / "subtitles",
    PROJECT_ROOT / "assets" / "audio",
)
PYTHON_PACKAGES = ("edge-tts", "pillow", "moviepy")


class SetupError(Exception):
    """初始化失败时抛出的可读错误。"""


def print_ok(message: str) -> None:
    print(f"[✓] {message}")


def print_error(message: str) -> None:
    print(f"[错误] {message}")


def print_tip(message: str) -> None:
    bold_yellow = "\033[1;33m"
    reset = "\033[0m"
    print(f"{bold_yellow}{message}{reset}")


def create_required_dirs() -> None:
    for target_dir in REQUIRED_DIRS:
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError as exc:
            raise SetupError(f"没有权限创建目录：{target_dir}") from exc
        except OSError as exc:
            raise SetupError(f"创建目录失败：{target_dir}，原因：{exc}") from exc

        print_ok(f"目录已就绪：{target_dir.relative_to(PROJECT_ROOT)}")


def check_ffmpeg() -> None:
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except FileNotFoundError as exc:
        raise SetupError(
            "未检测到系统 FFmpeg。你当前是 Mac 环境，请先运行：brew install ffmpeg"
        ) from exc
    except OSError as exc:
        raise SetupError(f"检测 FFmpeg 时失败：{exc}") from exc

    if result.returncode != 0:
        raise SetupError(
            "系统 FFmpeg 命令存在，但无法正常运行。你当前是 Mac 环境，请重新安装：brew install ffmpeg"
        )

    print_ok("检测到系统 FFmpeg 已就绪。")


def ensure_venv() -> None:
    if VENV_PIP.exists():
        print_ok("检测到项目本地虚拟环境 .venv。")
        return

    print("[信息] 未检测到 .venv/bin/pip，正在创建项目本地虚拟环境 .venv ...")
    try:
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)
    except PermissionError as exc:
        raise SetupError(f"没有权限创建虚拟环境：{VENV_DIR}") from exc
    except OSError as exc:
        raise SetupError(f"创建虚拟环境失败：{exc}") from exc

    if not VENV_PIP.exists():
        raise SetupError("虚拟环境已创建，但没有找到 .venv/bin/pip，请检查 Python 安装是否完整。")

    print_ok("项目本地虚拟环境 .venv 已创建。")


def install_python_packages() -> None:
    current_python = Path(sys.executable).resolve()
    print(f"[信息] 当前运行的 Python：{current_python}")
    print(f"[信息] 将使用项目本地 pip：{VENV_PIP}")

    command = [str(VENV_PIP), "install", *PYTHON_PACKAGES]

    try:
        result = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    except FileNotFoundError as exc:
        raise SetupError(f"未找到项目本地 pip：{VENV_PIP}") from exc
    except PermissionError as exc:
        raise SetupError(f"没有权限运行项目本地 pip：{VENV_PIP}") from exc
    except OSError as exc:
        raise SetupError(f"运行 pip 安装依赖失败：{exc}") from exc

    if result.returncode != 0:
        raise SetupError("Python 依赖安装失败，请检查网络、代理或 pip 输出。")

    print_ok("Python 多媒体核心库已安装：edge-tts、pillow、moviepy")


def main() -> int:
    print("[信息] 开始初始化 job-hunter 视频营销流水线本地环境。")

    try:
        os.chdir(PROJECT_ROOT)
        create_required_dirs()
        check_ffmpeg()
        ensure_venv()
        install_python_packages()
    except SetupError as exc:
        print_error(str(exc))
        return 1
    except KeyboardInterrupt:
        print_error("初始化已被手动中断。")
        return 130

    print_tip("[提示] 请手动下载开源中文像素字体 'Zpix.ttf'，并直接将其放入项目的根目录下。")
    print_ok("本地环境初始化完成。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
