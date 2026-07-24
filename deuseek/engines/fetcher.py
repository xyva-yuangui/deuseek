"""FetcherEngine — wraps Scrapling's Fetcher (curl_cffi HTTP).

Default engine: ~80%+ of URLs go through here. Pure HTTP, no browser
overhead. Data: 0.4-3.9s per page, 90% success rate on static sites.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from deuseek.contract import FetchResult
from deuseek.utils import now_iso as _now_iso
from deuseek.convert import html_to_markdown



class FetcherEngine:
    """Scrapling Fetcher — curl_cffi-based HTTP fetcher with TLS impersonation."""

    @staticmethod
    def fetch(
        url: str,
        *,
        timeout: float = 15,
        impersonate: str = "chrome",
        main_content_only: bool = True,
        **kwargs: Any,
    ) -> FetchResult:
        """Fetch a URL via Scrapling Fetcher.get().

        All Scrapling Fetcher.get() kwargs are passed through (impersonate,
        headers, cookies, proxy, follow_redirects, retries, etc.).
        """
        t0 = time.time()
        errors: list[str] = []
        try:
            from scrapling import Fetcher

            resp = Fetcher.get(url, timeout=timeout, impersonate=impersonate, **kwargs)
            elapsed = time.time() - t0

            md, html, sections, stats = html_to_markdown(resp, main_content_only=main_content_only)
            success = resp.status == 200 and len(md) > 50

            return FetchResult(
                url=url,
                backend="fetcher",
                success=success,
                content_markdown=md,
                content_html=html,
                status_code=resp.status,
                elapsed_s=elapsed,
                errors=errors,
                fetched_at=_now_iso(),
                sections=sections,
                content_stats=stats,
            )
        except Exception as e:  # noqa: BLE001
            return FetchResult(
                url=url,
                backend="fetcher",
                success=False,
                elapsed_s=time.time() - t0,
                errors=[f"fetcher: {e}"],
                fetched_at=_now_iso(),
            )

    @staticmethod
    def is_available() -> bool:
        """Check if Scrapling Fetcher is importable."""
        try:
            from scrapling import Fetcher  # noqa: F401
            return True
        except ImportError:
            return False
