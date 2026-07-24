# CLAUDE.md — deuseek (免费全网通搜索 fork)

## 项目是什么

deuseek 是一个免费多源搜索 CLI + Claude Code Skill。基于 Daily-AC/deuseek 开源项目 fork 改造,
精简为纯免费版本 (移除付费 booster 与 OpenCLI 类源, 保留全部 Scrapling 隐身抓取能力)。

两个核心子命令:
- `deuseek search <query>` — 全网搜索 (返 metadata + URL, content 截断到 ≤500 字)
- `deuseek fetch <url>` — URL 拉成全文 markdown (Scrapling 三层路由 + DomainKB)

## 架构

- **Adapter 模式**: 每个搜索源一个 adapter，实现 `AdapterBase` ABC
- **异步并发**: `Dispatcher` 用 `asyncio.gather` 并发查询所有源，单源错误隔离
- **YAML 注册**: `sources.yml` 声明源的 tier、adapter class、trust、timeout
- **Router**: query_hints 自动路由 + `--on` 显式指定 + `--mode quick/deep`
- **Scorer**: 40% recency + 60% trust 排序 (权重和=1.0, 有 assert)
- **缓存**: `perf/cache.py` L1 内存 + L2 文件 (`~/.deuseek/cache/`)，search TTL 10 分钟, fetch TTL 1 小时
- **抓取路由**: `FetchRouter` 按 host + DomainKB 路由, 三层递进 fallback
- **契约**: `contract.py` pydantic 模型, `content` field_validator 截断 500 字

## 可用源 (全部免费, sources.yml)

| 源 | tier | 后端 |
|---|---|---|
| web | ready | DuckDuckGo (ddgs) |
| hackernews | ready | Algolia HN Search API |
| youtube | ready | yt-dlp |
| github | ready | gh CLI |
| rss | ready | feedparser (query 必须是 URL) |
| wechat | ready | Sogou 微信搜索 (可选 Scrapling 隐身增强) |
| bilibili | ready | B站官方 search API |
| reddit | one_step | rdt-cli (需 `rdt login`) |

## Fetch 后端 (v0.11+ Scrapling 整合)

三层递进 fallback (越往后越重、越能破反爬):
- **Fetcher** (首选): `scrapling.Fetcher` (curl_cffi HTTP + TLS 指纹), 0.4-3.9s, 80%+ URL
- **jina** (fallback): `r.jina.ai` SaaS, 服务器 IP 穿透部分反爬
- **StealthyFetcher** (兜底): `scrapling.StealthyFetcher` (patchright 隐身 Chrome) + `solve_cloudflare`, 唯一能过 Cloudflare Turnstile

外加:
- **DynamicFetcher** (Playwright, JS 渲染): 显式 `--backend dynamic`
- **native 路径**: wechat (OpenCLI 登录态) / bilibili (官方 API) / douyin (OpenCLI fork)
- **DomainKB**: domain→backend 记忆, 24h TTL, 避免每次试错
- **BrowserPool**: 常驻 warm session, 冷启 2.4s → ~1s
- **验证码自动升级**: 命中关键词 → 自动重试 StealthyFetcher+solve_cloudflare

## 开发

```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git   # 或 pip install -e .
deuseek init
deuseek doctor          # 体检各源 + fetch backend
python -m pytest tests/ -x -q   # (tests 尚未随本 fork 发布)
```

## 关键文件

- `deuseek/sources.yml` — 源注册表 (单一真相源)
- `deuseek/adapters/` — 各源 adapter (含 `_wechat_sogou.py` / `_bilibili_api.py` 后端实现)
- `deuseek/cli.py` — CLI 入口 (search / doctor 内联)
- `deuseek/commands/fetch.py` — fetch 子命令 (验证码启发式 + 自动升级)
- `deuseek/commands/super.py` — 旗舰端到端 pipeline (流式 search→fetch)
- `deuseek/dispatcher.py` — 并发调度 + 缓存 + 超时 + 错误隔离
- `deuseek/fetch_router/router.py` — host/DomainKB 路由决策
- `deuseek/engines/` — Scrapling 封装 (Fetcher/Stealthy/Dynamic/Parser)
- `deuseek/convert/converter.py` — HTML→Markdown 三层降噪
- `deuseek/perf/` — DomainKB / Cache / BrowserPool
- `deuseek/native/` — wechat/bilibili/douyin 原生路径
- `.claude-plugin/skills/deuseek/SKILL.md` — Skill manifest

## 上游归属

本 fork 基于 [Daily-AC/deuseek](https://github.com/Daily-AC/deuseek) (MIT)。上游版权声明保留于 LICENSE。
