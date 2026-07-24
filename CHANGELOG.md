# Changelog

## v1.0.0-alpha (2026-07-24)

First public release of the free fork of [Daily-AC/deuseek](https://github.com/Daily-AC/deuseek) (MIT).

### Added

- **8 free search sources**: web (DuckDuckGo), HackerNews, YouTube, GitHub, RSS, WeChat, Bilibili, Reddit — zero API keys required.
- **Scrapling three-tier stealth fetch**: `Fetcher` (curl_cffi HTTP) → Jina SaaS → `StealthyFetcher` (patchright Chrome) + `solve_cloudflare` for Cloudflare bypass.
- **Pipeline mode** (`deuseek super`): streaming search → fetch → extract pipeline, ~40% faster than serial.
- **DomainKB**: per-domain backend memory with 24h TTL, self-healing.
- **BrowserPool**: warm browser sessions, drops cold-start from 2.4s to ~1s.
- **Captcha auto-upgrade**: detects captcha pages and auto-retries with stealthy + CF.
- **Adaptive self-healing selectors**: page redesigns don't break extraction.
- **Agent-agnostic JSON CLI**: works with Claude Code, Zcode, Codex, Reasonix, OpenClaw, Hermes, Antigravity, and any agent that can shell out.
- **`.claude-plugin/` Skill**: native integration for Claude-Code-compatible CLIs.
- **9-language README**: English (canonical) + العربية / Español / Português (Brasil) / Français / Deutsch / 简体中文 / 日本語 / Русский / 한국어.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`.
- Issue templates (bug, feature, source request).
- GitHub Discussions, 13 topics, bilingual repo description.
- CI pipeline (GitHub Actions: pytest + ruff on Python 3.10/3.11/3.12).

### Changed

- Stripped paid boosters and OpenCLI sources from upstream.
- Rewrote README as English canonical with Features, Demo, comparison table (4 columns), and grouped advantages.
- Aligned Claude Code SKILL.md with plugin.json description.
- Fixed stale `ddgs extract` claim in SKILL.md (actual is Scrapling three-tier).

### Removed

- Paid booster adapters (Tavily, Brave, Perplexity, Exa).
- OpenCLI-based adapters (Twitter, Xiaohongshu, TikTok).
- `~/.omnireach/` references (migrated to `~/.deuseek/`).