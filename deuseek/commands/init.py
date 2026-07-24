"""deuseek init — write default preferences + show next-step guidance."""

from __future__ import annotations

import click
from rich.console import Console

from deuseek.preferences import preferences_path, write_default_preferences

console = Console()


def _write_default_prefs_if_missing() -> bool:
    pref_path = preferences_path()
    if pref_path.exists():
        return False
    write_default_preferences(pref_path)
    click.echo(f"  ✅ 已写入默认偏好: {pref_path}")
    return True


@click.command("init")
@click.option("--yes", "-y", is_flag=True, help="(已弃用) 保留为兼容旧脚本; init 不再有交互步骤")
def init_cmd(yes: bool) -> None:
    """初始化用户配置 (写默认 preferences.toml + 打印源解锁指引)."""
    wrote = _write_default_prefs_if_missing()
    if not wrote:
        click.echo(f"  ✅ 偏好已存在: {preferences_path()}")

    console.print()
    console.print("[bold]✨ deuseek 已就绪[/bold]")
    console.print("零配置可用: [cyan]web[/cyan] · [cyan]hackernews[/cyan] · [cyan]rss[/cyan] · [cyan]wechat[/cyan] · [cyan]bilibili[/cyan]")
    console.print()
    console.print("下一步:")
    console.print("  [bold]deuseek sources[/bold]       — 查看所有源 + 当前可用状态")
    console.print("  [bold]deuseek doctor[/bold]        — 体检各源 (binary / API Key)")
    console.print("  [bold]deuseek setup <源名>[/bold]   — 解锁单个源 (例: setup youtube / setup reddit)")
    console.print()
    console.print("立即试试: [bold]deuseek search \"vibe coding\"[/bold]")
