# deuseek

> 面向所有 AI 编程 Agent 的通用搜索 + 隐身抓取层。绕过 WebSearch 门控,触达服务端搜索够不着的源,把任意 URL 变成干净的 markdown —— **100% 免费,无需任何 API Key**。

> 抓取层基于 [Scrapling](https://github.com/D4Vinci/Scrapling) by **D4Vinci** —— 在此致谢。🙏

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Sources](https://img.shields.io/badge/sources-8%20free-success.svg)](#-支持的源全部免费)
[![Status](https://img.shields.io/badge/status-1.0.0--alpha-orange.svg)](#)

🌐 [English](../README.md) | [العربية](README.ar.md) | [Español](README.es.md) | [Português (Brasil)](README.pt-BR.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | **简体中文** | [日本語](README.ja.md) | [Русский](README.ru.md) | [한국어](README.ko.md)

---

## 目录
- [✨ 为什么需要 deuseek?](#-为什么需要-deuseek)
- [🤖 兼容你的 Agent CLI](#-兼容你的-agent-cli)
- [🚀 快速开始](#-快速开始)
- [📦 安装](#-安装)
- [📋 命令](#-命令)
- [📚 支持的源(全部免费)](#-支持的源全部免费)
- [🥷 抓取引擎架构](#-抓取引擎架构)
- [🤝 Agent 调用约定](#-agent-调用约定)
- [⚙️ 用户偏好](#️-用户偏好)
- [🪟 平台支持](#-平台支持)
- [🏗️ 架构](#️-架构)
- [🙏 致谢](#-致谢)
- [🤝 贡献](#-贡献)
- [📄 许可证](#-许可证)

---

## ✨ 为什么需要 deuseek?

Anthropic 的 `WebSearch` 是**服务端工具**(`web_search_20250305`),经过两层门控:
1. **客户端门控** —— 仅在 first-party / 特定 provider 配置下才注册。
2. **上游门控** —— 上游 API 必须真正*实现*这个服务端工具。**OpenAI 兼容中转站**(cliproxy、anyrouter、自建网关)只是把 Claude API → OpenAI Chat Completions 转译,**没有实现它**,于是 `WebSearch` 静默失败。即便能用,它也够不着 HN 实时讨论、Reddit 深度评论、微信公众号文章、B站技术视频。

**deuseek 在客户端侧解决这一切** —— 一个 CLI + Skill,直连 Algolia / `yt-dlp` / `gh` / B站 API / Sogou / DuckDuckGo,不管你的 Agent CLI 指向哪个 API provider 都能用。

### 核心优势

| | deuseek | 原生 `WebSearch` | 付费搜索 API |
|---|:---:|:---:|:---:|
| 在 OpenAI 兼容中转/代理站上可用 | ✅ | ❌ | n/a |
| 触达 HN / Reddit / 微信 / B站 / RSS | ✅ | ❌ | 部分 |
| 绕过 Cloudflare / 反爬 | ✅ | ❌ | n/a |
| URL → 全文 markdown | ✅ | 仅 WebFetch | n/a |
| 成本 | **免费** | 已包含 | 💲 付费 |
| 上手时间 | ~3 分钟 | — | — |

- 🚪 **绕过两层 WebSearch 门控** —— 在中转/代理站上 `WebSearch` 因上游未实现服务端工具而静默失败,deuseek 照常工作。
- 🌐 **触达服务端搜索够不着的纵向源** —— HN 实时讨论、Reddit 深度评论、微信公众号文章、B站技术视频、RSS 订阅。
- 🆓 **100% 免费,核心零 API Key** —— DuckDuckGo、Algolia HN、B站 API、Sogou、`yt-dlp`、`gh`、`feedparser`。无信用卡、无配额、无限流烦恼。
- 🥷 **三层隐身抓取 + Cloudflare 绕过** —— `Fetcher`(curl_cffi HTTP)→ Jina SaaS → `StealthyFetcher`(patchright 隐身 Chrome)+ `solve_cloudflare`。唯一能破解 Cloudflare Turnstile/Interstitial 的层。
- 🧠 **DomainKB 按域名记忆** —— 每次抓取不再试错;24h TTL 强制 re-probe,站点改了反爬配置后知识库不会陈旧。
- ⚡ **流水线模式 ~40% 提速** —— `asyncio` 把搜索结果一到位就送进抓取(快源不等慢源)。
- 🛡️ **验证码自动升级** —— 检测验证码页(环境异常 / Cloudflare / Just a moment)并自动用 `stealthy + solve_cloudflare` 重试,把错误暴露给 Agent 自行裁决。
- 🔧 **自适应、可自愈的选择器** —— 页面改版不破坏提取(Scrapling 相似度重定位 + `auto_save`)。
- 🖥️ **跨平台** —— macOS 主力,Linux / WSL2 / Windows 尽力支持。
- 🧩 **一个 CLI + 一个 Skill,天然 Agent 无关** —— ~3 分钟接入任何 Agent CLI;`.claude-plugin/` manifest 让它成为 Claude-Code 兼容 CLI 的原生 Skill,其余则作为普通 JSON CLI。
- 🔍 **透明** —— `cost="free|paid"` 标记、结构化 `errors[]`、原始 `raw` 载荷保留,Agent 需要全文时可自取。

## 🤖 兼容你的 Agent CLI

deuseek 是一个会输出 JSON 的标准 CLI —— **任何能跑 shell 命令的 Agent 都能用**。`.claude-plugin/` manifest 为 Claude-Code 兼容 CLI 提供原生 Skill 集成。

| Agent 工具 | 如何使用 deuseek |
|---|---|
| **Claude Code**(Anthropic) | `/plugin marketplace add xyva-yuangui/deuseek` → `/plugin install deuseek`,然后说*"用 deuseek 搜一下 ..."*,也可直接当 CLI 用。 |
| **Zcode** | 从 shell 调 `deuseek search --json "..."` / `deuseek fetch --json <url>`,或加载为 Skill。 |
| **Codex**(OpenAI Codex CLI) | 把 `deuseek` 作为子进程运行,解析 JSON envelope。 |
| **Reasonix** | 子进程 JSON,或加载为 skill。 |
| **OpenClaw** | 把 `deuseek` 当 shell 命令跑,解析 JSON。 |
| **Hermes** | 子进程 JSON。 |
| **Antigravity**(`agy`) | `agy plugin install`(识别 `.claude-plugin/`)。 |
| 其他任何 Agent | 跑 `deuseek <命令> --json` 当 shell 命令,解析 JSON envelope。 |

> 因为契约就是"一个会打印 JSON 的 CLI",deuseek **天然 Agent 无关** —— 你不必等我们"支持"你的工具。只要你的 Agent 能拉起进程,今天就能用 deuseek。

## 🚀 快速开始

```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
deuseek init                   # 写默认 ~/.deuseek/preferences.toml
deuseek search "vibe coding"   # web + hackernews 零配置即可用
```

解锁需要上游工具的源:

```bash
deuseek setup youtube     # pip install yt-dlp
deuseek setup github      # brew install gh (macOS) / winget (Windows)
deuseek setup reddit      # uv tool install rdt-cli && rdt login
```

## 📦 安装

**方式 A —— uv(推荐):**
```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
```

**方式 B —— pip(可编辑开发安装):**
```bash
git clone https://github.com/xyva-yuangui/deuseek.git
cd deuseek
pip install -e ".[dev]"
```

**方式 C —— 一行脚本(macOS/Linux,自建 venv + 浏览器):**
```bash
bash install.sh
```

**可选抓取引擎**(用于绕过 Cloudflare 与 JS 渲染):
```bash
pip install "deuseek[fetchers]"          # patchright + curl_cffi + msgspec + protego
patchright install chromium               # 隐身 Chrome(绕 Cloudflare)
playwright install chromium               # JS 渲染
```

## 📋 命令

| 命令 | 作用 |
|---|---|
| `deuseek search "<query>"` | 多源搜索(SERP:metadata + URL;content ≤500 字) |
| `deuseek search --on hackernews,web "..."` | 限定源 |
| `deuseek search --mode quick "..."` | 只查 web + hackernews |
| `deuseek search --mode deep "..."` | 所有就绪源 |
| `deuseek search --json "..."` | 显式 JSON 输出 |
| `deuseek search --no-cache "..."` | 跳过缓存,强制刷新 |
| **`deuseek fetch <url>`** | **URL → 全文 markdown**(Scrapling 三层路由 + DomainKB) |
| `deuseek fetch <url> --backend jina` | 强制 Jina Reader SaaS(零本地依赖) |
| `deuseek fetch <url> --backend stealthy --solve-cloudflare` | 强制隐身 Chrome + 绕 CF |
| `deuseek fetch <url> --backend dynamic` | 强制 Playwright JS 渲染 |
| `deuseek fetch <url> --full` | 转换整页(默认只取正文) |
| **`deuseek super "<query>"`** | **端到端**:多源搜索 → 隐身抓取 →(可选)extract,流式流水线(~40% 提速) |
| `deuseek crawl <url>` | 多页 Spider 爬取(Scrapling async Spider + checkpoint) |
| `deuseek extract <url>` | 自适应结构化提取(CSS/XPath + 自愈重定位) |
| `deuseek domain-kb` | 查看/清空 domain→backend 知识库(`--clear`) |
| `deuseek init` | 写默认 `~/.deuseek/preferences.toml` |
| `deuseek sources` | 列出所有源 + 就绪状态(`--probe` 实测) |
| `deuseek setup <source>` | 引导式配置一个源 |
| `deuseek doctor` | 健康检查(sources + fetch backends + BrowserPool) |
| `deuseek check-update` | 比对 GitHub Releases |
| `deuseek preferences {show,edit,reset,path}` | 用户偏好 |

## 📚 支持的源(全部免费)

| 源 | tier | 依赖 | 说明 |
|---|---|---|---|
| web | ✅ ready | `ddgs`(pip) | DuckDuckGo 通用网页搜索 |
| hackernews | ✅ ready | 无 | Algolia HN API,零配置 |
| youtube | ✅ ready | `yt-dlp`(pip) | `deuseek setup youtube` |
| github | ✅ ready | `gh` CLI + `gh auth login` | `deuseek setup github` |
| rss | ✅ ready | 内置 `feedparser` | **query 必须是 feed URL** |
| wechat | ✅ ready | 无 | 微信公众号 —— Sogou 免费搜索(可选 Scrapling 隐身增强) |
| bilibili | ✅ ready | 无 | B站官方 search API |
| reddit | 🟡 one_step | `rdt-cli` + `rdt login` | `deuseek setup reddit` |

> **要全文?** 上游本身返全文的源把原始 payload 保留在 `result.raw`(如 wechat 的 `raw["item_html"]`)。其余源用 `deuseek fetch <url>` 取全文。

## 🥷 抓取引擎架构

`deuseek fetch` / `super` / `crawl` / `extract` 建立在 [Scrapling](https://github.com/D4Vinci/Scrapling) 之上 —— 一个依赖覆盖 HTTP 抓取、隐身浏览器、自适应解析、async Spider。

### 三层路由(FetchRouter)

| 引擎 | 实现 | 典型耗时 | 用途 |
|---|---|---|---|
| **Fetcher** | Scrapling `Fetcher`(curl_cffi HTTP + TLS 指纹) | 0.4–3.9s | 默认,80%+ URL,纯 HTTP 无浏览器 |
| **jina** | [Jina Reader](https://r.jina.ai/) SaaS(服务端 IP) | 2.2–5.7s | Fetcher 被拦时的 fallback |
| **StealthyFetcher** | Scrapling `StealthyFetcher`(patchright 隐身 Chrome)+ `solve_cloudflare` | 7.8s / 37s(解 CF) | 兜底 —— 唯一能破解 Cloudflare Turnstile |
| DynamicFetcher | Scrapling `DynamicFetcher`(Playwright) | 4.9–6.9s | JS 渲染专用,显式 `--backend dynamic` |

> 递进是有意为之:Fetcher 快但遇 Cloudflare 就废;StealthyFetcher 能破 CF 但 37s 太慢不能当默认。路由器先试快的,失败才升级。

### DomainKB —— 按域名记忆

记住每个域名"哪个引擎能用 / 哪些被 block",避免每次试错。
- 存储:平台路径(macOS `~/Library/Application Support/deuseek/`、Linux XDG `~/.local/share/deuseek/`、Windows `%APPDATA%/deuseek/`)
- **24h TTL** —— 过期 entry 强制 re-probe,站点改了反爬配置后自动自愈
- `record_success` / `record_failure` 在每次抓取后自动写回

```bash
deuseek domain-kb              # 列出所有 domain→backend 映射(含 expired 状态)
deuseek domain-kb --clear      # 清空知识库
```

### BrowserPool —— 预热浏览器会话

Stealthy/Dynamic 冷启 Chrome 要 2–4s。`BrowserPool` 维持 warm session 复用,后续抓取降到 ~1s。空闲 5 分钟自动 `shrink()`(释放 ~200–500MB/实例)。`deuseek doctor` 报告 warm 状态。

### 流水线模式 —— `deuseek super`

旗舰命令把 search → fetch → extract 串成真流水线:第一个搜索结果一到就开抓,跟剩余搜索重叠(~40% 提速)。

```bash
deuseek super "iPhone 16 评测"
deuseek super "Python asyncio" --sources hackernews,web --stream   # 流式 JSON Lines
deuseek super "React 19" --extract-fields '{"title":"h1::text"}'   # + 结构化提取
```

### 验证码自动升级

`fetch` 对每个 backend 返回内容做关键词扫描(`环境异常 / 完成验证后即可继续访问 / 请输入验证码 / Cloudflare / Just a moment / Checking your browser`)。命中时:
1. `errors[]` 加一条 `captcha_suspected: ...`
2. 若 StealthyFetcher 可用且本次没试过,**自动重试** `stealthy + solve_cloudflare=True`
3. 成功 → `auto_upgraded: stealthy+solve_cloudflare succeeded`;失败 → `auto_upgrade_failed`

优雅降级 —— Agent 读 `errors` 自行裁决;`markdown` 始终保留。

## 🤝 Agent 调用约定

从 Agent 调 deuseek 时**永远显式拿 JSON**,避免 TTY 表格 wrap 丢字段:

```bash
# 方式 1:每条命令加 --json
deuseek search --json "..."
deuseek fetch  --json "<url>"

# 方式 2:env var(整个 Agent harness 生效,推荐)
export DEUSEEK_FORCE_JSON=1
```

`not isatty()` 会自动切 JSON,但有些 Agent 终端(如 Antigravity)分配真 PTY 使 `isatty()` 为 True,自动检测失效 —— 显式 `--json` 或 env var 是 always-works 保险。

标准搜索 envelope:
```json
{
  "query": "...",
  "ts": "ISO 8601 Z",
  "results": [{"source","title","url","content","ts","score","raw","cost"}],
  "errors":  [{"source","error","category"}]
}
```

## ⚙️ 用户偏好

`~/.deuseek/preferences.toml` 配置默认源、语言、输出格式、`trust` 覆盖。

```bash
deuseek preferences show     # 查看当前配置
deuseek preferences edit     # 用 $EDITOR 编辑(Windows fallback:notepad)
deuseek preferences reset    # 重置(备份到 .bak)
deuseek preferences path     # 打印文件路径
```

API Key(可选 —— 核心不需要任何 Key)放 `~/.deuseek/secrets.env`(`KEY=VALUE`;POSIX 下权限宽松会警告)。

## 🪟 平台支持

| 平台 | 状态 | 说明 |
|---|---|---|
| macOS | ✅ 主力 | 全部源 + 三层 fetch backend 测试过 |
| Linux | 🟡 尽力 | 能 work;setup 流程对 `apt`/`pacman` 不自动 |
| WSL2 | 🟡 尽力 | 跟 Linux 一样 |
| Windows(原生 PowerShell) | 🟡 实验 | `secrets_env` 跳过 POSIX chmod;preferences edit fallback notepad;setup github 提示 `winget install GitHub.cli`。**遇到问题请提 issue。** |

`deuseek doctor` 顶部打印平台 / Python 版本 —— 提 issue 时附上。

## 🏗️ 架构

- **Adapter 模式** —— 每源一个 adapter,实现 `AdapterBase`(`is_ready` + `search`)
- **异步并发** —— `Dispatcher` 用 `asyncio.gather`,单源错误隔离(`unavailable` vs `failed`)
- **YAML 注册** —— `sources.yml` 单一真相源(tier / adapter / trust / timeout / deps)
- **Router** —— 子串 query_hints + `default_in_auto` 合并,`MAX_SOURCES=5`,RSS 需 URL query
- **Scorer** —— `0.4*recency_norm + 0.6*source_trust`(权重和=1.0,有 assert);无时间戳默认 0.5
- **缓存** —— L1 内存 + L2 文件;URL 规范化(剥 `utm_*`/`fbclid`/`gclid`/...)让 tracker 变体共享一条
- **契约** —— pydantic `SearchResult.content` validator 全局截 500 字;全文留 `raw`

关键文件:`deuseek/sources.yml`、`deuseek/adapters/`、`deuseek/cli.py`、`deuseek/commands/fetch.py`、`deuseek/commands/super.py`、`deuseek/dispatcher.py`、`deuseek/fetch_router/router.py`、`deuseek/engines/`、`deuseek/convert/converter.py`、`deuseek/perf/`、`deuseek/native/`、`.claude-plugin/skills/deuseek/SKILL.md`。

## 🙏 致谢

deuseek 站在巨人的肩膀上:

- **[Scrapling](https://github.com/D4Vinci/Scrapling)** by [**D4Vinci**](https://github.com/D4Vinci) —— 隐身抓取 / 自适应解析 / async Spider 框架,支撑 deuseek 整个抓取层(Fetcher / StealthyFetcher / DynamicFetcher / 自适应选择器 / Spider)。三层绕 Cloudflare 设计没有它根本不存在。🙏
- **[Daily-AC/deuseek](https://github.com/Daily-AC/deuseek)**(MIT)—— 本免费 fork 所基于的上游项目。
- 上游工具与库:`yt-dlp`、`gh`、`rdt-cli`、`feedparser`、`httpx`、`pydantic`、`rich`、`click`、[Jina Reader](https://r.jina.ai/)、`curl_cffi`、`patchright`、`Playwright`、`markdownify`、`html2text`、`lxml`。

## 🤝 贡献

欢迎贡献!请:
1. 报源/backend 问题时跑 `deuseek doctor` 并附上输出 —— 90% 的"某源不能用"是缺上游 binary。
2. 新增源或破坏性改动请先开 issue。
3. adapter 需符合 `AdapterBase`(`is_ready` + `search` 返 `SearchResult`)。

issue 模板见 [.github/ISSUE_TEMPLATE/](../.github/ISSUE_TEMPLATE/),含 bug 报告、功能建议、新源请求。

## 📄 许可证

MIT —— 见 [LICENSE](../LICENSE)。基于 [Daily-AC/deuseek](https://github.com/Daily-AC/deuseek)(MIT),上游版权声明保留。
