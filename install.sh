#!/usr/bin/env bash
# Install syskit locally for daily use on Arch/Manjaro

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$ROOT/.venv"
BIN_DIR="${HOME}/.local/bin"

echo "==> Installing syskit from $ROOT"

if [[ ! -d "$VENV" ]]; then
  echo "==> Creating virtualenv..."
  python3 -m venv "$VENV"
fi

echo "==> Installing package in editable mode..."
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q -e "$ROOT[dev]"

mkdir -p "$BIN_DIR"
ln -sf "$VENV/bin/syskit" "$BIN_DIR/syskit"

echo "==> Done."
echo "    syskit is available as: syskit"
echo "    (${BIN_DIR}/syskit -> ${VENV}/bin/syskit)"
echo
echo "Try:"
echo "  syskit --help"
echo "  syskit info"
echo "  syskit clean --dry-run"