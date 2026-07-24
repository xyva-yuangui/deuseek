"""Shared utility functions — extracted from duplicated copies across commands/engines/native.

Previously _should_emit_json and _now_iso were copy-pasted into 6+ files.
Now all modules import from here.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone


def should_emit_json(explicit_flag: bool) -> bool:
    """Decide whether to output JSON. Explicit flag > env var > not a TTY."""
    if explicit_flag:
        return True
    if os.environ.get("DEUSEEK_FORCE_JSON", "").lower() in ("1", "true", "yes"):
        return True
    return not sys.stdout.isatty()


def now_iso() -> str:
    """Current UTC time in ISO 8601 with Z suffix."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
