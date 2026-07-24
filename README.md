# deuseek

> 全网通搜索 — 一个 CLI + Claude Code Skill, 给中转站 Agent 用户补齐 WebSearch + 多平台读取能力。

> 基于 [Daily-AC/deuseek](https://github.com/Daily-AC/deuseek) (MIT) fork 改造, 精简为**纯免费版本**: 移除付费 booster 与 OpenCLI 类源, 保留全部 Scrapling 隐身抓取能力。

> **Works with**: Claude Code · Antigravity (`agy`) · 任何识别 `.claude-plugin/` manifest 的 Agent CLI。

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)

## 为什么需要 deuseek

Claude Code 的 WebSearch 是**服务端 server tool** (`web_search_20250305`), 真实可用性经过两层 gate:

1. **客户端 gate** — `WebSearchTool.isEnabled()` 看 API provider; 默认 `firstParty` 才注册。
2. **上游 server tool 实现 gate** — 上游 API 服务必须专门实现 `web_search_20250305`。

OpenAI 兼容中转站 (cliproxy / anyrouter 等单纯把 Claude API → OpenAI Chat Completions 转译) **不识 server tool 这套语义**, WebSearch 直接失败。即便真有 WebSearch, 它也搜不到 HN 实时讨论 / Reddit 深度评论 / 微信公众号文章 / B站技术视频 这些纵向源。

deuseek 给所有这些用户补一个**客户端实现的多源 search + fetch CLI** (直连 Algolia / `yt-dlp` / `gh` / B站 API / Sogou / DuckDuckGo), 对外只暴露一个轻量 CLI + 一个 Claude Skill, **3 分钟内**装好就能用。

## 快速开始

```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
deuseek init                  # 写默认 ~/.deuseek/preferences.toml
deuseek search "vibe coding"  # web + hackernews 立即可用 (零配置)
```

要打开需要上游工具的源:

```bash
deuseek setup youtube    # pip install yt-dlp
deuseek setup github     # 提示 brew install gh (macOS) / winget (Windows)
deuseek setup reddit     # uv tool install rdt-cli + rdt login
```

### 在 Claude Code 里用

```
/plugin marketplace add xyva-yuangui/deuseek
/plugin install deuseek
```

然后在对话里直接说: "用 deuseek 搜一下 ..."

## 命令

| 命令 | 干嘛 |
|---|---|
| `deuseek search "<query>"` | 搜索 (SERP: metadata + URL, content ≤500 字) |
| `deuseek search --on hackernews,web "..."` | 指定源 |
| `deuseek search --mode quick "..."` | 只查 web + hackernews |
| `deuseek search --mode deep "..."` | 查所有就绪源 |
| `deuseek search --json "..."` | 显式 JSON 输出 |
| `deuseek search --no-cache "..."` | 跳过缓存, 强制刷新 |
| **`deuseek fetch <url>`** | **URL → 全文 markdown** — Scrapling 三层路由 + DomainKB |
| `deuseek fetch <url> --backend jina` | 强制走 Jina Reader SaaS (零本地依赖) |
| `deuseek fetch <url> --backend stealthy --solve-cloudflare` | 强制隐身 Chrome + 绕 CF |
| `deuseek fetch <url> --backend dynamic` | 强制 Playwright JS 渲染 |
| `deuseek fetch <url> --full` | 转换整页 HTML (默认只取正文) |
| **`deuseek super "<query>"`** | **端到端**: 多源 search → Scrapling 抓取 → (可选) extract, pipeline 流式 (~40% 提速) |
| `deuseek crawl <url>` | 多页 Spider 爬取 (Scrapling async Spider + checkpoint) |
| `deuseek extract <url>` | 自适应结构化提取 (CSS/XPath + 改版自愈 adaptive 重定位) |
| `deuseek domain-kb` | 查看/清空 domain→backend 知识库 (`--clear`) |
| `deuseek init` | 写默认 `~/.deuseek/preferences.toml` |
| `deuseek sources` | 列出所有源 + 心愿单状态 (`--probe` 实测) |
| `deuseek setup <source>` | 引导式配置一个源 |
| `deuseek doctor` | 健康检查 (sources + fetch backends + BrowserPool) |
| `deuseek check-update` | 比对 GitHub Releases |
| `deuseek preferences {show,edit,reset,path}` | 用户偏好 |

### Agent 调用约定 (重要)

作为 Agent 调用 deuseek 时, **永远显式拿 JSON**, 防止 TTY 表格 wrap 让你抠不到字段:

```bash
# 方式 1: 每条命令加 --json
deuseek search --json "..."
deuseek fetch  --json "<url>"

# 方式 2: 一次性 env (整个 Agent harness 生效, 推荐)
export DEUSEEK_FORCE_JSON=1
```

`not isatty()` 会自动切 JSON, 但有些 Agent 终端 (如 Antigravity) 给子进程分配真 PTY 让 isatty()=True, 自动检测失效 —— 显式 `--json` 或 env var 是 always-works 保险。

## 支持的源 (全部免费)

