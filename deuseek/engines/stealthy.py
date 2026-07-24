"""StealthyEngine — wraps Scrapling's StealthyFetcher (patchright Chrome).

Cloudflare bypass specialist. Only used when Fetcher + jina both fail on
anti-bot pages, or when DomainKB marks a domain as 'cloudflare'.

Data: 7.8s (no CF solve) / 37s (with solve_cloudflare). 100% CF bypass
when solve_cloudflare=True + real patchright installed.

v0.11.1: BrowserPool integration — warm sessions reduce cold-start from
2.4s to ~1s on subsequent calls. Falls back to static method if pool
unavailable.
"""

from __future__ import annotations

import time
from typing import Any

from deuseek.contract import FetchResult
from deuseek.convert import html_to_markdown
from deuseek.utils import now_iso as _now_iso


class StealthyEngine:
    """Scrapling StealthyFetcher — patchright-based stealth Chrome with CF bypass."""

    @staticmethod
    def fetch(
        url: str,
        *,
        solve_cloudflare: bool = False,
        headless: bool = True,
        real_chrome: bool = True,
        timeout: int = 30000,
        network_idle: bool = False,
        main_content_only: bool = True,
        use_pool: bool = True,
        **kwargs: Any,
    ) -> FetchResult:
        """Fetch a URL via Scrapling StealthyFetcher.

        Key params passed through to Scrapling:
        - solve_cloudflare: bypass Cloudflare Turnstile/Interstitial
        - hide_canvas, block_webrtc, allow_webgl: stealth options
        - humanize: human-like mouse movements
        - proxy, proxy_rotator: proxy support
        - wait_selector, page_action: automation hooks

        Args:
            use_pool: If True (default), try warm BrowserPool session first.
                      Falls back to static StealthyFetcher.fetch() if pool
                      unavailable or session.fetch() fails.
        """
        t0 = time.time()

        # Try warm session from BrowserPool first
        if use_pool:
            result = StealthyEngine._fetch_via_pool(
                url, t0, solve_cloudflare=solve_cloudflare,
                network_idle=network_idle, timeout=timeout,
                main_content_only=main_content_only, **kwargs,
            )
            if result is not None:
                return result

        # Fallback: static method (creates + destroys browser per call)
        try:
            from scrapling import StealthyFetcher

            resp = StealthyFetcher.fetch(
                url,
                solve_cloudflare=solve_cloudflare,
                headless=headless,
                real_chrome=real_chrome,
                timeout=timeout,
                network_idle=network_idle,
                **kwargs,
            )
            elapsed = time.time() - t0
            md, html, sections, stats = html_to_markdown(resp, main_content_only=main_content_only)
            success = resp.status == 200 and len(md) > 50

            return FetchResult(
                url=url,
                backend="stealthy",
                success=success,
                content_markdown=md,
                content_html=html,
                sections=sections,
                content_stats=stats,
                status_code=resp.status,
                elapsed_s=elapsed,
                fetched_at=_now_iso(),
            )
        except ImportError as e:
            return FetchResult(
                url=url, backend="stealthy", success=False,
                errors=[f"stealthy unavailable: {e}"],
                fetched_at=_now_iso(),
            )
        except Exception as e:  # noqa: BLE001
            return FetchResult(
                url=url, backend="stealthy", success=False,
                elapsed_s=time.time() - t0,
                errors=[f"stealthy: {e}"],
                fetched_at=_now_iso(),
            )

    @staticmethod
    def _fetch_via_pool(
        url: str, t0: float, *, solve_cloudflare: bool, network_idle: bool,
        timeout: int, main_content_only: bool, **kwargs: Any,
    ) -> FetchResult | None:
        """Try fetching via warm BrowserPool session. Returns None if unavailable."""
        try:
            from deuseek.perf.browser_pool import BrowserPool
            session = BrowserPool.get_stealthy_session()
            if session is None:
                return None
            try:
                resp = session.fetch(
                    url,
                    solve_cloudflare=solve_cloudflare,
                    network_idle=network_idle,
                    timeout=timeout,
                    **kwargs,
                )

                elapsed = time.time() - t0
                md, html, sections, stats = html_to_markdown(resp, main_content_only=main_content_only)
                success = resp.status == 200 and len(md) > 50

                return FetchResult(
                    url=url, backend="stealthy",
                    success=success,
                    content_markdown=md, content_html=html,
                    sections=sections,
                    content_stats=stats,
                    status_code=resp.status,
                    elapsed_s=elapsed,
                    fetched_at=_now_iso(),
                )
            finally:
                # Always release (updates _last_used) even if fetch/processing
                # throws — otherwise shrink/timeout logic sees a stale timestamp.
                BrowserPool.release_stealthy_session()
        except Exception:
            # Pool fetch failed — return None to trigger fallback to static method
            return None

    @staticmethod
    def is_available() -> bool:
        """Check if StealthyFetcher + patchright are importable."""
        try:
            from scrapling import StealthyFetcher  # noqa: F401
            import patchright  # noqa: F401
            return True
        except ImportError:
            return False
