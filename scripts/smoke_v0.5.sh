#!/usr/bin/env bash
# v0.5 smoke: verify a fresh deployment can search HN (the only true zero-config source)
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== install (editable) ==="
uv pip install -e . --reinstall >/dev/null

VERSION=$(uv run deuseek --version 2>&1 | tail -1)
echo "deuseek version: $VERSION"
if [[ "$VERSION" != *"1.0.0-alpha"* ]]; then
    echo "WARN: version not 1.0.0-alpha (got: $VERSION)"
fi

echo
echo "=== deuseek sources ==="
uv run deuseek sources

echo
echo "=== deuseek doctor ==="
uv run deuseek doctor

echo
echo "=== search 'vibe coding' (HN only, no setup) ==="
uv run deuseek search "vibe coding" --limit 3 --timeout 30 || true

echo
echo "=== smoke complete ==="
