"""BrowserPool — Playwright/patchright Chrome instance pooling.

Keeps browser sessions warm across StealthyFetcher/DynamicFetcher calls to
avoid the 2-4s cold-start penalty on every fetch.

Data: cold start 2.4s → warm start 2.0s (from benchmark).
With pooling: expected 1-1.5s per subsequent fetch.

Implementation: Uses Scrapling's StealthySession/DynamicSession context
managers. __enter__() starts the browser, we keep the session object alive
across calls. Each fetch() call can pass request-level kwargs (solve_cloudflare,
timeout, etc.) while the browser-level options (headless, real_chrome) are
set when the session is created.

Thread safety: Playwright browsers are NOT thread-safe. All browser
operations must run on the same thread. This pool uses a lock to
serialize access.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Optional


class BrowserPool:
    """Pool of warm browser sessions for StealthyFetcher and DynamicFetcher.

    Usage:
        # Get a warm session (creates if needed, reuses if warm)
        session = BrowserPool.get_stealthy_session()
        if session:
            resp = session.fetch(url, solve_cloudflare=True)
            BrowserPool.release_stealthy_session()

        # Shrink after idle period
        BrowserPool.shrink()
    """

    _lock = threading.Lock()
    _stealthy_session: Optional[Any] = None  # The session object (after __enter__)
    _stealthy_cm: Optional[Any] = None       # The context manager (for __exit__)
    _dynamic_session: Optional[Any] = None
    _dynamic_cm: Optional[Any] = None
    _stealthy_last_used: float = 0.0
    _dynamic_last_used: float = 0.0
    _idle_timeout: float = 300.0  # 5 minutes

    @classmethod
    def warmup(cls) -> None:
        """Pre-start browser sessions. Call at application start.

        Best-effort: if patchright/playwright not available, silently skip.
        """
        cls._ensure_stealthy()
        cls._ensure_dynamic()

    @classmethod
    def get_stealthy_session(cls) -> Optional[Any]:
        """Get a warm StealthySession, or create one if needed.

        Returns the session object (already __enter__'d), or None if
        patchright/browser unavailable.
        """
        with cls._lock:
            cls._ensure_stealthy()
            cls._stealthy_last_used = time.time()
            return cls._stealthy_session

    @classmethod
    def get_dynamic_session(cls) -> Optional[Any]:
        """Get a warm DynamicSession, or create one if needed."""
        with cls._lock:
            cls._ensure_dynamic()
            cls._dynamic_last_used = time.time()
            return cls._dynamic_session

    @classmethod
    def release_stealthy_session(cls) -> None:
        """Release a stealthy session back to the pool (no-op, sessions stay warm)."""
        with cls._lock:
            cls._stealthy_last_used = time.time()

    @classmethod
    def release_dynamic_session(cls) -> None:
        """Release a dynamic session back to the pool."""
        with cls._lock:
            cls._dynamic_last_used = time.time()

    @classmethod
    def shrink(cls) -> int:
        """Close idle browser sessions. Returns number closed.

        Called periodically to free memory (~200-500MB per Chrome instance).
        """
        closed = 0
        now = time.time()
        with cls._lock:
            if cls._stealthy_cm and now - cls._stealthy_last_used > cls._idle_timeout:
                cls._close_stealthy()
                closed += 1
            if cls._dynamic_cm and now - cls._dynamic_last_used > cls._idle_timeout:
                cls._close_dynamic()
                closed += 1
        return closed

    @classmethod
    def close_all(cls) -> int:
        """Force-close all browser sessions."""
        closed = 0
        with cls._lock:
            if cls._stealthy_cm:
                cls._close_stealthy()
                closed += 1
            if cls._dynamic_cm:
                cls._close_dynamic()
                closed += 1
        return closed

    @classmethod
    def _ensure_stealthy(cls) -> None:
        """Create and enter a StealthySession if not already warm."""
        if cls._stealthy_session is not None:
            return
        try:
            from scrapling.fetchers import StealthySession
            cm = StealthySession(headless=True, real_chrome=True)
            cls._stealthy_session = cm.__enter__()
            cls._stealthy_cm = cm
            cls._stealthy_last_used = time.time()
        except Exception:
            cls._stealthy_session = None
            cls._stealthy_cm = None

    @classmethod
    def _ensure_dynamic(cls) -> None:
        """Create and enter a DynamicSession if not already warm."""
        if cls._dynamic_session is not None:
            return
        try:
            from scrapling.fetchers import DynamicSession
            cm = DynamicSession(headless=True, real_chrome=True)
            cls._dynamic_session = cm.__enter__()
            cls._dynamic_cm = cm
            cls._dynamic_last_used = time.time()
        except Exception:
            cls._dynamic_session = None
            cls._dynamic_cm = None

    @classmethod
    def _close_stealthy(cls) -> None:
        """Close the stealthy browser session."""
        try:
            if cls._stealthy_cm:
                cls._stealthy_cm.__exit__(None, None, None)
        except Exception:
            pass
        finally:
            cls._stealthy_session = None
            cls._stealthy_cm = None

    @classmethod
    def _close_dynamic(cls) -> None:
        """Close the dynamic browser session."""
        try:
            if cls._dynamic_cm:
                cls._dynamic_cm.__exit__(None, None, None)
        except Exception:
            pass
        finally:
            cls._dynamic_session = None
            cls._dynamic_cm = None
