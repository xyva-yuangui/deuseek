"""Dispatcher — concurrent fan-out across adapters, errors isolated, with cache."""

from __future__ import annotations

import asyncio

from deuseek.adapters.base import AdapterBase, AdapterUnavailable
from deuseek import cache
from deuseek.contract import SearchResult, SourceError


class Dispatcher:
    def __init__(
        self,
        *,
        timeout: float = 15.0,
        per_source_limit: int = 10,
        timeouts_by_source: dict[str, float | None] | None = None,
        use_cache: bool = True,
    ) -> None:
        self.timeout = timeout
        self.per_source_limit = per_source_limit
        self.timeouts_by_source = timeouts_by_source or {}
        self.use_cache = use_cache

    def _resolved_timeout(self, source_id: str) -> float:
        t = self.timeouts_by_source.get(source_id)
        return t if t is not None else self.timeout

    async def one(
        self, name: str, adapter: AdapterBase, query: str
    ) -> tuple[str, list[SearchResult] | SourceError]:
        """Search a single adapter with cache, timeout, and error isolation.

        Exposed publicly so callers that need streaming/pipeline semantics
        (e.g. ``asyncio.as_completed``) can fan out per-adapter without
        reimplementing the cache/timeout/error logic that ``run`` uses.
        """
        if self.use_cache:
            cached = cache.get(name, query, self.per_source_limit)
            if cached is not None:
                return name, [SearchResult.model_validate(r) for r in cached]

        resolved = self._resolved_timeout(name)
        try:
            results = await asyncio.wait_for(
                adapter.search(query, limit=self.per_source_limit), timeout=resolved
            )
            if self.use_cache and results:
                cache.put(name, query, self.per_source_limit,
                          [r.model_dump() for r in results])
            return name, results
        except asyncio.TimeoutError:
            return name, SourceError(
                source=name,
                error=f"timeout (>{resolved:.1f}s)",
                category="failed",
            )
        except AdapterUnavailable as e:
            return name, SourceError(
                source=name, error=str(e), category="unavailable"
            )
        except Exception as e:  # noqa: BLE001
            return name, SourceError(source=name, error=str(e), category="failed")

    async def run(
        self, adapters: dict[str, AdapterBase], query: str
    ) -> tuple[list[SearchResult], list[SourceError]]:
        outputs = await asyncio.gather(
            *[self.one(n, a, query) for n, a in adapters.items()]
        )

        all_results: list[SearchResult] = []
        errors: list[SourceError] = []
        for _name, payload in outputs:
            if isinstance(payload, list):
                all_results.extend(payload)
            else:
                errors.append(payload)
        return all_results, errors
