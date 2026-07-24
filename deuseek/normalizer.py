"""Normalizer — wraps adapter outputs into a SearchEnvelope."""

from __future__ import annotations

from datetime import datetime, timezone

from deuseek.contract import SearchEnvelope, SearchResult, SourceError


def build_envelope(
    *, query: str, results: list[SearchResult], errors: list[SourceError]
) -> SearchEnvelope:
    return SearchEnvelope(
        query=query,
        ts=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        results=results,
        errors=errors,
    )


def dedup_results(results: list[SearchResult]) -> list[SearchResult]:
    """Cross-source URL dedup: same article from HN + Reddit → keep one.

    Uses URL canonicalization (strips tracking params like utm_source)
    to detect duplicates across sources.
    """
    seen_urls: set[str] = set()
    deduped: list[SearchResult] = []
    for r in results:
        canonical = _canonicalize_url(r.url)
        if canonical in seen_urls:
            continue
        seen_urls.add(canonical)
        deduped.append(r)
    return deduped


def _canonicalize_url(url: str) -> str:
    """Normalize URL for dedup: strip tracking params, fragment, sort query."""
    from urllib.parse import urlparse, parse_qsl, urlencode

    _TRACKING = frozenset({
        "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
        "fbclid", "gclid", "mc_cid", "mc_eid",
    })
    try:
        parsed = urlparse(url)
        params = [(k, v) for k, v in parse_qsl(parsed.query) if k not in _TRACKING]
        params.sort()
        query = urlencode(params)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}{'?' + query if query else ''}"
    except Exception:
        return url