| 源 | tier | 依赖 | 说明 |
|---|---|---|---|
| web | ✅ ready | `ddgs` (pip) | DuckDuckGo 通用网页搜索 |
| hackernews | ✅ ready | 无 | 直连 Algolia HN API, 零配置 |
| youtube | ✅ ready | `yt-dlp` (pip) | `deuseek setup youtube` |
| github | ✅ ready | `gh` CLI + `gh auth login` | `deuseek setup github` |
| rss | ✅ ready | 内置 feedparser | **query 必须是 feed URL** |
| wechat | ✅ ready | 无 | 微信公众号 — Sogou 免费搜索 (可选 Scrapling StealthyFetcher 反检测增强) |
| bilibili | ✅ ready | 无 | B站 — 官方 search API (`api.bilibili.com/x/web-interface/search/all/v2`) |
| reddit | 🟡 one_step | `rdt-cli` + `rdt login` | `deuseek setup reddit` |

> 想要全文? 上游本身返全文的源 (wechat Sogou 卡片) 把完整 payload 保留在 `result.raw` (如 `raw["item_html"]`); 其他源 content 一般 < 500 字。真要全文走 `deuseek fetch <url>`。

## 如何取全文 — `deuseek fetch <url>`

`fetch` 是 search → 全文 pipeline 的官方收敛形态, **host-aware** 自动选 backend:

```bash
# 任意网页 → Fetcher (curl_cffi) 优先, jina fallback, Stealthy+CF 兜底
deuseek fetch https://example.com/article --json

# 微信公众号 → 自动走 OpenCLI 登录态 Chrome (需装 Daily-AC/OpenCLI fork)
deuseek fetch https://mp.weixin.qq.com/s/<token> --json

# B站视频 → 自动走 native 官方 view API
deuseek fetch https://www.bilibili.com/video/BVxxxx --json

# search → fetch pipeline 一气呵成
deuseek search --on wechat "claude 4.7" --json \
  | jq -r '.results[].url' \
  | xargs -I{} deuseek fetch --json {}
```

Backend 矩阵 (`--backend auto` 路由规则):

