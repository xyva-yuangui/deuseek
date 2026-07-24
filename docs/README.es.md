# deuseek

> La capa universal de búsqueda y captura furtiva para cualquier agente de codificación con IA. Omite la barrera de WebSearch, alcanza las fuentes que la búsqueda del lado del servidor no puede y convierte cualquier URL en markdown limpio — **100% gratis, sin claves de API**.

> La capa de captura está impulsada por [Scrapling](https://github.com/D4Vinci/Scrapling) de **D4Vinci** — usado con gratitud. 🙏

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Sources](https://img.shields.io/badge/sources-8%20free-success.svg)](#-fuentes-admitidas-todas-gratuitas)
[![Status](https://img.shields.io/badge/status-1.0.0--alpha-orange.svg)](#)

🌐 [English](../README.md) | [العربية](README.ar.md) | **Español** | [Português (Brasil)](README.pt-BR.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [Русский](README.ru.md) | [한국어](README.ko.md)

---

## Tabla de contenidos
- [✨ ¿Por qué deuseek?](#-por-qué-deuseek)
- [🤖 Funciona con tu CLI de agente](#-funciona-con-tu-cli-de-agente)
- [🚀 Inicio rápido](#-inicio-rápido)
- [📦 Instalación](#-instalación)
- [📋 Comandos](#-comandos)
- [📚 Fuentes admitidas (todas gratuitas)](#-fuentes-admitidas-todas-gratuitas)
- [🥷 Arquitectura del motor de captura](#-arquitectura-del-motor-de-captura)
- [🤝 Convención de llamada para agentes](#-convención-de-llamada-para-agentes)
- [⚙️ Preferencias](#️-preferencias)
- [🪟 Soporte de plataformas](#-soporte-de-plataformas)
- [🏗️ Arquitectura](#️-arquitectura)
- [🙏 Agradecimientos](#-agradecimientos)
- [🤝 Contribuir](#-contribuir)
- [📄 Licencia](#-licencia)

---

## ✨ ¿Por qué deuseek?

`WebSearch` de Anthropic es una **herramienta del lado del servidor** (`web_search_20250305`) protegida por dos controles:
1. **Control del cliente** — solo se registra para configuraciones first-party / de un proveedor específico.
2. **Control del proveedor upstream** — la API upstream debe *implementar* realmente la herramienta del servidor. Las **estaciones de retransmisión compatibles con OpenAI** (cliproxy, anyrouter, pasarelas autoalojadas) que simplemente traducen la API de Claude → OpenAI Chat Completions **no la implementan**, por lo que `WebSearch` falla silenciosamente. Incluso donde funciona, no puede alcanzar los hilos en tiempo real de HN, los comentarios profundos de Reddit, los artículos de WeChat 公众号 o los vídeos técnicos de Bilibili.

**deuseek soluciona esto del lado del cliente** — un único CLI + Skill que se conecta directamente a Algolia / `yt-dlp` / `gh` / API de Bilibili / Sogou / DuckDuckGo, por lo que funciona independientemente del proveedor de API al que apunte tu CLI de agente.

### Ventajas clave

| | deuseek | `WebSearch` nativo | APIs de búsqueda de pago |
|---|:---:|:---:|:---:|
| Funciona en estaciones de retransmisión/proxy compatibles con OpenAI | ✅ | ❌ | n/a |
| Alcanza HN / Reddit / WeChat / Bilibili / RSS | ✅ | ❌ | parcial |
| Omite Cloudflare / antibots | ✅ | ❌ | n/a |
| URL → markdown de texto completo | ✅ | solo WebFetch | n/a |
| Coste | **gratis** | incluido | 💲 de pago |
| Tiempo de configuración | ~3 min | — | — |

- 🚪 **Omite la barrera doble de WebSearch** — funciona en estaciones de retransmisión/proxy donde `WebSearch` falla silenciosamente porque el upstream no implementa la herramienta del servidor.
- 🌐 **Alcanza fuentes verticales que la búsqueda del lado del servidor no puede** — discusiones en tiempo real de HN, hilos de comentarios profundos de Reddit, artículos de WeChat 公众号, vídeos técnicos de Bilibili, feeds RSS.
- 🆓 **100% gratis, sin claves de API para el núcleo** — DuckDuckGo, Algolia HN, API de Bilibili, Sogou, `yt-dlp`, `gh`, `feedparser`. Sin tarjeta de crédito, sin cuota, sin dolores de cabeza por límites.
- 🥷 **Captura furtiva de tres niveles con omisión de Cloudflare** — `Fetcher` (HTTP curl_cffi) → Jina SaaS → `StealthyFetcher` (Chrome patchright) + `solve_cloudflare`. El único nivel que rompe Cloudflare Turnstile/Interstitial.
- 🧠 **DomainKB recuerda por dominio** — sin prueba y error en cada captura; un TTL de 24h fuerza un re-probe para que la base de conocimiento nunca quede obsoleta cuando un sitio cambia su configuración antibot.
- ⚡ **Modo pipeline ~40% más rápido** — `asyncio` transmite los resultados de búsqueda directamente a la captura (los resultados no esperan a la fuente más lenta).
- 🛡️ **Auto-escalada ante captchas** — detecta páginas de captcha (环境异常 / Cloudflare / Just a moment) y reintenta automáticamente con `stealthy + solve_cloudflare`, exponiendo los errores para que el agente decida en qué confiar.
- 🔧 **Selectores adaptativos y autoreparables** — los rediseños de página no rompen la extracción (reubicación por similitud de Scrapling + `auto_save`).
- 🖥️ **Multiplataforma** — macOS como principal, Linux / WSL2 / Windows con soporte de mejor esfuerzo.
- 🧩 **Un CLI + un Skill, agnóstico por diseño** — se integra en cualquier CLI de agente en ~3 minutos; un manifest `.claude-plugin/` lo convierte en un Skill nativo para CLIs compatibles con Claude Code, y en un CLI JSON plano para todo lo demás.
- 🔍 **Transparente** — etiquetado `cost="free|paid"`, `errors[]` estructurado y payloads `raw` originales preservados para que los agentes puedan obtener el texto completo cuando lo necesiten.

## 🤖 Funciona con tu CLI de agente

deuseek es un CLI estándar que emite JSON — **cualquier agente que pueda ejecutar comandos de shell puede usarlo**. El manifest `.claude-plugin/` añade integración nativa como Skill para CLIs compatibles con Claude Code.

| Herramienta de agente | Cómo usar deuseek |
|---|---|
| **Claude Code** (Anthropic) | `/plugin marketplace add xyva-yuangui/deuseek` → `/plugin install deuseek`, luego *"use deuseek to search ..."*. También funciona como CLI normal. |
| **Zcode** | Llama a `deuseek search --json "..."` / `deuseek fetch --json <url>` desde el shell, o carga el Skill. |
| **Codex** (OpenAI Codex CLI) | Ejecuta `deuseek` como subproceso y analiza el envelope JSON. |
| **Reasonix** | JSON por subproceso, o carga como skill. |
| **OpenClaw** | Ejecuta `deuseek` como comando de shell y analiza el JSON. |
| **Hermes** | JSON por subproceso. |
| **Antigravity** (`agy`) | `agy plugin install` (reconoce `.claude-plugin/`). |
| Cualquier otro agente | Ejecuta `deuseek <comando> --json` como comando de shell y analiza el envelope JSON. |

> Como el contrato es "un CLI que imprime JSON", deuseek es **agnóstico respecto al agente** — nunca tienes que esperar a que "admitamos" tu herramienta. Si tu agente puede lanzar un proceso, puede usar deuseek hoy.

## 🚀 Inicio rápido

```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
deuseek init                   # escribe ~/.deuseek/preferences.toml por defecto
deuseek search "vibe coding"   # web + hackernews funcionan sin configuración
```

Desbloquea fuentes que necesitan una herramienta upstream:

```bash
deuseek setup youtube     # pip install yt-dlp
deuseek setup github      # brew install gh (macOS) / winget (Windows)
deuseek setup reddit      # uv tool install rdt-cli && rdt login
```

## 📦 Instalación

**Opción A — uv (recomendado):**
```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
```

**Opción B — pip (instalación editable para desarrollo):**
```bash
git clone https://github.com/xyva-yuangui/deuseek.git
cd deuseek
pip install -e ".[dev]"
```

**Opción C — script de una línea (macOS/Linux, prepara venv + navegadores):**
```bash
bash install.sh
```

**Motores de captura opcionales** (para omisión de Cloudflare y renderizado JS):
```bash
pip install "deuseek[fetchers]"          # patchright + curl_cffi + msgspec + protego
patchright install chromium               # Chrome furtivo (omisión de Cloudflare)
playwright install chromium               # renderizado JS
```

## 📋 Comandos

| Comando | Qué hace |
|---|---|
| `deuseek search "<query>"` | Búsqueda multifuente (SERP: metadatos + URL; contenido ≤500 caracteres) |
| `deuseek search --on hackernews,web "..."` | Restringe a fuentes específicas |
| `deuseek search --mode quick "..."` | Solo web + hackernews |
| `deuseek search --mode deep "..."` | Todas las fuentes listas |
| `deuseek search --json "..."` | Salida JSON explícita |
| `deuseek search --no-cache "..."` | Omite la caché, fuerza actualización |
| **`deuseek fetch <url>`** | **URL → markdown de texto completo** (enrutamiento de tres niveles Scrapling + DomainKB) |
| `deuseek fetch <url> --backend jina` | Fuerza Jina Reader SaaS (sin dependencias locales) |
| `deuseek fetch <url> --backend stealthy --solve-cloudflare` | Fuerza Chrome furtivo + omisión de CF |
| `deuseek fetch <url> --backend dynamic` | Fuerza renderizado JS con Playwright |
| `deuseek fetch <url> --full` | Convierte la página completa (por defecto: solo contenido principal) |
| **`deuseek super "<query>"`** | **De extremo a extremo**: búsqueda multifuente → captura furtiva → (opcional) extract, pipeline en streaming (~40% más rápido) |
| `deuseek crawl <url>` | Rastreo Spider multipágina (Scrapling async Spider + checkpoint) |
| `deuseek extract <url>` | Extracción estructurada adaptativa (CSS/XPath + autoreparación por reubicación) |
| `deuseek domain-kb` | Ver/borrar la base de conocimiento dominio→backend (`--clear`) |
| `deuseek init` | Escribe el `~/.deuseek/preferences.toml` por defecto |
| `deuseek sources` | Lista todas las fuentes + disponibilidad (`--probe` para probar) |
| `deuseek setup <source>` | Configuración guiada de una fuente |
| `deuseek doctor` | Comprobación de salud (fuentes + backends de captura + BrowserPool) |
| `deuseek check-update` | Compara con los GitHub Releases |
| `deuseek preferences {show,edit,reset,path}` | Preferencias de usuario |

## 📚 Fuentes admitidas (todas gratuitas)

| Fuente | Nivel | Dependencia | Notas |
|---|---|---|---|
| web | ✅ ready | `ddgs` (pip) | Búsqueda web general DuckDuckGo |
| hackernews | ✅ ready | ninguna | API de HN de Algolia, sin configuración |
| youtube | ✅ ready | `yt-dlp` (pip) | `deuseek setup youtube` |
| github | ✅ ready | `gh` CLI + `gh auth login` | `deuseek setup github` |
| rss | ✅ ready | `feedparser` integrado | **la consulta debe ser una URL de feed** |
| wechat | ✅ ready | ninguna | WeChat 公众号 — búsqueda gratuita en Sogou (impulso furtivo opcional con Scrapling) |
| bilibili | ✅ ready | ninguna | API de búsqueda oficial de Bilibili |
| reddit | 🟡 one_step | `rdt-cli` + `rdt login` | `deuseek setup reddit` |

> **¿Texto completo?** Las fuentes cuyo upstream devuelve el contenido completo conservan el payload original en `result.raw` (p. ej. `raw["item_html"]` de wechat). Para todo lo demás, ejecuta `deuseek fetch <url>`.

## 🥷 Arquitectura del motor de captura

`deuseek fetch` / `super` / `crawl` / `extract` se construyen sobre [Scrapling](https://github.com/D4Vinci/Scrapling) — una dependencia que cubre captura HTTP, navegador furtivo, análisis adaptativo y Spider asíncrono.

### Enrutamiento de tres niveles (FetchRouter)

| Motor | Implementación | Tiempo típico | Uso |
|---|---|---|---|
| **Fetcher** | Scrapling `Fetcher` (HTTP curl_cffi + suplantación TLS) | 0.4–3.9s | Por defecto, 80%+ de las URLs, HTTP puro sin navegador |
| **jina** | [Jina Reader](https://r.jina.ai/) SaaS (IP del lado del servidor) | 2.2–5.7s | Fallback cuando Fetcher es bloqueado |
| **StealthyFetcher** | Scrapling `StealthyFetcher` (Chrome patchright furtivo) + `solve_cloudflare` | 7.8s / 37s (CF) | Último recurso — el único que rompe Cloudflare Turnstile |
| DynamicFetcher | Scrapling `DynamicFetcher` (Playwright) | 4.9–6.9s | Sitios solo con renderizado JS, explícito `--backend dynamic` |

> La escalada es intencionada: Fetcher es rápido pero muere en Cloudflare; StealthyFetcher rompe CF pero 37s es demasiado lento para ser el valor por defecto. El enrutador prueba lo rápido primero y escala solo ante fallos.

### DomainKB — memoria por dominio

Recuerda qué motor funciona y cuál está bloqueado por dominio, para no probar y equivocarnos en cada captura.
- Almacenamiento: ruta según plataforma (macOS `~/Library/Application Support/deuseek/`, Linux XDG `~/.local/share/deuseek/`, Windows `%APPDATA%/deuseek/`)
- **TTL de 24h** — las entradas expiradas fuerzan un re-probe, de modo que los registros obsoletos se autocuran cuando un sitio cambia su configuración antibot
- `record_success` / `record_failure` escriben de vuelta automáticamente en cada captura

```bash
deuseek domain-kb              # lista todos los mapeos dominio→backend (con estado de expiración)
deuseek domain-kb --clear      # vacía la base de conocimiento
```

### BrowserPool — sesiones de navegador calientes

Stealthy/Dynamic arrancan un Chrome en frío en 2–4s. `BrowserPool` mantiene una sesión caliente y la reutiliza, bajando las capturas posteriores a ~1s. Inactivo 5 min → `shrink()` automático (se liberan ~200–500MB por instancia). `deuseek doctor` informa del estado caliente.

### Modo pipeline — `deuseek super`

El comando insignia encadena búsqueda → captura → extract en un pipeline real: en cuanto llega el primer resultado de búsqueda, la captura comienza y se solapa con las búsquedas restantes (~40% más rápido que en serie).

```bash
deuseek super "iPhone 16 review"
deuseek super "Python asyncio" --sources hackernews,web --stream   # JSON Lines en streaming
deuseek super "React 19" --extract-fields '{"title":"h1::text"}'   # + extracción estructurada
```

### Auto-escalada ante captchas

`fetch` escanea la salida de cada backend en busca de palabras clave de captcha (`环境异常 / 完成验证后即可继续访问 / 请输入验证码 / Cloudflare / Just a moment / Checking your browser`). Si coincide:
1. `errors[]` recibe una entrada `captcha_suspected: ...`
2. Si StealthyFetcher está disponible y no se había probado, **reintenta automáticamente** con `stealthy + solve_cloudflare=True`
3. Éxito → `auto_upgraded: stealthy+solve_cloudflare succeeded`; fallo → `auto_upgrade_failed`

Degradación elegante — el agente lee `errors` y decide en qué confiar; `markdown` siempre se preserva.

## 🤝 Convención de llamada para agentes

**Toma siempre el JSON de forma explícita** al llamar a deuseek desde un agente, para que el ajuste de tabla del TTY no pierda campos:

```bash
# Opción 1: --json por comando
deuseek search --json "..."
deuseek fetch  --json "<url>"

# Opción 2: variable de entorno (se aplica a todo el harness del agente — recomendado)
export DEUSEEK_FORCE_JSON=1
```

`not isatty()` cambia automáticamente a JSON, pero algunos terminales de agente (p. ej. Antigravity) asignan un PTY real por lo que `isatty()` es True y la autodetección falla — `--json` explícito o la variable de entorno es la garantía que siempre funciona.

Envelope de búsqueda estándar:
```json
{
  "query": "...",
  "ts": "ISO 8601 Z",
  "results": [{"source","title","url","content","ts","score","raw","cost"}],
  "errors":  [{"source","error","category"}]
}
```

## ⚙️ Preferencias

`~/.deuseek/preferences.toml` configura las fuentes por defecto, el idioma, el formato de salida y las sobrescrituras de `trust`.

```bash
deuseek preferences show     # ver la configuración actual
deuseek preferences edit     # editar con $EDITOR (Windows: notepad)
deuseek preferences reset    # restablecer (copia de seguridad en .bak)
deuseek preferences path     # imprime la ruta del archivo
```

Las claves de API (opcionales — el núcleo no necesita ninguna) van en `~/.deuseek/secrets.env` (`KEY=VALUE`; en POSIX avisa si los permisos son laxos).

## 🪟 Soporte de plataformas

| Plataforma | Estado | Notas |
|---|---|---|
| macOS | ✅ Principal | Todas las fuentes + los tres backends de captura probados |
| Linux | 🟡 Mejor esfuerzo | Funciona; el flujo de setup no gestiona `apt`/`pacman` automáticamente |
| WSL2 | 🟡 Mejor esfuerzo | Igual que Linux |
| Windows (PowerShell nativo) | 🟡 Experimental | `secrets_env` omite chmod POSIX; preferences edit usa notepad; setup github sugiere `winget install GitHub.cli`. **Abre un issue si tienes problemas.** |

`deuseek doctor` imprime la plataforma / versión de Python al principio — inclúyelo al reportar issues.

## 🏗️ Arquitectura

- **Patrón Adapter** — un adapter por fuente, implementando `AdapterBase` (`is_ready` + `search`)
- **Fan-out asíncrono** — `Dispatcher` usa `asyncio.gather` con aislamiento de errores por fuente (`unavailable` vs `failed`)
- **Registro YAML** — `sources.yml` es la única fuente de verdad (tier / adapter / trust / timeout / deps)
- **Router** — coincidencia de subcadenas query_hints + fusión `default_in_auto`, `MAX_SOURCES=5`, RSS restringido a consultas URL
- **Scorer** — `0.4*recency_norm + 0.6*source_trust` (los pesos suman 1.0, con assert); los timestamps ausentes por defecto a 0.5
- **Caché** — L1 en memoria + L2 en archivo; canonización de URL (elimina `utm_*`/`fbclid`/`gclid`/...) para que las variantes con rastreadores compartan una entrada
- **Contrato** — el validador de `SearchResult.content` en pydantic trunca a 500 caracteres globalmente; el texto completo permanece en `raw`

Archivos clave: `deuseek/sources.yml`, `deuseek/adapters/`, `deuseek/cli.py`, `deuseek/commands/fetch.py`, `deuseek/commands/super.py`, `deuseek/dispatcher.py`, `deuseek/fetch_router/router.py`, `deuseek/engines/`, `deuseek/convert/converter.py`, `deuseek/perf/`, `deuseek/native/`, `.claude-plugin/skills/deuseek/SKILL.md`.

## 🙏 Agradecimientos

deuseek se apoya en los hombros de gigantes:

- **[Scrapling](https://github.com/D4Vinci/Scrapling)** de [**D4Vinci**](https://github.com/D4Vinci) — el framework de captura furtiva / análisis adaptativo / Spider asíncrono que impulsa toda la capa de captura de deuseek (Fetcher / StealthyFetcher / DynamicFetcher / selectores adaptativos / Spider). El diseño de tres niveles para omisión de Cloudflare simplemente no existiría sin él. 🙏
- **[Daily-AC/deuseek](https://github.com/Daily-AC/deuseek)** (MIT) — el proyecto upstream sobre el que se construye este fork gratuito.
- Herramientas y librerías upstream: `yt-dlp`, `gh`, `rdt-cli`, `feedparser`, `httpx`, `pydantic`, `rich`, `click`, [Jina Reader](https://r.jina.ai/), `curl_cffi`, `patchright`, `Playwright`, `markdownify`, `html2text`, `lxml`.

## 🤝 Contribuir

¡Se aceptan contribuciones! Por favor:
1. Ejecuta `deuseek doctor` e incluye su salida al reportar problemas de fuentes/backend — el 90% de los "una fuente no funciona" es un binario upstream que falta.
2. Abre un issue primero para nuevas fuentes o cambios disruptivos.
3. Haz que los adapters cumplan `AdapterBase` (`is_ready` + `search` devolviendo `SearchResult`).

Consulta las [plantillas de issue](../.github/ISSUE_TEMPLATE/) para reportes de bugs, peticiones de funciones y solicitudes de nuevas fuentes.

## 📄 Licencia

MIT — ver [LICENSE](../LICENSE). Basado en [Daily-AC/deuseek](https://github.com/Daily-AC/deuseek) (MIT); se preserva el aviso de copyright upstream.
