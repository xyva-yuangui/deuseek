"""Bilibili (bilibili.com) content fetcher via official API.

Uses B站's public video info API to get structured data (title, description,
play count, cover image) — more reliable than scraping the HTML page.
Falls back to Scrapling Fetcher if the API fails.

API endpoint: https://api.bilibili.com/x/web-interface/view
  GET ?bvid=BVxxxxxx → {data: {title, desc, stat: {view, like, ...}}}
"""

from __future__ import annotations

from deuseek.utils import now_iso as _now_iso

import re
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse, parse_qs



_BVID_RE = re.compile(r"(BV[a-zA-Z0-9]{10})")
_AVID_RE = re.compile(r"av(\d+)")


def _extract_ids(url: str) -> tuple[str | None, str | None]:
    """Extract bvid and avid from a bilibili URL."""
    bvid = None
    avid = None

    # Try path-based extraction
    m = _BVID_RE.search(url)
    if m:
        bvid = m.group(1)
    m = _AVID_RE.search(url, re.IGNORECASE)
    if m:
        avid = m.group(1)

    # Try query params
    parsed = parse_qs(urlparse(url).query)
    if not bvid and "bvid" in parsed:
        bvid = parsed["bvid"][0]
    if not avid and "aid" in parsed:
        avid = parsed["aid"][0]

    return bvid, avid


def is_available() -> bool:
    """B站 API is always available (no auth needed)."""
    return True


def fetch_bilibili(url: str, *, timeout: float = 15) -> dict[str, Any]:
    """Fetch Bilibili video info via official API.

    Returns markdown with video title, description, and stats.
    """
    import httpx

    t0 = time.time()
    bvid, avid = _extract_ids(url)

    if not bvid and not avid:
        return {
            "success": False,
            "content_markdown": "",
            "backend": "native_bilibili",
            "errors": ["could not extract bvid/avid from URL"],
            "fetched_at": _now_iso(),
        }

    # Call B站 API
    api_url = "https://api.bilibili.com/x/web-interface/view"
    params = {}
    if bvid:
        params["bvid"] = bvid
    elif avid:
        params["aid"] = avid

    try:
        with httpx.Client(timeout=timeout) as c:
            resp = c.get(api_url, params=params, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "Referer": "https://www.bilibili.com/",
            })
        elapsed = time.time() - t0

        if resp.status_code != 200:
            return {
                "success": False,
                "content_markdown": "",
                "backend": "native_bilibili",
                "status_code": resp.status_code,
                "elapsed_s": elapsed,
                "errors": [f"B站 API returned {resp.status_code}"],
                "fetched_at": _now_iso(),
            }

        data = resp.json()
        if data.get("code") != 0:
            return {
                "success": False,
                "content_markdown": "",
                "backend": "native_bilibili",
                "status_code": 200,
                "elapsed_s": elapsed,
                "errors": [f"B站 API error: {data.get('message', 'unknown')}"],
                "fetched_at": _now_iso(),
            }

        v = data.get("data", {})
        stat = v.get("stat", {})
        owner = v.get("owner", {})

        # Build markdown
        md = f"# {v.get('title', 'Untitled')}\n\n"
        md += f"**UP主**: {owner.get('name', 'N/A')}\n\n"
        desc = v.get("desc", "")
        if desc:
            md += f"**简介**:\n\n{desc}\n\n"
        md += f"**播放**: {stat.get('view', 'N/A')} · "
        md += f"**弹幕**: {stat.get('danmaku', 'N/A')} · "
        md += f"**点赞**: {stat.get('like', 'N/A')} · "
        md += f"**投币**: {stat.get('coin', 'N/A')} · "
        md += f"**收藏**: {stat.get('favorite', 'N/A')}\n\n"
        md += f"**链接**: {url}\n"

        return {
            "success": True,
            "content_markdown": md,
            "content_html": "",
            "backend": "native_bilibili",
            "status_code": 200,
            "elapsed_s": elapsed,
            "errors": [],
            "fetched_at": _now_iso(),
        }

    except Exception as e:  # noqa: BLE001
        return {
            "success": False,
            "content_markdown": "",
            "backend": "native_bilibili",
            "status_code": 0,
            "elapsed_s": time.time() - t0,
            "errors": [f"native_bilibili: {e}"],
            "fetched_at": _now_iso(),
        }
