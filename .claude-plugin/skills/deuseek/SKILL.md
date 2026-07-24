---
name: deuseek
description: deuseek — 全网通搜索 + 隐身抓取 Skill. Use when the user needs to search the web or specific platforms (HackerNews / YouTube / GitHub / Bilibili / 微信公众号 / Reddit / RSS), fetch any URL to full-text markdown, bypass Cloudflare/anti-bot, or extract structured data. Free multi-source search + Scrapling three-tier stealth fetch + adaptive parsing. No API keys needed for core. 当用户需要搜索网页/多平台、取 URL 全文 markdown、绕反爬抓取、或结构化提取时调用。
---

# deuseek

deuseek 是一个免费多源搜索 + 隐身抓取 CLI + Claude Code Skill。整合 web 搜索 (DuckDuckGo) + 多平台读取 (HN / YouTube / GitHub / B站 / 微信公众号 / Reddit / RSS) + Scrapling 三层抓取引擎 (Fetcher / StealthyFetcher / DynamicFetcher) 到一条命令。

核心子命令:
- `deuseek search <query>` → 全网 SERP (metadata + URL, content ≤500 字)
- `deuseek fetch <url>` → URL 拉成全文 markdown (Scrapling 三层路由 + DomainKB)
- `deuseek super <query>` → 端到端: 多源 search → 隐身 fetch → (可选) extract, 流式 pipeline

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

`content` 是 SERP snippet (≤500 字)。要全文用 `deuseek fetch <url>`。

### Fetch — URL → 全文 markdown

三层路由自动选 (越往后越重、越能破反爬):
- `Fetcher` (curl_cffi HTTP + TLS 指纹, 0.4–3.9s, 默认)
- `jina` ([r.jina.ai](https://r.jina.ai/) SaaS, 服务端 IP, fallback)
- `StealthyFetcher` (patchright 隐身 Chrome) + `solve_cloudflare` (兜底, 唯一能过 Cloudflare Turnstile)

```bash
deuseek fetch --json "https://example.com/article"                 # auto 三层路由
deuseek fetch --json "https://mp.weixin.qq.com/s/<token>"          # 自动走 OpenCLI 登录态
deuseek fetch --json <url> --backend stealthy --solve-cloudflare    # 强制隐身 + 绕 CF
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

搜索结果缓存 10 分钟, fetch 缓存 1 小时。用 `--no-cache` 强制刷新:
```bash
deuseek search --no-cache --json "..."
```

## 何时用 deuseek 而不是其他工具

- **用 `deuseek search`**: 搜 web + HN/GitHub/B站/微信/YouTube/Reddit 等多平台
- **用 `deuseek fetch`**: 拿到 URL 后想取全文 markdown, 尤其遇到 Cloudflare/反爬
- **用 `deuseek super`**: 一句话要"搜 + 抓 + 提"端到端
- **不用**: 简单网页打开 (用 WebFetch), 或代码搜索 (用 grep)
