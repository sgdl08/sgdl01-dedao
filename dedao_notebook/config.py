"""配置管理模块"""

import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

CONFIG_DIR = Path.home() / ".dedao-notebook"
CONFIG_FILE = CONFIG_DIR / "config.toml"
NOTEBOOKLM_AUTH_FILE = CONFIG_DIR / "notebooklm_auth.json"

_DEFAULT_CONFIG = {
    "dedao": {
        "binary_path": "",
        "download_dir": str(Path.home() / "Downloads" / "dedao"),
        "default_format": "md",
    },
    "notebooklm": {
        "auth_file": "",
        "default_notebook": "",
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result


def load() -> dict:
    """加载配置，不存在则使用默认值"""
    if not CONFIG_FILE.exists():
        return _DEFAULT_CONFIG
    with open(CONFIG_FILE, "rb") as f:
        user_config = tomllib.load(f)
    return _deep_merge(_DEFAULT_CONFIG, user_config)


def get_download_dir(cfg: dict | None = None) -> Path:
    cfg = cfg or load()
    return Path(cfg["dedao"]["download_dir"]).expanduser()


def get_dedao_binary(cfg: dict | None = None) -> str:
    cfg = cfg or load()
    return cfg["dedao"]["binary_path"]


def get_notebooklm_auth_file(cfg: dict | None = None) -> Path:
    cfg = cfg or load()
    path = cfg["notebooklm"]["auth_file"]
    return Path(path).expanduser() if path else NOTEBOOKLM_AUTH_FILE


def get_default_notebook(cfg: dict | None = None) -> str:
    cfg = cfg or load()
    return cfg["notebooklm"]["default_notebook"]


def ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
