"""Simple file-based search cache with TTL."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

CACHE_DIR = Path.home() / ".deuseek" / "cache"
DEFAULT_TTL = 600  # 10 minutes


def _cache_key(source: str, query: str, limit: int) -> str:
    raw = f"{source}:{query}:{limit}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def get(source: str, query: str, limit: int, *, ttl: float = DEFAULT_TTL) -> list[dict] | None:
    key = _cache_key(source, query, limit)
    path = CACHE_DIR / f"{key}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    if time.time() - data.get("ts", 0) > ttl:
        path.unlink(missing_ok=True)
        return None
    return data.get("results")


def put(source: str, query: str, limit: int, results: list[dict]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = _cache_key(source, query, limit)
    path = CACHE_DIR / f"{key}.json"
    data = {"ts": time.time(), "source": source, "query": query, "results": results}
    path.write_text(json.dumps(data, ensure_ascii=False))


def clear() -> int:
    if not CACHE_DIR.exists():
        return 0
    count = 0
    for f in CACHE_DIR.glob("*.json"):
        f.unlink()
        count += 1
    return count
