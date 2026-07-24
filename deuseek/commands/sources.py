"""deuseek sources — list registered sources grouped by tier."""

from __future__ import annotations

import asyncio
import json as _json
import os
import sys

import click
from rich.console import Console
from rich.table import Table

from deuseek.doctor import run_doctor
from deuseek.registry import load_registry
from deuseek.utils import should_emit_json as _should_emit_json

console = Console()

TIER_ICON = {
    "ready": "✅",
    "one_step": "🟡",
}
TIER_LABEL = {
    "ready": "ready",
    "one_step": "one_step",
}


@click.command("sources")
@click.option("--probe", is_flag=True, help="实际跑 is_ready 探测每个源 (慢一点)")
@click.option("--json", "json_out", is_flag=True, help="输出 JSON, 适合下游 pipe")
def sources_cmd(probe: bool, json_out: bool) -> None:
    """列出所有源 + 心愿单状态."""
    reg = load_registry()

    statuses: dict[str, bool] = {}
    if probe:
        for s in asyncio.run(run_doctor()):
            statuses[s.id] = s.ok

    if _should_emit_json(json_out):
        payload = {
            "sources": [
                {
                    "id": s.id,
                    "tier": s.tier,
                    "description": s.description,
                    "probe_ok": statuses.get(s.id) if probe else None,
                }
                for s in reg.sources
            ],
            "probed": probe,
        }
        click.echo(_json.dumps(payload, ensure_ascii=False))
        return

    by_tier: dict[str, list] = {
        "ready": [],
        "one_step": [],
    }
    for s in reg.sources:
        by_tier.setdefault(s.tier, []).append(s)

    for tier in ["ready", "one_step"]:
        items = by_tier.get(tier, [])
        if not items:
            continue
        label = TIER_LABEL.get(tier, tier)
        icon = TIER_ICON.get(tier, "")
        table = Table(title=f"{icon} {label} ({len(items)})", show_lines=False)
        table.add_column("id", style="cyan")
        table.add_column("描述")
        if probe:
            table.add_column("probe")
        for s in items:
            row = [s.id, s.description]
            if probe:
                row.append("✅" if statuses.get(s.id) else "❌")
            table.add_row(*row)
        console.print(table)
