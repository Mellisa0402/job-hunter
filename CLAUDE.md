# Job Hunter Project

## 项目概述
求职岗位爬取+匹配+PDF投递手册生成工具。从任意招聘官网自动爬取岗位、与简历匹配打分、生成可点击投递链接的PDF。

## 项目路径
项目根目录

## 核心架构
- hunter/crawler/ — 阶段1: 爬虫（YAML驱动通用爬虫 + Python适配器）
- hunter/matcher/ — 阶段2: 匹配打分（AI语义匹配 + 关键词匹配）
- hunter/reporter/ — 阶段3: 生成PDF

## 依赖
- playwright (Chromium)
- pdfplumber
- anthropic (AI匹配模式)
- pyyaml (可选，有内置降级解析器)

## 常见使用方式
用户提供目标网站URL和简历 → `python3 run.py --url "..." --resume ./resume.pdf` → 输出手册

## 关键参数
- --url: 招聘网站URL（任意网站，含token）
- --resume: 简历文件路径（PDF/文本）
- --cities: 目标城市（任意城市名，逗号分隔）
- --types: 招聘类型（full_time,campus,intern）
- --mode: 匹配模式（ai/keyword）
- --output: 输出PDF路径

## 配置
- config/user.example.yaml — 用户配置模板
- config/sites/ — 网站YAML配置文件
- hunter/crawler/adapters/ — 复杂网站的Python适配器
