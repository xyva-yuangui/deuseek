# deuseek

> طبقة البحث والجلب المتخفّي الشاملة لأي وكيل ذكاء اصطناعي للبرمجة. تجاوز بوابة WebSearch، والوصول إلى المصادر التي لا يستطيع البحث من جهة الخادم بلوغها، وتحويل أي عنوان URL إلى markdown نظيف — **مجاني 100%، دون الحاجة إلى مفاتيح API**.

> طبقة الجلب مدعومة بـ [Scrapling](https://github.com/D4Vinci/Scrapling) من **D4Vinci** — تُستخدم بامتنان. 🙏

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![Sources](https://img.shields.io/badge/sources-8%20free-success.svg)](#-المصادر-المدعومة-كلها-مجانية)
[![Status](https://img.shields.io/badge/status-1.0.0--alpha-orange.svg)](#)

🌐 [English](../README.md) | **العربية** | [Español](README.es.md) | [Português (Brasil)](README.pt-BR.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [Русский](README.ru.md) | [한국어](README.ko.md)

---

## جدول المحتويات
- [✨ لماذا deuseek؟](#-لماذا-deuseek)
- [🤖 يعمل مع واجهة سطر أوامر الوكيل لديك](#-يعمل-مع-واجهة-سطر-أوامر-الوكيل-لديك)
- [🚀 بداية سريعة](#-بداية-سريعة)
- [📦 التثبيت](#-التثبيت)
- [📋 الأوامر](#-الأوامر)
- [📚 المصادر المدعومة (كلها مجانية)](#-المصادر-المدعومة-كلها-مجانية)
- [🥷 معمارية محرك الجلب](#-معمارية-محرك-الجلب)
- [🤝 اصطلاح استدعاء الوكيل](#-اصطلاح-استدعاء-الوكيل)
- [⚙️ التفضيلات](#️-التفضيلات)
- [🪟 دعم المنصة](#-دعم-المنصة)
- [🏗️ المعمارية](#️-المعمارية)
- [🙏 شكر وتقدير](#-شكر-وتقدير)
- [🤝 المساهمة](#-المساهمة)
- [📄 الترخيص](#-الترخيص)

---

## ✨ لماذا deuseek؟

`WebSearch` الخاص بـ Anthropic هو **أداة من جهة الخادم** (`web_search_20250305`) محمية ببوابتين:
1. **بوابة العميل** — مسجّلة فقط لإعدادات first-party / provider محددة.
2. **بوابة المنبع** — يجب أن يُطبّق واجهة upstream API للأداة الخادمية فعليًا. **محطّات الترحيل المتوافقة مع OpenAI** (cliproxy، وanyrouter، والبوابات ذاتية الاستضافة) التي تكتفي بترجمة Claude API → OpenAI Chat Completions **لا تُطبّقها**، لذا يفشل `WebSearch` بصمت. وحتى حيث يعمل، فإنه لا يستطيع بلوغ نقاشات HN الفورية، أو خيوط تعليقات Reddit العميقة، أو مقالات WeChat 公众号، أو مقاطع Bilibili التقنية.

**يعالج deuseek ذلك من جهة العميل** — واجهة سطر أوامر واحدة + Skill تتصل مباشرة بـ Algolia / `yt-dlp` / `gh` / Bilibili API / Sogou / DuckDuckGo، لذا فهو يعمل بغض النظر عن موفّر API الذي يشير إليه واجهة سطر أوامر الوكيل لديك.

### المزايا الرئيسية

| | deuseek | `WebSearch` الأصلي | واجهات بحث مدفوعة |
|---|:---:|:---:|:---:|
| يعمل على محطّات الترحيل/البروكسي المتوافقة مع OpenAI | ✅ | ❌ | n/a |
| يصل إلى HN / Reddit / WeChat / Bilibili / RSS | ✅ | ❌ | جزئي |
| تجاوز Cloudflare / مكافحة البوتات | ✅ | ❌ | n/a |
| URL → markdown كامل النص | ✅ | WebFetch فقط | n/a |
| التكلفة | **مجاني** | مُضمّن | 💲 مدفوع |
| وقت الإعداد | ~3 دقائق | — | — |

- 🚪 **يتجاوز بوابة WebSearch ذات الطبقتين** — يعمل على محطّات الترحيل/البروكسي حيث يفشل `WebSearch` بصمت لأن المنبع لا يُطبّق الأداة الخادمية.
- 🌐 **يصل إلى المصادر العمودية التي لا يستطيع البحث من جهة الخادم بلوغها** — نقاشات HN الفورية، وخيوط تعليقات Reddit العميقة، ومقالات WeChat 公众号، ومقاطع Bilibili التقنية، وخلاصات RSS.
- 🆓 **مجاني 100%، صفر مفاتيح API للنواة** — DuckDuckGo، وAlgolia HN، وBilibili API، وSogou، و`yt-dlp`، و`gh`، و`feedparser`. دون بطاقة ائتمان، ودون حصة، ودون صداع حدود المعدل.
- 🥷 **جلب متخفٍّ ثلاثي الطبقات مع تجاوز Cloudflare** — `Fetcher` (HTTP عبر curl_cffi) → Jina SaaS → `StealthyFetcher` (Chrome عبر patchright) + `solve_cloudflare`. الطبقة الوحيدة التي تكسر Cloudflare Turnstile/Interstitial.
- 🧠 **يتذكّر DomainKB لكل نطاق** — لا تجربة ولا خطأ في كل عملية جلب؛ TTL مدته 24 ساعة يجبر إعادة التحقيق حتى لا تُصبح قاعدة المعرفة قديمة حين يغيّر الموقع إعداداته لمكافحة البوتات.
- ⚡ **وضع خط المعالجة أسرع بنحو 40%** — يبثّ `asyncio` نتائج البحث مباشرة إلى الجلب (النتائج لا تنتظر أبطأ مصدر).
- 🛡️ **ترقية تلقائية لرمز التحقق (Captcha)** — يكتشف صفحات رمز التحقق (环境异常 / Cloudflare / Just a moment) ويُعيد المحاولة تلقائيًا باستخدام `stealthy + solve_cloudflare`، مع إبراز الأخطاء ليقرّر الوكيل بما يثق به.
- 🔧 **محددات تكيّفية ذاتية الشفاء** — إعادة تصميم الصفحات لا تكسر الاستخراج (إعادة التموضع القائم على التشابه من Scrapling + `auto_save`).
- 🖥️ **عبر المنصات** — macOS أساسي، وLinux / WSL2 / Windows بأقصى جهد ممكن.
- 🧩 **واجهة سطر أوامر واحدة + Skill واحدة، غير مرتبط بوكيل بحكم التصميم** — يندمج في أي واجهة سطر أوامر لوكيل في ~3 دقائق؛ manifest ضمن `.claude-plugin/` يجعله Skill أصليًا لواجهات سطر الأوامر المتوافقة مع Claude-Code، وواجهة سطر أوامر JSON عادية لكل ما سوى ذلك.
- 🔍 **شفاف** — وسم `cost="free|paid"`، وأخطاء `errors[]` مهيكلة، وحِمَل `raw` الأصلية محفوظة حتى يستطيع الوكلاء انتزاع النص الكامل عند الحاجة.

## 🤖 يعمل مع واجهة سطر أوامر الوكيل لديك

deuseek هو واجهة سطر أوامر قياسية تُخرج JSON — **أي وكيل يستطيع تشغيل أوامر shell يستطيع استخدامه**. manifest ضمن `.claude-plugin/` يضيف تكامل Skill أصليًا لواجهات سطر الأوامر المتوافقة مع Claude-Code.

| أداة الوكيل | كيفية استخدام deuseek |
|---|---|
| **Claude Code** (Anthropic) | `/plugin marketplace add xyva-yuangui/deuseek` → `/plugin install deuseek`، ثم *"استخدم deuseek للبحث ..."*. يعمل أيضًا كواجهة سطر أوامر عادية. |
| **Zcode** | نادِ `deuseek search --json "..."` / `deuseek fetch --json <url>` من shell، أو حمّل الـ Skill. |
| **Codex** (OpenAI Codex CLI) | شغّل `deuseek` كعملية فرعية وحلّل غلاف JSON. |
| **Reasonix** | JSON كعملية فرعية، أو حمّله كـ skill. |
| **OpenClaw** | شغّل `deuseek` كأمر shell وحلّل JSON. |
| **Hermes** | JSON كعملية فرعية. |
| **Antigravity** (`agy`) | `agy plugin install` (يتعرّف على `.claude-plugin/`). |
| أي وكيل آخر | شغّل `deuseek <command> --json` كأمر shell، وحلّل غلاف JSON. |

> لأن العقد هو "واجهة سطر أوامر تطبع JSON"، فإن deuseek **غير مرتبط بوكيل** — لا تضطر أبدًا للانتظار حتى "ندعم" أداتك. إن استطاع وكيلك تشغيل عملية، فهو يستطيع استخدام deuseek اليوم.

## 🚀 بداية سريعة

```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
deuseek init                   # writes default ~/.deuseek/preferences.toml
deuseek search "vibe coding"   # web + hackernews work zero-config
```

افتح المصادر التي تحتاج إلى أداة upstream:

```bash
deuseek setup youtube     # pip install yt-dlp
deuseek setup github      # brew install gh (macOS) / winget (Windows)
deuseek setup reddit      # uv tool install rdt-cli && rdt login
```

## 📦 التثبيت

**الخيار A — uv (موصى به):**
```bash
uv tool install git+https://github.com/xyva-yuangui/deuseek.git
```

**الخيار B — pip (تثبيت تطوير قابل للتعديل):**
```bash
git clone https://github.com/xyva-yuangui/deuseek.git
cd deuseek
pip install -e ".[dev]"
```

**الخيار C — سكربت من سطر واحد (macOS/Linux، يُهيّئ venv + المتصفّحات):**
```bash
bash install.sh
```

**محركات جلب اختيارية** (لتجاوز Cloudflare وعرض JS):
```bash
pip install "deuseek[fetchers]"          # patchright + curl_cffi + msgspec + protego
patchright install chromium               # stealth Chrome (Cloudflare bypass)
playwright install chromium               # JS rendering
```

## 📋 الأوامر

| الأمر | ما الذي يفعله |
|---|---|
| `deuseek search "<query>"` | بحث متعدد المصادر (SERP: metadata + URL؛ content ≤500 حرفًا) |
| `deuseek search --on hackernews,web "..."` | التقييد بمصادر محددة |
| `deuseek search --mode quick "..."` | web + hackernews فقط |
| `deuseek search --mode deep "..."` | جميع المصادر الجاهزة |
| `deuseek search --json "..."` | إخراج JSON صريح |
| `deuseek search --no-cache "..."` | تخطّي الذاكرة المؤقتة، فرض التحديث |
| **`deuseek fetch <url>`** | **URL → markdown كامل النص** (توجيه Scrapling ثلاثي الطبقات + DomainKB) |
| `deuseek fetch <url> --backend jina` | إجبار Jina Reader SaaS (صفر اعتماديات محلية) |
| `deuseek fetch <url> --backend stealthy --solve-cloudflare` | إجبار Chrome متخفٍّ + تجاوز CF |
| `deuseek fetch <url> --backend dynamic` | إجبار عرض JS عبر Playwright |
| `deuseek fetch <url> --full` | تحويل الصفحة كاملة (الافتراضي: المحتوى الرئيسي فقط) |
| **`deuseek super "<query>"`** | **من البداية إلى النهاية**: بحث متعدد المصادر → جلب متخفٍّ → extract (اختياري)، خط معالجة بثّي (~40% أسرع) |
| `deuseek crawl <url>` | زحف Spider متعدد الصفحات (Scrapling async Spider + checkpoint) |
| `deuseek extract <url>` | استخراج مهيك تكيّفي (CSS/XPath + إعادة تموضع ذاتية الشفاء) |
| `deuseek domain-kb` | عرض/مسح قاعدة معرفة domain→backend (`--clear`) |
| `deuseek init` | كتابة `~/.deuseek/preferences.toml` الافتراضي |
| `deuseek sources` | سرد جميع المصادر + حالة الجاهزية (`--probe` للاختبار) |
| `deuseek setup <source>` | إعداد موجّه لمصدر |
| `deuseek doctor` | فحص الصحة (sources + fetch backends + BrowserPool) |
| `deuseek check-update` | المقارنة مع GitHub Releases |
| `deuseek preferences {show,edit,reset,path}` | تفضيلات المستخدم |

## 📚 المصادر المدعومة (كلها مجانية)

| المصدر | الطبقة | الاعتمادية | ملاحظات |
|---|---|---|---|
| web | ✅ ready | `ddgs` (pip) | بحث الويب العام عبر DuckDuckGo |
| hackernews | ✅ ready | none | Algolia HN API، صفر إعداد |
| youtube | ✅ ready | `yt-dlp` (pip) | `deuseek setup youtube` |
| github | ✅ ready | `gh` CLI + `gh auth login` | `deuseek setup github` |
| rss | ✅ ready | `feedparser` مدمج | **يجب أن يكون الاستعلام عنوان feed URL** |
| wechat | ✅ ready | none | WeChat 公众号 — بحث Sogou مجاني (دعم تعزيز متخفّي اختياري عبر Scrapling) |
| bilibili | ✅ ready | none | واجهة Bilibili الرسمية للبحث |
| reddit | 🟡 one_step | `rdt-cli` + `rdt login` | `deuseek setup reddit` |

> **تريد النص الكامل؟** المصادر التي يُرجع منبعها محتوى كاملًا تُبقي الحِمل الأصلي في `result.raw` (مثال `raw["item_html"]` الخاص بـ wechat). لكل ما سوى ذلك، شغّل `deuseek fetch <url>`.

## 🥷 معمارية محرك الجلب

`deuseek fetch` / `super` / `crawl` / `extract` مبنية على [Scrapling](https://github.com/D4Vinci/Scrapling) — اعتمادية واحدة تغطي جلب HTTP، والمتصفّح المتخفّي، والتحليل التكيّفي، وasync Spider.

### التوجيه ثلاثي الطبقات (FetchRouter)

| المحرك | التنفيذ | الزمن النموذجي | الاستخدام |
|---|---|---|---|
| **Fetcher** | Scrapling `Fetcher` (HTTP عبر curl_cffi + انتحال TLS) | 0.4–3.9s | الافتراضي، 80%+ من عناوين URL، HTTP صرف دون متصفّح |
| **jina** | [Jina Reader](https://r.jina.ai/) SaaS (IP من جهة الخادم) | 2.2–5.7s | احتياطي حين يُحجب Fetcher |
| **StealthyFetcher** | Scrapling `StealthyFetcher` (Chrome متخفٍّ عبر patchright) + `solve_cloudflare` | 7.8s / 37s (CF) | الملاذ الأخير — الوحيد الذي يكسر Cloudflare Turnstile |
| DynamicFetcher | Scrapling `DynamicFetcher` (Playwright) | 4.9–6.9s | مواقع عرض JS فقط، `--backend dynamic` صريح |

> التصعيد متعمّد: Fetcher سريع لكنه يموت أمام Cloudflare؛ StealthyFetcher يكسر CF لكن 37s بطيء جدًا ليكون افتراضيًا. يجرّب الموجّه السريع أولًا ولا يُصعّد إلا عند الفشل.

### DomainKB — ذاكرة لكل نطاق

يتذكّر أي محرك يعمل وأيّها محجوب لكل نطاق، حتى لا نجرّب ونخطئ في كل عملية جلب.
- التخزين: مسار المنصة (macOS `~/Library/Application Support/deuseek/`، Linux XDG `~/.local/share/deuseek/`، Windows `%APPDATA%/deuseek/`)
- **TTL مدته 24 ساعة** — المدخلات المنتهية تجبر إعادة التحقيق، فتُشفى السجلات القديمة ذاتيًا حين يغيّر الموقع إعداداته لمكافحة البوتات
- `record_success` / `record_failure` يُعيدان الكتابة تلقائيًا في كل عملية جلب

```bash
deuseek domain-kb              # list all domain→backend mappings (with expired status)
deuseek domain-kb --clear      # wipe the knowledge base
```

### BrowserPool — جلسات متصفّح دافئة

يستغرق الإقلاع البارد لـ Chrome في Stealthy/Dynamic 2–4s. يُبقي `BrowserPool` جلسة دافئة ويعيد استخدامها، مُنزِلًا عمليات الجلب اللاحقة إلى ~1s. الخمول 5 دقائق → `shrink()` تلقائي (يُحرّر ~200–500MB لكل نسخة). يُبلغ `deuseek doctor` عن الحالة الدافئة.

### وضع خط المعالجة — `deuseek super`

الأمر الرائد يُسلّسل البحث → الجلب → الاستخراج في خط معالجة حقيقي: ما إن تصل أول نتيجة بحث حتى يبدأ الجلب ويتداخل مع عمليات البحث المتبقية (~40% أسرع من التسلسلي).

```bash
deuseek super "iPhone 16 review"
deuseek super "Python asyncio" --sources hackernews,web --stream   # streaming JSON Lines
deuseek super "React 19" --extract-fields '{"title":"h1::text"}'   # + structured extraction
```

### ترقية رمز التحقق (Captcha) التلقائية

يمسح `fetch` مُخرجات كل backend بحثًا عن كلمات رمز التحقق المفتاحية (`环境异常 / 完成验证后即可继续访问 / 请输入验证码 / Cloudflare / Just a moment / Checking your browser`). عند المطابقة:
1. يحصل `errors[]` على مدخل `captcha_suspected: ...`
2. إن كان StealthyFetcher متاحًا ولم يُجرَّب، فإنه **يُعيد المحاولة تلقائيًا** بـ `stealthy + solve_cloudflare=True`
3. نجاح → `auto_upgraded: stealthy+solve_cloudflare succeeded`؛ فشل → `auto_upgrade_failed`

تدهور لطيف — يقرأ الوكيل `errors` ويقرّر بما يثق به؛ ويُحفظ `markdown` دائمًا.

## 🤝 اصطلاح استدعاء الوكيل

**خذ JSON صراحةً دائمًا** عند مناداة deuseek من وكيل، حتى لا يُفقد التفاف جدول TTY للحقول:

```bash
# Option 1: --json per command
deuseek search --json "..."
deuseek fetch  --json "<url>"

# Option 2: env var (applies to the whole agent harness — recommended)
export DEUSEEK_FORCE_JSON=1
```

`not isatty()` يتبدّل تلقائيًا إلى JSON، لكن بعض طرفيات الوكيل (مثل Antigravity) تُخصّص PTY حقيقيًا فيصير `isatty()` True ويفشل الكشف التلقائي — `--json` الصريح أو متغيّر البيئة هو ضمان يعمل دائمًا.

غلاف البحث القياسي:
```json
{
  "query": "...",
  "ts": "ISO 8601 Z",
  "results": [{"source","title","url","content","ts","score","raw","cost"}],
  "errors":  [{"source","error","category"}]
}
```

## ⚙️ التفضيلات

يُهيّئ `~/.deuseek/preferences.toml` المصادر الافتراضية، واللغة، وصيغة الإخراج، وتجاوزات `trust`.

```bash
deuseek preferences show     # view current config
deuseek preferences edit     # edit with $EDITOR (Windows fallback: notepad)
deuseek preferences reset    # reset (backs up to .bak)
deuseek preferences path     # print the file path
```

مفاتيح API (اختيارية — النواة لا تحتاج أيًا منها) تُوضع في `~/.deuseek/secrets.env` (`KEY=VALUE`؛ POSIX يحذّر من الأذونات الفضفاضة).

## 🪟 دعم المنصة

| المنصة | الحالة | ملاحظات |
|---|---|---|
| macOS | ✅ أساسي | جميع المصادر + جميع محركات الجلب الثلاثة مُختبَرة |
| Linux | 🟡 بأقصى جهد | يعمل؛ تدفّق الإعداد لا يُدير `apt`/`pacman` تلقائيًا |
| WSL2 | 🟡 بأقصى جهد | مثل Linux |
| Windows (PowerShell الأصلي) | 🟡 تجريبي | `secrets_env` يتخطّى POSIX chmod؛ edit للتفضيلات يلجأ إلى notepad؛ setup github يقترح `winget install GitHub.cli`. **يرجى فتح issue إن واجهت مشكلات.** |

يطبع `deuseek doctor` المنصة / إصدار Python في الأعلى — أرفقه عند تسجيل المشكلات.

## 🏗️ المعمارية

- **نمط المُكيّف (Adapter)** — مُكيّف واحد لكل مصدر، يُطبّق `AdapterBase` (`is_ready` + `search`)
- **تفرّق غير متزامن** — يستخدم `Dispatcher` `asyncio.gather` مع عزل أخطاء لكل مصدر (`unavailable` مقابل `failed`)
- **سجلّ YAML** — `sources.yml` هو مصدر الحقيقة الوحيد (tier / adapter / trust / timeout / deps)
- **Router** — دمج query_hints كـ substrings + `default_in_auto`، `MAX_SOURCES=5`، RSS مُقيّد على استعلامات URL
- **Scorer** — `0.4*recency_norm + 0.6*source_trust` (الأوزان مجموعها 1.0، مُؤكَّد)؛ الطوابع الزمنية المفقودة افتراضها 0.5
- **Cache** — L1 ذاكرة + L2 ملف؛ توحيد عنوان URL (يُزيّل `utm_*`/`fbclid`/`gclid`/...) حتى تتشارك تنويعات المتتبّع مدخلًا واحدًا
- **Contract** — مُصادِق `SearchResult.content` الخاص بـ pydantic يقتطع إلى 500 حرف عالميًا؛ يبقى النص الكامل في `raw`

الملفات الرئيسية: `deuseek/sources.yml`، `deuseek/adapters/`، `deuseek/cli.py`، `deuseek/commands/fetch.py`، `deuseek/commands/super.py`، `deuseek/dispatcher.py`، `deuseek/fetch_router/router.py`، `deuseek/engines/`، `deuseek/convert/converter.py`، `deuseek/perf/`، `deuseek/native/`، `.claude-plugin/skills/deuseek/SKILL.md`.

## 🙏 شكر وتقدير

يقف deuseek على أكتاف العمالقة:

- **[Scrapling](https://github.com/D4Vinci/Scrapling)** من [**D4Vinci**](https://github.com/D4Vinci) — إطار الجلب المتخفّي / التحليل التكيّفي / async Spider الذي يشغّل طبقة الجلب كاملةً في deuseek (Fetcher / StealthyFetcher / DynamicFetcher / المحددات التكيّفية / Spider). تصميم تجاوز Cloudflare ثلاثي الطبقات لن يوجد لولاه. 🙏
- **[Daily-AC/deuseek](https://github.com/Daily-AC/deuseek)** (MIT) — المشروع المنبع الذي يبني هذا الـ fork المجاني عليه.
- أدوات ومكتبات المنبع: `yt-dlp`، `gh`، `rdt-cli`، `feedparser`، `httpx`، `pydantic`، `rich`، `click`، [Jina Reader](https://r.jina.ai/)، `curl_cffi`، `patchright`، `Playwright`، `markdownify`، `html2text`، `lxml`.

## 🤝 المساهمة

المساهمات مرحّب بها! يرجى:
1. شغّل `deuseek doctor` وأرفق مُخرجاته عند الإبلاغ عن مشكلات source/backend — 90% من حالات "أحد المصادر لا يعمل" سببها binary upstream مفقود.
2. افتح issue أولًا للمصادر الجديدة أو التغييرات الجارحة.
3. أبقِ المُكيّفات مطابقة لـ `AdapterBase` (`is_ready` + `search` يُرجِع `SearchResult`).

انظر [قوالب issue](../.github/ISSUE_TEMPLATE/) لتقارير الأخطاء، وطلبات الميزات، وطلبات المصادر الجديدة.

## 📄 الترخيص

MIT — انظر [LICENSE](../LICENSE). مبني على [Daily-AC/deuseek](https://github.com/Daily-AC/deuseek) (MIT)؛ إشعار حقوق النشر الخاص بالمنبع محفوظ.
