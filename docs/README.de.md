# deuseek

> Die universelle Such- und Stealth-Fetch-Schicht für jeden KI-Coding-Agent. Umgehe das WebSearch-Gate, erreiche die Quellen, die die serverseitige Suche nicht erreicht, und verwandle jede URL in sauberes Markdown — **100 % kostenlos, keine API-Schlüssel nötig**.

> Fetch-Schicht powered by [Scrapling](https://github.com/D4Vinci/Scrapling) von **D4Vinci** — mit Dank eingesetzt. 🙏

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Sources](https://img.shields.io/badge/sources-8%20free-success.svg)](#-unterstützte-quellen-alle-kostenlos)
[![Status](https://img.shields.io/badge/status-1.0.0--alpha-orange.svg)](#)

🌐 [English](../README.md) | [العربية](README.ar.md) | [Español](README.es.md) | [Português (Brasil)](README.pt-BR.md) | [Français](README.fr.md) | **Deutsch** | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [Русский](README.ru.md) | [한국어](README.ko.md)

---

## Inhaltsverzeichnis
- [✨ Warum deuseek?](#-warum-deuseek)
- [🤖 Funktioniert mit deiner Agent-CLI](#-funktioniert-mit-deiner-agent-cli)
- [🚀 Schnellstart](#-schnellstart)
- [📦 Installation](#-installation)
- [📋 Befehle](#-befehle)
- [📚 Unterstützte Quellen (alle kostenlos)](#-unterstützte-quellen-alle-kostenlos)
- [🥷 Fetch-Engine-Architektur](#-fetch-engine-architektur)
- [🤝 Aufrufkonvention für Agenten](#-aufrufkonvention-für-agenten)
- [⚙️ Einstellungen](#️-einstellungen)
- [🪟 Plattformunterstützung](#-plattformunterstützung)
- [🏗️ Architektur](#️-architektur)
- [🙏 Danksagung](#-danksagung)
- [🤝 Mitwirken](#-mitwirken)
- [📄 Lizenz](#-lizenz)

---

## ✨ Warum deuseek?

Anthropics `WebSearch` ist ein **serverseitiges Tool** (`web_search_20250305`), das hinter zwei Checks liegt:
1. **Client-Gate** — nur für First-Party-/bestimmte Provider-Konfigurationen registriert.
2. **Upstream-Gate** — die Upstream-API muss das Server-Tool *tatsächlich implementieren*. **OpenAI-kompatible Relay-Stationen** (cliproxy, anyrouter, selbstgehostete Gateways), die lediglich Claude API → OpenAI Chat Completions übersetzen, **implementieren es nicht**, sodass `WebSearch` stillschweigend scheitert. Selbst wo es funktioniert, erreicht es keine Echtzeit-Threads auf HN, keine tiefen Reddit-Kommentare, keine WeChat 公众号-Artikel und keine Technik-Videos auf Bilibili.

**deuseek behebt das clientseitig** — ein einzelnes CLI + Skill, das direkt auf Algolia / `yt-dlp` / `gh` / Bilibili-API / Sogou / DuckDuckGo zugreift, unabhängig davon, auf welchen API-Provider deine Agent-CLI zeigt.

### Wesentliche Vorteile

| | deuseek | Natives `WebSearch` | Bezahlte Such-APIs |
|---|:---:|:---:|:---:|
| Funktioniert auf OpenAI-kompatiblen Relay-/Proxy-Stationen | ✅ | ❌ | n/a |
| Erreicht HN / Reddit / WeChat / Bilibili / RSS | ✅ | ❌ | teilweise |
| Umgeht Cloudflare / Anti-Bot | ✅ | ❌ | n/a |
| URL → Markdown-Volltext | ✅ | nur WebFetch | n/a |
| Kosten | **gratis** | inklusive | 💲 kostenpflichtig |
| Einrichtungszeit | ~3 Min. | — | — |

- 🚪 **Umgeht das zweistufige WebSearch-Gate** — läuft auf Relay-/Proxy-Stationen, wo `WebSearch` stillschweigend scheitert, weil der Upstream das Server-Tool nicht implementiert.
- 🌐 **Erreicht vertikale Quellen, die die serverseitige Suche nicht erreicht** — Echtzeit-Diskussionen auf HN, tiefe Kommentar-Threads auf Reddit, WeChat 公众号-Artikel, Technik-Videos auf Bilibili, RSS-Feeds.
- 🆓 **100 % kostenlos, null API-Schlüssel im Kern** — DuckDuckGo, Algolia HN, Bilibili-API, Sogou, `yt-dlp`, `gh`, `feedparser`. Keine Kreditkarte, kein Kontingent, keine Rate-Limit-Ärger.
- 🥷 **Dreistufiges Stealth-Fetch mit Cloudflare-Umgehung** — `Fetcher` (curl_cffi-HTTP) → Jina SaaS → `StealthyFetcher` (patchright-Chrome) + `solve_cloudflare`. Die einzige Stufe, die Cloudflare Turnstile/Interstitial knackt.
- 🧠 **DomainKB merkt sich pro Domain** — kein Try-and-Error bei jedem Fetch; ein 24h-TTL erzwingt einen Re-Probe, sodass die Wissensbasis nie veraltet, wenn eine Site ihre Anti-Bot-Konfiguration ändert.
- ⚡ **Pipeline-Modus ~40 % schneller** — `asyncio` streamt Suchergebnisse direkt in den Fetch (Ergebnisse warten nicht auf die langsamste Quelle).
- 🛡️ **Auto-Eskalation bei Captchas** — erkennt Captcha-Seiten (环境异常 / Cloudflare / Just a moment) und retryt automatisch mit `stealthy + solve_cloudflare`, wobei Fehler offengelegt werden, damit der Agent entscheidet, was vertrauenswürdig ist.
- 🔧 **Adaptive, selbstheilende Selektoren** — Seiten-Redesigns zerstören die Extraktion nicht (Scrapling-Ähnlichkeits-Repositionierung + `auto_save`).
- 🖥️ **Plattformübergreifend** — macOS primär, Linux / WSL2 / Windows best-effort.
- 🧩 **Ein CLI + ein Skill, agentenagnostisch by Design** — lässt sich in ~3 Min. in jede Agent-CLI einbinden; ein `.claude-plugin/`-Manifest macht es zum nativen Skill für Claude-Code-kompatible CLIs, ansonsten ein einfaches JSON-CLI.
- 🔍 **Transparent** — `cost="free|paid"`-Tagging, strukturierte `errors[]`, originale `raw`-Payloads bleiben erhalten, sodass Agenten bei Bedarf den Volltext holen können.

## 🤖 Funktioniert mit deiner Agent-CLI

deuseek ist ein Standard-CLI, das JSON ausgibt — **jeder Agent, der Shell-Befehle ausführen kann, kann es nutzen**. Das `.claude-plugin/`-Manifest ergänzt native Skill-Integration für Claude-Code-kompatible CLIs.

| Agent-Tool | So nutzt du deuseek |
|---|---|
| **Claude Code** (Anthropic) | `/plugin marketplace add xyva-yuangui/deuseek` → `/plugin install deuseek`, dann *"use deuseek to search ..."*. Funktioniert auch als normales CLI. |
| **Zcode** | Rufe `deuseek search --json "..."` / `deuseek fetch --json <url>` aus der Shell auf, oder lade den Skill. |
| **Codex** (OpenAI Codex CLI) | Führe `deuseek` als Subprocess aus und parse das JSON-Envelope. |
| **Reasonix** | JSON per Subprocess, oder als Skill laden. |
| **OpenClaw** | Führe `deuseek` als Shell-Befehl aus und parse JSON. |
| **Hermes** | JSON per Subprocess. |
| **Antigravity** (`agy`) | `agy plugin install` (erkennt `.claude-plugin/`). |
| Jeder andere Agent | Führe `deuseek <Befehl> --json` als Shell-Befehl aus und parse das JSON-Envelope. |

> Da der Vertrag lautet „ein CLI, das JSON ausgibt", ist deuseek **agentenagnostisch** — du musst nie darauf warten, dass wir dein Tool „unterstützen". Wenn dein Agent einen Prozess starten kann, kann er deuseek heute nutzen.

## 🚀 Schnellstart

```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
deuseek init                   # schreibt Standard ~/.deuseek/preferences.toml
deuseek search "vibe coding"   # web + hackernews funktionieren ohne Konfiguration
```

Quellen freischalten, die ein Upstream-Tool benötigen:

```bash
deuseek setup youtube     # pip install yt-dlp
deuseek setup github      # brew install gh (macOS) / winget (Windows)
deuseek setup reddit      # uv tool install rdt-cli && rdt login
```

## 📦 Installation

**Option A — uv (empfohlen):**
```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
```

**Option B — pip (Editable-Dev-Installation):**
```bash
git clone https://github.com/xyva-yuangui/deuseek.git
cd deuseek
pip install -e ".[dev]"
```

**Option C — Ein-Zeilen-Skript (macOS/Linux, richtet venv + Browser ein):**
```bash
bash install.sh
```

**Optionale Fetch-Engines** (für Cloudflare-Umgehung & JS-Rendering):
```bash
pip install "deuseek[fetchers]"          # patchright + curl_cffi + msgspec + protego
patchright install chromium               # Stealth-Chrome (Cloudflare-Umgehung)
playwright install chromium               # JS-Rendering
```

## 📋 Befehle

| Befehl | Was er macht |
|---|---|
| `deuseek search "<query>"` | Multiquellen-Suche (SERP: Metadaten + URL; Inhalt ≤500 Zeichen) |
| `deuseek search --on hackernews,web "..."` | Auf bestimmte Quellen beschränken |
| `deuseek search --mode quick "..."` | Nur web + hackernews |
| `deuseek search --mode deep "..."` | Alle bereiten Quellen |
| `deuseek search --json "..."` | Explizite JSON-Ausgabe |
| `deuseek search --no-cache "..."` | Cache überspringen, Aktualisierung erzwingen |
| **`deuseek fetch <url>`** | **URL → Markdown-Volltext** (Scrapling-Dreistufen-Routing + DomainKB) |
| `deuseek fetch <url> --backend jina` | Jina Reader SaaS erzwingen (keine lokalen Abhängigkeiten) |
| `deuseek fetch <url> --backend stealthy --solve-cloudflare` | Stealth-Chrome + CF-Umgehung erzwingen |
| `deuseek fetch <url> --backend dynamic` | Playwright-JS-Rendering erzwingen |
| `deuseek fetch <url> --full` | Ganze Seite konvertieren (Standard: nur Hauptinhalt) |
| **`deuseek super "<query>"`** | **End-to-End**: Multiquellen-Suche → Stealth-Fetch → (optional) extract, Streaming-Pipeline (~40 % schneller) |
| `deuseek crawl <url>` | Multipage-Spider-Crawl (Scrapling async Spider + Checkpoint) |
| `deuseek extract <url>` | Adaptive strukturierte Extraktion (CSS/XPath + Selbstheilungs-Repositionierung) |
| `deuseek domain-kb` | Domain→Backend-Wissensbasis ansehen/leeren (`--clear`) |
| `deuseek init` | Standard-`~/.deuseek/preferences.toml` schreiben |
| `deuseek sources` | Alle Quellen + Bereitschaft auflisten (`--probe` zum Testen) |
| `deuseek setup <source>` | Geführte Einrichtung einer Quelle |
| `deuseek doctor` | Gesundheits-Check (Quellen + Fetch-Backends + BrowserPool) |
| `deuseek check-update` | Mit GitHub Releases vergleichen |
| `deuseek preferences {show,edit,reset,path}` | Benutzereinstellungen |

## 📚 Unterstützte Quellen (alle kostenlos)

| Quelle | Stufe | Abhängigkeit | Hinweise |
|---|---|---|---|
| web | ✅ ready | `ddgs` (pip) | DuckDuckGo allgemeine Websuche |
| hackernews | ✅ ready | keine | Algolia HN-API, ohne Konfiguration |
| youtube | ✅ ready | `yt-dlp` (pip) | `deuseek setup youtube` |
| github | ✅ ready | `gh` CLI + `gh auth login` | `deuseek setup github` |
| rss | ✅ ready | integriertes `feedparser` | **Query muss eine Feed-URL sein** |
| wechat | ✅ ready | keine | WeChat 公众号 — kostenlose Sogou-Suche (optionaler Scrapling-Stealth-Boost) |
| bilibili | ✅ ready | keine | Offizielle Bilibili-Such-API |
| reddit | 🟡 one_step | `rdt-cli` + `rdt login` | `deuseek setup reddit` |

> **Volltext?** Quellen, deren Upstream den Vollinhalt zurückgibt, behalten das originale Payload in `result.raw` (z. B. wechat's `raw["item_html"]`). Für alles andere führe `deuseek fetch <url>` aus.

## 🥷 Fetch-Engine-Architektur

`deuseek fetch` / `super` / `crawl` / `extract` basieren auf [Scrapling](https://github.com/D4Vinci/Scrapling) — einer Abhängigkeit, die HTTP-Fetch, Stealth-Browser, adaptives Parsen und async-Spider abdeckt.

### Dreistufiges Routing (FetchRouter)

| Engine | Implementierung | Typische Zeit | Verwendung |
|---|---|---|---|
| **Fetcher** | Scrapling `Fetcher` (curl_cffi-HTTP + TLS-Imitation) | 0,4–3,9s | Standard, 80 %+ der URLs, reines HTTP ohne Browser |
| **jina** | [Jina Reader](https://r.jina.ai/) SaaS (serverseitige IP) | 2,2–5,7s | Fallback, wenn Fetcher blockiert ist |
| **StealthyFetcher** | Scrapling `StealthyFetcher` (patchright-Stealth-Chrome) + `solve_cloudflare` | 7,8s / 37s (CF) | Letzter Ausweg — einziger, der Cloudflare Turnstile knacket |
| DynamicFetcher | Scrapling `DynamicFetcher` (Playwright) | 4,9–6,9s | Nur-JS-Render-Seiten, explizit `--backend dynamic` |

> Die Eskalation ist absichtlich: Fetcher ist schnell, stirbt aber an Cloudflare; StealthyFetcher knackt CF, aber 37s sind zu langsam für den Standard. Der Router probiert schnell zuerst und eskaliert nur bei Misserfolg.

### DomainKB — Gedächtnis pro Domain

Merkt, welche Engine funktioniert und welche pro Domain blockiert ist, damit wir nicht bei jedem Fetch try-and-errorn.
- Speicher: Plattform-Pfad (macOS `~/Library/Application Support/deuseek/`, Linux XDG `~/.local/share/deuseek/`, Windows `%APPDATA%/deuseek/`)
- **24h-TTL** — abgelaufene Einträge erzwingen einen Re-Probe, sodass veraltete Einträge sich selbst heilen, wenn eine Site ihre Anti-Bot-Konfiguration ändert
- `record_success` / `record_failure` schreiben bei jedem Fetch automatisch zurück

```bash
deuseek domain-kb              # alle Domain→Backend-Mappings auflisten (mit Ablaufstatus)
deuseek domain-kb --clear      # Wissensbasis leeren
```

### BrowserPool — warme Browser-Sessions

Stealthy/Dynamic kalt-starten einen Chrome in 2–4s. `BrowserPool` hält eine warme Session und verwendet sie wieder, was spätere Fetches auf ~1s senkt. 5 Min. inaktiv → auto `shrink()` (~200–500MB/Instanz freigegeben). `deuseek doctor` meldet den Warm-Status.

### Pipeline-Modus — `deuseek super`

Der Vorzeigebefehl verkettet Suche → Fetch → Extract in eine echte Pipeline: sobald das erste Suchergebnis ankommt, beginnt der Fetch und überlappt mit den verbleibenden Suchen (~40 % schneller als seriell).

```bash
deuseek super "iPhone 16 review"
deuseek super "Python asyncio" --sources hackernews,web --stream   # Streaming-JSON-Lines
deuseek super "React 19" --extract-fields '{"title":"h1::text"}'   # + strukturierte Extraktion
```

### Auto-Eskalation bei Captchas

`fetch` durchsucht die Ausgabe jedes Backends nach Captcha-Schlüsselwörtern (`环境异常 / 完成验证后即可继续访问 / 请输入验证码 / Cloudflare / Just a moment / Checking your browser`). Bei Treffer:
1. `errors[]` erhält einen Eintrag `captcha_suspected: ...`
2. Wenn StealthyFetcher verfügbar ist und nicht probiert wurde, **retry automatisch** mit `stealthy + solve_cloudflare=True`
3. Erfolg → `auto_upgraded: stealthy+solve_cloudflare succeeded`; Misserfolg → `auto_upgrade_failed`

Graceful Degrade — der Agent liest `errors` und entscheidet, was vertrauenswürdig ist; `markdown` bleibt immer erhalten.

## 🤝 Aufrufkonvention für Agenten

**JSON immer explizit holen**, wenn deuseek aus einem Agenten aufgerufen wird, damit das TTY-Tabellen-Umbrechen keine Felder verliert:

```bash
# Option 1: --json pro Befehl
deuseek search --json "..."
deuseek fetch  --json "<url>"

# Option 2: Env-Variable (gilt für den gesamten Agent-Harness — empfohlen)
export DEUSEEK_FORCE_JSON=1
```

`not isatty()` schaltet automatisch auf JSON um, aber manche Agent-Terminals (z. B. Antigravity) weisen ein echtes PTY zu, sodass `isatty()` True ist und die Auto-Erkennung scheitert — explizites `--json` oder die Env-Variable ist die immer-funktionierende Garantie.

Standard-Such-Envelope:
```json
{
  "query": "...",
  "ts": "ISO 8601 Z",
  "results": [{"source","title","url","content","ts","score","raw","cost"}],
  "errors":  [{"source","error","category"}]
}
```

## ⚙️ Einstellungen

`~/.deuseek/preferences.toml` konfiguriert Standard-Quellen, Sprache, Ausgabeformat und `trust`-Überschreibungen.

```bash
deuseek preferences show     # aktuelle Konfiguration ansehen
deuseek preferences edit     # mit $EDITOR bearbeiten (Windows: notepad)
deuseek preferences reset    # zurücksetzen (Backup in .bak)
deuseek preferences path     # Dateipfad ausgeben
```

API-Schlüssel (optional — der Kern braucht keinen) gehören nach `~/.deuseek/secrets.env` (`KEY=VALUE`; POSIX warnt bei laxen Berechtigungen).

## 🪟 Plattformunterstützung

| Plattform | Status | Hinweise |
|---|---|---|
| macOS | ✅ Primär | Alle Quellen + alle drei Fetch-Backends getestet |
| Linux | 🟡 Best-effort | Funktioniert; Setup-Flow behandelt `apt`/`pacman` nicht automatisch |
| WSL2 | 🟡 Best-effort | Wie Linux |
| Windows (natives PowerShell) | 🟡 Experimentell | `secrets_env` überspringt POSIX-chmod; preferences edit nutzt notepad; setup github schlägt `winget install GitHub.cli` vor. **Bitte ein Issue öffnen bei Problemen.** |

`deuseek doctor` gibt Plattform / Python-Version oben aus — beim Issue-Erststellen anhängen.

## 🏗️ Architektur

- **Adapter-Pattern** — ein Adapter pro Quelle, der `AdapterBase` implementiert (`is_ready` + `search`)
- **Async Fan-out** — `Dispatcher` nutzt `asyncio.gather` mit Fehlerisolierung pro Quelle (`unavailable` vs `failed`)
- **YAML-Registry** — `sources.yml` ist die einzige Quelle der Wahrheit (tier / adapter / trust / timeout / deps)
- **Router** — Teilstring-query_hints + `default_in_auto`-Merge, `MAX_SOURCES=5`, RSS auf URL-Queries beschränkt
- **Scorer** — `0.4*recency_norm + 0.6*source_trust` (Gewichte summieren auf 1.0, mit assert); fehlende Timestamps default auf 0.5
- **Cache** — L1 Speicher + L2 Datei; URL-Kanonisierung (entfernt `utm_*`/`fbclid`/`gclid`/...), sodass Tracker-Varianten einen Eintrag teilen
- **Vertrag** — pydantics `SearchResult.content`-Validator kürzt global auf 500 Zeichen; Volltext bleibt in `raw`

Schlüsseldateien: `deuseek/sources.yml`, `deuseek/adapters/`, `deuseek/cli.py`, `deuseek/commands/fetch.py`, `deuseek/commands/super.py`, `deuseek/dispatcher.py`, `deuseek/fetch_router/router.py`, `deuseek/engines/`, `deuseek/convert/converter.py`, `deuseek/perf/`, `deuseek/native/`, `.claude-plugin/skills/deuseek/SKILL.md`.

## 🙏 Danksagung

deuseek steht auf den Schultern von Giganten:

- **[Scrapling](https://github.com/D4Vinci/Scrapling)** von [**D4Vinci**](https://github.com/D4Vinci) — das Stealth-Fetch-/adaptives-Parsing-/async-Spider-Framework, das die gesamte Fetch-Schicht von deuseek antreibt (Fetcher / StealthyFetcher / DynamicFetcher / adaptive Selektoren / Spider). Das dreistufige Cloudflare-Umgehungs-Design gäbe es ohne es schlicht nicht. 🙏
- **[Daily-AC/deuseek](https://github.com/Daily-AC/deuseek)** (MIT) — das Upstream-Projekt, auf dem dieser kostenlose Fork aufbaut.
- Upstream-Tools & -Bibliotheken: `yt-dlp`, `gh`, `rdt-cli`, `feedparser`, `httpx`, `pydantic`, `rich`, `click`, [Jina Reader](https://r.jina.ai/), `curl_cffi`, `patchright`, `Playwright`, `markdownify`, `html2text`, `lxml`.

## 🤝 Mitwirken

Beiträge sind willkommen! Bitte:
1. Führe `deuseek doctor` aus und schließe die Ausgabe bei Quellen-/Backend-Problemen ein — 90 % von „eine Quelle funktioniert nicht" ist eine fehlende Upstream-Binärdatei.
2. Öffne erst ein Issue für neue Quellen oder Breaking Changes.
3. Adapter müssen `AdapterBase` entsprechen (`is_ready` + `search` gibt `SearchResult` zurück).

Siehe [Issue-Vorlagen](../.github/ISSUE_TEMPLATE/) für Bug-Berichte, Feature-Wünsche und Anfragen für neue Quellen.

## 📄 Lizenz

MIT — siehe [LICENSE](../LICENSE). Basierend auf [Daily-AC/deuseek](https://github.com/Daily-AC/deuseek) (MIT); der Upstream-Copyright-Hinweis bleibt erhalten.
