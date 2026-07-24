# Contributing to deuseek

Thanks for considering contributing! 🎉

## Quick ways to help

| What | How |
|---|---|
| 🐛 **Report a bug** | [Open a bug report](https://github.com/xyva-yuangui/deuseek/issues/new?template=bug_report.yml) with `deuseek doctor` output attached. |
| 💡 **Suggest a feature** | [Open a feature request](https://github.com/xyva-yuangui/deuseek/issues/new?template=feature_request.yml). |
| 🔌 **Request a new source** | [Open a source request](https://github.com/xyva-yuangui/deuseek/issues/new?template=source_request.yml). |
| 🌐 **Improve translations** | The 9-language README set lives in `docs/README.<lang>.md`. PRs for existing translations and new languages are welcome. |
| 🐛 **Fix a bug** | Pick an issue, fork, open a PR. |

## Development setup

```bash
git clone https://github.com/xyva-yuangui/deuseek.git
cd deuseek
pip install -e ".[dev]"
```

## Pull request guidelines

- **Keep adapters conforming to `AdapterBase`** — every adapter must implement `is_ready()` and `search()` returning `list[SearchResult]`.
- **New sources** go in `deuseek/adapters/` and must be registered in `deuseek/sources.yml` (tier, adapter class, query_hints, trust, timeout).
- **Run `deuseek doctor`** and include its output if your change touches sources or fetch backends.
- **Fetch backends** live in `deuseek/engines/` (wrapping Scrapling) and `deuseek/native/` (platform-specific paths like WeChat/Bilibili). All engines must expose a static `fetch()` method returning `FetchResult`.
- **Tests** are appreciated but not required for alpha. A manual smoke test (`deuseek search "test" && deuseek fetch <url>`) is enough for now.

## Project structure

```
deuseek/
├── adapters/          # one adapter per source (web, hackernews, youtube, ...)
├── commands/          # click subcommands (fetch, super, crawl, extract, ...)
├── convert/           # HTML → Markdown converter
├── engines/           # Scrapling wrappers (Fetcher, Stealthy, Dynamic, Parser)
├── fetch_router/      # FetchRouter: host + DomainKB routing decisions
├── native/            # platform-specific fetch (wechat, bilibili, douyin)
├── perf/              # DomainKB, Cache (L1+L2), BrowserPool
├── cli.py             # main CLI entry point
├── contract.py        # pydantic models (SearchResult, FetchResult, ...)
├── dispatcher.py      # async fan-out across adapters
├── router.py          # source selection (hints + defaults + mode)
├── scorer.py          # result ranking (recency + trust)
├── sources.yml        # single source of truth for all registered sources
└── ...
```

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).