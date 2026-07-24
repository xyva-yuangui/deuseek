"""HTML→Markdown converter — shared by engines and pipeline.

v0.12: Full-text reading efficiency optimization. Core principle:
**don't delete content, delete noise; don't reduce reading, improve quality.**

Three layers of noise removal:
1. Expanded noise tags: script/style/noscript/svg + nav/footer/aside/form/iframe/button/input/select
2. Smart main-content extraction: article → main → [role=main] → #content → body
3. AI safety: CSS-hidden elements, zero-width Unicode, control chars

Plus: section structure extraction (h1-h6 + has_code), Markdown quality
repair (language tags, fragment merging), and content statistics.

Returns (markdown, html, sections, stats) — all four values.
Callers that only need markdown can ignore the extra returns.
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Tags that carry no readable content — removed via lxml drop_tree() (tree-based, not regex).
_NOISE_TAGS = frozenset({
    "script", "style", "noscript", "svg",
    "nav", "footer", "aside", "form", "iframe",
    "button", "input", "select", "textarea",
})

# CSS selectors for main content, tried in order (first match with >200 chars wins).
_CONTENT_SELECTORS = [
    "article",
    "main",
    "[role='main']",
    "#content", "#main-content", "#main", "#post-content",
    ".content", ".post-content", ".article-content", ".entry-content",
]

# Zero-width Unicode chars and XML control chars (except TAB/LF/CR).
_ZWC = re.compile(r"[\u200b\u200c\u200d\ufeff\u2060\u180e]")
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

# Regex for fallback path (serialized HTML).
_NOISE_TAG_RE = re.compile(
    r"<(script|style|noscript|svg|nav|footer|aside|form|iframe|button|input|select)\b[^>]*>.*?</\1>",
    flags=re.DOTALL | re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Noise stripping (tree-based, uses lxml drop_tree)
# ---------------------------------------------------------------------------

def _strip_noise(page: Any) -> Any:
    """Remove noise tags and CSS-hidden elements from the parsed tree.

    Uses lxml's drop_tree() — structurally correct, unlike regex on
    serialized HTML which can mis-handle > inside script blocks.

    v0.12.1: Replaced deepcopy(page._root) with lxml.html.fromstring()
    for ~5x speedup on large pages. Merged two root.iter() loops into one.
    """
    from scrapling.parser import Selector

    try:
        # Create independent tree via reparse (faster than deepcopy for large DOMs)
        html_str = str(page.html_content) if page.html_content else ""
        if not html_str:
            return page
        from lxml.html import fromstring
        root = fromstring(html_str)
    except Exception:
        return page  # can't reparse → return as-is

    # Single pass: remove noise tags + CSS-hidden + aria-hidden
    for el in list(root.iter()):
        if not isinstance(el.tag, str):
            continue
        tag = el.tag.lower()

        # Noise tags (script/style/nav/footer/aside/form/iframe/etc.)
        if tag in _NOISE_TAGS:
            el.drop_tree()
            continue

        # CSS-hidden elements (display:none / visibility:hidden / opacity:0)
        style = el.get("style", "") or ""
        style_lower = style.lower().replace(" ", "")
        if any(kw in style_lower for kw in (
            "display:none", "visibility:hidden", "opacity:0",
        )):
            el.drop_tree()
            continue

        # aria-hidden=true
        if el.get("aria-hidden", "").lower() == "true":
            el.drop_tree()
            continue

    return Selector(root=root, url=getattr(page, "url", ""))


# ---------------------------------------------------------------------------
# Smart main-content extraction
# ---------------------------------------------------------------------------

def _extract_main_content(page: Any) -> Any:
    """Try multiple CSS selectors to find the main content area.

    Falls back to <body> if no semantic content tag is found.
    Semantic tags (article, main, [role=main]) have no length threshold
    since they're reliable content markers. ID/class selectors need 200+ chars
    to avoid matching tiny ad widgets.
    """
    # Semantic tags: always use — they're reliable content markers
    _SEMANTIC = {"article", "main", "[role='main']"}
    for sel in _CONTENT_SELECTORS:
        found = page.css(sel)
        if found:
            content = found.first
            if content is None:
                continue
            html = str(content.html_content) if content.html_content else ""
            # Semantic tags: no length threshold (any match is valid)
            # ID/class selectors: need 200+ chars to avoid tiny ad widgets
            if sel in _SEMANTIC or len(html) > 200:
                return content

    # Fallback: <body>
    body = page.css("body").first
    return body if body is not None else page


# ---------------------------------------------------------------------------
# Section extraction (headings + has_code)
# ---------------------------------------------------------------------------

def _extract_sections(page: Any) -> list[dict]:
    """Extract h1-h6 headings, marking which sections contain code blocks."""
    sections: list[dict] = []
    try:
        headings = page.css("h1, h2, h3, h4, h5, h6")
        for h in headings:
            heading = str(h.text or "").strip()
            if not heading:
                continue
            level = int(h.tag[1]) if len(h.tag) > 1 and h.tag[1:].isdigit() else 6
            has_code = _section_has_code(page, h, level)
            sections.append({"heading": heading, "level": level, "has_code": has_code})
    except Exception:
        pass
    return sections


def _section_has_code(page: Any, heading_el: Any, heading_level: int) -> bool:
    """Check if there's a <pre> or <code> between this heading and the next same-or-higher level heading.

    Uses document-order traversal (not itersiblings) to correctly handle
    headings nested inside <div> wrappers — the code block may be in a
    sibling <div>, not a sibling element of the heading itself.
    """
    try:
        from lxml.etree import _Element

        root = heading_el._root if hasattr(heading_el, "_root") else heading_el
        if not isinstance(root, _Element):
            return False

        # Walk up to the page root for document-order traversal
        page_root = root
        while page_root.getparent() is not None:
            page_root = page_root.getparent()

        # Iterate all elements in document order, find this heading, scan forward
        found_heading = False
        for el in page_root.iter():
            if el is root:
                found_heading = True
                continue
            if not found_heading:
                continue
            if not isinstance(el.tag, str):
                continue
            tag = el.tag.lower()
            # Hit next heading at same or higher level → stop
            if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                if tag[1:2].isdigit() and int(tag[1]) <= heading_level:
                    break
            # Found code in this section
            if tag in ("pre", "code"):
                return True
        return False
    except Exception:
        return False


# ---------------------------------------------------------------------------
# AI safety: zero-width Unicode + control chars
# ---------------------------------------------------------------------------

def _clean_text(text: str) -> str:
    """Strip zero-width Unicode and XML control characters."""
    text = _ZWC.sub("", text)
    text = _CONTROL.sub("", text)
    return text


# ---------------------------------------------------------------------------
# Markdown quality repair
# ---------------------------------------------------------------------------

def _repair_markdown(md: str) -> str:
    """Fix common HTML→Markdown conversion issues."""
    # 1. Add language tags to code blocks that lack them
    #    Use [\r\n] to handle both Unix \n and Windows \r\n line endings
    # Go first: import " or import ( or package main or func (must check before Python)
    md = re.sub(r'```[\r\n](import ["(]|package main|func )', r"```go\n\1", md)
    # Python: import followed by identifier (not quote/paren), or from X import
    md = re.sub(r"```[\r\n](import [a-z_]|from \w+ import )", r"```python\n\1", md)
    # JavaScript
    md = re.sub(r"```[\r\n](function |const |let |var |=>|import .* from)", r"```javascript\n\1", md)
    md = re.sub(r"```[\r\n](public |private |protected |class )", r"```java\n\1", md)
    md = re.sub(r"```[\r\n](#include |int main|#define )", r"```cpp\n\1", md)
    md = re.sub(r"```[\r\n](curl |sudo |apt |pip |npm |docker )", r"```bash\n\1", md)
    md = re.sub(r"```[\r\n](echo |export |cat |ls |cd )", r"```bash\n\1", md)

    # 2. Clean zero-width chars and control chars from markdown
    md = _ZWC.sub("", md)
    md = _CONTROL.sub("", md)

    # 3. Fix fragmented single-word paragraphs: merge lines that are just 1-3 words
    #    followed by newline back with the previous paragraph.
    #    Only merge if the "paragraph" has no punctuation at the end.
    #    (Conservative: only merge very short orphaned lines)
    lines = md.split("\n")
    repaired: list[str] = []
    for line in lines:
        stripped = line.strip()
        if (stripped and len(stripped) <= 15 and not stripped.endswith(".")
                and not stripped.endswith(",") and not stripped.endswith(":")
                and not stripped.startswith("#") and not stripped.startswith("|")
                and not stripped.startswith("```") and not stripped.startswith("-")
                and repaired and repaired[-1].strip()):
            # Merge short orphan line with previous
            repaired[-1] = repaired[-1].rstrip() + " " + stripped
        else:
            repaired.append(line)
    md = "\n".join(repaired)

    return md


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def _compute_stats(md: str) -> dict:
    """Compute content statistics."""
    # Use count() instead of split() to avoid temporary list allocation
    words = md.count(" ") + md.count("\n") + 1  # approximate word count
    code_blocks = md.count("```") // 2
    return {"word_count": words, "code_block_count": code_blocks}


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def html_to_markdown(
    page_or_html: Any,
    *,
    url: str = "",
    main_content_only: bool = True,
    css_selector: str | None = None,
) -> tuple[str, str, list[dict], dict]:
    """Convert HTML content to (markdown, html, sections, stats).

    Args:
        page_or_html: A Scrapling Response/Selector object, or a raw HTML string.
        url: Source URL (for relative link resolution).
        main_content_only: If True, extract main content + strip noise.
        css_selector: If given, only convert elements matching this selector.

    Returns:
        (markdown_string, html_string, sections_list, stats_dict)
        sections_list: [{"heading": str, "level": int, "has_code": bool}]
        stats_dict: {"word_count": int, "code_block_count": int}
    """
    # If given a Scrapling page/Response object, use it directly
    if hasattr(page_or_html, "html_content"):
        return _convert_page(page_or_html, main_content_only, css_selector)

    # If given raw HTML string, wrap in a Selector first
    html = str(page_or_html) if page_or_html else ""
    if not html:
        return "", "", [], {"word_count": 0, "code_block_count": 0}

    try:
        from scrapling.parser import Selector

        page = Selector(content=html, url=url)
        return _convert_page(page, main_content_only, css_selector)
    except Exception:
        # Last resort: html2text directly on the string
        md = _fallback_html2text(html)
        md = _repair_markdown(md)
        md = _clean_text(md)
        stats = _compute_stats(md)
        return md, html, [], stats


def _convert_page(
    page: Any,
    main_content_only: bool = True,
    css_selector: str | None = None,
) -> tuple[str, str, list[dict], dict]:
    """Convert a Selector/Response to (markdown, html, sections, stats)."""
    html = str(page.html_content) if page.html_content else ""

    try:
        from markdownify import markdownify as md_func

        # Step 1: Smart main-content extraction
        if main_content_only:
            page = _extract_main_content(page)
            # Step 2: Noise stripping (tree-based)
            page = _strip_noise(page)

        # Step 3: Section extraction (before conversion, from parsed tree)
        sections = _extract_sections(page)

        # Step 4: Optionally narrow to user CSS selector
        if css_selector:
            pages = list(page.css(css_selector))
        else:
            pages = [page]

        # Step 5: Convert to markdown
        chunks: list[str] = []
        for p in pages:
            content = str(p.html_content) if p.html_content else ""
            chunks.append(md_func(content))
        md = "".join(chunks).strip()

        # Step 6: Markdown quality repair
        md = _repair_markdown(md)

        # Step 7: AI safety cleanup
        md = _clean_text(md)

        # Step 8: Statistics
        stats = _compute_stats(md)

        return md, html, sections, stats
    except Exception:
        md = _fallback_html2text(html)
        md = _repair_markdown(md)
        md = _clean_text(md)
        stats = _compute_stats(md)
        return md, html, [], stats


def _fallback_html2text(html: str) -> str:
    """html2text fallback when markdownify/Scrapling is unavailable."""
    try:
        import html2text

        h = html2text.HTML2Text()
        h.ignore_links = False
        h.body_width = 0
        return h.handle(html)
    except Exception:
        # Absolute last resort: strip tags with a regex
        clean = _NOISE_TAG_RE.sub("", html)
        text = re.sub(r"<[^>]+>", " ", clean)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
