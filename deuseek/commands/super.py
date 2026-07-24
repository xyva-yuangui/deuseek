"""deuseek super "<query>" — end-to-end search → fetch → extract pipeline.

The flagship command: say one query, get structured content from multiple
sources with Scrapling-powered stealth fetching. Streams results as they
arrive (fast results don't wait for slow ones).

Pipeline (v0.11.1 — true pipeline mode, not serial):
  1. search → multi-source aggregate, results stream as each adapter returns
  2. fetch → starts immediately on first URL, overlaps with remaining searches
  3. (optional) extract → structured fields per page

CLI:
    deuseek super "iPhone 16 评测"
    deuseek super "Python asyncio" --sources hackernews,web --stream
    deuseek super "React 19" --extract-fields '{"title":"h1::text"}'
"""

from __future__ import annotations

import asyncio
import json as _json
import time
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel

from deuseek.contract import FetchEnvelope
from deuseek.engines import FetcherEngine, StealthyEngine
from deuseek.perf.cache import Cache
from deuseek.fetch_router.router import FetchRouter
from deuseek.utils import should_emit_json as _should_emit_json, now_iso as _now_iso

console = Console()


async def _fetch_one(
    url: str,
    router: FetchRouter,
    *,
    full: bool = False,
    timeout: float = 15,
    sem: asyncio.Semaphore,
) -> dict[str, Any]:
    """Fetch a single URL through the router, return result dict."""
    async with sem:
        route = router.route(url)

        backends = [route.backend] + route.fallback_chain
        seen: set[str] = set()
        backends = [b for b in backends if not (b in seen or seen.add(b))]

        for b in backends:
            if b.startswith("native"):
                continue
            if b == "stealthy" and not StealthyEngine.is_available():
                continue

            loop = asyncio.get_event_loop()
            if b == "fetcher":
                r = await loop.run_in_executor(
                    None, lambda: FetcherEngine.fetch(url, timeout=timeout, main_content_only=not full)
                )
                r = r.model_dump() if hasattr(r, "model_dump") else r
            elif b == "stealthy":
                r = await loop.run_in_executor(
                    None, lambda: StealthyEngine.fetch(
                        url, solve_cloudflare=route.solve_cloudflare,
                        main_content_only=not full, timeout=int(timeout * 1000),
                    )
                )
                r = r.model_dump() if hasattr(r, "model_dump") else r
            elif b == "jina":
                r = await loop.run_in_executor(None, lambda: _fetch_jina(url, timeout))
            else:
                continue

            if r.get("success") and r.get("content_markdown"):
                router.record_success(url, b)
                return {
                    "url": url, "backend": b, "success": True,
                    "content_markdown": r["content_markdown"],
                    "status_code": r.get("status_code", 0),
                    "elapsed_s": r.get("elapsed_s", 0),
                    "errors": [],
                    "sections": r.get("sections", []),
                    "content_stats": r.get("content_stats"),
                }
            else:
                router.record_failure(url, b)

        return {
            "url": url, "backend": None, "success": False,
            "content_markdown": "", "status_code": 0,
            "elapsed_s": 0, "errors": ["all backends failed"],
        }


def _fetch_jina(url: str, timeout: float) -> dict:
    """Jina Reader fallback."""
    import httpx
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as c:
            resp = c.get(f"https://r.jina.ai/{url}", headers={"Accept": "text/markdown"})
        md = resp.text
        return {
            "success": resp.status_code < 400 and len(md) > 50,
            "content_markdown": md,
            "status_code": resp.status_code,
            "elapsed_s": 0,
            "sections": [],
            "content_stats": None,
        }
    except Exception as e:
        return {"success": False, "content_markdown": "", "status_code": 0,
                "elapsed_s": 0, "errors": [str(e)],
                "sections": [], "content_stats": None}


