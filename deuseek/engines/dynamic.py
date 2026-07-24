"""DynamicEngine — wraps Scrapling's DynamicFetcher (Playwright Chrome).

JS rendering specialist. Used when DomainKB marks a domain as 'js_render'
or when Fetcher returns an empty body (SPA with no server-side HTML).

Data: 4.9-6.9s per page. Times out on heavy real-world sites (bbc.com)
if timeout is too short. Use disable_resources=True for speed boost.

v0.11.1: BrowserPool integration — warm sessions reduce cold-start from
4.5s to ~1-2s on subsequent calls.
"""

from __future__ import annotations

import time
from typing import Any

from deuseek.contract import FetchResult
from deuseek.convert import html_to_markdown
from deuseek.utils import now_iso as _now_iso


class DynamicEngine:
    """Scrapling DynamicFetcher — Playwright-based browser automation."""

    @staticmethod
    def fetch(
        url: str,
        *,
        headless: bool = True,
        real_chrome: bool = True,
        disable_resources: bool = True,
        timeout: int = 15000,
        network_idle: bool = False,
        wait_selector: str | None = None,
        main_content_only: bool = True,
        use_pool: bool = True,
        **kwargs: Any,
    ) -> FetchResult:
        """Fetch a URL via Scrapling DynamicFetcher.

        Key params passed through to Scrapling:
        - disable_resources: drop font/image/media requests for speed
        - wait_selector: wait for a CSS selector before returning
        - page_action: callable(page) for custom automation
        - block_ads: block ~3500 ad/tracking domains
        - google_search: set Google referer (default True)
        - extra_headers, cookies, proxy, locale, timezone_id
        """
        t0 = time.time()

        # Try warm session from BrowserPool first
        if use_pool:
            result = DynamicEngine._fetch_via_pool(
                url, t0, disable_resources=disable_resources,
                network_idle=network_idle, timeout=timeout,
                main_content_only=main_content_only, **kwargs,
            )
            if result is not None:
                return result

        # Fallback: static method (creates + destroys browser per call)
        try:
            from scrapling import DynamicFetcher

            fetch_kwargs: dict[str, Any] = dict(
                headless=headless,
                real_chrome=real_chrome,
                disable_resources=disable_resources,
                timeout=timeout,
                network_idle=network_idle,
                **kwargs,
            )
            if wait_selector:
                fetch_kwargs["wait_selector"] = wait_selector

            resp = DynamicFetcher.fetch(url, **fetch_kwargs)
            elapsed = time.time() - t0
            md, html, sections, stats = html_to_markdown(resp, main_content_only=main_content_only)
            success = resp.status == 200 and len(md) > 50

            return FetchResult(
                url=url, backend="dynamic",
                success=success,
                content_markdown=md, content_html=html,
                sections=sections, content_stats=stats,
                status_code=resp.status,
                elapsed_s=elapsed,
                fetched_at=_now_iso(),
            )
        except ImportError as e:
            return FetchResult(
                url=url, backend="dynamic", success=False,
                errors=[f"dynamic unavailable: {e}"],
                fetched_at=_now_iso(),
            )
        except Exception as e:  # noqa: BLE001
            return FetchResult(
                url=url, backend="dynamic", success=False,
                elapsed_s=time.time() - t0,
                errors=[f"dynamic: {e}"],
                fetched_at=_now_iso(),
            )

    @staticmethod
    def _fetch_via_pool(
        url: str, t0: float, *, disable_resources: bool, network_idle: bool,
        timeout: int, main_content_only: bool, **kwargs: Any,
    ) -> FetchResult | None:
        """Try fetching via warm BrowserPool session. Returns None if unavailable."""
        try:
            from deuseek.perf.browser_pool import BrowserPool
            session = BrowserPool.get_dynamic_session()
            if session is None:
                return None
            try:
                resp = session.fetch(
                    url,
                    disable_resources=disable_resources,
                    network_idle=network_idle,
                    timeout=timeout,
                    **kwargs,
                )

                elapsed = time.time() - t0
                md, html, sections, stats = html_to_markdown(resp, main_content_only=main_content_only)
                success = resp.status == 200 and len(md) > 50

                return FetchResult(
                    url=url, backend="dynamic",
                    success=success,
                    content_markdown=md, content_html=html,
                    sections=sections, content_stats=stats,
                    status_code=resp.status,
                    elapsed_s=elapsed,
                    fetched_at=_now_iso(),
                )
            finally:
                # Always release (updates _last_used) even if fetch/processing
                # throws — otherwise shrink/timeout logic sees a stale timestamp.
                BrowserPool.release_dynamic_session()
        except Exception:
            # Pool fetch failed — return None to trigger fallback to static method
            return None

    @staticmethod
    def is_available() -> bool:
        """Check if DynamicFetcher + playwright are importable."""
        try:
            from scrapling import DynamicFetcher  # noqa: F401
            import playwright  # noqa: F401
            return True
        except ImportError:
            return False
