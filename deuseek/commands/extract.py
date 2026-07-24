"""deuseek extract <url> — structured data extraction with adaptive parser.

Uses Scrapling's adaptive parser to extract specific fields from a page.
When the page DOM changes, the parser auto-relocates elements using
similarity algorithms (auto_save + adaptive=True).

CLI:
    deuseek extract <url> --selector '.price::text'
    deuseek extract <url> -f '{"title":"h1::text","price":".price::text"}'
    deuseek extract <url> -f '{"item":".product","name":".name::text","price":".price::text"}'
    deuseek extract <url> --selector '.quote' --adaptive --auto-save
    deuseek extract <url> --find-similar '.product-card'
"""

from __future__ import annotations

import json as _json
import os
import sys
from datetime import datetime, timezone

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from deuseek.contract import ExtractResult
from deuseek.utils import should_emit_json as _should_emit_json, now_iso as _now_iso
from deuseek.engines.parser import ParserEngine

console = Console()



@click.command("extract")
@click.argument("url")
@click.option("--selector", "-s", default="", help="CSS 选择器 (单字段提取)")
@click.option("--fields", "-f", default="", help='字段映射 JSON: \'{"title":"h1::text","price":".price::text"}\'')
@click.option("--container", "-c", default="", help="容器选择器 (多 items 模式): 如 '.product'")
@click.option("--adaptive", is_flag=True, help="启用自适应重定位 (页面改版自愈)")
@click.option("--auto-save", "auto_save", is_flag=True, help="保存元素引用供下次自适应")
@click.option("--find-similar", "find_similar", default="", help="查找与选择器匹配的相似元素")
@click.option("--fetcher", type=click.Choice(["fetcher", "stealthy", "dynamic"]), default="fetcher",
              help="用哪个引擎抓取页面")
@click.option("--json", "json_out", is_flag=True, help="输出 JSON")
@click.option("--timeout", type=float, default=15.0)
def extract_cmd(url: str, selector: str, fields: str, container: str,
                adaptive: bool, auto_save: bool, find_similar: str,
                fetcher: str, json_out: bool, timeout: float) -> None:
    """从页面精准提取结构化数据.

    v0.11+: Scrapling 自适应解析器, CSS/XPath 选择 + auto_save + adaptive 重定位.
    页面改版后自动找到新位置 (similarity 算法).
    """
    # Build selectors dict
    if find_similar:
        # find_similar mode
        result = ParserEngine.find_similar(
            url, find_similar, fetcher=fetcher, timeout=timeout
        )
    elif fields:
        try:
            selectors = _json.loads(fields)
        except _json.JSONDecodeError as e:
            console.print(f"[red]fields JSON 解析失败: {e}[/red]")
            raise SystemExit(1) from e
        # Merge container selector into fields dict
        if container:
            selectors = {"container": container, **selectors}
        result = ParserEngine.extract(
            url, selectors, adaptive=adaptive, auto_save=auto_save,
            fetcher=fetcher, timeout=timeout,
        )
    elif selector:
        result = ParserEngine.extract(
            url, {container or "value": selector},
            adaptive=adaptive, auto_save=auto_save,
            fetcher=fetcher, timeout=timeout,
        )
    else:
        console.print("[red]需要 --selector 或 --fields 或 --find-similar[/red]")
        raise SystemExit(1)

    if _should_emit_json(json_out):
        click.echo(_json.dumps(result.model_dump(), ensure_ascii=False, default=str))
        return

    if not result.items:
        console.print(f"[yellow]未提取到数据 (url={url})[/yellow]")
        raise SystemExit(1)

    # Rich table output
    console.print(Panel.fit(
        f"[cyan]{url}[/cyan]\n[dim]{len(result.items)} items · "
        f"adaptive={result.adaptive} · relocated={result.relocated} · "
        f"{result.elapsed_s:.1f}s[/dim]",
        title="deuseek extract",
    ))

    # Build table from items
    if result.items:
        keys = list(result.items[0].keys())
        table = Table(show_header=True, header_style="bold cyan")
        for k in keys:
            table.add_column(k)
        for item in result.items[:20]:  # limit display
            table.add_row(*[str(item.get(k, ""))[:80] for k in keys])
        console.print(table)
        if len(result.items) > 20:
            console.print(f"[dim]…({len(result.items) - 20} more, 用 --json 拿全部)[/dim]")
