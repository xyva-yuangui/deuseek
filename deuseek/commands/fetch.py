"""deuseek fetch <url> — get full markdown content from a URL.

Data-driven routing (v0.11+):
  auto: Fetcher (0.4-3.9s) → jina (2.2-5.7s) → StealthyFetcher+CF (37s)
  DomainKB remembers which backend works per domain.
  Native paths for wechat/bilibili/douyin.

CLI:
    deuseek fetch <url>                           # auto routing
    deuseek fetch <url> --backend fetcher         # force basic HTTP
    deuseek fetch <url> --backend stealthy        # force stealth Chrome
    deuseek fetch <url> --backend dynamic         # force JS rendering
    deuseek fetch <url> --backend jina            # force Jina SaaS
    deuseek fetch <url> --solve-cloudflare       # enable CF bypass
    deuseek fetch <url> --full                    # full page (not main-only)
    deuseek fetch <url> --json                    # JSON envelope
"""

from __future__ import annotations

import json as _json
import os
import sys
from datetime import datetime, timezone

import click
import httpx
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from deuseek.contract import FetchEnvelope
from deuseek.utils import should_emit_json as _should_emit_json, now_iso as _now_iso
from deuseek.engines import FetcherEngine, StealthyEngine, DynamicEngine
from deuseek.perf.cache import Cache
from deuseek.fetch_router.router import FetchRouter

console = Console()

JINA_BASE = "https://r.jina.ai/"

CAPTCHA_KEYWORDS = (
    "环境异常",
    "完成验证后即可继续访问",
    "请输入验证码",
    "请完成安全验证",
    "Cloudflare",
    "Just a moment",
    "Checking your browser",
)



def _looks_like_captcha(markdown: str) -> tuple[bool, str | None]:
    if len(markdown) < 200:
        return False, None
    for kw in CAPTCHA_KEYWORDS:
        if kw in markdown:
            return True, kw
    return False, None


def _fetch_via_jina(url: str, timeout: float) -> tuple[str, int]:
    """Jina Reader SaaS — fallback backend with server-side IP."""
    target = JINA_BASE + url
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as c:
            resp = c.get(target, headers={"Accept": "text/markdown"})
    except httpx.HTTPError as e:
        raise RuntimeError(f"jina http error: {e}") from e
    if resp.status_code >= 400:
        raise RuntimeError(f"jina 返回 {resp.status_code}")
    if not resp.text.strip():
        raise RuntimeError("jina 返回空内容")
    return resp.text, resp.status_code


def _execute_backend(
    backend: str,
    url: str,
    *,
    solve_cloudflare: bool = False,
    full: bool = False,
    timeout: float = 15,
) -> tuple[str, int, str, bool, list, dict | None]:
    """Execute a single backend, return (markdown, status_code, backend_label, success, sections, content_stats)."""
    main_only = not full
    label = backend

    if backend == "fetcher":
        r = FetcherEngine.fetch(url, timeout=timeout, main_content_only=main_only)
        return r.content_markdown, r.status_code, label, r.success, r.sections, r.content_stats

    elif backend == "stealthy":
        r = StealthyEngine.fetch(
            url,
            solve_cloudflare=solve_cloudflare,
            main_content_only=main_only,
            timeout=int(timeout * 1000),
        )
        return r.content_markdown, r.status_code, label, r.success, r.sections, r.content_stats

    elif backend == "dynamic":
        r = DynamicEngine.fetch(
            url,
            main_content_only=main_only,
            timeout=int(timeout * 1000),
        )
        return r.content_markdown, r.status_code, label, r.success, r.sections, r.content_stats

    elif backend == "jina":
        try:
            md, status = _fetch_via_jina(url, timeout)
            return md, status, label, bool(md) and len(md) > 50, [], None
        except Exception:
            return "", 0, label, False, [], None

    elif backend.startswith("native"):
        from deuseek.native import native_fetch
        result = native_fetch(url, timeout=timeout)
        return (
            result.get("content_markdown", ""),
            result.get("status_code", 0),
            result.get("backend", label),
            result.get("success", False),
            [],
            None,
        )

    else:
        return "", 0, label, False, [], None


@click.command("fetch")
@click.argument("url")
@click.option("--backend", type=click.Choice(
    ["auto", "fetcher", "stealthy", "dynamic", "jina", "native"],
), default="auto", help="auto=router决策; 或显式指定")
@click.option("--json", "json_out", is_flag=True, help="输出 JSON envelope")
@click.option("--solve-cloudflare", "solve_cloudflare", is_flag=True,
              help="启用 Cloudflare Turnstile 绕过 (stealthy backend only)")
