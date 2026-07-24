"""Web search adapter — uses ddgs (DuckDuckGo metasearch), zero config."""

from __future__ import annotations

import asyncio

from deuseek.adapters.base import AdapterBase, AdapterUnavailable
from deuseek.contract import SearchResult


class WebSearchAdapter(AdapterBase):
    name = "web"
    requires: list[str] = []

    async def is_ready(self) -> bool:
        return True

    async def search(self, query: str, *, limit: int = 10) -> list[SearchResult]:
        try:
            from ddgs import DDGS
        except ImportError as e:
            raise AdapterUnavailable(
                "web", "ddgs 未安装", hint="pip install ddgs"
            ) from e

        try:
            hits = await asyncio.to_thread(
                DDGS(timeout=10).text, query, max_results=limit
            )
        except Exception as e:  # noqa: BLE001
            raise AdapterUnavailable("web", f"ddgs error: {e}") from e

        results: list[SearchResult] = []
        for hit in (hits or [])[:limit]:
            results.append(
                SearchResult(
                    source="web",
                    adapter="ddgs",
                    title=hit.get("title", ""),
                    url=hit.get("href", ""),
                    content=hit.get("body", ""),
                    score=0.5,
                    raw=hit,
                )
            )
        return results
