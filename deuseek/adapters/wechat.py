"""WeChat 公众号 adapter — free, uses Sogou weixin search."""

from __future__ import annotations

from deuseek.adapters.base import AdapterBase
from deuseek.adapters._wechat_sogou import search_sogou
from deuseek.contract import SearchResult


class WeChatAdapter(AdapterBase):
    name = "wechat"
    requires: list[str] = []

    async def is_ready(self) -> bool:
        return True

    async def search(self, query: str, *, limit: int = 10) -> list[SearchResult]:
        return await search_sogou(query, limit=limit)
