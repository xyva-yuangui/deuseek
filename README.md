# deuseek

> **One CLI. All sources. Zero API keys.**
> Give your AI agent real-time web search, stealth content fetching, and Cloudflare bypass — in 3 minutes.
> Works with Claude Code, Zcode, Codex, Reasonix, OpenClaw, Hermes, Antigravity, and any agent that can shell out.

> Powered by [Scrapling](https://github.com/D4Vinci/Scrapling) by **D4Vinci**. 🙏

[![GitHub stars](https://img.shields.io/github/stars/xyva-yuangui/deuseek?style=flat)](https://github.com/xyva-yuangui/deuseek/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Sources](https://img.shields.io/badge/sources-8%20free-success.svg)](#-supported-sources-all-free)
[![Status](https://img.shields.io/badge/status-1.0.0--alpha-orange.svg)](#)

🌐 **English** | [العربية](docs/README.ar.md) | [Español](docs/README.es.md) | [Português (Brasil)](docs/README.pt-BR.md) | [Français](docs/README.fr.md) | [Deutsch](docs/README.de.md) | [简体中文](docs/README.zh-CN.md) | [日本語](docs/README.ja.md) | [Русский](docs/README.ru.md) | [한국어](docs/README.ko.md)

---

## ✨ Features

- 🌐 **8 free sources, zero API keys** — web (DuckDuckGo), HackerNews, YouTube, GitHub, Reddit, WeChat 公众号, Bilibili, RSS. No credit card, no quota.
- 🥷 **Stealth fetch with Cloudflare bypass** — three-tier Scrapling engine: `Fetcher` (curl_cffi) → Jina SaaS → `StealthyFetcher` (patchright Chrome) + `solve_cloudflare`. The only tier that cracks Cloudflare Turnstile.
- ⚡ **Pipeline mode ~40% faster** — `deuseek super` chains search → fetch → extract in a streaming pipeline; results don't wait for the slowest source.
- 🧩 **Agent-agnostic, one JSON CLI** — works with Claude Code, Zcode, Codex, Reasonix, OpenClaw, Hermes, Antigravity (`agy`), and any agent that can run a shell command.
- 🛡️ **Captcha auto-upgrade** — detects captcha pages and auto-retries with stealth Chrome, surfacing errors so the agent decides what to trust.
- 🧠 **DomainKB** — remembers which engine works per domain (24h TTL, self-healing), so no trial-and-error on every fetch.
- 🔧 **Adaptive, self-healing selectors** — page redesigns don't break extraction (Scrapling similarity relocation + `auto_save`).
- 📚 **9 languages** — English (canonical) + العربية / Español / Português (Brasil) / Français / Deutsch / 简体中文 / 日本語 / Русский / 한국어.

## 🎬 See it in action

### Search — multi-source SERP
```bash
$ deuseek search "vibe coding" --json --limit 1
```
```json
{
  "query": "vibe coding",
  "ts": "2026-07-24T12:00:00Z",
  "results": [
    {"source":"web","title":"What Is Vibe Coding? A Beginner's Guide","url":"https://...","content":"Vibe coding is...","score":0.72}
  ],
  "errors": []
}
```

### Fetch — URL to full-text markdown (Cloudflare bypass)
```bash
$ deuseek fetch "https://nopecha.com/demo/cloudflare" --backend stealthy --solve-cloudflare --json
```
```
backend: stealthy  |  status: 200  |  content: 12,345 chars
```

### Pipeline — search → fetch, streamed
```bash
$ deuseek super "Python asyncio" --sources hackernews,web --stream
```
```
{"type":"search_hit","source":"hackernews","title":"Understanding Python asyncio...","url":"https://..."}
{"type":"fetch_result","url":"https://...","backend":"fetcher","success":true,"content_len":8765}
{"type":"done","total_urls":5,"ok":5,"elapsed_s":6.2}
```

## 📦 Install

```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
deuseek init
deuseek search "vibe coding"   # web + hackernews work zero-config
```

Unlock sources that need an upstream tool:

```bash
deuseek setup youtube     # pip install yt-dlp
deuseek setup github      # brew install gh (macOS) / winget (Windows)
deuseek setup reddit      # uv tool install rdt-cli && rdt login
```

Optional fetch engines (Cloudflare bypass & JS rendering):

```bash
pip install "deuseek[fetchers]"          # patchright + curl_cffi + msgspec + protego
patchright install chromium               # stealth Chrome
playwright install chromium               # JS rendering
```

---

## Table of contents
- [🤖 Works with your agent CLI](#-works-with-your-agent-cli)
- [✨ Why deuseek?](#-why-deuseek)
- [📋 Commands](#-commands)
- [📚 Supported sources (all free)](#-supported-sources-all-free)
- [🥷 Fetch engine architecture](#-fetch-engine-architecture)
- [🤝 Agent calling convention](#-agent-calling-convention)
- [⚙️ Preferences](#️-preferences)
- [🪟 Platform support](#-platform-support)
- [🏗️ Architecture](#️-architecture)
- [🙏 Acknowledgments](#-acknowledgments)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🤖 Works with your agent CLI

**Who is this for?** You're using an AI coding agent (Claude Code, Zcode, Codex, etc.) through a relay station, proxy, or self-hosted gateway, and `WebSearch` doesn't work — or you want to search platforms the built-in search can't reach (HN, Reddit, WeChat, Bilibili, RSS). deuseek fixes both.

deuseek is a standard CLI that emits JSON — **any agent that can run shell commands can use it**. The `.claude-plugin/` manifest adds native Skill integration for Claude-Code-compatible CLIs.

| Agent tool | How to use deuseek |
|---|---|
| **Claude Code** (Anthropic) | `/plugin marketplace add xyva-yuangui/deuseek` → `/plugin install deuseek`, then *"use deuseek to search ..."*. Also works as a plain CLI. |
| **Zcode** | Call `deuseek search --json "..."` / `deuseek fetch --json <url>` from the shell, or load the Skill. |
| **Codex** (OpenAI Codex CLI) | Run `deuseek` as a subprocess and parse the JSON envelope. |
| **Reasonix** | Subprocess JSON, or load as a skill. |
| **OpenClaw** | Run `deuseek` as a shell command and parse JSON. |
| **Hermes** | Subprocess JSON. |
| **Antigravity** (`agy`) | `agy plugin install` (recognizes `.claude-plugin/`). |
| Any other agent | Run `deuseek <command> --json` as a shell command, parse the JSON envelope. |

> Because the contract is "a CLI that prints JSON", deuseek is **agent-agnostic** — you never have to wait for us to "support" your tool. If your agent can spawn a process, it can use deuseek today.

## ✨ Why deuseek?

Anthropic's `WebSearch` is a **server-side tool** (`web_search_20250305`) gated behind two checks:
1. **Client gate** — only registered for first-party / specific provider configs.
2. **Upstream gate** — the upstream API must actually *implement* the server tool. **OpenAI-compatible relay stations** (cliproxy, anyrouter, self-hosted gateways) that merely translate Claude API → OpenAI Chat Completions **don't implement it**, so `WebSearch` silently fails. Even where it works, it can't reach HN real-time threads, Reddit deep comments, WeChat 公众号 articles, or Bilibili tech videos.

**deuseek fixes this client-side** — a single CLI + Skill that goes straight to Algolia / `yt-dlp` / `gh` / Bilibili API / Sogou / DuckDuckGo, so it works regardless of which API provider your agent CLI points at.

### How deuseek compares

| | deuseek | Native `WebSearch` | Paid search APIs | DIY (roll your own) |
|---|:---:|:---:|:---:|:---:|
| Works on relay / proxy stations | ✅ | ❌ | n/a | ✅ |
| Reaches HN / Reddit / WeChat / Bilibili / RSS | ✅ | ❌ | partial | ✅ |
| Cloudflare / anti-bot bypass | ✅ | ❌ | n/a | ❌ (hard) |
| URL → full-text markdown | ✅ | WebFetch only | n/a | ✅ |
| Cost | **free** | included | 💲 paid | free (your time) |
| Setup time | ~3 min | — | — | hours → days |

### Search

- 🌐 **8 free sources, zero API keys** — DuckDuckGo, Algolia HN, Bilibili API, Sogou, `yt-dlp`, `gh`, `feedparser`. No credit card, no quota, no rate-limit headaches.
- 🚪 **Works on relay/proxy stations** — where `WebSearch` fails because the upstream doesn't implement the server tool.
- 🔍 **Transparent** — `cost="free|paid"` tagging, structured `errors[]`, and original `raw` payloads preserved so agents can grab full text when needed.

### Fetch

- 🥷 **Three-tier stealth with Cloudflare bypass** — `Fetcher` (curl_cffi HTTP) → Jina SaaS → `StealthyFetcher` (patchright Chrome) + `solve_cloudflare`. The only tier that cracks Cloudflare Turnstile/Interstitial.
- 🧠 **DomainKB remembers per-domain** — no trial-and-error on every fetch; 24h TTL forces re-probe so the knowledge base self-heals when a site changes its anti-bot config.
- ⚡ **Pipeline mode ~40% faster** — `asyncio` streams search results straight into fetch (results don't wait for the slowest source).
- 🛡️ **Captcha auto-upgrade** — detects captcha pages and auto-retries with `stealthy + solve_cloudflare`, surfacing errors so the agent decides.

### Integration

- 🧩 **One CLI, agent-agnostic** — drops into any agent CLI in ~3 minutes; `.claude-plugin/` manifest for native Skill in Claude-Code-compatible CLIs, plain JSON CLI for everything else.
- 🔧 **Adaptive, self-healing selectors** — page redesigns don't break extraction (Scrapling similarity-based relocation + `auto_save`).
- 🖥️ **Cross-platform** — macOS primary, Linux / WSL2 / Windows best-effort.
- 📚 **9 languages** — English (canonical) + العربية / Español / Português (Brasil) / Français / Deutsch / 简体中文 / 日本語 / Русский / 한국어.

## 📋 Commands

| Command | What it does |
|---|---|
| `deuseek search "<query>"` | Multi-source search (SERP: metadata + URL; content ≤500 chars) |
| `deuseek search --on hackernews,web "..."` | Restrict to specific sources |
| `deuseek search --mode quick "..."` | Only web + hackernews |
| `deuseek search --mode deep "..."` | All ready sources |
| `deuseek search --json "..."` | Explicit JSON output |
| `deuseek search --no-cache "..."` | Skip cache, force refresh |
| **`deuseek fetch <url>`** | **URL → full-text markdown** (Scrapling three-tier routing + DomainKB) |
| `deuseek fetch <url> --backend jina` | Force Jina Reader SaaS (zero local deps) |
| `deuseek fetch <url> --backend stealthy --solve-cloudflare` | Force stealth Chrome + CF bypass |
| `deuseek fetch <url> --backend dynamic` | Force Playwright JS rendering |
| `deuseek fetch <url> --full` | Convert whole page (default: main content only) |
| **`deuseek super "<query>"`** | **End-to-end**: multi-source search → stealth fetch → (optional) extract, streaming pipeline (~40% faster) |
| `deuseek crawl <url>` | Multi-page Spider crawl (Scrapling async Spider + checkpoint) |
| `deuseek extract <url>` | Adaptive structured extraction (CSS/XPath + self-healing relocation) |
| `deuseek domain-kb` | View/clear the domain→backend knowledge base (`--clear`) |
| `deuseek init` | Write default `~/.deuseek/preferences.toml` |
| `deuseek sources` | List all sources + readiness (`--probe` to test) |
| `deuseek setup <source>` | Guided setup for a source |
| `deuseek doctor` | Health check (sources + fetch backends + BrowserPool) |
| `deuseek check-update` | Compare against GitHub Releases |
| `deuseek preferences {show,edit,reset,path}` | User preferences |

## 📚 Supported sources (all free)

| Source | Tier | Dependency | Notes |
|---|---|---|---|
| web | ✅ ready | `ddgs` (pip) | DuckDuckGo general web search |
| hackernews | ✅ ready | none | Algolia HN API, zero-config |
| youtube | ✅ ready | `yt-dlp` (pip) | `deuseek setup youtube` |
| github | ✅ ready | `gh` CLI + `gh auth login` | `deuseek setup github` |
| rss | ✅ ready | built-in `feedparser` | **query must be a feed URL** |
| wechat | ✅ ready | none | WeChat 公众号 — free Sogou search (optional Scrapling stealth boost) |
| bilibili | ✅ ready | none | Bilibili official search API |
| reddit | 🟡 one_step | `rdt-cli` + `rdt login` | `deuseek setup reddit` |

> **Full text?** Sources whose upstream returns full content keep the original payload in `result.raw` (e.g. wechat's `raw["item_html"]`). For everything else, run `deuseek fetch <url>`.

## 🥷 Fetch engine architecture

`deuseek fetch` / `super` / `crawl` / `extract` are built on [Scrapling](https://github.com/D4Vinci/Scrapling) — one dependency covering HTTP fetch, stealth browser, adaptive parsing, and async Spider.

### Three-tier routing (FetchRouter)

| Engine | Implementation | Typical time | Use |
|---|---|---|---|
| **Fetcher** | Scrapling `Fetcher` (curl_cffi HTTP + TLS impersonation) | 0.4–3.9s | Default, 80%+ of URLs, pure HTTP no browser |
| **jina** | [Jina Reader](https://r.jina.ai/) SaaS (server-side IP) | 2.2–5.7s | Fallback when Fetcher is blocked |
| **StealthyFetcher** | Scrapling `StealthyFetcher` (patchright stealth Chrome) + `solve_cloudflare` | 7.8s / 37s (CF) | Last resort — only one that cracks Cloudflare Turnstile |
| DynamicFetcher | Scrapling `DynamicFetcher` (Playwright) | 4.9–6.9s | JS-render-only sites, explicit `--backend dynamic` |

> The escalation is intentional: Fetcher is fast but dies on Cloudflare; StealthyFetcher cracks CF but 37s is too slow to be default. The router tries fast first and escalates only on failure.

### DomainKB — per-domain memory

Remembers which engine works and which is blocked per domain, so we don't trial-and-error every fetch.
- Storage: platform path (macOS `~/Library/Application Support/deuseek/`, Linux XDG `~/.local/share/deuseek/`, Windows `%APPDATA%/deuseek/`)
- **24h TTL** — expired entries force a re-probe, so stale records self-heal when a site changes its anti-bot config
- `record_success` / `record_failure` write back automatically on every fetch

```bash
deuseek domain-kb              # list all domain→backend mappings (with expired status)
deuseek domain-kb --clear      # wipe the knowledge base
```

### BrowserPool — warm browser sessions

Stealthy/Dynamic cold-start a Chrome in 2–4s. `BrowserPool` keeps a warm session and reuses it, dropping subsequent fetches to ~1s. Idle 5 min → auto `shrink()` (~200–500MB/instance freed). `deuseek doctor` reports the warm state.

### Pipeline mode — `deuseek super`

The flagship command chains search → fetch → extract into a real pipeline: as soon as the first search result arrives, fetching starts and overlaps the remaining searches (~40% faster than serial).

```bash
deuseek super "iPhone 16 review"
deuseek super "Python asyncio" --sources hackernews,web --stream   # streaming JSON Lines
deuseek super "React 19" --extract-fields '{"title":"h1::text"}'   # + structured extraction
```

### Captcha auto-upgrade

`fetch` scans every backend's output for captcha keywords (`环境异常 / 完成验证后即可继续访问 / 请输入验证码 / Cloudflare / Just a moment / Checking your browser`). On a hit:
1. `errors[]` gets a `captcha_suspected: ...` entry
2. If StealthyFetcher is available and wasn't tried, it **auto-retries** `stealthy + solve_cloudflare=True`
3. Success → `auto_upgraded: stealthy+solve_cloudflare succeeded`; failure → `auto_upgrade_failed`

Graceful degrade — the agent reads `errors` and decides what to trust; `markdown` is always preserved.

## 🤝 Agent calling convention

**Always take JSON explicitly** when calling deuseek from an agent, so TTY table wrapping doesn't lose fields:

```bash
# Option 1: --json per command
deuseek search --json "..."
deuseek fetch  --json "<url>"

# Option 2: env var (applies to the whole agent harness — recommended)
export DEUSEEK_FORCE_JSON=1
```

`not isatty()` auto-switches to JSON, but some agent terminals (e.g. Antigravity) allocate a real PTY so `isatty()` is True and auto-detection fails — explicit `--json` or the env var is the always-works guarantee.

Standard search envelope:
```json
{
  "query": "...",
  "ts": "ISO 8601 Z",
  "results": [{"source","title","url","content","ts","score","raw","cost"}],
  "errors":  [{"source","error","category"}]
}
```

## ⚙️ Preferences

`~/.deuseek/preferences.toml` configures default sources, language, output format, and `trust` overrides.

```bash
deuseek preferences show     # view current config
deuseek preferences edit     # edit with $EDITOR (Windows fallback: notepad)
deuseek preferences reset    # reset (backs up to .bak)
deuseek preferences path     # print the file path
```

API keys (optional — the core needs none) go in `~/.deuseek/secrets.env` (`KEY=VALUE`; POSIX warns on loose permissions).

## 🪟 Platform support

| Platform | Status | Notes |
|---|---|---|
| macOS | ✅ Primary | All sources + all three fetch backends tested |
| Linux | 🟡 Best-effort | Works; setup flow doesn't auto-handle `apt`/`pacman` |
| WSL2 | 🟡 Best-effort | Same as Linux |
| Windows (native PowerShell) | 🟡 Experimental | `secrets_env` skips POSIX chmod; preferences edit falls back to notepad; setup github suggests `winget install GitHub.cli`. **Please open an issue if you hit problems.** |

`deuseek doctor` prints platform / Python version at the top — attach it when filing issues.

## 🏗️ Architecture

- **Adapter pattern** — one adapter per source, implementing `AdapterBase` (`is_ready` + `search`)
- **Async fan-out** — `Dispatcher` uses `asyncio.gather` with per-source error isolation (`unavailable` vs `failed`)
- **YAML registry** — `sources.yml` is the single source of truth (tier / adapter / trust / timeout / deps)
- **Router** — substring query_hints + `default_in_auto` merge, `MAX_SOURCES=5`, RSS gated on URL queries
- **Scorer** — `0.4*recency_norm + 0.6*source_trust` (weights sum to 1.0, asserted); missing timestamps default to 0.5
- **Cache** — L1 memory + L2 file; URL canonicalization (strips `utm_*`/`fbclid`/`gclid`/...) so tracker variants share one entry
- **Contract** — pydantic `SearchResult.content` validator truncates to 500 chars globally; full text stays in `raw`

Key files: `deuseek/sources.yml`, `deuseek/adapters/`, `deuseek/cli.py`, `deuseek/commands/fetch.py`, `deuseek/commands/super.py`, `deuseek/dispatcher.py`, `deuseek/fetch_router/router.py`, `deuseek/engines/`, `deuseek/convert/converter.py`, `deuseek/perf/`, `deuseek/native/`, `.claude-plugin/skills/deuseek/SKILL.md`.

## 🙏 Acknowledgments

deuseek stands on the shoulders of giants:

- **[Scrapling](https://github.com/D4Vinci/Scrapling)** by [**D4Vinci**](https://github.com/D4Vinci) — the stealth-fetch / adaptive-parsing / async-Spider framework that powers deuseek's entire fetch layer (Fetcher / StealthyFetcher / DynamicFetcher / adaptive selectors / Spider). The three-tier Cloudflare-bypass design simply wouldn't exist without it. 🙏
- **[Daily-AC/deuseek](https://github.com/Daily-AC/deuseek)** (MIT) — the upstream project this free fork builds on.
- Upstream tools & libraries: `yt-dlp`, `gh`, `rdt-cli`, `feedparser`, `httpx`, `pydantic`, `rich`, `click`, [Jina Reader](https://r.jina.ai/), `curl_cffi`, `patchright`, `Playwright`, `markdownify`, `html2text`, `lxml`.

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and [issue templates](.github/ISSUE_TEMPLATE/) for bug reports, feature requests, and new-source requests.

Please run `deuseek doctor` and include its output when reporting source/backend issues — 90% of "a source doesn't work" is a missing upstream binary.

## 📄 License

MIT — see [LICENSE](LICENSE). Based on [Daily-AC/deuseek](https://github.com/Daily-AC/deuseek) (MIT); upstream copyright notice preserved.