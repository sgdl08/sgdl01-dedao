"""端到端工作流：下载得到课程 → 上传到 NotebookLM"""

from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console

from dedao_notebook import config
from dedao_notebook.dedao import downloader
from dedao_notebook.notebooklm import notebooks, uploader

console = Console()


@dataclass
class WorkflowResult:
    course_id: str
    notebook_title: str
    notebook_id: str = ""
    download_success: bool = False
    uploaded: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)


def run(
    course_id: str,
    notebook_title: str,
    formats: list[str] | None = None,
    output_dir: Path | None = None,
    content_type: str = "course",
    merge: bool = True,
) -> WorkflowResult:
    """完整工作流：下载得到课程 → 上传到 NotebookLM

    Args:
        course_id: 得到课程/电子书/听书 ID
        notebook_title: 目标 NotebookLM 笔记本名称
        formats: 下载格式列表，如 ['md', 'pdf', 'mp3']，None 表示使用配置默认值
        output_dir: 下载目录，None 则使用配置默认目录
        content_type: 内容类型，'course'（专栏）/ 'ebook'（电子书）/ 'audiobook'（听书）
        merge: 是否合并章节（仅 md 格式的课程有效）

    Returns:
        WorkflowResult 结果摘要
    """
    cfg = config.load()
    result = WorkflowResult(course_id=course_id, notebook_title=notebook_title)

    if formats is None:
        default_fmt = cfg["dedao"]["default_format"]
        formats = [default_fmt]

    if output_dir is None:
        output_dir = config.get_download_dir(cfg) / course_id
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── 步骤 1：下载课程内容 ──────────────────────────────────────────
    console.print(f"\n[bold blue]步骤 1/3[/bold blue] 下载课程 {course_id}（格式: {', '.join(formats)}）")
    download_ok = True

    for fmt in formats:
        console.print(f"  下载格式: [cyan]{fmt}[/cyan]")
        if content_type == "course":
            rc = downloader.download_course(course_id, fmt=fmt, output_dir=output_dir, merge=merge)
        elif content_type == "ebook":
            rc = downloader.download_ebook(course_id, fmt=fmt, output_dir=output_dir)
        elif content_type == "audiobook":
            rc = downloader.download_audiobook(course_id, fmt=fmt, output_dir=output_dir)
        else:
            result.errors.append(f"未知内容类型: {content_type}")
            download_ok = False
            break

        if rc != 0:
            result.errors.append(f"下载 {fmt} 格式失败（退出码 {rc}）")
            download_ok = False

    result.download_success = download_ok
    if not download_ok:
        console.print(f"[yellow]下载部分失败，错误: {result.errors}[/yellow]")

    # ── 步骤 2：获取或创建 NotebookLM 笔记本 ─────────────────────────
    console.print(f"\n[bold blue]步骤 2/3[/bold blue] 查找或创建笔记本: [cyan]{notebook_title}[/cyan]")
    try:
        nb = notebooks.get_or_create(notebook_title)
        result.notebook_id = nb.id
        console.print(f"  笔记本 ID: {nb.id}")
    except Exception as e:
        result.errors.append(f"获取/创建笔记本失败: {e}")
        console.print(f"[red]笔记本操作失败: {e}[/red]")
        return result

    # ── 步骤 3：上传下载的文件 ────────────────────────────────────────
    # 仅上传 NotebookLM 支持的格式（md/pdf/txt），不上传 mp3
    upload_formats = [f for f in formats if f.lower() in ("md", "pdf", "txt")]
    if not upload_formats:
        console.print("[yellow]下载格式中没有可上传到 NotebookLM 的文件（支持 md/pdf/txt）[/yellow]")
        return result

    console.print(f"\n[bold blue]步骤 3/3[/bold blue] 上传文件到 NotebookLM 笔记本")
    success, fail = uploader.upload_directory(nb.id, output_dir, formats=upload_formats)
    result.uploaded = success
    result.failed = fail

    # ── 汇总 ─────────────────────────────────────────────────────────
    console.print(f"\n[bold green]完成！[/bold green]")
    console.print(f"  下载: {'成功' if result.download_success else '部分失败'}")
    console.print(f"  上传: {success} 个成功, {fail} 个失败")
    console.print(f"  笔记本: {notebook_title}（ID: {nb.id}）")

    return result