def _dedup_fetch_results(results: list[dict]) -> list[dict]:
    """Detect near-duplicate content across sources and merge them.

    Uses difflib.SequenceMatcher on first 500 chars of content.
    If similarity > 0.85, the later result is dropped and its URL
    is added to the earlier result's duplicate_urls list.
    """
    from difflib import SequenceMatcher
    deduped = []
    for r in results:
        if not r.get("success") or not r.get("content_markdown"):
            deduped.append(r)
            continue
        is_dup = False
        for d in deduped:
            if not d.get("success") or not d.get("content_markdown"):
                continue
            ratio = SequenceMatcher(None,
                r["content_markdown"][:500],
                d["content_markdown"][:500]
            ).ratio()
            if ratio > 0.85:
                d.setdefault("duplicate_urls", []).append(r["url"])
                is_dup = True
                break
        if not is_dup:
            deduped.append(r)
    return deduped


async def _run_pipeline(
    query: str,
    adapters: dict[str, Any],
    *,
    limit: int = 10,
    concurrent: int = 5,
    full: bool = False,
    timeout: float = 15,
    no_cache: bool = False,
    stream: bool = False,
    json_out: bool = False,
):
    """Single-async pipeline: search streams into fetch, results stream out.

    v0.11.1: Replaces the old serial (search-all → fetch-all) with a true
    pipeline where fetching starts as soon as the first search result arrives.
    Expected ~40% total time reduction (11s → ~6-7s).
    """
    from deuseek.dispatcher import Dispatcher

    fetch_router = FetchRouter()
    sem = asyncio.Semaphore(concurrent)

    all_search_results = []
    all_search_errors = []
    fetch_results = []
    fetch_tasks: list[asyncio.Task] = []
    seen_urls: set[str] = set()

    # ---- Phase 1: Search (streaming per-adapter) ----
    dispatcher = Dispatcher(timeout=15, per_source_limit=limit)

    async def _search_one_adapter(name: str, adapter):
        """Search one adapter via Dispatcher (handles cache + timeout + errors).

        Delegates to ``Dispatcher.one`` so the pipeline reuses the same cache
        get/put, per-source timeout, and SourceError isolation as ``Dispatcher.run``,
        instead of reimplementing that logic here. Still a coroutine so the
        ``asyncio.as_completed`` pipeline keeps streaming results per-adapter.
        """
        return await dispatcher.one(name, adapter, query)

    # Start all adapter searches concurrently
    search_coros = [_search_one_adapter(n, a) for n, a in adapters.items()]

    # As each search completes, immediately start fetching its URLs
    for coro in asyncio.as_completed(search_coros):
        name, payload = await coro
        if isinstance(payload, list):
            all_search_results.extend(payload)
            # Queue fetch tasks for new URLs
            for r in payload:
                if r.url and r.url not in seen_urls:
                    seen_urls.add(r.url)
                    task = asyncio.create_task(
                        _fetch_one(r.url, fetch_router, full=full, timeout=timeout, sem=sem)
                    )
                    fetch_tasks.append(task)

                    # Stream search discovery
                    if stream:
                        line = _json.dumps({
                            "type": "search_hit",
                            "source": r.source,
                            "title": r.title[:80],
                            "url": r.url,
                            "ts": _now_iso(),
                        }, ensure_ascii=False)
                        click.echo(line)
        else:
            all_search_errors.append(payload)

    # ---- Phase 2: Fetch (already started, collect results) ----
    for coro in asyncio.as_completed(fetch_tasks):
        result = await coro
        fetch_results.append(result)

        # Cache successful fetches
        if result["success"] and not no_cache:
            Cache.put_fetch(result["url"], result)

        # Stream fetch results
        if stream:
            line = _json.dumps({
                "type": "fetch_result",
                "url": result["url"],
                "backend": result["backend"],
                "success": result["success"],
                "content_len": len(result.get("content_markdown", "")),
                "elapsed_s": result.get("elapsed_s", 0),
                "ts": _now_iso(),
            }, ensure_ascii=False)
            click.echo(line)

    # ---- Cross-source content dedup ----
    fetch_results = _dedup_fetch_results(fetch_results)

    return all_search_results, all_search_errors, fetch_results


