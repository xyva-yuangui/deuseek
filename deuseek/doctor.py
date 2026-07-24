"""Doctor — per-source readiness check + fetch-backend probe."""

from __future__ import annotations

import shutil
from dataclasses import dataclass

from deuseek.registry import load_registry


@dataclass
class SourceStatus:
    id: str
    tier: str
    ok: bool
    detail: str
    fix_hint: str = ""


@dataclass
class FetchBackendStatus:
    tool: str
    ok: bool
    detail: str
    fix_hint: str = ""


BINARY_FOR_SOURCE = {
    "youtube": "yt-dlp",
    "github": "gh",
    "reddit": "rdt-cli",
}

FREE_BACKEND_DETAIL = {
    "web": "DuckDuckGo (ddgs)",
    "wechat": "Sogou 免费搜索 (httpx)",
    "bilibili": "B站官方 search API",
}


def run_fetch_backend_doctor() -> list[FetchBackendStatus]:
    out: list[FetchBackendStatus] = []
    try:
        from ddgs import DDGS  # noqa: F401
        out.append(FetchBackendStatus(
            tool="ddgs", ok=True,
            detail="ddgs extract — URL → Markdown",
        ))
    except ImportError:
        out.append(FetchBackendStatus(
            tool="ddgs", ok=False,
            detail="ddgs 未安装",
            fix_hint="pip install ddgs",
        ))
    out.append(FetchBackendStatus(
        tool="jina (r.jina.ai)",
        ok=True,
        detail="Jina Reader SaaS — 零配置 fallback",
    ))

    # Scrapling engines (v0.11+)
    try:
        from scrapling import Fetcher  # noqa: F401
        out.append(FetchBackendStatus(
            tool="scrapling:Fetcher",
            ok=True,
            detail="curl_cffi HTTP — 默认引擎 (0.4-3.9s)",
        ))
    except ImportError:
        out.append(FetchBackendStatus(
            tool="scrapling:Fetcher",
            ok=False,
            detail="scrapling 未安装",
            fix_hint="pip install scrapling",
        ))

    try:
        from scrapling import StealthyFetcher  # noqa: F401
        import patchright  # noqa: F401
        out.append(FetchBackendStatus(
            tool="scrapling:StealthyFetcher",
            ok=True,
            detail="patchright Chrome — Cloudflare 绕过 (solve_cloudflare)",
        ))
    except ImportError:
        out.append(FetchBackendStatus(
            tool="scrapling:StealthyFetcher",
            ok=False,
            detail="patchright 未安装",
            fix_hint="pip install patchright && patchright install chromium",
        ))

    try:
        from scrapling import DynamicFetcher  # noqa: F401
        import playwright  # noqa: F401
        out.append(FetchBackendStatus(
            tool="scrapling:DynamicFetcher",
            ok=True,
            detail="Playwright Chrome — JS 渲染",
        ))
    except ImportError:
        out.append(FetchBackendStatus(
            tool="scrapling:DynamicFetcher",
            ok=False,
            detail="playwright 未安装",
            fix_hint="pip install playwright && playwright install chromium",
        ))

    # BrowserPool warm status
    try:
        from deuseek.perf.browser_pool import BrowserPool
        stealthy_warm = BrowserPool._stealthy_session is not None
        dynamic_warm = BrowserPool._dynamic_session is not None
        status = []
        if stealthy_warm:
            status.append("stealthy warm")
        if dynamic_warm:
            status.append("dynamic warm")
        detail = ", ".join(status) if status else "not warmed up (cold start on first fetch)"
        out.append(FetchBackendStatus(
            tool="BrowserPool",
            ok=True,
            detail=detail,
        ))
    except ImportError:
        pass  # BrowserPool not available

    return out


async def run_doctor() -> list[SourceStatus]:
    reg = load_registry()
    statuses: list[SourceStatus] = []
    for spec in reg.sources:
        sid = spec.id
        if sid == "hackernews":
            statuses.append(SourceStatus(sid, spec.tier, ok=True,
                detail="HTTP API (Algolia)"))
            continue
        if sid == "rss":
            statuses.append(SourceStatus(sid, spec.tier, ok=True,
                detail="feedparser (内置)"))
            continue
        if sid in BINARY_FOR_SOURCE:
            binary = BINARY_FOR_SOURCE[sid]
            if shutil.which(binary):
                statuses.append(SourceStatus(sid, spec.tier, ok=True,
                    detail=f"{binary} 在 PATH"))
            else:
                statuses.append(SourceStatus(sid, spec.tier, ok=False,
                    detail=f"{binary} 不在 PATH",
                    fix_hint=f"deuseek setup {sid}"))
            continue
        if sid in FREE_BACKEND_DETAIL:
            statuses.append(SourceStatus(sid, spec.tier, ok=True,
                detail=FREE_BACKEND_DETAIL[sid]))
            continue
        statuses.append(SourceStatus(sid, spec.tier, ok=False,
            detail="未实现", fix_hint=""))
    return statuses
