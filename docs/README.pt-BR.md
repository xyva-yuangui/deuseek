# deuseek

> A camada universal de busca e fetch furtivo para qualquer agent de programação com IA. Ignore o gate do WebSearch, alcance as fontes que a busca server-side não consegue e transforme qualquer URL em markdown limpo — **100% gratuito, sem necessidade de API keys**.

> Camada de fetch alimentada por [Scrapling](https://github.com/D4Vinci/Scrapling) de **D4Vinci** — usado com gratidão. 🙏

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Sources](https://img.shields.io/badge/sources-8%20free-success.svg)](#-fontes-suportadas-todas-gratuitas)
[![Status](https://img.shields.io/badge/status-1.0.0--alpha-orange.svg)](#)

🌐 [English](../README.md) | [العربية](README.ar.md) | [Español](README.es.md) | **Português (Brasil)** | [Français](README.fr.md) | [Deutsch](README.de.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [Русский](README.ru.md) | [한국어](README.ko.md)

---

## Sumário
- [✨ Por que o deuseek?](#-por-que-o-deuseek)
- [🤖 Funciona com seu agent CLI](#-funciona-com-seu-agent-cli)
- [🚀 Início rápido](#-início-rápido)
- [📦 Instalação](#-instalação)
- [📋 Comandos](#-comandos)
- [📚 Fontes suportadas (todas gratuitas)](#-fontes-suportadas-todas-gratuitas)
- [🥷 Arquitetura do mecanismo de fetch](#-arquitetura-do-mecanismo-de-fetch)
- [🤝 Convenção de chamada pelo agent](#-convenção-de-chamada-pelo-agent)
- [⚙️ Preferências](#️-preferências)
- [🪟 Suporte a plataformas](#-suporte-a-plataformas)
- [🏗️ Arquitetura](#️-arquitetura)
- [🙏 Agradecimentos](#-agradecimentos)
- [🤝 Contribuindo](#-contribuindo)
- [📄 Licença](#-licença)

---

## ✨ Por que o deuseek?

O `WebSearch` da Anthropic é uma **ferramenta server-side** (`web_search_20250305`) protegida por duas verificações:
1. **Gate do cliente** — registrado apenas para configurações first-party / de provedores específicos.
2. **Gate do upstream** — a API upstream precisa de fato *implementar* a ferramenta server-side. **Estações de retransmissão compatíveis com OpenAI** (cliproxy, anyrouter, gateways self-hosted) que apenas traduzem Claude API → OpenAI Chat Completions **não a implementam**, então o `WebSearch` falha silenciosamente. Mesmo onde funciona, não alcança threads em tempo real do HN, comentários profundos do Reddit, artigos de WeChat 公众号, nem vídeos técnicos do Bilibili.

**O deuseek resolve isso no lado do cliente** — um único CLI + Skill que vai direto para Algolia / `yt-dlp` / `gh` / Bilibili API / Sogou / DuckDuckGo, então funciona independentemente do provedor de API para o qual o seu agent CLI aponta.

### Principais vantagens

| | deuseek | `WebSearch` nativo | APIs de busca pagas |
|---|:---:|:---:|:---:|
| Funciona em estações de retransmissão/proxy compatíveis com OpenAI | ✅ | ❌ | n/a |
| Alcance HN / Reddit / WeChat / Bilibili / RSS | ✅ | ❌ | parcial |
| Bypass de Cloudflare / anti-bot | ✅ | ❌ | n/a |
| URL → markdown com texto completo | ✅ | apenas WebFetch | n/a |
| Custo | **gratuito** | incluído | 💲 pago |
| Tempo de configuração | ~3 min | — | — |

- 🚪 **Bypassa o gate de duas camadas do WebSearch** — roda em estações de retransmissão/proxy onde o `WebSearch` falha silenciosamente porque o upstream não implementa a ferramenta server-side.
- 🌐 **Alcança fontes verticais que a busca server-side não consegue** — discussões em tempo real do HN, threads de comentários profundos do Reddit, artigos de WeChat 公众号, vídeos técnicos do Bilibili, feeds RSS.
- 🆓 **100% gratuito, zero API keys no núcleo** — DuckDuckGo, Algolia HN, Bilibili API, Sogou, `yt-dlp`, `gh`, `feedparser`. Sem cartão de crédito, sem cota, sem dor de cabeça com rate-limit.
- 🥷 **Fetch furtivo de três camadas com bypass de Cloudflare** — `Fetcher` (curl_cffi HTTP) → Jina SaaS → `StealthyFetcher` (patchright Chrome) + `solve_cloudflare`. A única camada que quebra Cloudflare Turnstile/Interstitial.
- 🧠 **O DomainKB lembra por domínio** — sem tentativa e erro a cada fetch; um TTL de 24h força um re-probe, então a base de conhecimento nunca fica desatualizada quando um site muda sua configuração anti-bot.
- ⚡ **Modo pipeline ~40% mais rápido** — o `asyncio` envia os resultados da busca direto para o fetch (os resultados não esperam a fonte mais lenta).
- 🛡️ **Upgrade automático de captcha** — detecta páginas de captcha (环境异常 / Cloudflare / Just a moment) e re-tenta automaticamente com `stealthy + solve_cloudflare`, expondo erros para que o agent decida no que confiar.
- 🔧 **Seletores adaptativos e self-healing** — redesigns de página não quebram a extração (relocação por similaridade do Scrapling + `auto_save`).
- 🖥️ **Multiplataforma** — macOS prioritário, Linux / WSL2 / Windows com melhor esforço.
- 🧩 **Um CLI + um Skill, agent-agnostic por design** — encaixa em qualquer agent CLI em ~3 minutos; um manifest `.claude-plugin/` o torna um Skill nativo para CLIs compatíveis com Claude Code, e um CLI JSON simples para todo o resto.
- 🔍 **Transparente** — marcação `cost="free|paid"`, `errors[]` estruturado e payloads `raw` originais preservados, para que os agents possam pegar o texto completo quando preciso.

## 🤖 Funciona com seu agent CLI

O deuseek é um CLI padrão que emite JSON — **qualquer agent que consiga rodar comandos shell pode usá-lo**. O manifest `.claude-plugin/` adiciona integração nativa como Skill para CLIs compatíveis com Claude Code.

| Ferramenta de agent | Como usar o deuseek |
|---|---|
| **Claude Code** (Anthropic) | `/plugin marketplace add xyva-yuangui/deuseek` → `/plugin install deuseek`, depois *"use o deuseek para buscar ..."*. Também funciona como um CLI comum. |
| **Zcode** | Chame `deuseek search --json "..."` / `deuseek fetch --json <url>` a partir do shell, ou carregue o Skill. |
| **Codex** (OpenAI Codex CLI) | Rode `deuseek` como subprocesso e faça o parse do envelope JSON. |
| **Reasonix** | JSON via subprocesso, ou carregue como skill. |
| **OpenClaw** | Rode `deuseek` como um comando shell e faça o parse do JSON. |
| **Hermes** | JSON via subprocesso. |
| **Antigravity** (`agy`) | `agy plugin install` (reconhece `.claude-plugin/`). |
| Qualquer outro agent | Rode `deuseek <command> --json` como um comando shell e faça o parse do envelope JSON. |

> Como o contrato é "um CLI que imprime JSON", o deuseek é **agent-agnostic** — você nunca precisa esperar que nós "suportemos" sua ferramenta. Se o seu agent consegue spawnar um processo, ele pode usar o deuseek hoje.

## 🚀 Início rápido

```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
deuseek init                   # writes default ~/.deuseek/preferences.toml
deuseek search "vibe coding"   # web + hackernews work zero-config
```

Desbloqueie fontes que precisam de uma ferramenta upstream:

```bash
deuseek setup youtube     # pip install yt-dlp
deuseek setup github      # brew install gh (macOS) / winget (Windows)
deuseek setup reddit      # uv tool install rdt-cli && rdt login
```

## 📦 Instalação

**Opção A — uv (recomendado):**
```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
```

**Opção B — pip (instalação editável de desenvolvimento):**
```bash
git clone https://github.com/xyva-yuangui/deuseek.git
cd deuseek
pip install -e ".[dev]"
```

**Opção C — script de uma linha (macOS/Linux, configura venv + navegadores):**
```bash
bash install.sh
```

**Mecanismos de fetch opcionais** (para bypass de Cloudflare e renderização JS):
```bash
pip install "deuseek[fetchers]"          # patchright + curl_cffi + msgspec + protego
patchright install chromium               # stealth Chrome (Cloudflare bypass)
playwright install chromium               # JS rendering
```

## 📋 Comandos

| Comando | O que faz |
|---|---|
| `deuseek search "<query>"` | Busca multi-fonte (SERP: metadata + URL; content ≤500 caracteres) |
| `deuseek search --on hackernews,web "..."` | Restringe a fontes específicas |
| `deuseek search --mode quick "..."` | Apenas web + hackernews |
| `deuseek search --mode deep "..."` | Todas as fontes prontas |
| `deuseek search --json "..."` | Saída JSON explícita |
| `deuseek search --no-cache "..."` | Ignora o cache, força atualização |
| **`deuseek fetch <url>`** | **URL → markdown com texto completo** (roteamento de três camadas do Scrapling + DomainKB) |
| `deuseek fetch <url> --backend jina` | Força Jina Reader SaaS (zero dependências locais) |
| `deuseek fetch <url> --backend stealthy --solve-cloudflare` | Força Chrome furtivo + bypass de CF |
| `deuseek fetch <url> --backend dynamic` | Força renderização JS com Playwright |
| `deuseek fetch <url> --full` | Converte a página inteira (padrão: apenas o conteúdo principal) |
| **`deuseek super "<query>"`** | **Ponta a ponta**: busca multi-fonte → fetch furtivo → extract (opcional), pipeline com streaming (~40% mais rápido) |
| `deuseek crawl <url>` | Crawl multi-página com Spider (Scrapling async Spider + checkpoint) |
| `deuseek extract <url>` | Extração estruturada adaptativa (CSS/XPath + relocação self-healing) |
| `deuseek domain-kb` | Visualiza/limpa a base de conhecimento domain→backend (`--clear`) |
| `deuseek init` | Escreve o `~/.deuseek/preferences.toml` padrão |
| `deuseek sources` | Lista todas as fontes + prontidão (`--probe` para testar) |
| `deuseek setup <source>` | Configuração guiada de uma fonte |
| `deuseek doctor` | Verificação de saúde (sources + fetch backends + BrowserPool) |
| `deuseek check-update` | Compara com GitHub Releases |
| `deuseek preferences {show,edit,reset,path}` | Preferências do usuário |

## 📚 Fontes suportadas (todas gratuitas)

| Fonte | Tier | Dependência | Observações |
|---|---|---|---|
| web | ✅ ready | `ddgs` (pip) | Busca geral na web pelo DuckDuckGo |
| hackernews | ✅ ready | nenhuma | Algolia HN API, zero-config |
| youtube | ✅ ready | `yt-dlp` (pip) | `deuseek setup youtube` |
| github | ✅ ready | `gh` CLI + `gh auth login` | `deuseek setup github` |
| rss | ✅ ready | `feedparser` embutido | **a query deve ser uma URL de feed** |
| wechat | ✅ ready | nenhuma | WeChat 公众号 — busca gratuita via Sogou (boost furtivo opcional com Scrapling) |
| bilibili | ✅ ready | nenhuma | API de busca oficial do Bilibili |
| reddit | 🟡 one_step | `rdt-cli` + `rdt login` | `deuseek setup reddit` |

> **Quer o texto completo?** As fontes cujo upstream retorna o conteúdo completo preservam o payload original em `result.raw` (ex.: `raw["item_html"]` do wechat). Para todo o resto, rode `deuseek fetch <url>`.

## 🥷 Arquitetura do mecanismo de fetch

O `deuseek fetch` / `super` / `crawl` / `extract` são construídos sobre o [Scrapling](https://github.com/D4Vinci/Scrapling) — uma única dependência que cobre fetch HTTP, navegador furtivo, parsing adaptativo e Spider assíncrono.

### Roteamento de três camadas (FetchRouter)

| Mecanismo | Implementação | Tempo típico | Uso |
|---|---|---|---|
| **Fetcher** | Scrapling `Fetcher` (curl_cffi HTTP + impersonação de TLS) | 0.4–3.9s | Padrão, 80%+ das URLs, HTTP puro sem navegador |
| **jina** | SaaS do [Jina Reader](https://r.jina.ai/) (IP server-side) | 2.2–5.7s | Fallback quando o Fetcher é bloqueado |
| **StealthyFetcher** | Scrapling `StealthyFetcher` (patchright Chrome furtivo) + `solve_cloudflare` | 7.8s / 37s (CF) | Último recurso — o único que quebra Cloudflare Turnstile |
| DynamicFetcher | Scrapling `DynamicFetcher` (Playwright) | 4.9–6.9s | Sites só de renderização JS, `--backend dynamic` explícito |

> A escalação é intencional: o Fetcher é rápido, mas morre no Cloudflare; o StealthyFetcher quebra o CF, mas 37s é lento demais para ser o padrão. O router testa o rápido primeiro e escala apenas em caso de falha.

### DomainKB — memória por domínio

Lembra qual engine funciona e qual está bloqueado por domínio, para não ficar tentando e errando a cada fetch.
- Armazenamento: caminho da plataforma (macOS `~/Library/Application Support/deuseek/`, Linux XDG `~/.local/share/deuseek/`, Windows `%APPDATA%/deuseek/`)
- **TTL de 24h** — entradas expiradas forçam um re-probe, então registros defasados se auto-corrigem quando um site muda sua configuração anti-bot
- `record_success` / `record_failure` gravam de volta automaticamente a cada fetch

```bash
deuseek domain-kb              # list all domain→backend mappings (with expired status)
deuseek domain-kb --clear      # wipe the knowledge base
```

### BrowserPool — sessões de navegador pré-aquecidas

Stealthy/Dynamic fazem cold-start de um Chrome em 2–4s. O `BrowserPool` mantém uma sessão warm e a reutiliza, reduzindo os fetches subsequentes a ~1s. Ocioso por 5 min → `shrink()` automático (~200–500MB/instância liberados). O `deuseek doctor` informa o estado warm.

### Modo pipeline — `deuseek super`

O comando flagship encadeia search → fetch → extract em um pipeline de verdade: assim que o primeiro resultado de busca chega, o fetch começa e se sobrepõe às buscas restantes (~40% mais rápido que em série).

```bash
deuseek super "iPhone 16 review"
deuseek super "Python asyncio" --sources hackernews,web --stream   # streaming JSON Lines
deuseek super "React 19" --extract-fields '{"title":"h1::text"}'   # + structured extraction
```

### Upgrade automático de captcha

O `fetch` examina a saída de cada backend em busca de palavras-chave de captcha (`环境异常 / 完成验证后即可继续访问 / 请输入验证码 / Cloudflare / Just a moment / Checking your browser`). Em caso de acerto:
1. `errors[]` recebe uma entrada `captcha_suspected: ...`
2. Se o StealthyFetcher estiver disponível e não tiver sido tentado, ele **re-tenta automaticamente** com `stealthy + solve_cloudflare=True`
3. Sucesso → `auto_upgraded: stealthy+solve_cloudflare succeeded`; falha → `auto_upgrade_failed`

Degradação elegante — o agent lê os `errors` e decide no que confiar; o `markdown` é sempre preservado.

## 🤝 Convenção de chamada pelo agent

**Sempre pegue o JSON explicitamente** ao chamar o deuseek a partir de um agent, para que a quebra de tabela TTY não perca campos:

```bash
# Option 1: --json per command
deuseek search --json "..."
deuseek fetch  --json "<url>"

# Option 2: env var (applies to the whole agent harness — recommended)
export DEUSEEK_FORCE_JSON=1
```

O `not isatty()` alterna para JSON automaticamente, mas alguns terminais de agent (ex.: Antigravity) alocam um PTY real, então `isatty()` é True e a auto-detecção falha — `--json` explícito ou a env var é a garantia que sempre funciona.

Envelope padrão de busca:
```json
{
  "query": "...",
  "ts": "ISO 8601 Z",
  "results": [{"source","title","url","content","ts","score","raw","cost"}],
  "errors":  [{"source","error","category"}]
}
```

## ⚙️ Preferências

O `~/.deuseek/preferences.toml` configura fontes padrão, idioma, formato de saída e overrides de `trust`.

```bash
deuseek preferences show     # view current config
deuseek preferences edit     # edit with $EDITOR (Windows fallback: notepad)
deuseek preferences reset    # reset (backs up to .bak)
deuseek preferences path     # print the file path
```

API keys (opcionais — o núcleo não precisa de nenhuma) ficam em `~/.deuseek/secrets.env` (`KEY=VALUE`; no POSIX, permissões frouxas geram aviso).

## 🪟 Suporte a plataformas

| Plataforma | Status | Observações |
|---|---|---|
| macOS | ✅ Primário | Todas as fontes + os três fetch backends testados |
| Linux | 🟡 melhor esforço | Funciona; o fluxo de setup não cuida de `apt`/`pacman` automaticamente |
| WSL2 | 🟡 melhor esforço | Mesmo que o Linux |
| Windows (PowerShell nativo) | 🟡 Experimental | `secrets_env` pula o chmod POSIX; o preferences edit usa o notepad como fallback; o setup github sugere `winget install GitHub.cli`. **Abra uma issue se encontrar problemas.** |

O `deuseek doctor` imprime a plataforma / versão do Python no topo — anexe isso ao abrir issues.

## 🏗️ Arquitetura

- **Padrão Adapter** — um adapter por fonte, implementando `AdapterBase` (`is_ready` + `search`)
- **Fan-out assíncrono** — o `Dispatcher` usa `asyncio.gather` com isolamento de erro por fonte (`unavailable` vs `failed`)
- **Registro YAML** — `sources.yml` é a fonte única de verdade (tier / adapter / trust / timeout / deps)
- **Router** — merge de query_hints por substring + `default_in_auto`, `MAX_SOURCES=5`, RSS restrito a queries de URL
- **Scorer** — `0.4*recency_norm + 0.6*source_trust` (pesos somam 1.0, com assert); timestamps ausentes usam 0.5 como padrão
- **Cache** — L1 em memória + L2 em arquivo; canonicalização de URL (remove `utm_*`/`fbclid`/`gclid`/...) para que variantes de tracker compartilhem uma entrada
- **Contrato** — o validator `SearchResult.content` do pydantic trunca para 500 caracteres globalmente; o texto completo fica em `raw`

Arquivos-chave: `deuseek/sources.yml`, `deuseek/adapters/`, `deuseek/cli.py`, `deuseek/commands/fetch.py`, `deuseek/commands/super.py`, `deuseek/dispatcher.py`, `deuseek/fetch_router/router.py`, `deuseek/engines/`, `deuseek/convert/converter.py`, `deuseek/perf/`, `deuseek/native/`, `.claude-plugin/skills/deuseek/SKILL.md`.

## 🙏 Agradecimentos

O deuseek apoia-se no ombro de gigantes:

- **[Scrapling](https://github.com/D4Vinci/Scrapling)** de [**D4Vinci**](https://github.com/D4Vinci) — o framework de fetch furtivo / parsing adaptativo / Spider assíncrono que sustenta toda a camada de fetch do deuseek (Fetcher / StealthyFetcher / DynamicFetcher / seletores adaptativos / Spider). O design de três camadas para bypass de Cloudflare simplesmente não existiria sem ele. 🙏
- **[Daily-AC/deuseek](https://github.com/Daily-AC/deuseek)** (MIT) — o projeto upstream sobre o qual este fork gratuito é construído.
- Ferramentas e bibliotecas upstream: `yt-dlp`, `gh`, `rdt-cli`, `feedparser`, `httpx`, `pydantic`, `rich`, `click`, [Jina Reader](https://r.jina.ai/), `curl_cffi`, `patchright`, `Playwright`, `markdownify`, `html2text`, `lxml`.

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:
1. Rode `deuseek doctor` e inclua sua saída ao reportar problemas de source/backend — 90% dos "uma fonte não funciona" é um binário upstream ausente.
2. Abra uma issue primeiro para novas fontes ou mudanças que quebram compatibilidade.
3. Mantenha os adapters em conformidade com `AdapterBase` (`is_ready` + `search` retornando `SearchResult`).

Veja os [modelos de issue](../.github/ISSUE_TEMPLATE/) para relatos de bugs, pedidos de funcionalidades e pedidos de novas fontes.

## 📄 Licença

MIT — veja o [LICENSE](../LICENSE). Baseado em [Daily-AC/deuseek](https://github.com/Daily-AC/deuseek) (MIT); aviso de copyright do upstream preservado.
