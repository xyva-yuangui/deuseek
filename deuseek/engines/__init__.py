"""engines/ — Scrapling 全能力封装层.

Three fetcher engines + one parser engine, each wrapping the corresponding
Scrapling API without stripping parameters. deuseek's router layer decides
which engine to use; engines themselves are stateless singletons.
"""

from deuseek.engines.fetcher import FetcherEngine
from deuseek.engines.stealthy import StealthyEngine
from deuseek.engines.dynamic import DynamicEngine
from deuseek.engines.parser import ParserEngine

__all__ = ["FetcherEngine", "StealthyEngine", "DynamicEngine", "ParserEngine"]
