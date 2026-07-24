#!/usr/bin/env bash
# 搜索之神 (deuseek) — 一键安装脚本
# 用法: bash install.sh
#
# 自动完成:
# 1. 检查 Python 3.10+ 环境
# 2. 复制代码到 ~/.agents/skills/deuseek/
# 3. 创建 venv 并安装全部依赖 (含 Scrapling/patchright/playwright)
# 4. 下载浏览器 (Chromium for Playwright/Patchright)
# 5. 运行 doctor 验证

set -euo pipefail

SKILL_DIR="$HOME/.agents/skills/deuseek"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔══════════════════════════════════════════════════════╗"
echo "║        搜索之神 (deuseek) — 安装程序                ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ---- Step 1: Check Python ----
echo "▸ [1/5] 检查 Python 环境..."

if command -v python3.12 &>/dev/null; then
    PYTHON=python3.12
elif command -v python3.11 &>/dev/null; then
    PYTHON=python3.11
elif command -v python3.10 &>/dev/null; then
    PYTHON=python3.10
else
    PYTHON=python3
fi

PY_VERSION=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$($PYTHON -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$($PYTHON -c 'import sys; print(sys.version_info.minor)')

if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]); then
    echo "  ✗ Python $PY_VERSION — 需要 3.10+ (Scrapling 要求)"
    echo "  请安装 Python 3.10+:"
    echo "    macOS:  brew install python@3.12"
    echo "    Linux:  sudo apt install python3.12  (或 pyenv install 3.12)"
    exit 1
fi
echo "  ✓ Python $PY_VERSION"

# ---- Step 2: Copy files ----
echo ""
echo "▸ [2/5] 复制代码到 $SKILL_DIR ..."

# Remove old installation if exists
if [ -d "$SKILL_DIR" ]; then
    echo "  发现旧安装, 备份到 ${SKILL_DIR}.bak"
    rm -rf "${SKILL_DIR}.bak"
    mv "$SKILL_DIR" "${SKILL_DIR}.bak"
fi

mkdir -p "$SKILL_DIR"
# Copy everything except .venv, .git, __pycache__, tests, docs, benchmarks
rsync -a --exclude='.venv' --exclude='.git' --exclude='__pycache__' \
         --exclude='tests' --exclude='.pytest_cache' --exclude='docs' \
         --exclude='benchmark*' --exclude='*.tar.gz' --exclude='install.sh' \
         "$SCRIPT_DIR/" "$SKILL_DIR/"
echo "  ✓ 代码已复制"

# ---- Step 3: Create venv + install ----
echo ""
echo "▸ [3/5] 创建虚拟环境并安装依赖..."

$PYTHON -m venv "$SKILL_DIR/.venv"
PIP="$SKILL_DIR/.venv/bin/pip"

echo "  升级 pip..."
$PIP install --upgrade pip --quiet 2>&1 | tail -1

echo "  安装 deuseek + 核心依赖 (scrapling, httpx, pydantic, rich, ddgs)..."
$PIP install "$SKILL_DIR" --quiet 2>&1 | tail -3

echo "  安装 fetcher 引擎依赖 (patchright, playwright, browserforge, markdownify)..."
$PIP install patchright playwright browserforge markdownify msgspec protego --quiet 2>&1 | tail -3

echo "  ✓ 依赖安装完成"

# ---- Step 4: Install browsers ----
echo ""
echo "▸ [4/5] 下载浏览器 (Chromium)..."

# Playwright Chromium (for DynamicFetcher + Scrapling convertor)
PLAYWRIGHT_SKIP_DOWNLOAD=0 $SKILL_DIR/.venv/bin/playwright install chromium --with-deps 2>&1 | tail -3 || \
    echo "  ⚠ Playwright Chromium 安装跳过 (可能需要手动运行: playwright install chromium)"

# Patchright Chromium (for StealthyFetcher / Cloudflare bypass)
$SKILL_DIR/.venv/bin/patchright install chromium 2>&1 | tail -3 || \
    echo "  ⚠ Patchright Chromium 安装跳过 (可能需要手动运行: patchright install chromium)"

echo "  ✓ 浏览器就绪"

# ---- Step 5: Verify ----
echo ""
echo "▸ [5/5] 验证安装..."

DEUSEEK="$SKILL_DIR/.venv/bin/deuseek"

if [ ! -f "$DEUSEEK" ]; then
    echo "  ✗ deuseek CLI 未找到 — 安装可能失败"
    exit 1
fi

VERSION=$($DEUSEEK --version 2>&1)
echo "  $VERSION"

echo ""
echo "  Doctor 检查:"
$DEUSEEK doctor 2>/dev/null | $PYTHON -c "
import sys, json
d = json.load(sys.stdin)
for b in d.get('fetch_backends', []):
    icon = '✓' if b['ok'] else '✗'
    print(f'    {icon} {b[\"tool\"]}: {b[\"detail\"]}')
for s in d.get('sources', []):
    icon = '✓' if s['ok'] else '✗'
    print(f'    {icon} {s[\"id\"]}: {s[\"detail\"]}')
" 2>/dev/null || echo "  (运行 deuseek doctor 查看详情)"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║              ✅ 安装完成!                            ║"
echo "║                                                      ║"
echo "║  试用:                                               ║"
echo "║    deuseek search \"Python asyncio\"                  ║"
echo "║    deuseek fetch https://example.com                 ║"
echo "║    deuseek super \"梁文峰 DeepSeek\" --stream          ║"
echo "║    deuseek doctor                                    ║"
echo "║                                                      ║"
echo "║  Skill 位置: $SKILL_DIR"
echo "║  CLI 路径:   $SKILL_DIR/.venv/bin/deuseek"
echo "╚══════════════════════════════════════════════════════╝"

# Add to PATH hint
if ! echo "$PATH" | grep -q "$SKILL_DIR/.venv/bin"; then
    echo ""
    echo "⚠ 提示: deuseek 不在 PATH 中。添加以下行到 ~/.zshrc 或 ~/.bashrc:"
    echo "  export PATH=\"$SKILL_DIR/.venv/bin:\$PATH\""
fi
