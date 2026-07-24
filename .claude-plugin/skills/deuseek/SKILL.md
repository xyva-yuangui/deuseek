---
name: deuseek
description: 搜索之神 (deuseek) — Use when the user needs to search the web or specific platforms (HackerNews / YouTube / GitHub / Bilibili / 微信公众号 / Reddit / RSS). Provides free multi-source search + Scrapling-powered stealth fetch (Cloudflare bypass) + adaptive parsing + full-text content extraction. All sources are free, no API keys needed for core functionality.
---

# 搜索之神 (deuseek)

deuseek 是一个免费多源搜索 + 隐身抓取 CLI，整合 web 搜索 (DuckDuckGo) + 多平台读取 (HN / YouTube / GitHub / B站 / 微信公众号 / Reddit / RSS) + Scrapling 三档抓取引擎 (Fetcher/StealthyFetcher/DynamicFetcher) 到一条命令。

两个核心子命令:
- `deuseek search <query>` → 全网 SERP (metadata + URL)
- `deuseek fetch <url>` → URL 拉成全文 markdown (ddgs extract 优先, Jina Reader fallback)

## Agent 调用约定 (重要)

**作为 Agent 调用 deuseek 时, 永远显式拿 JSON**:

1. 每条命令加 `--json`: `deuseek search --json "..."` / `deuseek fetch --json "<url>"`
2. 或设环境变量: `export DEUSEEK_FORCE_JSON=1`

## 如何使用

### 安装

```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
deuseek init
```

### Search — 拿 URL + metadata

```bash
deuseek search --json "Python asyncio best practices"
```

返回标准化 envelope:
```json
{
  "query": "...",
  "ts": "ISO 8601 Z",
  "results": [{"source", "title", "url", "content", "ts", "score"}],
  "errors": [{"source", "error", "category"}]
}
```

`content` 是 SERP snippet (≤ 500 字)。要全文用 `deuseek fetch <url>`。

### Fetch — URL → 全文 markdown

```bash
deuseek fetch --json "https://example.com/article"   # auto → ddgs → jina
```

### 限定源

```bash
deuseek search --on hackernews --json "show hn"
deuseek search --on bilibili --json "编程教程"
deuseek search --on wechat --json "claude 4.7"
```

### 模式

```bash
deuseek search --mode quick "..."  # 只查 web + hackernews
deuseek search --mode deep  "..."  # 全部就绪源
```

### 缓存

搜索结果缓存 10 分钟。用 `--no-cache` 强制刷新:
```bash
deuseek search --no-cache --json "..."
```

## 何时用 deuseek 而不是其他工具

- **用 `deuseek search`**: 搜 web + HN/GitHub/B站/微信/YouTube 等多平台
- **用 `deuseek fetch`**: 拿到 URL 后想取全文 markdown
- **不用**: 简单网页打开 (用 WebFetch), 或代码搜索 (用 grep)
