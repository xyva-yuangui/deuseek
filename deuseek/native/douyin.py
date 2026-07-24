"""Douyin (douyin.com) content fetcher via OpenCLI fork.

Uses the Daily-AC/OpenCLI fork to fetch Douyin content with login-state
Chrome cookies. If OpenCLI is not installed, returns success=False so
the fetch router falls back to Scrapling engines.
"""

from __future__ import annotations

from deuseek.utils import now_iso as _now_iso

import shutil
import subprocess
import time
from datetime import datetime, timezone



def is_available() -> bool:
    """Check if OpenCLI (douyin) is installed."""
    return shutil.which("douyin") is not None or shutil.which("opencli") is not None


def fetch_douyin(url: str, *, timeout: float = 30) -> dict:
    """Fetch a Douyin page via OpenCLI fork.

    Args:
        url: douyin.com video/share URL.
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
            "backend": "native_douyin",
            "errors": [f"invalid URL scheme (expected http/https): {url[:60]}"],
            "fetched_at": _now_iso(),
        }

    douyin_bin = shutil.which("douyin")
    if not douyin_bin:
        opencli_bin = shutil.which("opencli")
        if not opencli_bin:
            return {
                "success": False,
                "content_markdown": "",
                "backend": "native_douyin",
                "errors": ["opencli/douyin not installed"],
                "fetched_at": _now_iso(),
            }
        cmd = [opencli_bin, "douyin", "download", "--stdout", url]
    else:
        cmd = [douyin_bin, "download", "--stdout", url]

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
                "backend": "native_douyin",
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
                "backend": "native_douyin",
                "status_code": 0,
                "elapsed_s": elapsed,
                "errors": ["opencli returned empty content"],
                "fetched_at": _now_iso(),
            }

        return {
            "success": True,
            "content_markdown": content,
            "content_html": "",
            "backend": "native_douyin",
            "status_code": 200,
            "elapsed_s": elapsed,
            "errors": [],
            "fetched_at": _now_iso(),
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "content_markdown": "",
            "backend": "native_douyin",
            "status_code": 0,
            "elapsed_s": time.time() - t0,
            "errors": [f"opencli timeout (>{timeout}s)"],
            "fetched_at": _now_iso(),
        }
    except Exception as e:  # noqa: BLE001
        return {
            "success": False,
            "content_markdown": "",
            "backend": "native_douyin",
            "status_code": 0,
            "elapsed_s": time.time() - t0,
            "errors": [f"native_douyin: {e}"],
            "fetched_at": _now_iso(),
        }
