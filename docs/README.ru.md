# deuseek

> Универсальный слой поиска и скрытого получения данных для любого AI-агента программирования. Обходите барьер WebSearch, получаете доступ к источникам, недоступным серверному поиску, и превращаете любой URL в чистый markdown — **100 % бесплатно, ключи API не требуются**.

> Слой получения данных работает на [Scrapling](https://github.com/D4Vinci/Scrapling) от **D4Vinci** — используется с благодарностью. 🙏

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Sources](https://img.shields.io/badge/sources-8%20free-success.svg)](#-supported-sources-all-free)
[![Status](https://img.shields.io/badge/status-1.0.0--alpha-orange.svg)](#)

🌐 [English](../README.md) | [العربية](README.ar.md) | [Español](README.es.md) | [Português (Brasil)](README.pt-BR.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | **Русский** | [한국어](README.ko.md)

---

## Содержание
- [✨ Почему deuseek?](#-почему-deuseek)
- [🤖 Работает с вашим агентом CLI](#-работает-с-вашим-агентом-cli)
- [🚀 Быстрый старт](#-быстрый-старт)
- [📦 Установка](#-установка)
- [📋 Команды](#-команды)
- [📚 Поддерживаемые источники (все бесплатные)](#-поддерживаемые-источники-все-бесплатные)
- [🥷 Архитектура движка получения данных](#-архитектура-движка-получения-данных)
- [🤝 Соглашение о вызове агента](#-соглашение-о-вызове-агента)
- [⚙️ Настройки](#️-настройки)
- [🪟 Поддержка платформ](#-поддержка-платформ)
- [🏗️ Архитектура](#️-архитектура)
- [🙏 Благодарности](#-благодарности)
- [🤝 Содействие](#-содействие)
- [📄 Лицензия](#-лицензия)

---

## ✨ Почему deuseek?

Инструмент `WebSearch` от Anthropic — это **серверный инструмент** (`web_search_20250305`), защищённый двумя проверками:
1. **Клиентский барьер** — регистрируется только для собственных / специфических конфигураций провайдеров.
2. **Барьер на стороне вышестоящего API** — вышестоящий API должен фактически *реализовывать* серверный инструмент. **OpenAI-совместимые релейные станции** (cliproxy, self-hosted шлюзы), которые лишь транслируют Claude API → OpenAI Chat Completions, **не реализуют его**, поэтому `WebSearch` незаметно завершается сбоем. Даже там, где он работает, он не может добраться до обсуждений HN в реальном времени, глубоких комментариев Reddit, статей WeChat 公众号 или технических видео Bilibili.

**deuseek решает это на стороне клиента** — единый CLI + Skill, который идёт напрямую к Algolia / `yt-dlp` / `gh` / Bilibili API / Sogou / DuckDuckGo, поэтому работает независимо от того, на какого провайдера API указывает ваш агент CLI.

### Ключевые преимущества

| | deuseek | Нативный `WebSearch` | Платные поисковые API |
|---|:---:|:---:|:---:|
| Работает на OpenAI-совместимых релейных/прокси-станциях | ✅ | ❌ | н/д |
| Добирается до HN / Reddit / WeChat / Bilibili / RSS | ✅ | ❌ | частично |
| Обход Cloudflare / анти-бот-защиты | ✅ | ❌ | н/д |
| URL → markdown с полным текстом | ✅ | только WebFetch | н/д |
| Стоимость | **бесплатно** | включено | 💲 платно |
| Время настройки | ~3 мин | — | — |

- 🚪 **Обходит двухуровневый барьер WebSearch** — работает на релейных/прокси-станциях, где `WebSearch` незаметно завершается сбоем, потому что вышестоящий API не реализует серверный инструмент.
- 🌐 **Добирается до вертикальных источников, недоступных серверному поиску** — обсуждения HN в реальном времени, глубокие ветки комментариев Reddit, статьи WeChat 公众号, технические видео Bilibili, RSS-ленты.
- 🆓 **100 % бесплатно, ноль ключей API для ядра** — DuckDuckGo, Algolia HN, Bilibili API, Sogou, `yt-dlp`, `gh`, `feedparser`. Без кредитной карты, без квот, без головной боли с ограничениями частоты запросов.
- 🥷 **Трёхуровневое скрытое получение данных с обходом Cloudflare** — `Fetcher` (curl_cffi HTTP) → Jina SaaS → `StealthyFetcher` (patchright Chrome) + `solve_cloudflare`. Единственный уровень, который взламывает Cloudflare Turnstile/Interstitial.
- 🧠 **DomainKB запоминает по доменам** — никаких проб и ошибок при каждом получении данных; TTL 24 ч принудительно перепроверяет, поэтому база знаний никогда не устаревает, когда сайт меняет свою анти-бот-конфигурацию.
- ⚡ **Конвейерный режим примерно на 40 % быстрее** — `asyncio` направляет результаты поиска сразу в получение данных (результаты не ждут самый медленный источник).
- 🛡️ **Автоматическое переключение при капче** — обнаруживает страницы с капчей (环境异常 / Cloudflare / Just a moment) и автоматически повторяет попытку с `stealthy + solve_cloudflare`, отображая ошибки, чтобы агент решал, чему доверять.
- 🔧 **Адаптивные самовосстанавливающиеся селекторы** — редизайны страниц не ломают извлечение (перемещение на основе similarity в Scrapling + `auto_save`).
- 🖥️ **Кроссплатформенность** — macOS как основная, Linux / WSL2 / Windows по возможности.
- 🧩 **Один CLI + один Skill, не зависит от агента по задумке** — встраивается в любой агент CLI примерно за 3 минуты; манифест `.claude-plugin/` делает его нативным Skill для CLI, совместимых с Claude Code, и обычным CLI на JSON для всего остального.
- 🔍 **Прозрачность** — тегирование `cost="free|paid"`, структурированные `errors[]` и сохранение исходных `raw`-полей, чтобы агенты могли получить полный текст при необходимости.

## 🤖 Работает с вашим агентом CLI

deuseek — это стандартный CLI, который выдаёт JSON — **любой агент, способный запускать команды оболочки, может им пользоваться**. Манифест `.claude-plugin/` добавляет нативную интеграцию Skill для CLI, совместимых с Claude Code.

| Агент-инструмент | Как использовать deuseek |
|---|---|
| **Claude Code** (Anthropic) | `/plugin marketplace add xyva-yuangui/deuseek` → `/plugin install deuseek`, затем *"используйте deuseek для поиска ..."*. Также работает как обычный CLI. |
| **Zcode** | Вызывайте `deuseek search --json "..."` / `deuseek fetch --json <url>` из оболочки или загрузите Skill. |
| **Codex** (OpenAI Codex CLI) | Запускайте `deuseek` как подпроцесс и разбирайте JSON-конверт. |
| **Reasonix** | JSON через подпроцесс или загрузите как skill. |
| **OpenClaw** | Запускайте `deuseek` как команду оболочки и разбирайте JSON. |
| **Hermes** | JSON через подпроцесс. |
| **Antigravity** (`agy`) | `agy plugin install` (распознаёт `.claude-plugin/`). |
| Любой другой агент | Запускайте `deuseek <command> --json` как команду оболочки, разбирайте JSON-конверт. |

> Поскольку контракт — «CLI, который выводит JSON», deuseek **не зависит от конкретного агента** — вам никогда не придётся ждать, пока мы «поддержим» ваш инструмент. Если ваш агент может породить процесс, он может использовать deuseek уже сегодня.

## 🚀 Быстрый старт

```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
deuseek init                   # writes default ~/.deuseek/preferences.toml
deuseek search "vibe coding"   # web + hackernews work zero-config
```

Разблокируйте источники, которым требуется вышестоящий инструмент:

```bash
deuseek setup youtube     # pip install yt-dlp
deuseek setup github      # brew install gh (macOS) / winget (Windows)
deuseek setup reddit      # uv tool install rdt-cli && rdt login
```

## 📦 Установка

**Вариант A — uv (рекомендуется):**
```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
```

**Вариант B — pip (редактируемая dev-установка):**
```bash
git clone https://github.com/xyva-yuangui/deuseek.git
cd deuseek
pip install -e ".[dev]"
```

**Вариант C — однострочный скрипт (macOS/Linux, настраивает venv + браузеры):**
```bash
bash install.sh
```

**Дополнительные движки получения данных** (для обхода Cloudflare и рендеринга JS):
```bash
pip install "deuseek[fetchers]"          # patchright + curl_cffi + msgspec + protego
patchright install chromium               # stealth Chrome (Cloudflare bypass)
playwright install chromium               # JS rendering
```

## 📋 Команды

| Команда | Что делает |
|---|---|
| `deuseek search "<query>"` | Многоисточниковый поиск (SERP: метаданные + URL; контент ≤500 символов) |
| `deuseek search --on hackernews,web "..."` | Ограничить конкретными источниками |
| `deuseek search --mode quick "..."` | Только web + hackernews |
| `deuseek search --mode deep "..."` | Все готовые источники |
| `deuseek search --json "..."` | Явный вывод JSON |
| `deuseek search --no-cache "..."` | Пропустить кэш, принудительно обновить |
| **`deuseek fetch <url>`** | **URL → markdown с полным текстом** (трёхуровневая маршрутизация Scrapling + DomainKB) |
| `deuseek fetch <url> --backend jina` | Принудительно Jina Reader SaaS (ноль локальных зависимостей) |
| `deuseek fetch <url> --backend stealthy --solve-cloudflare` | Принудительно stealth Chrome + обход CF |
| `deuseek fetch <url> --backend dynamic` | Принудительно рендеринг JS через Playwright |
| `deuseek fetch <url> --full` | Преобразовать всю страницу (по умолчанию: только основное содержимое) |
| **`deuseek super "<query>"`** | **Полный цикл**: многоисточниковый поиск → скрытое получение → (опционально) извлечение, потоковый конвейер (~на 40 % быстрее) |
| `deuseek crawl <url>` | Многостраничный обход Spider (асинхронный Spider в Scrapling + checkpoint) |
| `deuseek extract <url>` | Адаптивное структурированное извлечение (CSS/XPath + самовосстанавливающееся перемещение) |
| `deuseek domain-kb` | Просмотреть/очистить базу знаний domain→backend (`--clear`) |
| `deuseek init` | Записать `~/.deuseek/preferences.toml` по умолчанию |
| `deuseek sources` | Список всех источников + готовность (`--probe` для проверки) |
| `deuseek setup <source>` | Направляемая настройка источника |
| `deuseek doctor` | Проверка работоспособности (источники + бэкенды получения + BrowserPool) |
| `deuseek check-update` | Сравнить с GitHub Releases |
| `deuseek preferences {show,edit,reset,path}` | Пользовательские настройки |

## 📚 Поддерживаемые источники (все бесплатные)

| Источник | Уровень | Зависимость | Примечания |
|---|---|---|---|
| web | ✅ ready | `ddgs` (pip) | Общий веб-поиск DuckDuckGo |
| hackernews | ✅ ready | нет | Algolia HN API, без настройки |
| youtube | ✅ ready | `yt-dlp` (pip) | `deuseek setup youtube` |
| github | ✅ ready | `gh` CLI + `gh auth login` | `deuseek setup github` |
| rss | ✅ ready | встроенный `feedparser` | **запрос должен быть URL ленты** |
| wechat | ✅ ready | нет | WeChat 公众号 — бесплатный поиск Sogou (опциональное усиление скрытности Scrapling) |
| bilibili | ✅ ready | нет | Официальный поисковый API Bilibili |
| reddit | 🟡 one_step | `rdt-cli` + `rdt login` | `deuseek setup reddit` |

> **Полный текст?** Источники, вышестоящий API которых возвращает полный контент, сохраняют исходный payload в `result.raw` (например, `raw["item_html"]` у wechat). Для всего остального выполните `deuseek fetch <url>`.

## 🥷 Архитектура движка получения данных

`deuseek fetch` / `super` / `crawl` / `extract` построены на [Scrapling](https://github.com/D4Vinci/Scrapling) — одна зависимость, покрывающая HTTP-получение, скрытый браузер, адаптивный парсинг и асинхронный Spider.

### Трёхуровневая маршрутизация (FetchRouter)

| Движок | Реализация | Типичное время | Применение |
|---|---|---|---|
| **Fetcher** | Scrapling `Fetcher` (curl_cffi HTTP + имитация TLS) | 0.4–3.9s | По умолчанию, 80 %+ URL, чистый HTTP без браузера |
| **jina** | [Jina Reader](https://r.jina.ai/) SaaS (IP на стороне сервера) | 2.2–5.7s | Запасной, когда Fetcher заблокирован |
| **StealthyFetcher** | Scrapling `StealthyFetcher` (patchright stealth Chrome) + `solve_cloudflare` | 7.8s / 37s (CF) | Последнее средство — единственный, который взламывает Cloudflare Turnstile |
| DynamicFetcher | Scrapling `DynamicFetcher` (Playwright) | 4.9–6.9s | Только JS-рендер-сайты, явный `--backend dynamic` |

> Эскалация намеренная: Fetcher быстрый, но «умирает» на Cloudflare; StealthyFetcher взламывает CF, но 37 с — слишком медленно для варианта по умолчанию. Маршрутизатор сначала пробует быстрый и эскалирует только при сбое.

### DomainKB — память по доменам

Запоминает, какой движок работает, а какой заблокирован по каждому домену, поэтому нам не приходится пробовать и ошибаться при каждом получении данных.
- Хранилище: платформенный путь (macOS `~/Library/Application Support/deuseek/`, Linux XDG `~/.local/share/deuseek/`, Windows `%APPDATA%/deuseek/`)
- **TTL 24 ч** — устаревшие записи принудительно перепроверяются, поэтому старые записи самовосстанавливаются, когда сайт меняет свою анти-бот-конфигурацию
- `record_success` / `record_failure` автоматически записывают обратно при каждом получении данных

```bash
deuseek domain-kb              # list all domain→backend mappings (with expired status)
deuseek domain-kb --clear      # wipe the knowledge base
```

### BrowserPool — горячие сеансы браузера

Stealthy/Dynamic делают холодный старт Chrome за 2–4 с. `BrowserPool` хранит горячий сеанс и переиспользует его, снижая последующие получения данных до ~1 с. При простое 5 мин → авто-`shrink()` (~200–500 МБ на экземпляр освобождается). `deuseek doctor` сообщает о горячем состоянии.

### Конвейерный режим — `deuseek super`

Флагманская команда объединяет поиск → получение → извлечение в настоящий конвейер: как только приходит первый результат поиска, начинается получение и перекрывает оставшиеся поиски (~на 40 % быстрее последовательного выполнения).

```bash
deuseek super "iPhone 16 review"
deuseek super "Python asyncio" --sources hackernews,web --stream   # streaming JSON Lines
deuseek super "React 19" --extract-fields '{"title":"h1::text"}'   # + structured extraction
```

### Автоматическое переключение при капче

`fetch` сканирует вывод каждого бэкенда на ключевые слова капчи (`环境异常 / 完成验证后即可继续访问 / 请输入验证码 / Cloudflare / Just a moment / Checking your browser`). При совпадении:
1. `errors[]` получает запись `captcha_suspected: ...`
2. Если StealthyFetcher доступен и не был опробован, он **автоматически повторяет попытку** с `stealthy + solve_cloudflare=True`
3. Успех → `auto_upgraded: stealthy+solve_cloudflare succeeded`; сбой → `auto_upgrade_failed`

Корректная деградация — агент читает `errors` и решает, чему доверять; `markdown` всегда сохраняется.

## 🤝 Соглашение о вызове агента

**Всегда запрашивайте JSON явно** при вызове deuseek из агента, чтобы перенос таблицы в TTY не терял поля:

```bash
# Option 1: --json per command
deuseek search --json "..."
deuseek fetch  --json "<url>"

# Option 2: env var (applies to the whole agent harness — recommended)
export DEUSEEK_FORCE_JSON=1
```

`not isatty()` автоматически переключается на JSON, но некоторые терминалы агентов (например, Antigravity) выделяют реальный PTY, поэтому `isatty()` возвращает True и автоопределение не срабатывает — явный `--json` или переменная окружения — это гарантия, что сработает всегда.

Стандартный конверт поиска:
```json
{
  "query": "...",
  "ts": "ISO 8601 Z",
  "results": [{"source","title","url","content","ts","score","raw","cost"}],
  "errors":  [{"source","error","category"}]
}
```

## ⚙️ Настройки

`~/.deuseek/preferences.toml` настраивает источники по умолчанию, язык, формат вывода и переопределения `trust`.

```bash
deuseek preferences show     # view current config
deuseek preferences edit     # edit with $EDITOR (Windows fallback: notepad)
deuseek preferences reset    # reset (backs up to .bak)
deuseek preferences path     # print the file path
```

Ключи API (опционально — ядру они не нужны) помещаются в `~/.deuseek/secrets.env` (`KEY=VALUE`; POSIX предупреждает о слишком широких правах доступа).

## 🪟 Поддержка платформ

| Платформа | Статус | Примечания |
|---|---|---|
| macOS | ✅ Основная | Все источники + все три бэкенда получения протестированы |
| Linux | 🟡 По возможности | Работает; процесс настройки не обрабатывает `apt`/`pacman` автоматически |
| WSL2 | 🟡 По возможности | То же, что и Linux |
| Windows (нативный PowerShell) | 🟡 Экспериментальная | `secrets_env` пропускает POSIX chmod; редактирование настроек использует notepad как запасной вариант; setup github предлагает `winget install GitHub.cli`. **Пожалуйста, откройте issue, если столкнётесь с проблемами.** |

`deuseek doctor` выводит платформу / версию Python вверху — прилагайте это при подаче issue.

## 🏗️ Архитектура

- **Паттерн адаптер** — по одному адаптеру на источник, реализующему `AdapterBase` (`is_ready` + `search`)
- **Асинхронный fan-out** — `Dispatcher` использует `asyncio.gather` с изоляцией ошибок по каждому источнику (`unavailable` против `failed`)
- **Реестр YAML** — `sources.yml` — единый источник истины (tier / adapter / trust / timeout / deps)
- **Маршрутизатор** — слияние подстрок query_hints + `default_in_auto`, `MAX_SOURCES=5`, RSS ограничен запросами по URL
- **Оценщик** — `0.4*recency_norm + 0.6*source_trust` (веса в сумме дают 1.0, проверяется ассертами); отсутствующие временные метки по умолчанию 0.5
- **Кэш** — память L1 + файл L2; канонизация URL (вырезает `utm_*`/`fbclid`/`gclid`/...), поэтому варианты с трекерами делят одну запись
- **Контракт** — валидатор pydantic `SearchResult.content` глобально обрезает до 500 символов; полный текст остаётся в `raw`

Ключевые файлы: `deuseek/sources.yml`, `deuseek/adapters/`, `deuseek/cli.py`, `deuseek/commands/fetch.py`, `deuseek/commands/super.py`, `deuseek/dispatcher.py`, `deuseek/fetch_router/router.py`, `deuseek/engines/`, `deuseek/convert/converter.py`, `deuseek/perf/`, `deuseek/native/`, `.claude-plugin/skills/deuseek/SKILL.md`.

## 🙏 Благодарности

deuseek стоит на плечах гигантов:

- **[Scrapling](https://github.com/D4Vinci/Scrapling)** от [**D4Vinci**](https://github.com/D4Vinci) — фреймворк скрытого получения данных / адаптивного парсинга / асинхронного Spider, на котором работает весь слой получения данных deuseek (Fetcher / StealthyFetcher / DynamicFetcher / адаптивные селекторы / Spider). Трёхуровневая конструкция обхода Cloudflare просто не существовала бы без него. 🙏
- **[Daily-AC/deuseek](https://github.com/Daily-AC/deuseek)** (MIT) — вышестоящий проект, на котором основан этот бесплатный форк.
- Вышестоящие инструменты и библиотеки: `yt-dlp`, `gh`, `rdt-cli`, `feedparser`, `httpx`, `pydantic`, `rich`, `click`, [Jina Reader](https://r.jina.ai/), `curl_cffi`, `patchright`, `Playwright`, `markdownify`, `html2text`, `lxml`.

## 🤝 Содействие

Вклад приветствуется! Пожалуйста:
1. Запустите `deuseek doctor` и приложите его вывод при сообщении о проблемах с источниками/бэкендами — 90 % случаев «источник не работает» — это отсутствующий вышестоящий бинарник.
2. Сначала откройте issue для новых источников или ломающих изменений.
3. Сохраняйте адаптеры, соответствующие `AdapterBase` (`is_ready` + `search`, возвращающий `SearchResult`).

См. [шаблоны issue](../.github/ISSUE_TEMPLATE/) для отчётов об ошибках, запросов функций и запросов новых источников.

## 📄 Лицензия

MIT — см. [LICENSE](../LICENSE). Основан на [Daily-AC/deuseek](https://github.com/Daily-AC/deuseek) (MIT); уведомление об авторских правах вышестоящего проекта сохранено.
