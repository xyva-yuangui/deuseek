"""ParserEngine — wraps Scrapling's adaptive parser for structured extraction.

Uses Scrapling's CSS/XPath selectors with auto_save + adaptive relocation.
When a website changes its DOM structure, the parser automatically relocates
previously-saved elements using intelligent similarity algorithms.

Three-level adaptive opt-in:
1. BaseFetcher.configure(adaptive=True) — global switch
2. .css(selector, adaptive=True) — per-call relocation trigger
3. .css(selector, auto_save=True) — persist element fingerprints
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from deuseek.contract import ExtractResult
from deuseek.utils import now_iso as _now_iso



class ParserEngine:
    """Scrapling adaptive parser — structured data extraction with self-healing selectors."""

    @staticmethod
    def extract(
        url: str,
        selectors: dict[str, str],
        *,
        adaptive: bool = False,
        auto_save: bool = False,
        fetcher: str = "fetcher",
        timeout: float = 15,
        **fetch_kwargs: Any,
    ) -> ExtractResult:
        """Extract structured data from a page using CSS selectors.

        Args:
            url: Target URL to fetch and parse.
            selectors: Field map, e.g. {"title": "h1::text", "price": ".price::text"}.
            adaptive: If True, enable adaptive relocation when selectors miss.
            auto_save: If True (requires adaptive), save element fingerprints.
            fetcher: Which engine to use for fetching: "fetcher" | "stealthy" | "dynamic".
            timeout: Fetch timeout in seconds (ms for browser engines).
            **fetch_kwargs: Passed through to the fetch engine.

        Returns:
            ExtractResult with items list (one dict per matched element group).
        """
        t0 = time.time()
        try:
            # Enable adaptive globally if requested
            if adaptive:
                from scrapling import Fetcher as _F
                _F.adaptive = True

            # Fetch the page using the specified engine
            page = ParserEngine._fetch_page(
                url, fetcher=fetcher, timeout=timeout, adaptive=adaptive, **fetch_kwargs
            )
            if page is None:
                return ExtractResult(
                    url=url, selector=str(selectors),
                    adaptive=adaptive, elapsed_s=time.time() - t0,
                    fetched_at=_now_iso(),
                )

            # Extract fields
            items: list[dict[str, Any]] = []

            # If selectors map to single fields (not repeating), build one item
            # If any selector matches multiple elements, build items per element
            # Detect if we have a "container" selector that wraps repeating items
            container_key = None
            for k, v in selectors.items():
                # If a selector value is just a CSS path (no ::text), treat as container
                if "::" not in v and k in ("item", "container", "card", "row", "entry"):
                    container_key = k
                    break

            if container_key:
                # Multi-item extraction: iterate containers
                container_sel = selectors[container_key]
                containers = page.css(container_sel, adaptive=adaptive, auto_save=auto_save)
                for container in containers:
                    item: dict[str, Any] = {}
                    for field, sel in selectors.items():
                        if field == container_key:
                            continue
                        val = container.css(sel).get()
                        item[field] = str(val) if val else ""
                    items.append(item)
            else:
                # Single-item extraction
                item = {}
                for field, sel in selectors.items():
                    val = page.css(sel, adaptive=adaptive, auto_save=auto_save).get()
                    item[field] = str(val) if val else ""
                if any(v for v in item.values()):
                    items.append(item)

            # Relocation detection: if adaptive=True and we got results,
            # check whether the original selector matched directly (no relocation)
            # or whether relocation was needed (selector missed → adaptive found it).
            # We track this by seeing if css() without adaptive also matches.
            relocated = False
            if adaptive and items:
                # If the selector doesn't match without adaptive=True,
                # then relocation was triggered to find the elements
                try:
                    direct_match = any(
                        page.css(sel).get() is not None
                        for sel in selectors.values()
                        if "::" in sel  # only check field selectors, not containers
                    )
                    relocated = not direct_match
                except Exception:
                    relocated = True  # assume relocation if check fails

            return ExtractResult(
                url=url,
                selector=str(selectors),
                items=items,
                adaptive=adaptive,
                relocated=relocated,
                elapsed_s=time.time() - t0,
                fetched_at=_now_iso(),
            )
        except Exception as e:  # noqa: BLE001
            return ExtractResult(
                url=url, selector=str(selectors),
                adaptive=adaptive,
                elapsed_s=time.time() - t0,
                fetched_at=_now_iso(),
            )

    @staticmethod
    def find_similar(url: str, example_selector: str, *,
                     fetcher: str = "fetcher", timeout: float = 15,
                     similarity_threshold: float = 0.2,
                     **fetch_kwargs: Any) -> ExtractResult:
        """Find all elements similar to the one matched by example_selector.

        Uses Scrapling's find_similar() — AutoScraper-inspired sibling harvesting.
        """
        t0 = time.time()
        try:
            page = ParserEngine._fetch_page(
                url, fetcher=fetcher, timeout=timeout, adaptive=False, **fetch_kwargs
            )
            if page is None:
                return ExtractResult(url=url, selector=example_selector,
                                      elapsed_s=time.time() - t0, fetched_at=_now_iso())

            seed = page.css(example_selector)
            items: list[dict[str, Any]] = []
            if seed:
                similar = seed[0].find_similar(similarity_threshold=similarity_threshold)
                for el in similar:
                    items.append({
                        "tag": el.tag,
                        "text": str(el.text or "")[:200],
                        "html": str(el.html_content or "")[:500],
                    })

            return ExtractResult(
                url=url, selector=example_selector,
                items=items, elapsed_s=time.time() - t0,
                fetched_at=_now_iso(),
            )
        except Exception as e:  # noqa: BLE001
            return ExtractResult(url=url, selector=example_selector,
                                  elapsed_s=time.time() - t0, fetched_at=_now_iso())

    @staticmethod
    def _fetch_page(url: str, *, fetcher: str = "fetcher",
                    timeout: float = 15, adaptive: bool = False,
                    **kwargs: Any) -> Any:
        """Fetch a page and return the Scrapling Response/Selector object."""
        if fetcher == "stealthy":
            from scrapling import StealthyFetcher
            if adaptive:
                StealthyFetcher.adaptive = True
            return StealthyFetcher.fetch(url, real_chrome=True, timeout=int(timeout * 1000), **kwargs)
        elif fetcher == "dynamic":
            from scrapling import DynamicFetcher
            if adaptive:
                DynamicFetcher.adaptive = True
            return DynamicFetcher.fetch(url, real_chrome=True, timeout=int(timeout * 1000), **kwargs)
        else:
            from scrapling import Fetcher
            if adaptive:
                Fetcher.adaptive = True
            return Fetcher.get(url, timeout=timeout, **kwargs)
