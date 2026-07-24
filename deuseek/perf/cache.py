"""Cache — L1 memory + L2 disk cache for search results and fetched content.

L1: in-process dict (millisecond hits, cleared on restart).
L2: file-based JSON (persistent, TTL-based expiry).

Two cache namespaces:
- search: keyed by (source, query, limit) — delegates to existing cache.py
- fetch: keyed by URL — caches FetchResult content_markdown with content hash
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse

# Reuse the existing cache.py for search results
from deuseek import cache as _search_cache

DEFAULT_TTL = 600  # 10 minutes — matches existing search cache
FETCH_TTL = 3600   # 1 hour for fetched content (pages change less often)

# Query parameters that carry no content meaning — stripped during URL
# canonicalization so that the same page reached via different trackers
# (utm_source, fbclid, gclid, mailchimp ids, …) shares one cache entry.
_TRACKING_PARAMS = frozenset({
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
})


class Cache:
    """Thread-safe two-level cache: L1 memory → L2 disk."""

    _l1_search: dict[str, tuple[float, list[dict]]] = {}
    _l1_fetch: dict[str, tuple[float, dict]] = {}
    _lock = threading.Lock()

    # ---- Search cache (delegates to existing cache.py with L1 overlay) ----

    @classmethod
    def get_search(
        cls, source: str, query: str, limit: int, *, ttl: float = DEFAULT_TTL
    ) -> list[dict] | None:
        """Get cached search results. L1 → L2."""
        key = f"{source}:{query}:{limit}"
        # L1
        with cls._lock:
            entry = cls._l1_search.get(key)
            if entry and time.time() - entry[0] <= ttl:
                return entry[1]
        # L2
        results = _search_cache.get(source, query, limit, ttl=ttl)
        if results is not None:
            with cls._lock:
                cls._l1_search[key] = (time.time(), results)
        return results

    @classmethod
    def put_search(cls, source: str, query: str, limit: int, results: list[dict]) -> None:
        """Cache search results in both L1 and L2."""
        key = f"{source}:{query}:{limit}"
        with cls._lock:
            cls._l1_search[key] = (time.time(), results)
        _search_cache.put(source, query, limit, results)

    # ---- Fetch cache (URL → content, L1 + L2) ----

    @staticmethod
    def _canonicalize_url(url: str) -> str:
        """Normalize a URL so tracking variants share one cache entry.

        Strips tracking query params (utm_*, fbclid, gclid, mc_cid, mc_eid),
        removes the fragment, and sorts the remaining query params so that
        different orderings of the same params canonicalize identically.
        """
        parsed = urlparse(url)
        kept = [
            (k, v)
            for k, v in parse_qsl(parsed.query, keep_blank_values=True)
            if k not in _TRACKING_PARAMS
        ]
        kept.sort()
        query = urlencode(kept)
        return parsed._replace(query=query, fragment="").geturl()

    @classmethod
    def _fetch_key(cls, url: str) -> str:
        return hashlib.sha256(cls._canonicalize_url(url).encode()).hexdigest()[:16]

    @staticmethod
    def _fetch_dir() -> Path:
        return _search_cache.CACHE_DIR / "fetch"

    @classmethod
    def get_fetch(cls, url: str, *, ttl: float = FETCH_TTL) -> dict | None:
        """Get cached fetch result by URL."""
        key = cls._fetch_key(url)
        # L1
        with cls._lock:
            entry = cls._l1_fetch.get(key)
            if entry and time.time() - entry[0] <= ttl:
                return entry[1]
        # L2
        path = cls._fetch_dir() / f"{key}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        if time.time() - data.get("ts", 0) > ttl:
            path.unlink(missing_ok=True)
            return None
        result = data.get("result")
        if result is not None:
            with cls._lock:
                cls._l1_fetch[key] = (time.time(), result)
        return result

    @classmethod
    def put_fetch(cls, url: str, result: dict) -> None:
        """Cache a fetch result by URL."""
        key = cls._fetch_key(url)
        with cls._lock:
            cls._l1_fetch[key] = (time.time(), result)
        try:
            d = cls._fetch_dir()
            d.mkdir(parents=True, exist_ok=True)
            path = d / f"{key}.json"
            path.write_text(
                json.dumps({"ts": time.time(), "url": url, "result": result},
                           ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError:
            pass  # Best-effort

    # ---- Maintenance ----

    @classmethod
    def clear(cls) -> int:
        """Clear all caches (L1 + L2). Returns number of L2 files removed."""
        with cls._lock:
            cls._l1_search.clear()
            cls._l1_fetch.clear()
        n = _search_cache.clear()
        # Also clear fetch cache dir
        fetch_dir = cls._fetch_dir()
        if fetch_dir.exists():
            for f in fetch_dir.glob("*.json"):
                f.unlink()
                n += 1
        return n

    @classmethod
    def warm_fetch(cls, url: str, result: Any) -> None:
        """Warm the cache with a pre-fetched result (alias for put_fetch)."""
        if hasattr(result, "model_dump"):
            result = result.model_dump()
        cls.put_fetch(url, result if isinstance(result, dict) else {})