@click.option("--full", is_flag=True, help="转换整页 HTML (默认只取正文 main_content)")
@click.option("--timeout", type=float, default=15.0, help="单 backend 超时秒数")
@click.option("--no-cache", is_flag=True, help="跳过缓存")
def fetch_cmd(url: str, backend: str, json_out: bool,
              solve_cloudflare: bool, full: bool,
              timeout: float, no_cache: bool) -> None:
    """获取 URL 的全文 markdown.

    v0.11+: Scrapling 引擎加持, 三车道路由 (Fetcher → jina → Stealthy+CF).
    DomainKB 记住域名→后端映射, 避免每次试错.

    示例:
        deuseek fetch https://example.com/article
        deuseek fetch https://example.com/article --backend stealthy --solve-cloudflare
    """
    router = FetchRouter()
    route = router.route(
        url, explicit_backend=backend if backend != "auto" else None,
        solve_cloudflare=solve_cloudflare,
    )

    # Check cache first
    if not no_cache:
        cached = Cache.get_fetch(url)
        if cached and cached.get("content_markdown"):
            if _should_emit_json(json_out):
                envelope = FetchEnvelope(
                    url=url,
                    backend=cached.get("backend", "cached"),
                    fetched_at=cached.get("fetched_at", _now_iso()),
                    content_markdown=cached["content_markdown"],
                    status_code=cached.get("status_code", 200),
                    sections=cached.get("sections", []),
                    content_stats=cached.get("content_stats"),
                    errors=["cache_hit"],
                )
                click.echo(_json.dumps(envelope.model_dump(), ensure_ascii=False))
                return
            console.print(Panel.fit(
                f"[cyan]{url}[/cyan]\n[dim]backend: cached[/dim]",
                title="deuseek fetch (cached)",
            ))
            console.print(Markdown(cached["content_markdown"][:5000]))
            return

    # Execute primary backend, then fallback chain
    backends_to_try = [route.backend] + route.fallback_chain
    # Deduplicate while preserving order
    seen: set[str] = set()
    backends_to_try = [b for b in backends_to_try if not (b in seen or seen.add(b))]

    content = ""
    used_backend = ""
    status_code = 0
    errors: list[str] = []
    sections: list = []
    stats: dict | None = None

    for b in backends_to_try:
        # Native backends are handled by the native module
        if b.startswith("native"):
            pass  # _execute_backend handles it via native_fetch()
        elif b == "stealthy" and not StealthyEngine.is_available():
            errors.append("stealthy: patchright not installed")
            continue

        try:
            md, status, label, success, sections, stats = _execute_backend(
                b, url,
                solve_cloudflare=route.solve_cloudflare,
                full=full,
                timeout=timeout,
            )
            used_backend = label

            if success and md and len(md) > 50:
                content = md
                status_code = status
                # Record success in DomainKB
                router.record_success(url, b)
                break
            else:
                errors.append(f"{b}: {'empty' if not md else f'status {status}'}")
                router.record_failure(url, b)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{b}: {e}")
            router.record_failure(url, b)

    # Captcha detection → auto-upgrade to StealthyFetcher+CF if available
    if content:
        suspicious, kw = _looks_like_captcha(content)
        if suspicious:
            errors.append(
                f"captcha_suspected: {used_backend} 返回内容包含验证页关键词 '{kw}'"
            )
            # Auto-upgrade: if stealthy wasn't tried and is available, retry with CF
            if used_backend != "stealthy" and StealthyEngine.is_available():
                try:
                    md, status, label, success, sections, stats = _execute_backend(
                        "stealthy", url,
                        solve_cloudflare=True,
                        full=full,
                        timeout=max(timeout, 30),  # CF solve needs more time
                    )
                    if success and md and len(md) > 50:
                        content = md
                        status_code = status
                        used_backend = label
                        errors.append("auto_upgraded: stealthy+solve_cloudflare succeeded")
                    else:
                        errors.append("auto_upgrade_failed: stealthy+CF also failed")
                except Exception as e:  # noqa: BLE001
                    errors.append(f"auto_upgrade_error: {e}")

    envelope = FetchEnvelope(
        url=url,
        backend=used_backend or None,
        fetched_at=_now_iso(),
        content_markdown=content,
        status_code=status_code,
        sections=sections,
        content_stats=stats,
        errors=errors,
    )

    # Cache successful fetches
    if content and used_backend and not no_cache:
        Cache.put_fetch(url, envelope.model_dump())

    if _should_emit_json(json_out):
        click.echo(_json.dumps(envelope.model_dump(), ensure_ascii=False))
        return

    if not content:
        for e in errors:
            console.print(f"[red]✗ {e}[/red]")
        raise SystemExit(1)

    console.print(Panel.fit(
        f"[cyan]{url}[/cyan]\n[dim]backend: {used_backend} · status: {status_code} · "
        f"{len(content)} chars · route: {route.rationale}[/dim]",
        title="deuseek fetch",
    ))
    preview = content[:5000]
    if len(content) > 5000:
        preview += "\n\n…(truncated; 用 --json 拿完整内容)"
    console.print(Markdown(preview))
