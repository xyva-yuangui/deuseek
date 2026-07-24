"""router/ — fetch routing decision layer.

Decides which engine handles each URL based on:
1. Explicit --backend override (user wins)
2. Host-based native routing (wechat/bilibili/douyin)
3. DomainKB knowledge (cloudflare/js_render/static)
4. Default: Fetcher → jina → StealthyFetcher+CF fallback chain
"""

from deuseek.fetch_router.router import FetchRouter, Route

__all__ = ["FetchRouter", "Route"]
