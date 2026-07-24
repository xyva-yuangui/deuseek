"""Tests for the source router (query hints, modes, explicit --on)."""

import pytest

from deuseek.registry import load_registry
from deuseek.router import RouteRequest, Router


@pytest.fixture
def router():
    reg = load_registry()
    return Router(reg)


class TestRouter:
    def test_explicit_sources(self, router):
        route = router.plan(RouteRequest(query="test", explicit_sources=["hackernews", "web"]))
        assert route.source_ids == ["hackernews", "web"]
        assert route.rationale == "explicit --on"

    def test_explicit_unknown_source(self, router):
        route = router.plan(RouteRequest(query="test", explicit_sources=["nonexistent", "web"]))
        assert "web" in route.source_ids
        assert "nonexistent" in route.unknown_sources

    def test_mode_quick(self, router):
        route = router.plan(RouteRequest(query="test", mode="quick"))
        assert "web" in route.source_ids
        assert "hackernews" in route.source_ids
        assert route.rationale == "mode=quick"

    def test_mode_deep(self, router):
        route = router.plan(RouteRequest(query="test", mode="deep"))
        assert len(route.source_ids) >= 3  # at least web + hn + some
        assert len(route.source_ids) <= 5  # MAX_SOURCES
        assert route.rationale == "mode=deep"

    def test_auto_with_hints(self, router):
        route = router.plan(RouteRequest(query="github repo search"))
        assert "github" in route.source_ids
        assert route.rationale == "auto: hints + defaults"

    def test_auto_no_hints(self, router):
        route = router.plan(RouteRequest(query="zzz_no_match"))
        # defaults only
        assert "web" in route.source_ids
        assert "hackernews" in route.source_ids

    def test_rss_gated_on_url(self, router):
        """RSS should only be included when the query is a URL."""
        non_url = router.plan(RouteRequest(query="some topic"))
        assert "rss" not in non_url.source_ids

        url = router.plan(RouteRequest(query="https://example.com/feed.xml"))
        assert "rss" in url.source_ids