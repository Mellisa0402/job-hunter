#!/usr/bin/env python3
"""
保存浏览器登录 Session — 启动有界面浏览器，手动登录后持久化登录态。
后续爬取时传入 --session 参数即可复用，无需重复登录。
"""

from playwright.sync_api import sync_playwright


def save_session(output_path='storage_state.json'):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto('https://jobs.bytedance.com')
        print('请在浏览器中完成登录，登录成功后按回车键保存 session...')
        input()
        context.storage_state(path=output_path)
        browser.close()
        print(f'Session 已保存到 {output_path}')


if __name__ == '__main__':
    save_session()
