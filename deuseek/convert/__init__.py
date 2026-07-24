"""convert/ — HTML→Markdown conversion layer.

v0.12: Full-text reading efficiency optimization. Core principle:
**don't delete content, delete noise; don't reduce reading, improve quality.**

Three layers of noise removal:
1. Expanded noise tags: script/style/noscript/svg + nav/footer/aside/form/iframe/button/input/select
2. Smart main-content extraction: article → main → [role=main] → #content → body
3. AI safety: CSS-hidden elements, zero-width Unicode, control chars

Plus: section structure extraction (h1-h6 headings + has_code flags),
Markdown quality repair (code-block language tags, fragment merging),
and content statistics.

Exposes a single function: ``html_to_markdown()``, which returns four
values ``(markdown, html, sections, stats)`` — callers that only need
markdown can ignore the extra returns. Falls back to ``html2text`` and
a regex tag-stripper when ``markdownify``/Scrapling is unavailable.
"""

from deuseek.convert.converter import html_to_markdown

__all__ = ["html_to_markdown"]
