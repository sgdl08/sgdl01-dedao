"""得到课程内容下载"""

from pathlib import Path

from dedao_notebook.dedao import runner

# 格式代码映射（对应 dedao-dl -t 参数）
FORMAT_MAP = {
    "mp3": "1",
    "pdf": "2",
    "md": "3",
}

EBOOK_FORMAT_MAP = {
    "html": "1",
    "pdf": "2",
    "epub": "3",
    "md": "4",  # 笔记
}


def _format_args(fmt: str, format_map: dict) -> list[str]:
    code = format_map.get(fmt.lower())
    if not code:
        raise ValueError(f"不支持的格式: {fmt}，可选: {list(format_map.keys())}")
    return ["-t", code]


def download_course(
    course_id: str,
    fmt: str = "md",
    output_dir: Path | None = None,
    merge: bool = False,
    comments: bool = False,
) -> int:
    """下载专栏课程

    Args:
        course_id: 课程 ID
        fmt: 格式 (md/pdf/mp3)
        output_dir: 输出目录（None 则使用 dedao-dl 默认路径）
        merge: 是否合并章节（仅 md 格式有效）
        comments: 是否包含精选评论（仅 md 格式有效）

    Returns:
        退出码，0 表示成功
    """
    args = ["dl", course_id] + _format_args(fmt, FORMAT_MAP)
    if merge:
        args.append("-m")
    if comments:
        args.append("-c")
    if output_dir:
        args += ["-o", str(output_dir)]
    return runner.run_streaming(args)


def download_audiobook(
    book_id: str,
    fmt: str = "md",
    output_dir: Path | None = None,
) -> int:
    """下载每天听本书

    Args:
        book_id: 书籍 ID
        fmt: 格式 (md/pdf/mp3)
        output_dir: 输出目录

    Returns:
        退出码
    """
    args = ["dlo", book_id] + _format_args(fmt, FORMAT_MAP)
    if output_dir:
        args += ["-o", str(output_dir)]
    return runner.run_streaming(args)


def download_ebook(
    book_id: str,
    fmt: str = "epub",
    output_dir: Path | None = None,
) -> int:
    """下载电子书

    Args:
        book_id: 电子书 ID
        fmt: 格式 (html/pdf/epub/md)
        output_dir: 输出目录

    Returns:
        退出码
    """
    args = ["dle", book_id] + _format_args(fmt, EBOOK_FORMAT_MAP)
    if output_dir:
        args += ["-o", str(output_dir)]
    return runner.run_streaming(args)
