"""主 CLI 入口"""

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.version_option()
def cli():
    """dedao-notebook: 下载得到APP课程并上传到 Google NotebookLM"""


# ─────────────────────────────────────────────────────────────
# auth 命令组
# ─────────────────────────────────────────────────────────────

@cli.group()
def auth():
    """账号登录管理"""


@auth.group("dedao")
def auth_dedao():
    """得到APP账号管理"""


@auth_dedao.command("login")
@click.option("--cookie", "-c", default=None, help="直接提供 cookie 字符串登录")
def dedao_login(cookie):
    """登录得到APP账号"""
    from dedao_notebook.dedao import auth as dedao_auth
    try:
        if cookie:
            console.print("通过 cookie 登录...")
            dedao_auth.login_cookie(cookie)
        else:
            console.print("通过二维码登录，请用得到APP扫码...")
            dedao_auth.login_qrcode()
    except Exception as e:
        console.print(f"[red]登录失败: {e}[/red]")
        raise SystemExit(1)


@auth_dedao.command("whoami")
def dedao_whoami():
    """显示当前得到账号"""
    from dedao_notebook.dedao import auth as dedao_auth
    try:
        user = dedao_auth.get_current_user()
        if user:
            console.print(f"当前用户: [cyan]{user.name}[/cyan]（UID: {user.uid}）")
        else:
            console.print("[yellow]未登录或无法获取用户信息[/yellow]")
    except Exception as e:
        console.print(f"[red]{e}[/red]")


@auth_dedao.command("users")
def dedao_users():
    """列出所有已登录的得到账号"""
    from dedao_notebook.dedao import auth as dedao_auth
    try:
        output = dedao_auth.list_users()
        console.print(output)
    except Exception as e:
        console.print(f"[red]{e}[/red]")


@auth_dedao.command("switch")
@click.argument("uid")
def dedao_switch(uid):
    """切换得到账号"""
    from dedao_notebook.dedao import auth as dedao_auth
    try:
        dedao_auth.switch_user(uid)
    except Exception as e:
        console.print(f"[red]{e}[/red]")


@auth.group("notebooklm")
def auth_notebooklm():
    """Google NotebookLM 账号管理"""


@auth_notebooklm.command("login")
def notebooklm_login():
    """登录 Google NotebookLM（打开浏览器完成 Google 登录）"""
    from dedao_notebook.notebooklm import auth as nb_auth
    try:
        nb_auth.login()
    except SystemExit:
        raise
    except Exception as e:
        console.print(f"[red]登录失败: {e}[/red]")
        raise SystemExit(1)


@auth_notebooklm.command("status")
def notebooklm_status():
    """检查 NotebookLM 登录状态"""
    from dedao_notebook.notebooklm import auth as nb_auth
    auth_file = nb_auth.get_auth_file()
    if not nb_auth.is_logged_in():
        console.print(f"[yellow]未找到认证文件: {auth_file}[/yellow]")
        console.print("请运行: dedao-notebook auth notebooklm login")
    else:
        console.print(f"[green]认证文件存在: {auth_file}[/green]")


# ─────────────────────────────────────────────────────────────
# dedao 命令组
# ─────────────────────────────────────────────────────────────

@cli.group()
def dedao():
    """得到APP内容管理"""


@dedao.command("courses")
def list_courses():
    """列出已购专栏课程"""
    from dedao_notebook.dedao import courses
    try:
        items = courses.list_courses()
        if not items:
            console.print("[yellow]未找到课程，请确认已登录并购买课程[/yellow]")
            return
        table = Table(title="已购专栏课程")
        table.add_column("ID", style="cyan")
        table.add_column("ClassID", style="dim")
        table.add_column("标题")
        table.add_column("作者")
        for item in items:
            table.add_row(item.id, item.class_id, item.title, item.author)
        console.print(table)
    except Exception as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)


@dedao.command("ebooks")
def list_ebooks():
    """列出已购电子书"""
    from dedao_notebook.dedao import courses
    try:
        items = courses.list_ebooks()
        if not items:
            console.print("[yellow]未找到电子书[/yellow]")
            return
        table = Table(title="已购电子书")
        table.add_column("ID", style="cyan")
        table.add_column("标题")
        table.add_column("作者")
        for item in items:
            table.add_row(item.id, item.title, item.author)
        console.print(table)
    except Exception as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)


@dedao.command("audiobooks")
def list_audiobooks():
    """列出已购每天听本书"""
    from dedao_notebook.dedao import courses
    try:
        items = courses.list_audiobooks()
        if not items:
            console.print("[yellow]未找到听书内容[/yellow]")
            return
        table = Table(title="已购每天听本书")
        table.add_column("ID", style="cyan")
        table.add_column("标题")
        table.add_column("作者")
        for item in items:
            table.add_row(item.id, item.title, item.author)
        console.print(table)
    except Exception as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)


@dedao.command("download")
@click.argument("course_id")
@click.option(
    "--format", "-f", "fmt",
    default=None,
    help="下载格式: md, pdf, mp3, all（默认使用配置文件设置）",
)
@click.option("--output", "-o", default=None, help="输出目录")
@click.option("--type", "-t", "content_type",
              type=click.Choice(["course", "ebook", "audiobook"]),
              default="course", help="内容类型（默认: course）")
