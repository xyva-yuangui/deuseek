"""deuseek CLI entry."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from deuseek import __version__
from deuseek.commands.check_update import check_update_cmd
from deuseek.commands.fetch import fetch_cmd
from deuseek.commands.init import init_cmd
from deuseek.commands.setup import setup_cmd
from deuseek.commands.preferences import preferences_cmd
from deuseek.commands.sources import sources_cmd
from deuseek.commands.crawl import crawl_cmd
from deuseek.commands.domain_kb import domain_kb_cmd
from deuseek.commands.extract import extract_cmd
from deuseek.commands.super import super_cmd
from deuseek.dispatcher import Dispatcher
from deuseek.normalizer import build_envelope, dedup_results
from deuseek.registry import load_registry
from deuseek.router import RouteRequest, Router
from deuseek.scorer import rank
from deuseek.secrets_env import load_secrets_env
from deuseek.utils import should_emit_json as _should_emit_json

_SECRETS_PATH = Path.home() / ".deuseek" / "secrets.env"
load_secrets_env(_SECRETS_PATH)

ISSUE_URL = "https://github.com/xyva-yuangui/deuseek/issues/new/choose"

console = Console()



@click.group()
@click.version_option(__version__, "-V", "--version")
def main() -> None:
    """deuseek — 全网通搜索 CLI."""


@main.command("search")
@click.argument("query")
@click.option("--on", "on_", help="只用这些源, 逗号分隔. 例: --on hackernews,web")
@click.option("--mode", type=click.Choice(["auto", "quick", "deep"]), default="auto")
@click.option("--limit", type=int, default=10, help="每个源最多返回多少条")
@click.option("--timeout", type=float, default=30.0,
              help="全局默认 timeout (秒); 被 sources.yml 中各源的 timeout_seconds 覆盖")
@click.option("--json", "json_out", is_flag=True, help="输出 JSON, 适合下游 pipe")
@click.option("--no-cache", "no_cache", is_flag=True, help="跳过缓存, 强制重新搜索")
def search_cmd(query: str, on_: str | None, mode: str, limit: int, timeout: float, json_out: bool, no_cache: bool) -> None:
    """运行一次搜索."""
    explicit = [s.strip() for s in on_.split(",")] if on_ else None
    reg = load_registry()
    router = Router(reg)
    route = router.plan(RouteRequest(query=query, explicit_sources=explicit, mode=mode))

    for unknown in route.unknown_sources:
        click.echo(f"warning: 未知源 '{unknown}' — 跳过 (用 `deuseek sources` 查看可用源)", err=True)

    adapters = {}
    for sid in route.source_ids:
        try:
            spec = reg.get(sid)
            adapters[sid] = spec.load_adapter_class()()
        except Exception as e:  # noqa: BLE001
            click.echo(f"skip {sid}: {e}", err=True)

    timeouts_by_source = {s.id: s.timeout_seconds for s in reg.sources}
    dispatcher = Dispatcher(timeout=timeout, per_source_limit=limit,
                            timeouts_by_source=timeouts_by_source,
                            use_cache=not no_cache)
    results, errors = asyncio.run(dispatcher.run(adapters, query))
    results = dedup_results(results)
    trust_map = {s.id: s.trust for s in reg.sources}
    ranked = rank(results, trust_map=trust_map)
    envelope = build_envelope(query=query, results=ranked, errors=errors)

    if _should_emit_json(json_out):
        click.echo(envelope.model_dump_json())
        return

    table = Table(title=f"deuseek: {query}  ({len(ranked)} hits, {len(errors)} errors)")
    table.add_column("源", style="cyan")
    table.add_column("标题")
    table.add_column("URL", style="dim")
    for r in ranked:
        source_label = f"💎 {r.source}" if r.cost == "paid" else r.source
        table.add_row(source_label, r.title[:80], r.url)
    console.print(table)
    failed = [e for e in errors if e.category == "failed"]
    unavailable = [e for e in errors if e.category == "unavailable"]
    for err in failed:
        console.print(f"[red]✗ {err.source}: {err.error}[/red]")
    if failed:
        console.print(
            f"[dim]💬 觉得是 bug? 提 issue: {ISSUE_URL}[/dim]"
        )
    if unavailable:
        n = len(unavailable)
        console.print(f"[dim]ℹ️  {n} 个源未配置 (跑 `deuseek doctor` 查看修复建议)[/dim]")


@main.command("doctor")
@click.option("--json", "json_out", is_flag=True, help="输出 JSON, 适合下游 pipe")
def doctor_cmd(json_out: bool) -> None:
    """检查每个源 + fetch backend 的就绪状态."""
    import platform
    import json as _json

    from deuseek.doctor import (
        run_doctor,
        run_fetch_backend_doctor,
    )

    plat = f"{platform.system()} {platform.release()} ({platform.machine()})"
    pyver = f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    statuses = asyncio.run(run_doctor())
    fetch_backends = run_fetch_backend_doctor()

    if _should_emit_json(json_out):
        payload = {
            "deuseek_version": __version__,
            "python": pyver,
            "platform": plat,
            "sources": [
                {"id": s.id, "tier": s.tier, "ok": s.ok,
                 "detail": s.detail, "fix_hint": s.fix_hint}
                for s in statuses
            ],
            "fetch_backends": [
                {"tool": b.tool, "ok": b.ok,
                 "detail": b.detail, "fix_hint": b.fix_hint}
                for b in fetch_backends
            ],
        }
        click.echo(_json.dumps(payload, ensure_ascii=False))
        return

    console.print(f"[dim]deuseek {__version__} · {pyver} · {plat}[/dim]")
    table = Table(title="deuseek doctor — sources")
    table.add_column("源", style="cyan")
    table.add_column("tier")
    table.add_column("状态")
    table.add_column("说明", style="dim")
    table.add_column("修复")
    for s in statuses:
        icon = "✅" if s.ok else "❌"
        table.add_row(s.id, s.tier, icon, s.detail, s.fix_hint)
    console.print(table)

    # v0.9.3: separate panel for fetch backends (URL → 全文 工具, deuseek 自己不做)
    fb_table = Table(title="fetch backends — 把 search URL 拉成全文 (可选, 自动检测 PATH)")
    fb_table.add_column("工具", style="cyan")
    fb_table.add_column("状态")
    fb_table.add_column("说明", style="dim")
    fb_table.add_column("修复")
    for b in fetch_backends:
        icon = "✅" if b.ok else "❌"
        fb_table.add_row(b.tool, icon, b.detail, b.fix_hint)
    console.print(fb_table)



main.add_command(init_cmd)
main.add_command(setup_cmd)
main.add_command(sources_cmd)
main.add_command(preferences_cmd)
main.add_command(check_update_cmd)
main.add_command(fetch_cmd)
main.add_command(crawl_cmd)
main.add_command(extract_cmd)
main.add_command(super_cmd)
main.add_command(domain_kb_cmd)


def _entrypoint() -> None:
    """Console-script wrapper that catches unhandled exceptions and points users at issues."""
    try:
        main.main(standalone_mode=True)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        console.print("\n[yellow]中断[/yellow]")
        raise SystemExit(130)
    except Exception as exc:  # noqa: BLE001
        import traceback
        console.print(f"\n[red]deuseek 内部错误: {exc.__class__.__name__}: {exc}[/red]")
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        console.print(
            f"\n[bold]💬 请把上面这段 traceback + `deuseek --version` 一起提 issue:[/bold]\n   {ISSUE_URL}"
        )
        raise SystemExit(2)


if __name__ == "__main__":
    _entrypoint()
