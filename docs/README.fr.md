# deuseek

> La couche universelle de recherche et de récupération furtive pour tout agent de codage IA. Contournez le verrouillage WebSearch, accédez aux sources inaccessibles à la recherche côté serveur, et transformez n'importe quelle URL en markdown propre — **100% gratuit, aucune clé API requise**.

> Couche de récupération propulsée par [Scrapling](https://github.com/D4Vinci/Scrapling) par **D4Vinci** — utilisée avec gratitude. 🙏

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Sources](https://img.shields.io/badge/sources-8%20free-success.svg)](#-sources-prises-en-charge-toutes-gratuites)
[![Status](https://img.shields.io/badge/status-1.0.0--alpha-orange.svg)](#)

🌐 [English](../README.md) | [العربية](README.ar.md) | [Español](README.es.md) | [Português (Brasil)](README.pt-BR.md) | **Français** | [Deutsch](README.de.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [Русский](README.ru.md) | [한국어](README.ko.md)

---

## Table des matières
- [✨ Pourquoi deuseek?](#-pourquoi-deuseek)
- [🤖 Fonctionne avec votre agent CLI](#-fonctionne-avec-votre-agent-cli)
- [🚀 Démarrage rapide](#-démarrage-rapide)
- [📦 Installation](#-installation)
- [📋 Commandes](#-commandes)
- [📚 Sources prises en charge (toutes gratuites)](#-sources-prises-en-charge-toutes-gratuites)
- [🥷 Architecture du moteur de fetch](#-architecture-du-moteur-de-fetch)
- [🤝 Convention d'appel par l'agent](#-convention-dappel-par-lagent)
- [⚙️ Préférences](#️-préférences)
- [🪟 Prise en charge des plateformes](#-prise-en-charge-des-plateformes)
- [🏗️ Architecture](#️-architecture)
- [🙏 Remerciements](#-remerciements)
- [🤝 Contribuer](#-contribuer)
- [📄 Licence](#-licence)

---

## ✨ Pourquoi deuseek?

Le `WebSearch` d'Anthropic est un **outil côté serveur** (`web_search_20250305`) placé derrière deux verrous :
1. **Verrou client** — enregistré uniquement pour les configurations first-party / fournisseurs spécifiques.
2. **Verrou amont** — l'API amont doit réellement *implémenter* l'outil serveur. Les **stations relais compatibles OpenAI** (cliproxy, anyrouter, passerelles auto-hébergées) qui se contentent de traduire Claude API → OpenAI Chat Completions **ne l'implémentent pas**, donc `WebSearch` échoue silencieusement. Même là où il fonctionne, il ne peut pas atteindre les fils de discussion en temps réel de HN, les commentaires profonds de Reddit, les articles WeChat 公众号, ou les vidéos techniques de Bilibili.

**deuseek corrige cela côté client** — un seul CLI + Skill qui va directement à Algolia / `yt-dlp` / `gh` / l'API Bilibili / Sogou / DuckDuckGo, de sorte qu'il fonctionne quel que soit le fournisseur d'API vers lequel votre agent CLI pointe.

### Avantages clés

| | deuseek | `WebSearch` natif | API de recherche payantes |
|---|:---:|:---:|:---:|
| Fonctionne sur les stations relais/proxy compatibles OpenAI | ✅ | ❌ | n/a |
| Atteint HN / Reddit / WeChat / Bilibili / RSS | ✅ | ❌ | partiel |
| Contournement Cloudflare / anti-bot | ✅ | ❌ | n/a |
| URL → markdown plein texte | ✅ | WebFetch uniquement | n/a |
| Coût | **gratuit** | inclus | 💲 payant |
| Temps de mise en place | ~3 min | — | — |

- 🚪 **Contourne le verrou WebSearch à deux niveaux** — fonctionne sur les stations relais/proxy là où `WebSearch` échoue silencieusement parce que l'amont n'implémente pas l'outil serveur.
- 🌐 **Atteint les sources verticales que la recherche côté serveur ne peut pas** — discussions en temps réel de HN, fils de commentaires profonds de Reddit, articles WeChat 公众号, vidéos techniques de Bilibili, flux RSS.
- 🆓 **100% gratuit, zéro clé API pour le cœur** — DuckDuckGo, Algolia HN, API Bilibili, Sogou, `yt-dlp`, `gh`, `feedparser`. Aucune carte bancaire, aucun quota, aucune galère de limite de débit.
- 🥷 **Récupération furtive à trois niveaux avec contournement Cloudflare** — `Fetcher` (HTTP curl_cffi) → Jina SaaS → `StealthyFetcher` (Chrome patchright) + `solve_cloudflare`. Le seul niveau qui vient à bout de Cloudflare Turnstile/Interstitial.
- 🧠 **DomainKB mémorise par domaine** — fini les essais-erreurs à chaque récupération ; un TTL de 24h force une re-probe, de sorte que la base de connaissances ne devient jamais obsolète quand un site modifie sa configuration anti-bot.
- ⚡ **Mode pipeline ~40% plus rapide** — `asyncio` envoie les résultats de recherche directement au fetch (les résultats n'attendent pas la source la plus lente).
- 🛡️ **Mise à niveau automatique en cas de captcha** — détecte les pages de captcha (环境异常 / Cloudflare / Just a moment) et réessaye automatiquement avec `stealthy + solve_cloudflare`, en exposant les erreurs pour que l'agent décide à quoi se fier.
- 🔧 **Sélecteurs adaptatifs et auto-réparateurs** — les refontes de page ne cassent pas l'extraction (relocalisation par similarité Scrapling + `auto_save`).
- 🖥️ **Multiplateforme** — macOS en principal, Linux / WSL2 / Windows au mieux.
- 🧩 **Un CLI + un Skill, agnostique à l'agent par conception** — s'intègre à n'importe quel agent CLI en ~3 minutes ; un manifeste `.claude-plugin/` en fait un Skill natif pour les CLI compatibles Claude Code, et un simple CLI JSON pour tout le reste.
- 🔍 **Transparent** — marquage `cost="free|paid"`, `errors[]` structurés, et charges utiles `raw` d'origine conservées pour que les agents puissent récupérer le texte complet quand besoin.

## 🤖 Fonctionne avec votre agent CLI

deuseek est un CLI standard qui émet du JSON — **tout agent capable de lancer des commandes shell peut l'utiliser**. Le manifeste `.claude-plugin/` ajoute une intégration Skill native pour les CLI compatibles Claude Code.

| Outil d'agent | Comment utiliser deuseek |
|---|---|
| **Claude Code** (Anthropic) | `/plugin marketplace add xyva-yuangui/deuseek` → `/plugin install deuseek`, puis *« utilise deuseek pour chercher ... »*. Fonctionne aussi comme simple CLI. |
| **Zcode** | Appelez `deuseek search --json "..."` / `deuseek fetch --json <url>` depuis le shell, ou chargez le Skill. |
| **Codex** (OpenAI Codex CLI) | Lancez `deuseek` comme sous-processus et analysez l'enveloppe JSON. |
| **Reasonix** | JSON en sous-processus, ou chargez comme skill. |
| **OpenClaw** | Lancez `deuseek` comme commande shell et analysez le JSON. |
| **Hermes** | JSON en sous-processus. |
| **Antigravity** (`agy`) | `agy plugin install` (reconnaît `.claude-plugin/`). |
| Tout autre agent | Lancez `deuseek <commande> --json` comme commande shell, analysez l'enveloppe JSON. |

> Comme le contrat est « un CLI qui affiche du JSON », deuseek est **agnostique de l'agent** — vous n'avez jamais à attendre que nous « supportions » votre outil. Si votre agent peut lancer un processus, il peut utiliser deuseek aujourd'hui.

## 🚀 Démarrage rapide

```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
deuseek init                   # writes default ~/.deuseek/preferences.toml
deuseek search "vibe coding"   # web + hackernews work zero-config
```

Débloquez les sources nécessitant un outil amont :

```bash
deuseek setup youtube     # pip install yt-dlp
deuseek setup github      # brew install gh (macOS) / winget (Windows)
deuseek setup reddit      # uv tool install rdt-cli && rdt login
```

## 📦 Installation

**Option A — uv (recommandé) :**
```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
```

**Option B — pip (installation en mode développement éditable) :**
```bash
git clone https://github.com/xyva-yuangui/deuseek.git
cd deuseek
pip install -e ".[dev]"
```

**Option C — script en une ligne (macOS/Linux, met en place le venv + les navigateurs) :**
```bash
bash install.sh
```

**Moteurs de fetch optionnels** (pour le contournement Cloudflare et le rendu JS) :
```bash
pip install "deuseek[fetchers]"          # patchright + curl_cffi + msgspec + protego
patchright install chromium               # stealth Chrome (Cloudflare bypass)
playwright install chromium               # JS rendering
```

## 📋 Commandes

| Commande | Ce qu'elle fait |
|---|---|
| `deuseek search "<query>"` | Recherche multi-sources (SERP : métadonnées + URL ; contenu ≤500 caractères) |
| `deuseek search --on hackernews,web "..."` | Restreindre à des sources spécifiques |
| `deuseek search --mode quick "..."` | Uniquement web + hackernews |
| `deuseek search --mode deep "..."` | Toutes les sources prêtes |
| `deuseek search --json "..."` | Sortie JSON explicite |
| `deuseek search --no-cache "..."` | Ignorer le cache, forcer le rafraîchissement |
| **`deuseek fetch <url>`** | **URL → markdown plein texte** (routage à trois niveaux Scrapling + DomainKB) |
| `deuseek fetch <url> --backend jina` | Forcer Jina Reader SaaS (zéro dépendance locale) |
| `deuseek fetch <url> --backend stealthy --solve-cloudflare` | Forcer Chrome furtif + contournement CF |
| `deuseek fetch <url> --backend dynamic` | Forcer le rendu JS Playwright |
| `deuseek fetch <url> --full` | Convertir la page entière (par défaut : contenu principal uniquement) |
| **`deuseek super "<query>"`** | **Bout en bout** : recherche multi-sources → fetch furtif → (optionnel) extract, pipeline en flux (~40% plus rapide) |
| `deuseek crawl <url>` | Exploration Spider multi-pages (Scrapling async Spider + checkpoint) |
| `deuseek extract <url>` | Extraction structurée adaptative (CSS/XPath + relocalisation auto-réparatrice) |
| `deuseek domain-kb` | Voir/vider la base de connaissances domaine→backend (`--clear`) |
| `deuseek init` | Écrire le `~/.deuseek/preferences.toml` par défaut |
| `deuseek sources` | Lister toutes les sources + état de préparation (`--probe` pour tester) |
| `deuseek setup <source>` | Configuration guidée d'une source |
| `deuseek doctor` | Vérification de santé (sources + backends de fetch + BrowserPool) |
| `deuseek check-update` | Comparer aux GitHub Releases |
| `deuseek preferences {show,edit,reset,path}` | Préférences utilisateur |

## 📚 Sources prises en charge (toutes gratuites)

| Source | Niveau | Dépendance | Notes |
|---|---|---|---|
| web | ✅ ready | `ddgs` (pip) | Recherche web générale DuckDuckGo |
| hackernews | ✅ ready | aucune | API Algolia HN, sans configuration |
| youtube | ✅ ready | `yt-dlp` (pip) | `deuseek setup youtube` |
| github | ✅ ready | CLI `gh` + `gh auth login` | `deuseek setup github` |
| rss | ✅ ready | `feedparser` intégré | **la requête doit être une URL de flux** |
| wechat | ✅ ready | aucune | WeChat 公众号 — recherche Sogou gratuite (boost furtif Scrapling optionnel) |
| bilibili | ✅ ready | aucune | API de recherche officielle Bilibili |
| reddit | 🟡 one_step | `rdt-cli` + `rdt login` | `deuseek setup reddit` |

> **Texte complet ?** Les sources dont l'amont renvoie le contenu complet conservent la charge utile d'origine dans `result.raw` (ex. `raw["item_html"]` de wechat). Pour tout le reste, lancez `deuseek fetch <url>`.

## 🥷 Architecture du moteur de fetch

`deuseek fetch` / `super` / `crawl` / `extract` sont construits sur [Scrapling](https://github.com/D4Vinci/Scrapling) — une dépendance couvrant la récupération HTTP, le navigateur furtif, l'analyse adaptative et le Spider asynchrone.

### Routage à trois niveaux (FetchRouter)

| Moteur | Implémentation | Temps typique | Usage |
|---|---|---|---|
| **Fetcher** | Scrapling `Fetcher` (HTTP curl_cffi + usurpation TLS) | 0.4–3.9s | Par défaut, 80%+ des URL, HTTP pur sans navigateur |
| **jina** | SaaS [Jina Reader](https://r.jina.ai/) (IP côté serveur) | 2.2–5.7s | Fallback quand Fetcher est bloqué |
| **StealthyFetcher** | Scrapling `StealthyFetcher` (Chrome furtif patchright) + `solve_cloudflare` | 7.8s / 37s (CF) | Recours ultime — le seul qui vient à bout de Cloudflare Turnstile |
| DynamicFetcher | Scrapling `DynamicFetcher` (Playwright) | 4.9–6.9s | Sites à rendu JS uniquement, `--backend dynamic` explicite |

> L'escalade est intentionnelle : Fetcher est rapide mais meurt sur Cloudflare ; StealthyFetcher vient à bout de CF mais 37s est trop lent pour être le défaut. Le routeur essaie d'abord le rapide et n'escalade qu'en cas d'échec.

### DomainKB — mémoire par domaine

Mémorise quel moteur fonctionne et lequel est bloqué par domaine, afin de ne pas faire d'essais-erreurs à chaque récupération.
- Stockage : chemin selon la plateforme (macOS `~/Library/Application Support/deuseek/`, Linux XDG `~/.local/share/deuseek/`, Windows `%APPDATA%/deuseek/`)
- **TTL de 24h** — les entrées expirées forcent une re-probe, de sorte que les enregistrements obsolètes s'auto-réparent quand un site modifie sa configuration anti-bot
- `record_success` / `record_failure` réécrivent automatiquement à chaque récupération

```bash
deuseek domain-kb              # list all domain→backend mappings (with expired status)
deuseek domain-kb --clear      # wipe the knowledge base
```

### BrowserPool — sessions de navigateur préchauffées

Stealthy/Dynamic démarrent un Chrome à froid en 2–4s. `BrowserPool` garde une session préchauffée et la réutilise, ramenant les récupérations suivantes à ~1s. Inactif 5 min → `shrink()` automatique (~200–500MB/instance libérés). `deuseek doctor` signale l'état préchauffé.

### Mode pipeline — `deuseek super`

La commande phare enchaîne recherche → fetch → extract dans un véritable pipeline : dès qu'arrive le premier résultat de recherche, la récupération commence et chevauche les recherches restantes (~40% plus rapide qu'en série).

```bash
deuseek super "iPhone 16 review"
deuseek super "Python asyncio" --sources hackernews,web --stream   # streaming JSON Lines
deuseek super "React 19" --extract-fields '{"title":"h1::text"}'   # + structured extraction
```

### Mise à niveau automatique en cas de captcha

`fetch` analyse la sortie de chaque backend à la recherche de mots-clés de captcha (`环境异常 / 完成验证后即可继续访问 / 请输入验证码 / Cloudflare / Just a moment / Checking your browser`). En cas de correspondance :
1. `errors[]` reçoit une entrée `captcha_suspected: ...`
2. Si StealthyFetcher est disponible et n'a pas été essayé, il **réessaie automatiquement** avec `stealthy + solve_cloudflare=True`
3. Succès → `auto_upgraded: stealthy+solve_cloudflare succeeded` ; échec → `auto_upgrade_failed`

Dégradation progressive — l'agent lit `errors` et décide à quoi se fier ; `markdown` est toujours conservé.

## 🤝 Convention d'appel par l'agent

**Prenez toujours le JSON explicitement** quand vous appelez deuseek depuis un agent, afin que le retour à la ligne des tables TTY ne perde pas de champs :

```bash
# Option 1: --json per command
deuseek search --json "..."
deuseek fetch  --json "<url>"

# Option 2: env var (applies to the whole agent harness — recommended)
export DEUSEEK_FORCE_JSON=1
```

`not isatty()` bascule automatiquement en JSON, mais certains terminaux d'agent (ex. Antigravity) allouent un véritable PTY donc `isatty()` vaut True et la détection automatique échoue — `--json` explicite ou la variable d'env est la garantie qui fonctionne toujours.

Enveloppe de recherche standard :
```json
{
  "query": "...",
  "ts": "ISO 8601 Z",
  "results": [{"source","title","url","content","ts","score","raw","cost"}],
  "errors":  [{"source","error","category"}]
}
```

## ⚙️ Préférences

`~/.deuseek/preferences.toml` configure les sources par défaut, la langue, le format de sortie et les surcharges `trust`.

```bash
deuseek preferences show     # view current config
deuseek preferences edit     # edit with $EDITOR (Windows fallback: notepad)
deuseek preferences reset    # reset (backs up to .bak)
deuseek preferences path     # print the file path
```

Les clés API (optionnelles — le cœur n'en a besoin d'aucune) vont dans `~/.deuseek/secrets.env` (`KEY=VALUE` ; POSIX avertit en cas de permissions trop lâches).

## 🪟 Prise en charge des plateformes

| Plateforme | État | Notes |
|---|---|---|
| macOS | ✅ Principal | Toutes les sources + les trois backends de fetch testés |
| Linux | 🟡 Au mieux | Fonctionne ; le flux de configuration ne gère pas automatiquement `apt`/`pacman` |
| WSL2 | 🟡 Au mieux | Identique à Linux |
| Windows (PowerShell natif) | 🟡 Expérimental | `secrets_env` ignore le chmod POSIX ; preferences edit utilise notepad en repli ; setup github suggère `winget install GitHub.cli`. **Veuillez ouvrir une issue si vous rencontrez des problèmes.** |

`deuseek doctor` affiche la plateforme / la version de Python en haut — joignez-le lors de la création d'issues.

## 🏗️ Architecture

- **Patron Adapter** — un adaptateur par source, implémentant `AdapterBase` (`is_ready` + `search`)
- **Fan-out asynchrone** — `Dispatcher` utilise `asyncio.gather` avec isolation d'erreur par source (`unavailable` vs `failed`)
- **Registre YAML** — `sources.yml` est l'unique source de vérité (tier / adapter / trust / timeout / deps)
- **Routeur** — fusion par sous-chaîne de query_hints + `default_in_auto`, `MAX_SOURCES=5`, RSS conditionné aux requêtes URL
- **Scoreur** — `0.4*recency_norm + 0.6*source_trust` (les poids somment à 1.0, vérifié par assert) ; les horodatages manquants valent 0.5 par défaut
- **Cache** — L1 mémoire + L2 fichier ; canonicalisation d'URL (retire `utm_*`/`fbclid`/`gclid`/...) de sorte que les variantes de tracker partagent une seule entrée
- **Contrat** — le validateur pydantic `SearchResult.content` tronque à 500 caractères globalement ; le texte complet reste dans `raw`

Fichiers clés : `deuseek/sources.yml`, `deuseek/adapters/`, `deuseek/cli.py`, `deuseek/commands/fetch.py`, `deuseek/commands/super.py`, `deuseek/dispatcher.py`, `deuseek/fetch_router/router.py`, `deuseek/engines/`, `deuseek/convert/converter.py`, `deuseek/perf/`, `deuseek/native/`, `.claude-plugin/skills/deuseek/SKILL.md`.

## 🙏 Remerciements

deuseek se tient sur les épaules de géants :

- **[Scrapling](https://github.com/D4Vinci/Scrapling)** par [**D4Vinci**](https://github.com/D4Vinci) — le framework de récupération furtive / d'analyse adaptative / de Spider asynchrone qui propulse toute la couche de fetch de deuseek (Fetcher / StealthyFetcher / DynamicFetcher / sélecteurs adaptatifs / Spider). Le design à trois niveaux de contournement Cloudflare n'existerait tout simplement pas sans lui. 🙏
- **[Daily-AC/deuseek](https://github.com/Daily-AC/deuseek)** (MIT) — le projet amont sur lequel ce fork gratuit se construit.
- Outils et bibliothèques amont : `yt-dlp`, `gh`, `rdt-cli`, `feedparser`, `httpx`, `pydantic`, `rich`, `click`, [Jina Reader](https://r.jina.ai/), `curl_cffi`, `patchright`, `Playwright`, `markdownify`, `html2text`, `lxml`.

## 🤝 Contribuer

Les contributions sont les bienvenues ! Veuillez :
1. Lancer `deuseek doctor` et inclure sa sortie lors du signalement de problèmes de source/backend — 90% des « une source ne fonctionne pas » sont dus à un binaire amont manquant.
2. Ouvrir d'abord une issue pour les nouvelles sources ou les changements cassants.
3. Garder les adaptateurs conformes à `AdapterBase` (`is_ready` + `search` renvoyant un `SearchResult`).

Voir les [modèles d'issue](../.github/ISSUE_TEMPLATE/) pour les rapports de bug, les demandes de fonctionnalités et les demandes de nouvelle source.

## 📄 Licence

MIT — voir [LICENSE](../LICENSE). Basé sur [Daily-AC/deuseek](https://github.com/Daily-AC/deuseek) (MIT) ; mention du droit d'auteur amont conservée.
