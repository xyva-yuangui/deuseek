"""deuseek domain-kb — view/manage the domain→backend knowledge base (DomainKB)."""

from __future__ import annotations

import json as _json

import click
from rich.console import Console
from rich.table import Table

from deuseek.perf.domain_kb import DomainKB
from deuseek.utils import should_emit_json as _should_emit_json

console = Console()


@click.command("domain-kb")
@click.option("--clear", "clear_kb", is_flag=True, help="清空域名知识库")
@click.option("--json", "json_out", is_flag=True, help="JSON 输出")
def domain_kb_cmd(clear_kb: bool, json_out: bool) -> None:
    """查看/管理域名→后端知识库 (DomainKB)."""
    kb = DomainKB()

    if clear_kb:
        kb.clear()
        console.print("[green]✓ 域名知识库已清空[/green]")
        return

    data = kb.all()

    if _should_emit_json(json_out):
        payload = {
            "path": str(kb._path),
            "count": len(data),
            "entries": {
                domain: {
                    "backend": entry.get("backend", ""),
                    "blocked": entry.get("blocked", []),
                    "updated": entry.get("updated", ""),
                    "expired": kb._is_expired(entry),
                }
                for domain, entry in data.items()
            },
        }
        click.echo(_json.dumps(payload, ensure_ascii=False))
        return

    if not data:
        console.print("[dim]域名知识库为空 (尚未记录任何 domain→backend 映射)[/dim]")
        console.print(f"[dim]存储路径: {kb._path}[/dim]")
        return

    table = Table(title=f"DomainKB — domain→backend ({len(data)} entries)")
    table.add_column("domain", style="cyan")
    table.add_column("backend")
    table.add_column("blocked", style="dim")
    table.add_column("updated", style="dim")
    table.add_column("status")
    for domain, entry in sorted(data.items()):
        backend = entry.get("backend", "") or "-"
        blocked = entry.get("blocked", [])
        blocked_str = ", ".join(blocked) if blocked else "-"
        updated = entry.get("updated", "") or "-"
        expired = kb._is_expired(entry)
        status = "⏰ expired" if expired else "✓ active"
        table.add_row(domain, backend, blocked_str, updated, status)
    console.print(table)
    console.print(f"[dim]存储路径: {kb._path}[/dim]")
