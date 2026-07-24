"""Tests for the source registry (sources.yml loading and adapter importability)."""

import pytest

from deuseek.registry import Registry, SourceSpec, load_registry


class TestRegistry:
    def test_load_registry(self):
        reg = load_registry()
        assert isinstance(reg, Registry)
        assert len(reg.sources) >= 8

    def test_all_source_ids(self):
        reg = load_registry()
        ids = {s.id for s in reg.sources}
        expected = {"web", "hackernews", "youtube", "github", "rss", "wechat", "bilibili", "reddit"}
        assert ids >= expected

    def test_get_valid_source(self):
        reg = load_registry()
        spec = reg.get("hackernews")
        assert spec.id == "hackernews"
        assert spec.tier == "ready"
        assert spec.trust > 0.0

    def test_get_invalid_source(self):
        reg = load_registry()
        with pytest.raises(KeyError):
            reg.get("nonexistent")

    def test_default_auto_sources(self):
        reg = load_registry()
        auto = reg.default_auto_sources()
        ids = {s.id for s in auto}
        assert "web" in ids
        assert "hackernews" in ids
        assert "rss" not in ids  # default_in_auto=false

    def test_hints_match(self):
        reg = load_registry()
        matches = reg.sources_matching_hints("github repo")
        ids = {s.id for s in matches}
        assert "github" in ids

    def test_hints_no_match(self):
        reg = load_registry()
        matches = reg.sources_matching_hints("zzz_nonexistent_hint_zzz")
        assert len(matches) == 0

    def test_all_adapters_importable(self):
        """Every adapter class path in sources.yml must be importable."""
        reg = load_registry()
        failed = []
        for s in reg.sources:
            try:
                cls = s.load_adapter_class()
                assert cls is not None
            except Exception as e:
                failed.append(f"{s.id}: {e}")
        assert not failed, f"Failed to import adapters: {failed}"