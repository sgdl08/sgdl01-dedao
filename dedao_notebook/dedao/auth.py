"""得到APP登录辅助"""

from dataclasses import dataclass

from dedao_notebook.dedao import runner


@dataclass
class UserInfo:
    uid: str
    name: str
    raw: str


def login_qrcode() -> None:
    """通过二维码登录（调用 dedao-dl login --qrcode，用户扫码）"""
    runner.run_streaming(["login", "--qrcode"])


def login_cookie(cookie: str) -> None:
    """通过 cookie 字符串登录"""
    runner.run_streaming(["login", "-c", cookie])


def get_current_user() -> UserInfo | None:
    """获取当前登录用户信息"""
    result = runner.run(["who"], check=False)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    raw = result.stdout.strip()
    # dedao-dl who 输出格式示例：
    # UID: 12345678  Name: 张三
    uid, name = "", raw
    for line in raw.splitlines():
        line = line.strip()
        if "UID" in line or "uid" in line:
            parts = line.split()
            for i, p in enumerate(parts):
                if p.lower() in ("uid:", "uid") and i + 1 < len(parts):
                    uid = parts[i + 1]
                if p.lower() in ("name:", "name") and i + 1 < len(parts):
                    name = " ".join(parts[i + 1 :])
    return UserInfo(uid=uid, name=name, raw=raw)


def list_users() -> str:
    """列出所有已登录账号"""
    result = runner.run(["users"], check=False)
    return result.stdout


def switch_user(uid: str) -> None:
    """切换到指定用户"""
    runner.run_streaming(["su", uid])
