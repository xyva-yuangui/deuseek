# deuseek

> あらゆる AI コーディングエージェントのための汎用検索 & ステルスフェッチレイヤー。WebSearch のゲートをバイパスし、サーバーサイド検索が届かないソースに到達し、任意の URL をクリーンな markdown に変換 —— **100% 無料、API キー不要**。

> フェッチレイヤーは [Scrapling](https://github.com/D4Vinci/Scrapling) by **D4Vinci** によって実現 —— 感謝とともに使用しています。🙏

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Sources](https://img.shields.io/badge/sources-8%20free-success.svg)](#-対応ソースすべて無料)
[![Status](https://img.shields.io/badge/status-1.0.0--alpha-orange.svg)](#)

🌐 [English](../README.md) | [العربية](README.ar.md) | [Español](README.es.md) | [Português (Brasil)](README.pt-BR.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [简体中文](README.zh-CN.md) | **日本語** | [Русский](README.ru.md) | [한국어](README.ko.md)

---

## 目次
- [✨ なぜ deuseek なのか?](#-なぜ-deuseek-なのか)
- [🤖 あなたのエージェント CLI で動作](#-あなたのエージェント-cli-で動作)
- [🚀 クイックスタート](#-クイックスタート)
- [📦 インストール](#-インストール)
- [📋 コマンド](#-コマンド)
- [📚 対応ソース(すべて無料)](#-対応ソースすべて無料)
- [🥷 フェッチエンジンアーキテクチャ](#-フェッチエンジンアーキテクチャ)
- [🤝 エージェント呼び出し規約](#-エージェント呼び出し規約)
- [⚙️ プリファレンス](#️-プリファレンス)
- [🪟 プラットフォームサポート](#-プラットフォームサポート)
- [🏗️ アーキテクチャ](#️-アーキテクチャ)
- [🙏 謝辞](#-謝辞)
- [🤝 貢献](#-貢献)
- [📄 ライセンス](#-ライセンス)

---

## ✨ なぜ deuseek なのか?

Anthropic の `WebSearch` は **サーバーサイドツール** (`web_search_20250305`) であり、2 つのチェックでゲートされています:
1. **クライアントゲート** — ファーストパーティ / 特定のプロバイダー設定でのみ登録されます。
2. **アップストリームゲート** — 上流 API が実際にサーバーツールを*実装*していなければなりません。Claude API → OpenAI Chat Completions に変換するだけの **OpenAI 互換中継ステーション** (cliproxy、anyrouter、セルフホストゲートウェイ) は**それを実装していない**ため、`WebSearch` は暗黙に失敗します。機能する環境であっても、HN のリアルタイムスレッド、Reddit の深いコメント、WeChat 公式アカウントの記事、Bilibili の技術動画には届きません。

**deuseek はこれをクライアントサイドで解決します** — Algolia / `yt-dlp` / `gh` / Bilibili API / Sogou / DuckDuckGo に直接アクセスする単一の CLI + Skill で、あなたのエージェント CLI がどの API プロバイダーを向いていても機能します。

### 主な利点

| | deuseek | ネイティブ `WebSearch` | 有料検索 API |
|---|:---:|:---:|:---:|
| OpenAI 互換中継/プロキシステーションで動作 | ✅ | ❌ | n/a |
| HN / Reddit / WeChat / Bilibili / RSS に到達 | ✅ | ❌ | 部分 |
| Cloudflare / アンチボットをバイパス | ✅ | ❌ | n/a |
| URL → 全文 markdown | ✅ | WebFetch のみ | n/a |
| コスト | **無料** | 含まれる | 💲 有料 |
| セットアップ時間 | ~3 分 | — | — |

- 🚪 **2 層の WebSearch ゲートをバイパス** — 中継/プロキシステーション上で、上流がサーバーツールを実装していないため `WebSearch` が暗黙に失敗する環境でも動作します。
- 🌐 **サーバーサイド検索が届かない縦のソースに到達** — HN リアルタイムの議論、Reddit の深いコメントスレッド、WeChat 公式アカウントの記事、Bilibili の技術動画、RSS フィード。
- 🆓 **100% 無料、コアに API キー不要** — DuckDuckGo、Algolia HN、Bilibili API、Sogou、`yt-dlp`、`gh`、`feedparser`。クレジットカード不要、クォータ不要、レート制限の悩みなし。
- 🥷 **3 層のステルスフェッチ + Cloudflare バイパス** — `Fetcher` (curl_cffi HTTP) → Jina SaaS → `StealthyFetcher` (patchright ステルス Chrome) + `solve_cloudflare`。Cloudflare Turnstile/Interstitial を突破できる唯一の層。
- 🧠 **DomainKB がドメインごとに記憶** — 毎回のフェッチで試行錯誤不要。24h TTL が再プローブを強制し、サイトがアンチボット設定を変更しても知識ベースが古くなりません。
- ⚡ **パイプラインモードで ~40% 高速化** — `asyncio` が検索結果を到着次第フェッチに直接流し込みます (遅いソースを待ちません)。
- 🛡️ **CAPTCHA 自動昇格** — CAPTCHA ページ (環境異常 / Cloudflare / Just a moment など) を検出し、`stealthy + solve_cloudflare` で自動リトライ。エラーを表面化させ、エージェントが何を信じるか判断します。
- 🔧 **適応的かつ自己修復するセレクタ** — ページの redesign でも抽出が壊れません (Scrapling の類似度ベース再配置 + `auto_save`)。
- 🖥️ **クロスプラットフォーム** — macOS が主力、Linux / WSL2 / Windows はベストエフォート。
- 🧩 **1 つの CLI + 1 つの Skill、設計上エージェント非依存** — ~3 分で任意のエージェント CLI に導入。`.claude-plugin/` マニフェストにより Claude-Code 互換 CLI 向けにはネイティブ Skill、それ以外にはプレーンな JSON CLI として動作。
- 🔍 **透明** — `cost="free|paid"` タグ付け、構造化 `errors[]`、オリジナルの `raw` ペイロード保持で、エージェントは必要時に全文を取得できます。

## 🤖 あなたのエージェント CLI で動作

deuseek は JSON を出力する標準的な CLI です —— **シェルコマンドを実行できるエージェントなら何でも使えます**。`.claude-plugin/` マニフェストが Claude-Code 互換 CLI 向けにネイティブ Skill 統合を追加します。

| エージェントツール | deuseek の使い方 |
|---|---|
| **Claude Code** (Anthropic) | `/plugin marketplace add xyva-yuangui/deuseek` → `/plugin install deuseek`、その後 *「deuseek を使って検索してください ...」*。プレーンな CLI としても動作します。 |
| **Zcode** | シェルから `deuseek search --json "..."` / `deuseek fetch --json <url>` を呼ぶか、Skill を読み込みます。 |
| **Codex** (OpenAI Codex CLI) | `deuseek` をサブプロセスとして実行し、JSON envelope をパースします。 |
| **Reasonix** | サブプロセス JSON、または skill として読み込み。 |
| **OpenClaw** | `deuseek` をシェルコマンドとして実行し、JSON をパースします。 |
| **Hermes** | サブプロセス JSON。 |
| **Antigravity** (`agy`) | `agy plugin install` (`.claude-plugin/` を認識)。 |
| その他のエージェント | `deuseek <command> --json` をシェルコマンドとして実行し、JSON envelope をパースします。 |

> 契約は「JSON を出力する CLI」なので、deuseek は **エージェント非依存** です —— 私たちがあなたのツールを「サポート」するのを待つ必要はありません。あなたのエージェントがプロセスを起動できるなら、今日から deuseek を使えます。

## 🚀 クイックスタート

```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
deuseek init                   # writes default ~/.deuseek/preferences.toml
deuseek search "vibe coding"   # web + hackernews work zero-config
```

アップストリームツールが必要なソースをアンロック:

```bash
deuseek setup youtube     # pip install yt-dlp
deuseek setup github      # brew install gh (macOS) / winget (Windows)
deuseek setup reddit      # uv tool install rdt-cli && rdt login
```

## 📦 インストール

**方式 A — uv (推奨):**
```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
```

**方式 B — pip (編集可能な開発インストール):**
```bash
git clone https://github.com/xyva-yuangui/deuseek.git
cd deuseek
pip install -e ".[dev]"
```

**方式 C — 1 行スクリプト (macOS/Linux、venv + ブラウザをセットアップ):**
```bash
bash install.sh
```

**オプションのフェッチエンジン** (Cloudflare バイパス & JS レンダリング用):
```bash
pip install "deuseek[fetchers]"          # patchright + curl_cffi + msgspec + protego
patchright install chromium               # stealth Chrome (Cloudflare bypass)
playwright install chromium               # JS rendering
```

## 📋 コマンド

| コマンド | 内容 |
|---|---|
| `deuseek search "<query>"` | マルチソース検索 (SERP: metadata + URL; content ≤500 文字) |
| `deuseek search --on hackernews,web "..."` | 特定ソースに制限 |
| `deuseek search --mode quick "..."` | web + hackernews のみ |
| `deuseek search --mode deep "..."` | 準備済みの全ソース |
| `deuseek search --json "..."` | 明示的 JSON 出力 |
| `deuseek search --no-cache "..."` | キャッシュをスキップし強制リフレッシュ |
| **`deuseek fetch <url>`** | **URL → 全文 markdown** (Scrapling 3 層ルーティング + DomainKB) |
| `deuseek fetch <url> --backend jina` | Jina Reader SaaS を強制 (ローカル依存ゼロ) |
| `deuseek fetch <url> --backend stealthy --solve-cloudflare` | ステルス Chrome + CF バイパスを強制 |
| `deuseek fetch <url> --backend dynamic` | Playwright JS レンダリングを強制 |
| `deuseek fetch <url> --full` | ページ全体を変換 (デフォルト: 本文のみ) |
| **`deuseek super "<query>"`** | **エンドツーエンド**: マルチソース検索 → ステルスフェッチ → (オプション) extract、ストリーミングパイプライン (~40% 高速化) |
| `deuseek crawl <url>` | 複数ページ Spider クロール (Scrapling async Spider + checkpoint) |
| `deuseek extract <url>` | 適応的構造化抽出 (CSS/XPath + 自己修復再配置) |
| `deuseek domain-kb` | domain→backend ナレッジベースの閲覧/クリア (`--clear`) |
| `deuseek init` | デフォルトの `~/.deuseek/preferences.toml` を書き込み |
| `deuseek sources` | 全ソース + 準備状態を一覧 (`--probe` でテスト) |
| `deuseek setup <source>` | ソースのガイド付きセットアップ |
| `deuseek doctor` | ヘルスチェック (sources + fetch backends + BrowserPool) |
| `deuseek check-update` | GitHub Releases と比較 |
| `deuseek preferences {show,edit,reset,path}` | ユーザープリファレンス |

## 📚 対応ソース(すべて無料)

| ソース | Tier | 依存 | 備考 |
|---|---|---|---|
| web | ✅ ready | `ddgs` (pip) | DuckDuckGo 一般ウェブ検索 |
| hackernews | ✅ ready | なし | Algolia HN API、ゼロ設定 |
| youtube | ✅ ready | `yt-dlp` (pip) | `deuseek setup youtube` |
| github | ✅ ready | `gh` CLI + `gh auth login` | `deuseek setup github` |
| rss | ✅ ready | 組み込み `feedparser` | **query は feed URL である必要があります** |
| wechat | ✅ ready | なし | WeChat 公式アカウント — 無料の Sogou 検索 (オプションで Scrapling ステルスブースト) |
| bilibili | ✅ ready | なし | Bilibili 公式 search API |
| reddit | 🟡 one_step | `rdt-cli` + `rdt login` | `deuseek setup reddit` |

> **全文が必要?** 上流が全文を返すソースは、オリジナルのペイロードを `result.raw` に保持します (例: wechat の `raw["item_html"]`)。それ以外は `deuseek fetch <url>` を実行してください。

## 🥷 フェッチエンジンアーキテクチャ

`deuseek fetch` / `super` / `crawl` / `extract` は [Scrapling](https://github.com/D4Vinci/Scrapling) の上に構築されています —— HTTP フェッチ、ステルスブラウザ、適応的パース、async Spider を 1 つの依存でカバーします。

### 3 層ルーティング (FetchRouter)

| エンジン | 実装 | 典型的な所要時間 | 用途 |
|---|---|---|---|
| **Fetcher** | Scrapling `Fetcher` (curl_cffi HTTP + TLS 偽装) | 0.4–3.9s | デフォルト、URL の 80% 以上、純粋な HTTP でブラウザ不要 |
| **jina** | [Jina Reader](https://r.jina.ai/) SaaS (サーバーサイド IP) | 2.2–5.7s | Fetcher がブロックされた際のフォールバック |
| **StealthyFetcher** | Scrapling `StealthyFetcher` (patchright ステルス Chrome) + `solve_cloudflare` | 7.8s / 37s (CF) | 最後の手段 — Cloudflare Turnstile を突破できる唯一のもの |
| DynamicFetcher | Scrapling `DynamicFetcher` (Playwright) | 4.9–6.9s | JS レンダリング専用、明示的な `--backend dynamic` |

> 段階的な昇格は意図的です: Fetcher は速いですが Cloudflare で死にます; StealthyFetcher は CF を突破できますが 37s は遅すぎてデフォルトにできません。ルーターはまず高速なものを試し、失敗時のみ昇格します。

### DomainKB — ドメインごとの記憶

ドメインごとにどのエンジンが機能し、どれがブロックされているかを記憶し、毎回のフェッチでの試行錯誤をなくします。
- ストレージ: プラットフォームパス (macOS `~/Library/Application Support/deuseek/`、Linux XDG `~/.local/share/deuseek/`、Windows `%APPDATA%/deuseek/`)
- **24h TTL** — 期限切れの entry は再プローブを強制し、サイトがアンチボット設定を変更しても古いレコードが自己修復します
- `record_success` / `record_failure` が毎回のフェッチで自動的に書き戻されます

```bash
deuseek domain-kb              # list all domain→backend mappings (with expired status)
deuseek domain-kb --clear      # wipe the knowledge base
```

### BrowserPool — ウォームなブラウザセッション

Stealthy/Dynamic は Chrome をコールドスタートするのに 2–4s かかります。`BrowserPool` はウォームセッションを維持して再利用し、後続のフェッチを ~1s に短縮します。5 分アイドルで自動 `shrink()` (インスタンスあたり ~200–500MB 解放)。`deuseek doctor` がウォーム状態を報告します。

### パイプラインモード — `deuseek super`

旗艦コマンドは search → fetch → extract を本当のパイプラインに束ねます: 最初の検索結果が届いた瞬間にフェッチが開始され、残りの検索とオーバーラップします (直列より ~40% 高速)。

```bash
deuseek super "iPhone 16 review"
deuseek super "Python asyncio" --sources hackernews,web --stream   # streaming JSON Lines
deuseek super "React 19" --extract-fields '{"title":"h1::text"}'   # + structured extraction
```

### CAPTCHA 自動昇格

`fetch` は各バックエンドの出力を CAPTCHA キーワードでスキャンします (`环境异常 / 完成验证后即可继续访问 / 请输入验证码 / Cloudflare / Just a moment / Checking your browser`)。ヒット時は:
1. `errors[]` に `captcha_suspected: ...` エントリが追加されます
2. StealthyFetcher が利用可能かつ未試行の場合、`stealthy + solve_cloudflare=True` で **自動リトライ** します
3. 成功 → `auto_upgraded: stealthy+solve_cloudflare succeeded`; 失敗 → `auto_upgrade_failed`

グレースフルデグレード — エージェントは `errors` を読んで何を信じるか判断します; `markdown` は常に保持されます。

## 🤝 エージェント呼び出し規約

エージェントから deuseek を呼ぶ際は **常に JSON を明示的に取得** してください。そうしないと TTY テーブルの折り返しでフィールドが欠落します:

```bash
# Option 1: --json per command
deuseek search --json "..."
deuseek fetch  --json "<url>"

# Option 2: env var (applies to the whole agent harness — recommended)
export DEUSEEK_FORCE_JSON=1
```

`not isatty()` で自動的に JSON に切り替わりますが、一部のエージェント端末 (例: Antigravity) は実際の PTY を割り当てるため `isatty()` が True になり、自動検出が失敗します —— 明示的な `--json` または env var が常に機能する保証です。

標準の検索 envelope:
```json
{
  "query": "...",
  "ts": "ISO 8601 Z",
  "results": [{"source","title","url","content","ts","score","raw","cost"}],
  "errors":  [{"source","error","category"}]
}
```

## ⚙️ プリファレンス

`~/.deuseek/preferences.toml` がデフォルトのソース、言語、出力形式、`trust` オーバーライドを設定します。

```bash
deuseek preferences show     # view current config
deuseek preferences edit     # edit with $EDITOR (Windows fallback: notepad)
deuseek preferences reset    # reset (backs up to .bak)
deuseek preferences path     # print the file path
```

API キー (オプション — コアにはキー不要) は `~/.deuseek/secrets.env` に置きます (`KEY=VALUE`; POSIX では緩い権限に警告します)。

## 🪟 プラットフォームサポート

| プラットフォーム | 状態 | 備考 |
|---|---|---|
| macOS | ✅ 主力 | 全ソース + 3 つのフェッチバックエンドすべてをテスト済み |
| Linux | 🟡 ベストエフォート | 動作します; setup フローは `apt`/`pacman` を自動処理しません |
| WSL2 | 🟡 ベストエフォート | Linux と同様 |
| Windows (ネイティブ PowerShell) | 🟡 実験的 | `secrets_env` は POSIX chmod をスキップ; preferences edit は notepad にフォールバック; setup github は `winget install GitHub.cli` を提案。**問題に遭遇したら issue を立ててください。** |

`deuseek doctor` は先頭にプラットフォーム / Python バージョンを出力します —— issue を立てる際に添付してください。

## 🏗️ アーキテクチャ

- **Adapter パターン** — ソースごとに 1 つの adapter が `AdapterBase` (`is_ready` + `search`) を実装
- **非同期ファンアウト** — `Dispatcher` が `asyncio.gather` を使用し、ソースごとのエラーを隔離 (`unavailable` vs `failed`)
- **YAML レジストリ** — `sources.yml` が唯一の信頼できる情報源 (tier / adapter / trust / timeout / deps)
- **Router** — 部分文字列 query_hints + `default_in_auto` のマージ、`MAX_SOURCES=5`、RSS は URL クエリでゲート
- **Scorer** — `0.4*recency_norm + 0.6*source_trust` (重みの合計 = 1.0、assert 付き); タイムスタンプ欠落時はデフォルト 0.5
- **キャッシュ** — L1 メモリ + L2 ファイル; URL 正規化 (`utm_*`/`fbclid`/`gclid`/... を剥離) によりトラッカーのバリアントが 1 つの entry を共有
- **契約** — pydantic `SearchResult.content` validator が全体で 500 文字に切り詰め; 全文は `raw` に保持

主なファイル: `deuseek/sources.yml`、`deuseek/adapters/`、`deuseek/cli.py`、`deuseek/commands/fetch.py`、`deuseek/commands/super.py`、`deuseek/dispatcher.py`、`deuseek/fetch_router/router.py`、`deuseek/engines/`、`deuseek/convert/converter.py`、`deuseek/perf/`、`deuseek/native/`、`.claude-plugin/skills/deuseek/SKILL.md`。

## 🙏 謝辞

deuseek は巨人の肩の上に成り立っています:

- **[Scrapling](https://github.com/D4Vinci/Scrapling)** by [**D4Vinci**](https://github.com/D4Vinci) — deuseek のフェッチレイヤー全体を支えるステルスフェッチ / 適応的パース / async Spider フレームワーク (Fetcher / StealthyFetcher / DynamicFetcher / 適応的セレクタ / Spider)。3 層の Cloudflare バイパス設計は、これなしには存在し得ませんでした。🙏
- **[Daily-AC/deuseek](https://github.com/Daily-AC/deuseek)** (MIT) — この無料 fork が基づく上流プロジェクト。
- 上流のツール & ライブラリ: `yt-dlp`、`gh`、`rdt-cli`、`feedparser`、`httpx`、`pydantic`、`rich`、`click`、[Jina Reader](https://r.jina.ai/)、`curl_cffi`、`patchright`、`Playwright`、`markdownify`、`html2text`、`lxml`。

## 🤝 貢献

コントリビューションを歓迎します! 以下をお願いします:
1. ソース/バックエンドの問題を報告する際は `deuseek doctor` を実行し、その出力を含めてください —— "あるソースが動かない" の 90% は上流バイナリの欠落です。
2. 新しいソースや破壊的変更については、まず issue を立ててください。
3. adapter は `AdapterBase` (`is_ready` + `search` が `SearchResult` を返す) に準拠させてください。

バグ報告、機能リクエスト、新規ソースリクエストについては [issue テンプレート](../.github/ISSUE_TEMPLATE/) を参照してください。

## 📄 ライセンス

MIT — [LICENSE](../LICENSE) を参照してください。[Daily-AC/deuseek](https://github.com/Daily-AC/deuseek) (MIT) に基づきます; 上流の著作権表示は保持されています。
