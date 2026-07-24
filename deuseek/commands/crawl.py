"""deuseek crawl <url> — multi-page Spider crawl with Scrapling.

Wraps Scrapling's async Spider framework. Define start URL + extraction
rules, get structured items back. Supports concurrency, checkpoints,
and streaming output.

CLI:
    deuseek crawl https://quotes.toscrape.com/ --selector '.quote' \\
        --fields '{"text":".text::text","author":".author::text"}' \\
        --follow '.next a::attr(href)' --depth 3

    deuseek crawl https://example.com --stream --json
"""

from __future__ import annotations

import json as _json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel

from deuseek.contract import CrawlResult, CrawlStats
from deuseek.utils import should_emit_json as _should_emit_json, now_iso as _now_iso

console = Console()



@click.command("crawl")
@click.argument("url")
@click.option("--selector", "-s", default="", help="容器 CSS 选择器 (如 '.quote')")
@click.option("--fields", "-f", default="",
              help='字段映射 JSON: \'{"text":".text::text","author":".author::text"}\'')
@click.option("--follow", default="", help="跟进链接的 CSS 选择器 (如 '.next a::attr(href)')")
@click.option("--depth", type=int, default=1, help="最大爬取深度")
@click.option("--concurrent", type=int, default=4, help="并发请求数")
@click.option("--checkpoint", is_flag=True, help="启用断点续传")
@click.option("--checkpoint-dir", "checkpoint_dir", default="",
              help="checkpoint 目录 (默认: ~/.deuseek/crawl/<host>)")
@click.option("--stream", is_flag=True, help="流式 JSON Lines 输出")
@click.option("--json", "json_out", is_flag=True, help="输出 JSON (非流式)")
@click.option("--timeout", type=float, default=30.0, help="总超时秒数")
def crawl_cmd(url: str, selector: str, fields: str, follow: str,
              depth: int, concurrent: int, checkpoint: bool,
              checkpoint_dir: str, stream: bool, json_out: bool,
              timeout: float) -> None:
    """多页 Spider 爬取, 返回结构化 items.

    v0.11+: Scrapling Spider 框架 (async, concurrent, checkpoint, robots.txt).
    """
    # Parse fields
    field_map: dict[str, str] = {}
    if fields:
        try:
            field_map = _json.loads(fields)
        except _json.JSONDecodeError as e:
            console.print(f"[red]fields JSON 解析失败: {e}[/red]")
            raise SystemExit(1) from e
    elif selector:
        field_map = {"item": selector}

    if not field_map and not stream:
        console.print("[yellow]提示: 无 --selector/--fields, 将只爬取不提取[/yellow]")

    t0 = time.time()
    items: list[dict[str, Any]] = []
    stats_dict: dict[str, Any] = {}

    try:
        # Build a dynamic Spider subclass
        from scrapling.spiders import Spider, Request

        container_key = None
        clean_fields = dict(field_map)
        for k in list(clean_fields.keys()):
            if "::" not in clean_fields[k] and k in ("item", "container", "card", "row"):
                container_key = k
                del clean_fields[k]
                break

        import logging as _logging

        class DynamicSpider(Spider):
            name = "deuseek_crawl"
            start_urls = [url]
            concurrent_requests = concurrent
            logging_level = _logging.WARNING  # suppress DEBUG/INFO on stdout
            log_file = None  # don't write to file

            async def parse(self, response):
                if container_key and selector:
                    containers = response.css(selector)
                    for container in containers:
                        item = {}
                        for field, sel in clean_fields.items():
                            val = container.css(sel).get()
                            item[field] = str(val) if val else ""
                        if any(v for v in item.values()):
                            yield item

                elif clean_fields:
                    item = {}
                    for field, sel in clean_fields.items():
                        val = response.css(sel).get()
                        item[field] = str(val) if val else ""
                    if any(v for v in item.values()):
                        yield item

                # Follow links
                if follow:
                    next_links = response.css(follow).getall()
                    for link in next_links[:depth]:
                        if link:
                            yield response.follow(link)

        # Configure checkpoint
        crawldir = None
        if checkpoint:
            from pathlib import Path
            if checkpoint_dir:
                crawldir = Path(checkpoint_dir)
            else:
                from urllib.parse import urlparse
                host = urlparse(url).hostname or "default"
                crawldir = Path.home() / ".deuseek" / "crawl" / host

        spider = DynamicSpider(crawldir=crawldir)

        if stream:
            # Streaming mode: yield items as they come
            import asyncio

            async def _stream():
                async for item in spider.stream():
                    items.append(item)
                    line = _json.dumps(item, ensure_ascii=False, default=str)
                    click.echo(line)

            asyncio.run(_stream())
            stats_dict = spider.stats.to_dict() if hasattr(spider, 'stats') else {}
        else:
            # Batch mode
            result = spider.start()
            items = list(result.items)
            stats_dict = result.stats.to_dict()

    except ImportError as e:
        console.print(f"[red]Scrapling 未安装: {e}[/red]")
        raise SystemExit(1) from e
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]crawl 失败: {e}[/red]")
        if not stream:
            raise SystemExit(1)
        raise

    elapsed = time.time() - t0

    if stream:
        # Already streamed, just print stats
        if not _should_emit_json(json_out):
            console.print(Panel.fit(
                f"[cyan]{url}[/cyan]\n[dim]{len(items)} items · {elapsed:.1f}s · "
                f"{stats_dict.get('requests_count', 0)} requests[/dim]",
                title="deuseek crawl (streamed)",
            ))
        return

    result = CrawlResult(
        start_url=url,
        items=items,
        stats=CrawlStats(**{k: v for k, v in stats_dict.items()
                           if k in CrawlStats.model_fields}),
        elapsed_s=elapsed,
        completed=True,
        fetched_at=_now_iso(),
    )

    if _should_emit_json(json_out):
        click.echo(_json.dumps(result.model_dump(), ensure_ascii=False, default=str))
        return

    console.print(Panel.fit(
        f"[cyan]{url}[/cyan]\n[dim]{len(items)} items · {elapsed:.1f}s · "
        f"{stats_dict.get('requests_count', 0)} requests · "
        f"{stats_dict.get('failed_requests_count', 0)} failed[/dim]",
        title="deuseek crawl",
    ))

    # Show first few items
    for i, item in enumerate(items[:5]):
        console.print(f"  [dim]{i+1}.[/dim] {_json.dumps(item, ensure_ascii=False)[:120]}")
    if len(items) > 5:
        console.print(f"  [dim]…({len(items) - 5} more, 用 --json 拿全部)[/dim]")
