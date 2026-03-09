"""dedao-dl 二进制文件的 subprocess 封装"""

import shutil
import subprocess
from pathlib import Path

from rich.console import Console

from dedao_notebook import config

console = Console()

_COMMON_PATHS = [
    Path.home() / "go" / "bin" / "dedao-dl",
    Path("/usr/local/bin/dedao-dl"),
    Path("/usr/bin/dedao-dl"),
]


class DedaoBinaryNotFound(Exception):
    """找不到 dedao-dl 二进制文件"""


def find_binary() -> str:
    """查找 dedao-dl 可执行文件路径"""
    cfg = config.load()
    configured = config.get_dedao_binary(cfg)
    if configured:
        p = Path(configured).expanduser()
        if p.exists():
            return str(p)
        raise DedaoBinaryNotFound(f"配置的 dedao-dl 路径不存在: {p}")

    # 从 PATH 查找
    found = shutil.which("dedao-dl")
    if found:
        return found

    # 常见安装路径
    for p in _COMMON_PATHS:
        if p.exists():
            return str(p)

    raise DedaoBinaryNotFound(
        "找不到 dedao-dl，请先安装：https://github.com/yann0917/dedao-dl\n"
        "安装后可通过配置文件指定路径：~/.dedao-notebook/config.toml"
    )


def run(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """运行 dedao-dl 命令，返回结果"""
    binary = find_binary()
    cmd = [binary] + args
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def run_streaming(args: list[str]) -> int:
    """运行 dedao-dl 命令并实时流式输出，返回退出码"""
    binary = find_binary()
    cmd = [binary] + args
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
        for line in proc.stdout:
            console.print(line, end="")
    return proc.returncode