| URL host | `--backend auto` 走 | 备注 |
|---|---|---|
| `mp.weixin.qq.com` | **native_wechat** (OpenCLI 登录态) | 装 [Daily-AC/OpenCLI fork](https://github.com/Daily-AC/OpenCLI) 拿 `weixin download --stdout`; 直接 fetcher/jina 会被微信"环境异常"验证码拦 |
| `bilibili.com` | **native_bilibili** (官方 view API) | 抽 bvid/avid 调 `api.bilibili.com/x/web-interface/view` |
| `douyin.com` | **native_douyin** (OpenCLI fork) | 需 OpenCLI fork + Chrome 登录态 |
| 其它 host | **fetcher → jina → stealthy** | 三层递进, 越往后越能破反爬 |

显式 `--backend` 覆盖 auto: `fetcher` / `stealthy` / `dynamic` / `jina` / `native`。

## Scrapling 引擎整合

`deuseek fetch` / `super` / `crawl` / `extract` 底层用 [Scrapling](https://github.com/D4Vinci/Scrapling) —— 把 HTTP 抓取 / 浏览器隐身 / 自适应解析 / 多页 Spider 全收敛到一个依赖。

### 三层 fetch 引擎 (FetchRouter)

| 引擎 | 实现 | 典型耗时 | 用途 |
|---|---|---|---|
| **Fetcher** | Scrapling `Fetcher` (curl_cffi HTTP + TLS 指纹 impersonate) | 0.4-3.9s | 默认引擎, 80%+ URL 走这里, 纯 HTTP 无浏览器开销 |
| **jina** | [Jina Reader](https://r.jina.ai/) SaaS (服务端 IP) | 2.2-5.7s | Fetcher 失败/被拦时的 fallback, 服务器 IP 穿透部分反爬 |
| **StealthyFetcher** | Scrapling `StealthyFetcher` (patchright 隐身 Chrome) + `solve_cloudflare` | 7.8s (无 CF) / 37s (解 CF) | 兜底, 唯一能过 Cloudflare Turnstile/Interstitial |
| DynamicFetcher | Scrapling `DynamicFetcher` (Playwright) | 4.9-6.9s | JS 渲染专用, 显式 `--backend dynamic` 才走 |

> 三层递进是有意为之: Fetcher 快但遇 Cloudflare 就废, StealthyFetcher 能破 CF 但 37s 太慢不能当默认。路由器先试快的, 失败才升级。

### DomainKB — domain→backend 记忆

每个 domain 记一个"哪个引擎能 work" + "哪些被 block"的映射, 避免每次 trial-and-error。

- 存储: 平台路径 (macOS `~/Library/Application Support/deuseek/`, Linux XDG `~/.local/share/deuseek/`, Windows `%APPDATA%/deuseek/`)
- **TTL 24h**: entry 过期后强制 re-probe, 防止站点改了反爬配置后知识库陈旧
- `FetchRouter.record_success()` / `record_failure()` 在 fetch 成功/失败时自动写回

```bash
deuseek domain-kb              # 列出所有 domain→backend 映射 (含 expired 状态)
deuseek domain-kb --clear      # 清空知识库
deuseek domain-kb --json       # JSON 输出
```

### BrowserPool — 浏览器实例预热

StealthyFetcher / DynamicFetcher 每次冷启 Chrome 要 2-4s。`BrowserPool` 维护常驻 warm session, 后续 fetch 复用, 冷启从 2.4s 降到 ~1s。空闲 5 分钟自动 `shrink()` 关浏览器 (~200-500MB/实例)。`deuseek doctor` 会 surface warm 状态。

### pipeline 模式 — `deuseek super`

旗舰命令把 search → fetch → extract 串成一条流水线, 用 `asyncio.as_completed` 真流式: 第一个搜索结果一到就立刻开抓, 跟剩余搜索重叠 (~40% 提速)。

```bash
deuseek super "iPhone 16 评测"
deuseek super "Python asyncio" --sources hackernews,web --stream   # 流式 JSON Lines
deuseek super "React 19" --extract-fields '{"title":"h1::text"}'   # 顺带结构化提取
```

### 验证码自动升级

`fetch` 命令对每个 backend 返回内容做关键词启发式 (`环境异常 / 完成验证后即可继续访问 / 请输入验证码 / Cloudflare / Just a moment / Checking your browser` 等)。命中验证码页时:

1. envelope `errors[]` 加 `captcha_suspected: ...`
2. 若 StealthyFetcher 可用且本次没试过, **自动重试** `StealthyEngine.fetch(url, solve_cloudflare=True)`
3. 成功则 `errors[]` 追加 `auto_upgraded: stealthy+solve_cloudflare succeeded`, 失败则 `auto_upgrade_failed`

(graceful degrade —— Agent 自己读 errors 决定信不信; markdown 字段保留。)

## ⚙️ 用户偏好

`~/.deuseek/preferences.toml` 可配置默认源、语言、输出格式、source_trust 覆盖。

```bash
deuseek preferences show     # 查看当前配置
deuseek preferences edit     # 用 $EDITOR 编辑 (Windows fallback notepad)
deuseek preferences reset    # 重置 (备份原文件到 .bak)
deuseek preferences path     # 打印文件位置
```

API Key (本 fork 默认不需要任何 Key): 如有需要可放 `~/.deuseek/secrets.env` (KEY=VALUE, POSIX 下权限宽松会警告)。

## 升级

```bash
deuseek check-update                                            # 比对 GitHub Releases
uv tool install --force git+https://github.com/xyva-yuangui/deuseek.git   # 拉最新
```

> ⚠️  `uv tool upgrade deuseek` **不会**拉新 commit (uv 把 git URL 装的工具锁在 install 时的 commit 上)。`--force` 重装才会去 fetch 最新。

## 🪟 平台支持

| 平台 | 状态 | 说明 |
|---|---|---|
| macOS | ✅ 主要开发平台 | 全部源 + 三 fetch backend 测试过 |
| Linux | 🟡 best-effort | 应能 work；setup 流程对 `apt`/`pacman` 不自动 |
| WSL2 | 🟡 best-effort | 跟 Linux 一样 |
| Windows (原生 PowerShell) | 🟡 实验性 | `secrets_env` 不调 POSIX chmod；preferences edit fallback notepad；setup github 提示 `winget install GitHub.cli`。**遇到问题请提 issue**。 |

跑 `deuseek doctor` 会在顶部打印 platform / Python 版本, 方便提 issue 时附上。

## 安装 (一键脚本, macOS/Linux)

```bash
bash install.sh   # 检查 Python 3.10+ → 复制到 ~/.agents/skills/deuseek/ → venv → 装依赖 → 下 Chromium → doctor
```

## 开发

```bash
git clone https://github.com/xyva-yuangui/deuseek.git
cd deuseek
uv sync            # 或 pip install -e ".[dev]"
python -m pytest tests/ -x -q
```

## 设计要点

- **Adapter 模式**: 每源一个 adapter, 实现 `AdapterBase` ABC (`is_ready` + `search`)
- **异步并发**: `Dispatcher` `asyncio.gather` + 单源错误隔离 (unavailable vs failed)
- **YAML 注册**: `sources.yml` 单一真相源 (tier / adapter / trust / timeout / deps)
- **Router**: query_hints 子串匹配 + default_auto 合并, MAX_SOURCES=5, RSS 需 URL query
- **Scorer**: `0.4*recency_norm + 0.6*source_trust`, 无时间戳默认 0.5
- **缓存**: L1 内存 + L2 文件, URL 规范化 (剥 utm_*/fbclid 等 tracking) 共享条目
- **契约**: pydantic `SearchResult.content` field_validator 全局截 500 字, 全文留 `raw`

## License

MIT — 见 [LICENSE](LICENSE)。基于 [Daily-AC/deuseek](https://github.com/Daily-AC/deuseek) (MIT) fork, 上游版权声明保留。
