"""B站 (Bilibili) adapter — free, uses Bilibili official search API."""

from __future__ import annotations

from deuseek.adapters.base import AdapterBase
from deuseek.adapters._bilibili_api import search_bilibili
from deuseek.contract import SearchResult


class BilibiliAdapter(AdapterBase):
    name = "bilibili"
    requires: list[str] = []

    async def is_ready(self) -> bool:
        return True

    async def search(self, query: str, *, limit: int = 10) -> list[SearchResult]:
        return await search_bilibili(query, limit=limit)
