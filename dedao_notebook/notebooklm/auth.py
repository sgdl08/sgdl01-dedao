"""Google NotebookLM 登录辅助"""

import asyncio
from pathlib import Path

from rich.console import Console

from dedao_notebook import config

console = Console()


def get_auth_file() -> Path:
    return config.get_notebooklm_auth_file()


def is_logged_in() -> bool:
    """检查是否已有有效的认证文件"""
    return get_auth_file().exists()


def login() -> None:
    """通过 Playwright 浏览器完成 Google 登录，保存 cookies"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        console.print(
            "[red]需要安装 playwright：pip install 'dedao-notebook[browser]'[/red]\n"
            "安装后运行：playwright install chromium"
        )
        raise SystemExit(1)

    config.ensure_config_dir()
    auth_file = get_auth_file()

    console.print("[bold]正在打开浏览器，请完成 Google 账号登录...[/bold]")
    console.print(f"登录完成后 cookies 将保存到：{auth_file}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://notebooklm.google.com")
        console.print("[yellow]请在浏览器中完成登录，登录后按 Enter 继续...[/yellow]")
        input()
        context.storage_state(path=str(auth_file))
        browser.close()

    console.print(f"[green]登录成功，认证信息已保存到 {auth_file}[/green]")


async def check_auth_async() -> bool:
    """异步验证 cookies 是否有效（尝试连接 NotebookLM）"""
    if not is_logged_in():
        return False
    try:
        from notebooklm import NotebookLMClient
        client = await NotebookLMClient.from_storage(str(get_auth_file()))
        await client.notebooks.list()
        return True
    except Exception:
        return False


def check_auth() -> bool:
    return asyncio.run(check_auth_async())
