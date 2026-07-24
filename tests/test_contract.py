"""Tests for the pydantic contract models (SearchResult, SearchEnvelope, FetchResult, etc.)."""

from datetime import datetime, timezone

import pytest

from deuseek.contract import (
    CrawlResult,
    CrawlStats,
    Engagement,
    ExtractResult,
    FetchEnvelope,
    FetchResult,
    SearchEnvelope,
    SearchResult,
    SourceError,
)


class TestSearchResult:
    def test_basic_creation(self):
        r = SearchResult(
            source="web",
            adapter="ddgs",
            title="Test Title",
            url="https://example.com",
            content="Short content",
            score=0.5,
        )
        assert r.source == "web"
        assert r.title == "Test Title"
        assert r.cost == "free"
        assert r.raw_score == 0.0

    def test_content_truncation(self):
        """Content must be truncated to 500 chars + '…'."""
        long_content = "x" * 1000
        r = SearchResult(
            source="web",
            adapter="ddgs",
            title="T",
            url="https://example.com",
            content=long_content,
        )
        assert len(r.content) == 501  # 500 + '…'
        assert r.content.endswith("…")

    def test_content_no_truncation_short(self):
        short = "x" * 300
        r = SearchResult(
            source="web",
            adapter="ddgs",
            title="T",
            url="https://example.com",
            content=short,
        )
        assert r.content == short

    def test_engagement_none(self):
        r = SearchResult(
            source="web", adapter="ddgs", title="T", url="https://example.com",
        )
        assert r.engagement is None

    def test_engagement_with_data(self):
        e = Engagement(likes=10, comments=5, views=100)
        r = SearchResult(
            source="web", adapter="ddgs", title="T", url="https://example.com",
            engagement=e,
        )
        assert r.engagement is not None
        assert r.engagement.likes == 10

    def test_raw_preserved(self):
        raw = {"custom": "payload", "deep": {"nested": True}}
        r = SearchResult(
            source="web", adapter="ddgs", title="T", url="https://example.com",
            raw=raw,
        )
        assert r.raw == raw

    def test_extra_fields_forbidden(self):
        """SearchResult has extra='forbid', so unknown fields raise."""
        with pytest.raises(ValueError):
            SearchResult(
                source="web", adapter="ddgs", title="T", url="https://example.com",
                unknown_field="should_fail",
            )


class TestEngagement:
    def test_extra_allow(self):
        """Engagement has extra='allow', so unknown fields pass through."""
        e = Engagement(likes=1, unknown="passes")
        assert e.likes == 1
        assert e.unknown == "passes"


class TestSourceError:
    def test_categories(self):
        e1 = SourceError(source="test", error="msg", category="unavailable")
        e2 = SourceError(source="test", error="msg", category="failed")
        assert e1.category == "unavailable"
        assert e2.category == "failed"

    def test_default_category(self):
        e = SourceError(source="test", error="msg")
        assert e.category == "failed"


class TestSearchEnvelope:
    def test_basic(self):
        r = SearchResult(
            source="web", adapter="ddgs", title="T", url="https://example.com",
        )
        env = SearchEnvelope(query="test", ts="2026-01-01T00:00:00Z", results=[r], errors=[])
        assert env.query == "test"
        assert len(env.results) == 1
        assert len(env.errors) == 0
        assert env.ts.endswith("Z")

    def test_json_roundtrip(self):
        r = SearchResult(
            source="web", adapter="ddgs", title="T", url="https://example.com",
        )
        env = SearchEnvelope(query="test", ts="2026-01-01T00:00:00Z", results=[r], errors=[])
        data = env.model_dump_json()
        loaded = SearchEnvelope.model_validate_json(data)
        assert loaded.query == "test"
        assert loaded.results[0].title == "T"


class TestFetchResult:
    def test_basic(self):
        r = FetchResult(
            url="https://example.com",
            backend="fetcher",
            success=True,
            content_markdown="# Hello",
            status_code=200,
            elapsed_s=1.2,
        )
        assert r.success
        assert r.status_code == 200
        assert r.content_markdown == "# Hello"

    def test_errors_list(self):
        r = FetchResult(url="https://example.com", backend="fetcher", errors=["timeout"])
        assert len(r.errors) == 1


class TestFetchEnvelope:
    def test_basic(self):
        env = FetchEnvelope(
            url="https://example.com",
            fetched_at="2026-01-01T00:00:00Z",
            content_markdown="# Hello",
            status_code=200,
        )
        assert env.url == "https://example.com"
        assert env.content_markdown == "# Hello"


class TestExtractResult:
    def test_basic(self):
        r = ExtractResult(
            url="https://example.com",
            selector="h1::text",
            items=[{"title": "Hello"}],
            adaptive=True,
            elapsed_s=0.5,
        )
        assert r.adaptive is True
        assert len(r.items) == 1


class TestCrawlResult:
    def test_basic(self):
        stats = CrawlStats(requests_count=10, items_scraped=5)
        r = CrawlResult(
            start_url="https://example.com",
            items=[{"a": 1}],
            stats=stats,
            elapsed_s=3.0,
        )
        assert r.stats.requests_count == 10
        assert r.stats.items_scraped == 5
        assert r.completed is True