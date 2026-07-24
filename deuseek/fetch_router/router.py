"""FetchRouter — decides which engine handles each URL.

Data-driven routing (see benchmark results):
- Fetcher (0.4-3.9s) is the default for 80%+ of URLs.
- jina SaaS (2.2-5.7s) is fallback — server IP pierces some anti-bot.
- StealthyFetcher+solve_cloudflare (37s) is last resort — only one that
  bypasses Cloudflare Turnstile, but too slow for default.
- DynamicFetcher (4.9-6.9s) for known JS-render-only sites.
- deuseek native paths for wechat/bilibili/douyin (login-state/API).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlparse

from deuseek.perf.domain_kb import DomainKB
from deuseek.perf.cache import Cache

# Hosts that go through deuseek native paths, not Scrapling.
_NATIVE_HOSTS: dict[str, str] = {
    "mp.weixin.qq.com": "native_wechat",
    "bilibili.com": "native_bilibili",
    "www.bilibili.com": "native_bilibili",
    "m.bilibili.com": "native_bilibili",
    "douyin.com": "native_douyin",
    "www.douyin.com": "native_douyin",
}

# Backend IDs that are available as Scrapling engines.
_ENGINE_BACKENDS = {"fetcher", "stealthy", "dynamic", "jina"}

# Default fallback chain for unknown domains.
_DEFAULT_FALLBACK = ["fetcher", "jina", "stealthy"]

# Fallback when DomainKB says the domain needs a specific engine.
_KNOWN_FALLBACK: dict[str, list[str]] = {
    "stealthy": ["jina"],              # CF sites: stealthy then jina (different IP)
    "dynamic": ["jina", "fetcher"],    # JS sites: jina (SaaS) then fetcher (static fallback)
    "jina": ["fetcher", "stealthy"],   # jina-known: try fetcher then stealthy+CF
    "static": ["jina", "stealthy"],    # static: jina then stealthy
}


@dataclass
class Route:
    """The router's decision for a single URL."""

    backend: str
    """Primary backend to try: 'fetcher' | 'stealthy' | 'dynamic' | 'jina' | 'native_*'."""

    fallback_chain: list[str] = field(default_factory=list)
    """Backends to try if the primary fails, in order."""

    rationale: str = ""
    """Human-readable reason for this routing decision."""

    solve_cloudflare: bool = False
    """Whether to enable solve_cloudflare on StealthyFetcher (only for CF domains)."""


class FetchRouter:
    """Route URLs to the optimal fetch backend."""

    def __init__(
        self,
        domain_kb: DomainKB | None = None,
        cache: type[Cache] | None = None,
    ) -> None:
        self.domain_kb = domain_kb or DomainKB()
        self.cache = cache or Cache

    def route(
        self,
        url: str,
        *,
        explicit_backend: str | None = None,
        solve_cloudflare: bool = False,
    ) -> Route:
        """Decide which backend to use for `url`.

        Args:
            url: The URL to fetch.
            explicit_backend: User-specified backend via --backend. Overrides
                everything. One of: fetcher, stealthy, dynamic, jina, native.
            solve_cloudflare: User-specified --solve-cloudflare flag.
        """
        # 1. Explicit override — user wins
        if explicit_backend:
            return Route(
                backend=explicit_backend,
                fallback_chain=[],
                rationale="explicit --backend",
                solve_cloudflare=solve_cloudflare,
            )

        # 2. Native host routing (wechat/bilibili/douyin)
        host = self._host_of(url)
        if host in _NATIVE_HOSTS:
            native = _NATIVE_HOSTS[host]
            return Route(
                backend=native,
                fallback_chain=["fetcher", "jina"],
                rationale=f"native host: {host}",
            )

        # 3. DomainKB lookup
        known = self.domain_kb.get(url)
        blocked = self.domain_kb.get_blocked(url)

        if known:
            # DomainKB says this backend works — skip trial-and-error
            cf_needed = known == "stealthy" or "stealthy" in blocked
            return Route(
                backend=known,
                fallback_chain=_KNOWN_FALLBACK.get(known, ["jina", "stealthy"]),
                rationale=f"domain_kb: {known}",
                solve_cloudflare=cf_needed or solve_cloudflare,
            )

        # 4. Unknown domain — Fetcher first, then escalate
        # Filter out blocked backends from the fallback chain
        chain = [b for b in _DEFAULT_FALLBACK if b not in blocked]
        cf_needed = solve_cloudflare

        return Route(
            backend="fetcher",
            fallback_chain=chain,
            rationale="default: fetcher → jina → stealthy",
            solve_cloudflare=cf_needed,
        )

    def record_success(self, url: str, backend: str) -> None:
        """Tell DomainKB that `backend` worked for this domain."""
        self.domain_kb.set(url, backend)

    def record_failure(self, url: str, backend: str) -> None:
        """Tell DomainKB that `backend` failed for this domain."""
        self.domain_kb.set_blocked(url, backend)

    @staticmethod
    def _host_of(url: str) -> str:
        try:
            return urlparse(url).hostname or ""
        except Exception:
            return ""
