#!/usr/bin/env bash
set -euo pipefail

PROGNAME="safety-checker"

if command -v pipx >/dev/null 2>&1; then
  echo "Uninstalling via pipx..."
  pipx uninstall ${PROGNAME} || true
else
  echo "Uninstalling via pip..."
  python3 -m pip uninstall -y safety_checker || true
fi

echo "Uninstall complete. Remove any leftover files in ~/.local/bin if necessary."
