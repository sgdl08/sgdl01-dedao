"""文件工具函数"""

from pathlib import Path


def find_downloaded_files(directory: Path, formats: list[str]) -> list[Path]:
    """在目录中递归查找指定格式的文件"""
    suffixes = {"." + f.lstrip(".").lower() for f in formats}
    return [f for f in directory.rglob("*") if f.is_file() and f.suffix.lower() in suffixes]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