@click.option("--merge/--no-merge", default=True, help="合并 Markdown 章节（仅 md 格式）")
@click.option("--comments/--no-comments", default=False, help="包含精选评论（仅 md 格式）")
def download(course_id, fmt, output, content_type, merge, comments):
    """下载得到课程内容"""
    from dedao_notebook import config
    from dedao_notebook.dedao import downloader as dl

    cfg = config.load()
    output_dir = Path(output).expanduser() if output else config.get_download_dir(cfg) / course_id

    if fmt == "all":
        formats = ["md", "pdf", "mp3"]
    elif fmt:
        formats = [fmt]
    else:
        formats = [cfg["dedao"]["default_format"]]

    for f in formats:
        console.print(f"下载 [cyan]{course_id}[/cyan] 格式: [cyan]{f}[/cyan] → {output_dir}")
        try:
            if content_type == "course":
                rc = dl.download_course(course_id, fmt=f, output_dir=output_dir, merge=merge, comments=comments)
            elif content_type == "ebook":
                rc = dl.download_ebook(course_id, fmt=f, output_dir=output_dir)
            else:
                rc = dl.download_audiobook(course_id, fmt=f, output_dir=output_dir)
            if rc != 0:
                console.print(f"[red]下载失败（退出码 {rc}）[/red]")
        except Exception as e:
            console.print(f"[red]{e}[/red]")
            raise SystemExit(1)


# ─────────────────────────────────────────────────────────────
# notebooklm 命令组
# ─────────────────────────────────────────────────────────────

@cli.group()
def notebooklm():
    """Google NotebookLM 笔记本管理"""


@notebooklm.command("notebooks")
def list_notebooks_cmd():
    """列出所有笔记本"""
    from dedao_notebook.notebooklm import notebooks as nb
    try:
        items = nb.list_notebooks()
        if not items:
            console.print("[yellow]没有笔记本[/yellow]")
            return
        table = Table(title="NotebookLM 笔记本")
        table.add_column("ID", style="dim")
        table.add_column("标题", style="cyan")
        for item in items:
            table.add_row(item.id, item.title)
        console.print(table)
    except Exception as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)


@notebooklm.command("upload")
@click.argument("file_or_dir")
@click.option("--notebook", "-n", default=None, help="笔记本名称（不存在则创建）")
def upload_cmd(file_or_dir, notebook):
    """上传文件或目录到 NotebookLM 笔记本"""
    from dedao_notebook import config
    from dedao_notebook.notebooklm import notebooks as nb, uploader as ul

    cfg = config.load()
    notebook_title = notebook or config.get_default_notebook(cfg)
    if not notebook_title:
        notebook_title = click.prompt("请输入笔记本名称")

    try:
        target_nb = nb.get_or_create(notebook_title)
        path = Path(file_or_dir).expanduser()

        if path.is_dir():
            success, fail = ul.upload_directory(target_nb.id, path)
            console.print(f"[green]上传完成: {success} 成功, {fail} 失败[/green]")
        elif path.is_file():
            ok = ul.upload_file(target_nb.id, path)
            if ok:
                console.print(f"[green]上传成功: {path.name}[/green]")
            else:
                console.print(f"[red]不支持的文件格式: {path.suffix}[/red]")
        else:
            console.print(f"[red]路径不存在: {path}[/red]")
            raise SystemExit(1)
    except Exception as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)


# ─────────────────────────────────────────────────────────────
# pipeline 命令组
# ─────────────────────────────────────────────────────────────

@cli.group()
def pipeline():
    """端到端工作流"""


@pipeline.command("run")
@click.argument("course_id")
@click.option("--notebook", "-n", default=None, help="目标笔记本名称（不存在则创建）")
@click.option(
    "--format", "-f", "fmt",
    default=None,
    help="下载格式: md, pdf, mp3, all（默认使用配置文件设置）",
)
@click.option("--output", "-o", default=None, help="下载临时目录")
@click.option("--type", "-t", "content_type",
              type=click.Choice(["course", "ebook", "audiobook"]),
              default="course", help="内容类型（默认: course）")
@click.option("--merge/--no-merge", default=True, help="合并 Markdown 章节")
def pipeline_run(course_id, notebook, fmt, output, content_type, merge):
    """完整流程：下载得到课程 → 上传到 NotebookLM"""
    from dedao_notebook import config
    from dedao_notebook.pipeline import workflow

    cfg = config.load()
    notebook_title = notebook or config.get_default_notebook(cfg)
    if not notebook_title:
        notebook_title = click.prompt("请输入目标笔记本名称")

    output_dir = Path(output).expanduser() if output else None

    if fmt == "all":
        formats = ["md", "pdf", "mp3"]
    elif fmt:
        formats = [fmt]
    else:
        formats = None  # 使用配置默认值

    try:
        result = workflow.run(
            course_id=course_id,
            notebook_title=notebook_title,
            formats=formats,
            output_dir=output_dir,
            content_type=content_type,
            merge=merge,
        )
        if result.errors:
            for err in result.errors:
                console.print(f"[yellow]警告: {err}[/yellow]")
    except Exception as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
