"""perf/ — performance infrastructure.

DomainKB: domain→backend mapping (avoids trial-and-error on every fetch).
BrowserPool: Playwright/patchright Chrome instance pooling (warm start).
Cache: L1 memory + L2 disk cache for search results and fetched content.

Note: SessionPool was removed — Scrapling's FetcherClient is already a
process-level singleton with curl_cffi connection pooling built-in. No
additional wrapper needed.
"""

from deuseek.perf.domain_kb import DomainKB
from deuseek.perf.cache import Cache
from deuseek.perf.browser_pool import BrowserPool

__all__ = ["DomainKB", "Cache", "BrowserPool"]
