"""上传文件到 NotebookLM"""

import asyncio
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from dedao_notebook.notebooklm.auth import get_auth_file

console = Console()

SUPPORTED_UPLOAD_SUFFIXES = {".md", ".pdf", ".txt"}


async def _get_client():
    from notebooklm import NotebookLMClient
    return await NotebookLMClient.from_storage(str(get_auth_file()))


async def upload_file_async(notebook_id: str, file_path: Path) -> bool:
    """上传单个文件到笔记本，返回是否成功"""
    client = await _get_client()
    suffix = file_path.suffix.lower()
    if suffix == ".md" or suffix == ".txt":
        content = file_path.read_text(encoding="utf-8")
        await client.sources.add_text(notebook_id, content, title=file_path.stem)
    elif suffix == ".pdf":
        with open(file_path, "rb") as f:
            await client.sources.upload_file(notebook_id, f, filename=file_path.name)
    else:
        return False
    return True


async def upload_directory_async(
    notebook_id: str,
    dir_path: Path,
    formats: list[str] | None = None,
) -> tuple[int, int]:
    """批量上传目录中的文件

    Args:
        notebook_id: 笔记本 ID
        dir_path: 扫描目录
        formats: 允许的格式列表（如 ['md', 'pdf']），None 表示全部支持格式

    Returns:
        (成功数, 失败数)
    """
    if formats:
        allowed = {"." + f.lstrip(".").lower() for f in formats}
    else:
        allowed = SUPPORTED_UPLOAD_SUFFIXES

    files = [
        f for f in dir_path.rglob("*")
        if f.is_file() and f.suffix.lower() in allowed
    ]

    if not files:
        console.print(f"[yellow]目录 {dir_path} 中没有找到可上传的文件[/yellow]")
        return 0, 0

    success, fail = 0, 0
    client = await _get_client()

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        task = progress.add_task(f"上传 {len(files)} 个文件...", total=len(files))
        for file_path in files:
            progress.update(task, description=f"上传: {file_path.name}")
            try:
                suffix = file_path.suffix.lower()
                if suffix in (".md", ".txt"):
                    content = file_path.read_text(encoding="utf-8")
                    await client.sources.add_text(notebook_id, content, title=file_path.stem)
                elif suffix == ".pdf":
                    with open(file_path, "rb") as f:
                        await client.sources.upload_file(notebook_id, f, filename=file_path.name)
                success += 1
            except Exception as e:
                console.print(f"[red]上传失败 {file_path.name}: {e}[/red]")
                fail += 1
            progress.advance(task)

    return success, fail


async def upload_text_async(notebook_id: str, content: str, title: str) -> None:
    """上传文本内容到笔记本"""
    client = await _get_client()
    await client.sources.add_text(notebook_id, content, title=title)


def upload_file(notebook_id: str, file_path: Path) -> bool:
    return asyncio.run(upload_file_async(notebook_id, file_path))


def upload_directory(
    notebook_id: str,
    dir_path: Path,
    formats: list[str] | None = None,
) -> tuple[int, int]:
    return asyncio.run(upload_directory_async(notebook_id, dir_path, formats))


def upload_text(notebook_id: str, content: str, title: str) -> None:
    asyncio.run(upload_text_async(notebook_id, content, title))
