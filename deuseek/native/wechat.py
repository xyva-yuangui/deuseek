"""WeChat (mp.weixin.qq.com) article fetcher via OpenCLI login-state.

Uses the Daily-AC/OpenCLI fork's `weixin download --stdout` command,
which leverages Chrome login cookies to bypass WeChat's "环境异常"
verification. Requires: Chrome opened any mp.weixin.qq.com article
before (cookies persisted in browser).

If OpenCLI is not installed, returns success=False so the fetch router
can fall back to Scrapling StealthyFetcher (which may hit captcha).
"""

from __future__ import annotations

from deuseek.utils import now_iso as _now_iso

import shutil
import subprocess
import time
from datetime import datetime, timezone



def is_available() -> bool:
    """Check if OpenCLI (weixin) is installed."""
    return shutil.which("weixin") is not None or shutil.which("opencli") is not None


def fetch_wechat(url: str, *, timeout: float = 30) -> dict:
    """Fetch a WeChat article via OpenCLI login-state Chrome.

    Args:
        url: mp.weixin.qq.com article URL.
        timeout: Command timeout in seconds.

    Returns:
        Dict with success, content_markdown, backend, errors, fetched_at.
    """
    t0 = time.time()

    # URL scheme validation: ensure http/https before passing to subprocess
    if not url.startswith(("http://", "https://")):
        return {
            "success": False,
            "content_markdown": "",
            "backend": "native_wechat",
            "errors": [f"invalid URL scheme (expected http/https): {url[:60]}"],
            "fetched_at": _now_iso(),
        }

    # Try weixin binary first (Daily-AC/OpenCLI fork installs as `weixin`)
    weixin_bin = shutil.which("weixin")
    if not weixin_bin:
        # Fall back to opencli with weixin subcommand
        opencli_bin = shutil.which("opencli")
        if not opencli_bin:
            return {
                "success": False,
                "content_markdown": "",
                "backend": "native_wechat",
                "errors": ["opencli/weixin not installed"],
                "fetched_at": _now_iso(),
            }
        cmd = [opencli_bin, "weixin", "download", "--stdout", url]
    else:
        cmd = [weixin_bin, "download", "--stdout", url]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        elapsed = time.time() - t0

        if result.returncode != 0:
            return {
                "success": False,
                "content_markdown": "",
                "backend": "native_wechat",
                "status_code": 0,
                "elapsed_s": elapsed,
                "errors": [f"opencli exit {result.returncode}: {result.stderr[:200]}"],
                "fetched_at": _now_iso(),
            }

        content = result.stdout.strip()
        if not content or len(content) < 50:
            return {
                "success": False,
                "content_markdown": "",
                "backend": "native_wechat",
                "status_code": 0,
                "elapsed_s": elapsed,
                "errors": ["opencli returned empty content"],
                "fetched_at": _now_iso(),
            }

        # OpenCLI returns markdown directly
        return {
            "success": True,
            "content_markdown": content,
            "content_html": "",
            "backend": "native_wechat",
            "status_code": 200,
            "elapsed_s": elapsed,
            "errors": [],
            "fetched_at": _now_iso(),
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "content_markdown": "",
            "backend": "native_wechat",
            "status_code": 0,
            "elapsed_s": time.time() - t0,
            "errors": [f"opencli timeout (>{timeout}s)"],
            "fetched_at": _now_iso(),
        }
    except Exception as e:  # noqa: BLE001
        return {
            "success": False,
            "content_markdown": "",
            "backend": "native_wechat",
            "status_code": 0,
            "elapsed_s": time.time() - t0,
            "errors": [f"native_wechat: {e}"],
            "fetched_at": _now_iso(),
        }
