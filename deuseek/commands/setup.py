"""deuseek setup <source> — conversational setup wizard."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import click
from rich.console import Console

from deuseek.registry import load_registry

console = Console()


BINARY_GUIDES = {
    "youtube": {
        "binary": "yt-dlp",
        "install": ["pip", "install", "yt-dlp"],
        "label": "yt-dlp",
    },
    "github": {
        "binary": "gh",
        "install": None,
        "label": "GitHub CLI",
        "manual_hint": (
            "macOS: `brew install gh`  ·  "
            "Windows: `winget install --id GitHub.cli` (或 https://cli.github.com)  ·  "
            "Linux: 看 https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
        ),
    },
    "reddit": {
        "binary": "rdt-cli",
        "install": ["uv", "tool", "install", "rdt-cli"],
        "label": "rdt-cli",
        "post_install": "运行 `rdt login` 完成 Reddit OAuth (浏览器扫码)",
    },
    "rss": {
        "binary": None,
        "install": None,
        "label": "RSS (内置 feedparser)",
    },
}


def _setup_binary(source_id: str) -> None:
    g = BINARY_GUIDES[source_id]
    binary = g["binary"]
    if binary is None:
        click.echo(f"✅ {g['label']} 已内置, 无需配置.")
        return
    if shutil.which(binary):
        click.echo(f"✅ {binary} 已在 PATH, 可直接使用.")
        if g.get("post_install"):
            click.echo(f"  ⚠️  下一步: {g['post_install']}")
        return
    click.echo(f"{g['label']} 未安装.")
    if g["install"]:
        if not click.confirm(f"运行 `{' '.join(g['install'])}` 安装?", default=True):
            return
        try:
            subprocess.run(g["install"], check=True)
        except subprocess.CalledProcessError as e:
            click.echo(f"❌ 安装失败: {e}", err=True)
            return
        click.echo(f"✅ {binary} 安装完成.")
        if g.get("post_install"):
            click.echo(f"  ⚠️  下一步: {g['post_install']}")
    else:
        click.echo(f"  👤 请手动安装: {g['manual_hint']}")


@click.command("setup")
@click.argument("source_id")
@click.option("--yes", "-y", is_flag=True, help="跳过所有确认 (CI / 自动化)")
def setup_cmd(source_id: str, yes: bool) -> None:
    """配置一个源 (装上游工具 + 引导用户登录)."""
    reg = load_registry()
    try:
        reg.get(source_id)
    except KeyError:
        click.echo(f"未知源 '{source_id}'. 可用源: 跑 `deuseek sources`", err=True)
        raise SystemExit(2)

    if source_id in ("hackernews", "web", "wechat", "bilibili"):
        click.echo(f"✅ {source_id} 零配置, 无需 setup.")
        return

    if source_id in BINARY_GUIDES:
        _setup_binary(source_id)
        return

    click.echo(f"未知源 '{source_id}'. 可用源: 跑 `deuseek sources`", err=True)
    raise SystemExit(2)