@click.command("super")
@click.argument("query")
@click.option("--sources", default="", help="指定搜索源, 逗号分隔 (如 'hackernews,web')")
@click.option("--limit", type=int, default=10, help="搜索结果数上限")
@click.option("--extract-fields", "extract_fields", default="",
              help="提取字段 JSON (如 '{\"title\":\"h1::text\"}')")
@click.option("--stream", is_flag=True, help="流式 JSON Lines 输出")
@click.option("--full", is_flag=True, help="整页 HTML 转换")
@click.option("--json", "json_out", is_flag=True, help="输出 JSON")
@click.option("--timeout", type=float, default=15.0, help="单页超时秒数")
@click.option("--concurrent", type=int, default=5, help="并行抓取数")
@click.option("--no-cache", is_flag=True, help="跳过缓存")
def super_cmd(query: str, sources: str, limit: int, extract_fields: str,
              stream: bool, full: bool, json_out: bool,
              timeout: float, concurrent: int, no_cache: bool) -> None:
    """超级搜索: 多源搜索 → Scrapling 隐身抓取 → 结构化提取 → 一站式.

    v0.11.1: 真正的 pipeline 模式 — 搜索结果流式到达即开始抓取,
    不等全部搜索完成. 总时间从 search+fetch 降到 max(search, fetch).
    """
    t0 = time.time()

    # ---- Load search adapters ----
    from deuseek.registry import load_registry
    from deuseek.router import RouteRequest, Router as SearchRouter

    registry = load_registry()
    router_search = SearchRouter(registry)

    explicit_sources = [s.strip() for s in sources.split(",")] if sources else None
    route_req = RouteRequest(query=query, explicit_sources=explicit_sources)
    route = router_search.plan(route_req)

    adapters: dict[str, Any] = {}
    for sid in route.source_ids:
        try:
            spec = registry.get(sid)
            cls = spec.load_adapter_class()
            adapters[sid] = cls()
        except Exception:
            pass

    if not adapters:
        console.print("[red]没有可用的搜索源[/red]")
        raise SystemExit(1)

    # ---- Run single-async pipeline (search → fetch overlapped) ----
    search_results, search_errors, fetch_results = asyncio.run(
        _run_pipeline(
            query, adapters,
            limit=limit, concurrent=concurrent,
            full=full, timeout=timeout,
            no_cache=no_cache, stream=stream, json_out=json_out,
        )
    )

    elapsed = time.time() - t0
    urls_count = len(fetch_results)
    ok_count = sum(1 for r in fetch_results if r["success"])

    if not fetch_results:
        console.print("[red]搜索未返回任何可抓取的 URL[/red]")
        raise SystemExit(1)

    # ---- Output ----
    if stream:
        summary = _json.dumps({
            "type": "done",
            "query": query,
            "total_urls": urls_count,
            "ok": ok_count,
            "failed": urls_count - ok_count,
            "elapsed_s": elapsed,
            "ts": _now_iso(),
        }, ensure_ascii=False)
        click.echo(summary)
        return

    if _should_emit_json(json_out):
        envelope = {
            "query": query,
            "ts": _now_iso(),
            "search_results": [r.model_dump() for r in search_results],
            "fetch_results": fetch_results,
            "stats": {
                "total_urls": urls_count,
                "ok": ok_count,
                "failed": urls_count - ok_count,
                "elapsed_s": elapsed,
            },
        }
        click.echo(_json.dumps(envelope, ensure_ascii=False, default=str))
        return

    # Rich terminal output
    console.print(Panel.fit(
        f"[bold]deuseek super: {query}[/bold]\n[dim]"
        f"search: {urls_count} URLs from {len(adapters)} sources · "
        f"fetched: {ok_count}/{urls_count} ok · {elapsed:.1f}s[/dim]",
        title="deuseek super",
    ))

    for r in fetch_results:
        icon = "✅" if r["success"] else "❌"
        md_len = len(r.get("content_markdown", ""))
        console.print(f"  {icon} [{r.get('backend', '?')}] {r['url'][:60]}... ({md_len} chars)")

    console.print(f"\n[dim]用 --json 拿完整内容, --stream 流式输出[/dim]")
