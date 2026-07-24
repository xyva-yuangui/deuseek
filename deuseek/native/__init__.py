"""native/ — deuseek 原生抓取路径 (微信/B站/抖音).

These platforms have specialized access methods that Scrapling can't replace:
- WeChat (mp.weixin.qq.com): OpenCLI login-state Chrome cookies
- Bilibili: Official API for structured video data
- Douyin: OpenCLI fork for login-state content

If the required tool isn't available, native_fetch returns success=False
with a clear error, and the fetch router falls back to Scrapling engines.
"""

from deuseek.native.wechat import fetch_wechat
from deuseek.native.bilibili import fetch_bilibili
from deuseek.native.douyin import fetch_douyin

__all__ = ["native_fetch", "fetch_wechat", "fetch_bilibili", "fetch_douyin"]


def native_fetch(url: str, *, timeout: float = 30) -> dict:
    """Route URL to the appropriate native fetcher by host.

    Returns a dict with keys: success, content_markdown, backend, errors.
    If no native path matches or required tools are missing, returns
    success=False so the caller can fall back to Scrapling engines.
    """
    from urllib.parse import urlparse
    host = urlparse(url).hostname or ""

    if "weixin.qq.com" in host:
        return fetch_wechat(url, timeout=timeout)
    elif "bilibili.com" in host:
        return fetch_bilibili(url, timeout=timeout)
    elif "douyin.com" in host:
        return fetch_douyin(url, timeout=timeout)
    else:
        return {
            "success": False,
            "content_markdown": "",
            "backend": "native",
            "errors": [f"no native path for host: {host}"],
        }
