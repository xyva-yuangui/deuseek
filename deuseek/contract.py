"""SearchResult JSON contract — the boundary between deuseek core and adapters."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# v0.8: SERP-snippet rule enforced at the contract boundary. Full upstream
# payloads remain accessible via SearchResult.raw — see
# docs/superpowers/specs/2026-05-27-deuseek-v0.8-design.md.
_SNIPPET_MAX = 500
_ELLIPSIS = "…"


class Engagement(BaseModel):
    model_config = ConfigDict(extra="allow")
    likes: int | None = None
    comments: int | None = None
    shares: int | None = None
    views: int | None = None


class SearchResult(BaseModel):
    """One normalized hit from one source."""

    model_config = ConfigDict(extra="forbid")

    source: str = Field(description="logical source id, e.g. 'hackernews'")
    adapter: str = Field(description="which adapter produced this, e.g. 'agent-reach'")
    title: str
    url: str
    content: str = ""
    author: str | None = None
    ts: str | None = Field(default=None, description="ISO 8601 publish ts")
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    engagement: Engagement | None = None
    raw: dict[str, Any] = Field(default_factory=dict)
    cost: Literal["free", "paid"] = "free"
    raw_score: float = Field(default=0.0, ge=0.0, le=1.0)

    @field_validator("content")
    @classmethod
    def _truncate_content(cls, v: str) -> str:
        if len(v) <= _SNIPPET_MAX:
            return v
        return v[:_SNIPPET_MAX] + _ELLIPSIS


class SourceError(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source: str
    error: str
    category: Literal["unavailable", "failed"] = "failed"


class SearchEnvelope(BaseModel):
    """The top-level JSON returned by `deuseek "<query>"`."""

    model_config = ConfigDict(extra="forbid")

    query: str
    ts: str
    results: list[SearchResult] = Field(default_factory=list)
    errors: list[SourceError] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# v0.11: Fetch / Crawl / Extract result types — Scrapling integration layer
# ---------------------------------------------------------------------------

_BACKENDS = Literal["fetcher", "stealthy", "dynamic", "jina", "native"]


class FetchResult(BaseModel):
    """Result of fetching a single URL to full-text content."""

    model_config = ConfigDict(extra="forbid")

    url: str
    backend: str = Field(description="which engine handled this, e.g. 'fetcher'")
    success: bool = False
    content_markdown: str = ""
    content_html: str = ""
    status_code: int = 0
    elapsed_s: float = 0.0
    errors: list[str] = Field(default_factory=list)
    captcha_suspected: bool = False
    fetched_at: str = Field(default="", description="ISO 8601 UTC")
    sections: list[ContentSection] = Field(default_factory=list, description="headings with has_code flags")
    content_stats: ContentStats | None = None


class ContentSection(BaseModel):
    """One heading in a page, with code-block presence flag."""
    model_config = ConfigDict(extra="forbid")
    heading: str
    level: int = Field(ge=1, le=6)
    has_code: bool = False


class ContentStats(BaseModel):
    """Statistics about the converted content."""
    model_config = ConfigDict(extra="forbid")
    word_count: int = 0
    code_block_count: int = 0


class ExtractField(BaseModel):
    """One field extracted from a page via CSS/XPath selector."""

    model_config = ConfigDict(extra="forbid")

    name: str
    value: str = ""
    found: bool = True


class ExtractResult(BaseModel):
    """Result of structured extraction from a single page."""

    model_config = ConfigDict(extra="forbid")

    url: str
    selector: str = ""
    items: list[dict[str, Any]] = Field(default_factory=list)
    adaptive: bool = False
    relocated: bool = Field(default=False, description="whether adaptive relocation was triggered")
    elapsed_s: float = 0.0
    fetched_at: str = ""


class CrawlStats(BaseModel):
    """Statistics from a Spider crawl."""

    model_config = ConfigDict(extra="allow")

    requests_count: int = 0
    failed_requests_count: int = 0
    items_scraped: int = 0
    items_dropped: int = 0
    blocked_requests_count: int = 0
    elapsed_seconds: float = 0.0
    requests_per_second: float = 0.0


class CrawlResult(BaseModel):
    """Result of a multi-page Spider crawl."""

    model_config = ConfigDict(extra="forbid")

    start_url: str
    items: list[dict[str, Any]] = Field(default_factory=list)
    stats: CrawlStats = Field(default_factory=CrawlStats)
    elapsed_s: float = 0.0
    paused: bool = False
    completed: bool = True
    fetched_at: str = ""


class FetchEnvelope(BaseModel):
    """The top-level JSON returned by `deuseek fetch <url>`."""

    model_config = ConfigDict(extra="forbid")

    url: str
    backend: str | None = None
    fetched_at: str
    content_markdown: str = ""
    content_html: str = ""
    status_code: int = 0
    errors: list[str] = Field(default_factory=list)
    sections: list[ContentSection] = Field(default_factory=list)
    content_stats: ContentStats | None = None
