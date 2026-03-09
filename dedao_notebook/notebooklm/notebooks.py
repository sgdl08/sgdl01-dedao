"""NotebookLM 笔记本管理"""

import asyncio
from dataclasses import dataclass

from dedao_notebook.notebooklm.auth import get_auth_file


@dataclass
class Notebook:
    id: str
    title: str


async def _get_client():
    from notebooklm import NotebookLMClient
    return await NotebookLMClient.from_storage(str(get_auth_file()))


async def list_notebooks_async() -> list[Notebook]:
    client = await _get_client()
    notebooks = await client.notebooks.list()
    return [Notebook(id=nb.id, title=nb.title) for nb in notebooks]


async def create_notebook_async(title: str) -> Notebook:
    client = await _get_client()
    nb = await client.notebooks.create(title)
    return Notebook(id=nb.id, title=nb.title)


async def get_or_create_async(title: str) -> Notebook:
    """查找同名笔记本，不存在则创建"""
    notebooks = await list_notebooks_async()
    for nb in notebooks:
        if nb.title == title:
            return nb
    return await create_notebook_async(title)


def list_notebooks() -> list[Notebook]:
    return asyncio.run(list_notebooks_async())


def create_notebook(title: str) -> Notebook:
    return asyncio.run(create_notebook_async(title))


def get_or_create(title: str) -> Notebook:
    return asyncio.run(get_or_create_async(title))
