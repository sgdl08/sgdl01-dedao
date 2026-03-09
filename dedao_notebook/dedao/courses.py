"""得到课程列表查询"""

import re
from dataclasses import dataclass, field

from dedao_notebook.dedao import runner


@dataclass
class CourseItem:
    id: str
    class_id: str
    title: str
    author: str = ""
    raw: str = ""


@dataclass
class EbookItem:
    id: str
    title: str
    author: str = ""
    raw: str = ""


@dataclass
class AudiobookItem:
    id: str
    title: str
    author: str = ""
    raw: str = ""


def _parse_table(output: str) -> list[dict[str, str]]:
    """解析 dedao-dl 输出的表格（通过竖线分隔的文本表格）"""
    rows = []
    lines = output.splitlines()
    header_line = None
    headers = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("+"):
            continue
        if "|" in line:
            parts = [p.strip() for p in line.strip("|").split("|")]
            if not headers:
                headers = parts
                header_line = line
            else:
                if len(parts) == len(headers):
                    rows.append(dict(zip(headers, parts)))
    return rows


def list_courses() -> list[CourseItem]:
    """列出已购课程"""
    result = runner.run(["course"], check=False)
    rows = _parse_table(result.stdout)
    items = []
    for r in rows:
        # 字段名可能是: ID, ClassID, Title/Name 等
        cid = r.get("ID", r.get("id", ""))
        class_id = r.get("ClassID", r.get("classid", r.get("class_id", "")))
        title = r.get("Title", r.get("title", r.get("Name", r.get("name", ""))))
        author = r.get("Author", r.get("author", ""))
        if cid or title:
            items.append(CourseItem(id=cid, class_id=class_id, title=title, author=author))
    return items


def get_course(course_id: str) -> str:
    """获取指定课程详情（原始输出）"""
    result = runner.run(["course", "-i", course_id], check=False)
    return result.stdout


def list_ebooks() -> list[EbookItem]:
    """列出已购电子书"""
    result = runner.run(["ebook"], check=False)
    rows = _parse_table(result.stdout)
    items = []
    for r in rows:
        eid = r.get("ID", r.get("id", ""))
        title = r.get("Title", r.get("title", r.get("Name", r.get("name", ""))))
        author = r.get("Author", r.get("author", ""))
        if eid or title:
            items.append(EbookItem(id=eid, title=title, author=author))
    return items


def list_audiobooks() -> list[AudiobookItem]:
    """列出已购每天听本书"""
    result = runner.run(["odob"], check=False)
    rows = _parse_table(result.stdout)
    items = []
    for r in rows:
        aid = r.get("ID", r.get("id", ""))
        title = r.get("Title", r.get("title", r.get("Name", r.get("name", ""))))
        author = r.get("Author", r.get("author", ""))
        if aid or title:
            items.append(AudiobookItem(id=aid, title=title, author=author))
    return items
