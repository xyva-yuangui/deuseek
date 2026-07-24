# deuseek

> 모든 AI 코딩 에이전트를 위한 범용 검색 및 스텔스 패치 레이어. WebSearch 게이트를 우회하고, 서버 측 검색이 닿지 못하는 소스에 도달하며, 어떤 URL이든 깔끔한 마크다운으로 변환합니다 — **100% 무료, API 키 불필요**.

> 패치 레이어는 **D4Vinci**의 [Scrapling](https://github.com/D4Vinci/Scrapling)으로 구동됩니다 — 감사히 사용합니다. 🙏

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Sources](https://img.shields.io/badge/sources-8%20free-success.svg)](#-지원-소스-전체-무료)
[![Status](https://img.shields.io/badge/status-1.0.0--alpha-orange.svg)](#)

🌐 [English](../README.md) | [العربية](README.ar.md) | [Español](README.es.md) | [Português (Brasil)](README.pt-BR.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [Русский](README.ru.md) | **한국어**

---

## 목차
- [✨ 왜 deuseek인가?](#-왜-deuseek인가)
- [🤖 여러분의 에이전트 CLI에서 작동](#-여러분의-에이전트-cli에서-작동)
- [🚀 빠른 시작](#-빠른-시작)
- [📦 설치](#-설치)
- [📋 명령어](#-명령어)
- [📚 지원 소스(전체 무료)](#-지원-소스전체-무료)
- [🥷 패치 엔진 아키텍처](#-패치-엔진-아키텍처)
- [🤝 에이전트 호출 규칙](#-에이전트-호출-규칙)
- [⚙️ 환경설정](#️-환경설정)
- [🪟 플랫폼 지원](#-플랫폼-지원)
- [🏗️ 아키텍처](#️-아키텍처)
- [🙏 감사의 말](#-감사의-말)
- [🤝 기여](#-기여)
- [📄 라이선스](#-라이선스)

---

## ✨ 왜 deuseek인가?

Anthropic의 `WebSearch`는 두 가지 검사로 제어되는 **서버 측 도구**(`web_search_20250305`)입니다:
1. **클라이언트 게이트** — 퍼스트파티/특정 프로바이더 구성에서만 등록됩니다.
2. **업스트림 게이트** — 업스트림 API가 서버 도구를 *실제로 구현*해야 합니다. Claude API → OpenAI Chat Completions로 단순 변역하는 **OpenAI 호환 릴레이 스테이션**(cliproxy, anyrouter, 자체 호스팅 게이트웨이)은 **이를 구현하지 않아** `WebSearch`가 조용히 실패합니다. 작동하더라도 HN 실시간 스레드, Reddit 깊은 댓글, WeChat 公众号 글, Bilibili 기술 영상에 닿지 못합니다.

**deuseek은 이를 클라이언트 측에서 해결합니다** — Algolia / `yt-dlp` / `gh` / Bilibili API / Sogou / DuckDuckGo에 직접 연결하는 단일 CLI + Skill로, 여러분의 에이전트 CLI가 어떤 API 프로바이더를 가리키든 관계없이 작동합니다.

### 핵심 장점

| | deuseek | 네이티브 `WebSearch` | 유료 검색 API |
|---|:---:|:---:|:---:|
| OpenAI 호환 릴레이/프록시 스테이션에서 작동 | ✅ | ❌ | 해당 없음 |
| HN / Reddit / WeChat / Bilibili / RSS 도달 | ✅ | ❌ | 부분적 |
| Cloudflare / 안티봇 우회 | ✅ | ❌ | 해당 없음 |
| URL → 풀텍스트 마크다운 | ✅ | WebFetch만 | 해당 없음 |
| 비용 | **무료** | 포함 | 💲 유료 |
| 설치 시간 | ~3분 | — | — |

- 🚪 **2단계 WebSearch 게이트 우회** — 업스트림이 서버 도구를 구현하지 않아 `WebSearch`가 조용히 실패하는 릴레이/프록시 스테이션에서 작동합니다.
- 🌐 **서버 측 검색이 닿지 못하는 수직 소스 도달** — HN 실시간 토론, Reddit 깊은 댓글 스레드, WeChat 公众号 글, Bilibili 기술 영상, RSS 피드.
- 🆓 **100% 무료, 핵심에 API 키 불필요** — DuckDuckGo, Algolia HN, Bilibili API, Sogou, `yt-dlp`, `gh`, `feedparser`. 신용카드 없음, 할당량 없음, 레이트리밋 골칫거리 없음.
- 🥷 **Cloudflare 우회가 포함된 3단계 스텔스 패치** — `Fetcher`(curl_cffi HTTP) → Jina SaaS → `StealthyFetcher`(patchright Chrome) + `solve_cloudflare`. Cloudflare Turnstile/Interstitial을 깨는 유일한 단계.
- 🧠 **DomainKB가 도메인별로 기억** — 매 패치마다 시행착오하지 않음; 24h TTL이 재프로브를 강제해 사이트가 안티봇 설정을 바꿔도 지식 베이스가 낡아지지 않습니다.
- ⚡ **파이프라인 모드 ~40% 더 빠름** — `asyncio`가 검색 결과를 도착 즉시 패치로 스트리밍(결과가 가장 느린 소스를 기다리지 않음).
- 🛡️ **캡차 자동 업그레이드** — 캡차 페이지(环境异常 / Cloudflare / Just a moment)를 감지하고 `stealthy + solve_cloudflare`로 자동 재시도하며, 에러를 노출해 에이전트가 신뢰 여부를 결정하게 합니다.
- 🔧 **적응형, 자가 치유 셀렉터** — 페이지 리디자인이 추출을 망가뜨리지 않음(Scrapling 유사도 기반 재배치 + `auto_save`).
- 🖥️ **크로스 플랫폼** — macOS 주력, Linux / WSL2 / Windows 최선의 노력.
- 🧩 **하나의 CLI + 하나의 Skill, 설계상 에이전트 무관** — ~3분 만에 어떤 에이전트 CLI에든 투입; `.claude-plugin/` manifest가 Claude-Code 호환 CLI에는 네이티브 Skill로, 나머지에는 평범한 JSON CLI로 만듭니다.
- 🔍 **투명** — `cost="free|paid"` 태깅, 구조화된 `errors[]`, 원본 `raw` 페이로드 보존으로 에이전트가 필요시 풀텍스트를 가져갈 수 있습니다.

## 🤖 여러분의 에이전트 CLI에서 작동

deuseek은 JSON을 출력하는 표준 CLI입니다 — **셸 명령을 실행할 수 있는 에이전트라면 무엇이든 사용 가능**합니다. `.claude-plugin/` manifest는 Claude-Code 호환 CLI에 네이티브 Skill 통합을 추가합니다.

| 에이전트 도구 | deuseek 사용법 |
|---|---|
| **Claude Code**(Anthropic) | `/plugin marketplace add xyva-yuangui/deuseek` → `/plugin install deuseek`, 그리고 *"use deuseek to search ..."*. 일반 CLI로도 작동. |
| **Zcode** | 셸에서 `deuseek search --json "..."` / `deuseek fetch --json <url>` 호출, 또는 Skill 로드. |
| **Codex**(OpenAI Codex CLI) | `deuseek`를 서브프로세스로 실행하고 JSON envelope 파싱. |
| **Reasonix** | 서브프로세스 JSON, 또는 skill으로 로드. |
| **OpenClaw** | `deuseek`를 셸 명령으로 실행하고 JSON 파싱. |
| **Hermes** | 서브프로세스 JSON. |
| **Antigravity**(`agy`) | `agy plugin install`(`.claude-plugin/` 인식). |
| 그 외 모든 에이전트 | `deuseek <명령> --json`을 셸 명령으로 실행하고 JSON envelope 파싱. |

> 계약이 "JSON을 출력하는 CLI"이므로 deuseek은 **에이전트 무관**합니다 — 우리가 여러분의 도구를 "지원"하기를 기다릴 필요가 없습니다. 에이전트가 프로세스를 띄울 수 있다면 오늘 바로 deuseek을 쓸 수 있습니다.

## 🚀 빠른 시작

```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
deuseek init                   # 기본 ~/.deuseek/preferences.toml 작성
deuseek search "vibe coding"   # web + hackernews가 설정 없이 작동
```

업스트림 도구가 필요한 소스 해금:

```bash
deuseek setup youtube     # pip install yt-dlp
deuseek setup github      # brew install gh (macOS) / winget (Windows)
deuseek setup reddit      # uv tool install rdt-cli && rdt login
```

## 📦 설치

**옵션 A — uv(권장):**
```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
```

**옵션 B — pip(개발용 편집 설치):**
```bash
git clone https://github.com/xyva-yuangui/deuseek.git
cd deuseek
pip install -e ".[dev]"
```

**옵션 C — 한 줄 스크립트(macOS/Linux, venv + 브라우저 준비):**
```bash
bash install.sh
```

**선택적 패치 엔진**(Cloudflare 우회 및 JS 렌더링용):
```bash
pip install "deuseek[fetchers]"          # patchright + curl_cffi + msgspec + protego
patchright install chromium               # 스텔스 Chrome(Cloudflare 우회)
playwright install chromium               # JS 렌더링
```

## 📋 명령어

| 명령 | 하는 일 |
|---|---|
| `deuseek search "<query>"` | 다중 소스 검색(SERP: 메타데이터 + URL; 콘텐츠 ≤500자) |
| `deuseek search --on hackernews,web "..."` | 특정 소스로 제한 |
| `deuseek search --mode quick "..."` | web + hackernews만 |
| `deuseek search --mode deep "..."` | 모든 준비된 소스 |
| `deuseek search --json "..."` | 명시적 JSON 출력 |
| `deuseek search --no-cache "..."` | 캐시 건너뛰기, 강제 새로고침 |
| **`deuseek fetch <url>`** | **URL → 풀텍스트 마크다운**(Scrapling 3단계 라우팅 + DomainKB) |
| `deuseek fetch <url> --backend jina` | Jina Reader SaaS 강제(로컬 의존성 없음) |
| `deuseek fetch <url> --backend stealthy --solve-cloudflare` | 스텔스 Chrome + CF 우회 강제 |
| `deuseek fetch <url> --backend dynamic` | Playwright JS 렌더링 강제 |
| `deuseek fetch <url> --full` | 전체 페이지 변환(기본: 본문만) |
| **`deuseek super "<query>"`** | **엔드투엔드**: 다중 소스 검색 → 스텔스 패치 → (선택) extract, 스트리밍 파이프라인(~40% 더 빠름) |
| `deuseek crawl <url>` | 다중 페이지 Spider 크롤(Scrapling async Spider + 체크포인트) |
| `deuseek extract <url>` | 적응형 구조화 추출(CSS/XPath + 자가 치유 재배치) |
| `deuseek domain-kb` | 도메인→백엔드 지식 베이스 보기/비우기(`--clear`) |
| `deuseek init` | 기본 `~/.deuseek/preferences.toml` 작성 |
| `deuseek sources` | 모든 소스 + 준비 상태 나열(`--probe`로 테스트) |
| `deuseek setup <source>` | 소스 1개 안내 설정 |
| `deuseek doctor` | 헬스 체크(소스 + 패치 백엔드 + BrowserPool) |
| `deuseek check-update` | GitHub Releases와 비교 |
| `deuseek preferences {show,edit,reset,path}` | 사용자 환경설정 |

## 📚 지원 소스(전체 무료)

| 소스 | 단계 | 의존성 | 비고 |
|---|---|---|---|
| web | ✅ ready | `ddgs`(pip) | DuckDuckGo 일반 웹 검색 |
| hackernews | ✅ ready | 없음 | Algolia HN API, 설정 불필요 |
| youtube | ✅ ready | `yt-dlp`(pip) | `deuseek setup youtube` |
| github | ✅ ready | `gh` CLI + `gh auth login` | `deuseek setup github` |
| rss | ✅ ready | 내장 `feedparser` | **쿼리는 피드 URL이어야 함** |
| wechat | ✅ ready | 없음 | WeChat 公众号 — 무료 Sogou 검색(선택적 Scrapling 스텔스 부스트) |
| bilibili | ✅ ready | 없음 | Bilibili 공식 검색 API |
| reddit | 🟡 one_step | `rdt-cli` + `rdt login` | `deuseek setup reddit` |

> **풀텍스트?** 업스트림이 풀 콘텐츠를 반환하는 소스는 원본 페이로드를 `result.raw`에 보존합니다(예: wechat의 `raw["item_html"]`). 나머지는 `deuseek fetch <url>`을 실행하세요.

## 🥷 패치 엔진 아키텍처

`deuseek fetch` / `super` / `crawl` / `extract`는 [Scrapling](https://github.com/D4Vinci/Scrapling) 위에 구축됩니다 — HTTP 패치, 스텔스 브라우저, 적응형 파싱, async Spider를 하나의 의존성으로 아우릅니다.

### 3단계 라우팅(FetchRouter)

| 엔진 | 구현 | 전형적 소요 | 용도 |
|---|---|---|---|
| **Fetcher** | Scrapling `Fetcher`(curl_cffi HTTP + TLS 모방) | 0.4–3.9초 | 기본, URL의 80% 이상, 순 HTTP로 브라우저 없음 |
| **jina** | [Jina Reader](https://r.jina.ai/) SaaS(서버 측 IP) | 2.2–5.7초 | Fetcher가 차단될 때 폴백 |
| **StealthyFetcher** | Scrapling `StealthyFetcher`(patchright 스텔스 Chrome) + `solve_cloudflare` | 7.8초 / 37초(CF) | 최후의 수단 — Cloudflare Turnstile을 깨는 유일한 것 |
| DynamicFetcher | Scrapling `DynamicFetcher`(Playwright) | 4.9–6.9초 | JS 렌더 전용 사이트, 명시적 `--backend dynamic` |

> 단계적 에스컬레이션은 의도적입니다: Fetcher는 빠르지만 Cloudflare에서 죽고, StealthyFetcher는 CF를 깨지만 37초라 기본값으로 쓰긴 너무 느립니다. 라우터는 빠른 것을 먼저 시도하고 실패 시에만 에스컬레이션합니다.

### DomainKB — 도메인별 기억

도메인별로 어느 엔진이 작동하고 어느 것이 차단됐는지 기억해 매 패치마다 시행착오하지 않습니다.
- 저장: 플랫폼 경로(macOS `~/Library/Application Support/deuseek/`, Linux XDG `~/.local/share/deuseek/`, Windows `%APPDATA%/deuseek/`)
- **24h TTL** — 만료된 항목은 재프로브를 강제해, 사이트가 안티봇 설정을 바꿔도 오래된 기록이 스스로 치유됩니다
- `record_success` / `record_failure`이 매 패치 후 자동으로 기록합니다

```bash
deuseek domain-kb              # 모든 도메인→백엔드 매핑 나열(만료 상태 포함)
deuseek domain-kb --clear      # 지식 베이스 비우기
```

### BrowserPool — 따뜻한 브라우저 세션

Stealthy/Dynamic은 Chrome을 콜드스타트하는 데 2–4초가 걸립니다. `BrowserPool`은 따뜻한 세션을 유지·재사용해 이후 패치를 ~1초로 줄입니다. 5분 유휴 → 자동 `shrink()`(인스턴스당 ~200–500MB 해제). `deuseek doctor`가 warm 상태를 보고합니다.

### 파이프라인 모드 — `deuseek super`

선두 명령이 검색 → 패치 → extract를 진짜 파이프라인으로 연결합니다: 첫 검색 결과가 도착하자마자 패치가 시작되어 남은 검색과 겹칩니다(직렬 대비 ~40% 빠름).

```bash
deuseek super "iPhone 16 review"
deuseek super "Python asyncio" --sources hackernews,web --stream   # 스트리밍 JSON Lines
deuseek super "React 19" --extract-fields '{"title":"h1::text"}'   # + 구조화 추출
```

### 캡차 자동 업그레이드

`fetch`는 모든 백엔드의 출력에서 캡차 키워드(`环境异常 / 完成验证后即可继续访问 / 请输入验证码 / Cloudflare / Just a moment / Checking your browser`)를 스캔합니다. 적중 시:
1. `errors[]`에 `captcha_suspected: ...` 항목 추가
2. StealthyFetcher가 사용 가능하고 이번에 시도 안 했으면, `stealthy + solve_cloudflare=True`로 **자동 재시도**
3. 성공 → `auto_upgraded: stealthy+solve_cloudflare succeeded`; 실패 → `auto_upgrade_failed`

우아한 성능 저하 — 에이전트는 `errors`를 읽고 무엇을 신뢰할지 결정; `markdown`은 항상 보존됩니다.

## 🤝 에이전트 호출 규칙

에이전트에서 deuseek을 호출할 때 **항상 JSON을 명시적으로 가져오세요**, TTY 표 랩핑이 필드를 잃지 않게:

```bash
# 옵션 1: 명령마다 --json
deuseek search --json "..."
deuseek fetch  --json "<url>"

# 옵션 2: 환경변수(전체 에이전트 하네스에 적용 — 권장)
export DEUSEEK_FORCE_JSON=1
```

`not isatty()`가 자동으로 JSON으로 전환하지만, 어떤 에이전트 터미널(예: Antigravity)은 실제 PTY를 할당해 `isatty()`가 True가 되어 자동 감지가 실패합니다 — 명시적 `--json` 또는 환경변수가 항상 작동하는 보장입니다.

표준 검색 envelope:
```json
{
  "query": "...",
  "ts": "ISO 8601 Z",
  "results": [{"source","title","url","content","ts","score","raw","cost"}],
  "errors":  [{"source","error","category"}]
}
```

## ⚙️ 환경설정

`~/.deuseek/preferences.toml`이 기본 소스, 언어, 출력 형식, `trust` 재정의를 구성합니다.

```bash
deuseek preferences show     # 현재 설정 보기
deuseek preferences edit     # $EDITOR로 편집(Windows: notepad)
deuseek preferences reset    # 재설정(.bak에 백업)
deuseek preferences path     # 파일 경로 출력
```

API 키(선택 — 핵심은 불필요)는 `~/.deuseek/secrets.env`에 둡니다(`KEY=VALUE`; POSIX은 느슨한 권한에 경고).

## 🪟 플랫폼 지원

| 플랫폼 | 상태 | 비고 |
|---|---|---|
| macOS | ✅ 주력 | 모든 소스 + 세 패치 백엔드 테스트 완료 |
| Linux | 🟡 최선의 노력 | 작동; setup 흐름이 `apt`/`pacman`을 자동 처리하지 않음 |
| WSL2 | 🟡 최선의 노력 | Linux와 동일 |
| Windows(네이티브 PowerShell) | 🟡 실험적 | `secrets_env`는 POSIX chmod 건너뜀; preferences edit는 notepad; setup github은 `winget install GitHub.cli` 제안. **문제 발생 시 이슈를 열어주세요.** |

`deuseek doctor`가 상단에 플랫폼 / Python 버전을 출력합니다 — 이슈 제출 시 첨부하세요.

## 🏗️ 아키텍처

- **어댑터 패턴** — 소스마다 하나의 어댑터, `AdapterBase` 구현(`is_ready` + `search`)
- **비동기 팬아웃** — `Dispatcher`가 `asyncio.gather` 사용, 소스별 에러 격리(`unavailable` vs `failed`)
- **YAML 레지스트리** — `sources.yml`이 유일한 진실의 원천(tier / adapter / trust / timeout / deps)
- **라우터** — 부분문자열 query_hints + `default_in_auto` 병합, `MAX_SOURCES=5`, RSS는 URL 쿼리에만 제한
- **스코어러** — `0.4*recency_norm + 0.6*source_trust`(가중치 합=1.0, assert); 타임스탬프 없으면 기본 0.5
- **캐시** — L1 메모리 + L2 파일; URL 정규화(`utm_*`/`fbclid`/`gclid`/... 제거)로 트래커 변형이 한 항목 공유
- **계약** — pydantic의 `SearchResult.content` 검증자가 전역 500자로 자름; 풀텍스트는 `raw`에 보존

주요 파일: `deuseek/sources.yml`, `deuseek/adapters/`, `deuseek/cli.py`, `deuseek/commands/fetch.py`, `deuseek/commands/super.py`, `deuseek/dispatcher.py`, `deuseek/fetch_router/router.py`, `deuseek/engines/`, `deuseek/convert/converter.py`, `deuseek/perf/`, `deuseek/native/`, `.claude-plugin/skills/deuseek/SKILL.md`.

## 🙏 감사의 말

deuseek은 거인의 어깨 위에 서 있습니다:

- **[Scrapling](https://github.com/D4Vinci/Scrapling)**, [**D4Vinci**](https://github.com/D4Vinci) 작성 — deuseek의 패치 레이어 전체(Fetcher / StealthyFetcher / DynamicFetcher / 적응형 셀렉터 / Spider)를 구동하는 스텔스 패치 / 적응형 파싱 / async Spider 프레임워크. 3단계 Cloudflare 우회 설계는 이것 없이는 존재할 수 없었습니다. 🙏
- **[Daily-AC/deuseek](https://github.com/Daily-AC/deuseek)**(MIT) — 이 무료 fork가 구축되는 업스트림 프로젝트.
- 업스트림 도구 및 라이브러리: `yt-dlp`, `gh`, `rdt-cli`, `feedparser`, `httpx`, `pydantic`, `rich`, `click`, [Jina Reader](https://r.jina.ai/), `curl_cffi`, `patchright`, `Playwright`, `markdownify`, `html2text`, `lxml`.

## 🤝 기여

기여를 환영합니다! 부탁드립니다:
1. 소스/백엔드 문제 보고 시 `deuseek doctor`를 실행하고 출력을 포함하세요 — "소스가 작동하지 않는다"의 90%는 업스트림 바이너리 누락입니다.
2. 새 소스나 파괴적 변경은 먼저 이슈를 여세요.
3. 어댑터는 `AdapterBase`를 준수해야 합니다(`is_ready` + `search`가 `SearchResult` 반환).

버그 리포트, 기능 요청, 신규 소스 요청은 [이슈 템플릿](../.github/ISSUE_TEMPLATE/)을 참고하세요.

## 📄 라이선스

MIT — [LICENSE](../LICENSE) 참조. [Daily-AC/deuseek](https://github.com/Daily-AC/deuseek)(MIT) 기반; 업스트림 저작권 고지는 보존됩니다.
