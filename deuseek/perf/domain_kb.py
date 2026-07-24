"""DomainKB — domain→backend knowledge base.

Remembers which Scrapling engine works for each domain, so we don't waste
time on trial-and-error. Data: nopecha-cf wastes 0.5s on Fetcher + 5.7s on
jina before finally trying StealthyFetcher+CF (37s). If DomainKB remembers
"cloudflare", it skips straight to the right engine.

v0.11.1: TTL support — entries expire after 24h, forcing re-probe.
This prevents stale records when a site changes its anti-bot config.

Persistence: JSON file at platform-appropriate path.
"""

from __future__ import annotations

import json
import os
import platform
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

# Default TTL: 24 hours. After this, entries expire and force re-probe.
DEFAULT_TTL = 86400  # 24 * 60 * 60


def _default_path() -> Path:
    """Platform-appropriate storage path."""
    base = os.environ.get("DEUSEEK_HOME")
    if base:
        return Path(base) / "domain_kb.json"

    system = platform.system()
    if system == "Darwin":
        # macOS: ~/Library/Application Support/deuseek/
        return Path.home() / "Library/Application Support/deuseek" / "domain_kb.json"
    elif system == "Windows":
        # Windows: %APPDATA%/deuseek/
        appdata = os.environ.get("APPDATA", str(Path.home()))
        return Path(appdata) / "deuseek" / "domain_kb.json"
    else:
        # Linux/Unix: ~/.local/share/deuseek/ (XDG)
        xdg = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
        return Path(xdg) / "deuseek" / "domain_kb.json"


class DomainKB:
    """Thread-safe domain→backend knowledge base with JSON persistence and TTL."""

    def __init__(self, path: Path | None = None, *, ttl: float = DEFAULT_TTL) -> None:
        self._path = path or _default_path()
        self._ttl = ttl
        self._lock = threading.Lock()
        self._data: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        """Load from disk, or start empty."""
        try:
            if self._path.exists():
                raw = json.loads(self._path.read_text(encoding="utf-8"))
                self._data = raw if isinstance(raw, dict) else {}
        except (json.JSONDecodeError, OSError):
            self._data = {}

    def _save(self) -> None:
        """Persist to disk (best-effort)."""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(
                json.dumps(self._data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

    @staticmethod
    def _domain_of(url: str) -> str:
        """Extract registrable domain from URL."""
        try:
            host = urlparse(url).hostname or ""
            # Take last two labels for simple domain extraction
            parts = host.split(".")
            if len(parts) >= 2:
                return ".".join(parts[-2:])
            return host
        except Exception:
            return ""

    def _is_expired(self, entry: dict) -> bool:
        """Check if a DomainKB entry has expired (TTL)."""
        updated = entry.get("updated", "")
        if not updated:
            return True  # No timestamp → expired
        try:
            entry_ts = datetime.fromisoformat(updated.replace("Z", "+00:00")).timestamp()
            return time.time() - entry_ts > self._ttl
        except (ValueError, TypeError):
            return True

    def get(self, url: str) -> str | None:
        """Look up the best backend for a URL's domain.

        Returns one of: "fetcher", "stealthy", "dynamic", "jina", "native"
        or None if unknown or expired.
        """
        domain = self._domain_of(url)
        if not domain:
            return None
        with self._lock:
            entry = self._data.get(domain)
            if not entry:
                return None
            # TTL check: expired entries are treated as unknown
            if self._is_expired(entry):
                return None
            return entry.get("backend")

    def get_blocked(self, url: str) -> list[str]:
        """Get list of backends known to fail for this domain."""
        domain = self._domain_of(url)
        if not domain:
            return []
        with self._lock:
            entry = self._data.get(domain)
            if not entry:
                return []
            # Don't return blocked list for expired entries
            if self._is_expired(entry):
                return []
            return entry.get("blocked", [])

    def set(self, url: str, backend: str) -> None:
        """Record that `backend` successfully fetched this domain."""
        domain = self._domain_of(url)
        if not domain:
            return
        with self._lock:
            entry = self._data.setdefault(domain, {
                "backend": backend, "blocked": [], "updated": "",
            })
            entry["backend"] = backend
            entry["updated"] = datetime.now(timezone.utc).isoformat()
            if backend in entry.get("blocked", []):
                entry["blocked"].remove(backend)
            self._save()

    def set_blocked(self, url: str, backend: str) -> None:
        """Record that `backend` failed for this domain."""
        domain = self._domain_of(url)
        if not domain:
            return
        with self._lock:
            entry = self._data.setdefault(domain, {
                "backend": "", "blocked": [], "updated": "",
            })
            if backend not in entry["blocked"]:
                entry["blocked"].append(backend)
            entry["updated"] = datetime.now(timezone.utc).isoformat()
            self._save()

    def all(self) -> dict[str, dict]:
        """Return a snapshot of all known domains (for debugging)."""
        with self._lock:
            return dict(self._data)

    def clear(self) -> None:
        """Wipe the knowledge base."""
        with self._lock:
            self._data = {}
            self._save()
