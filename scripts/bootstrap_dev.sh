#!/usr/bin/env bash
set -euo pipefail

# Bootstrap developer environment for safety_checker
# Installs pre-commit hooks, optional pipx, and project dependencies locally.

echo "Installing project dependencies..."
python3 -m pip install --user -r requirements.txt

if command -v pre-commit >/dev/null 2>&1; then
  echo "pre-commit already installed"
else
  python3 -m pip install --user pre-commit
fi

echo "Installing pre-commit hooks..."
python3 -m pre_commit install || pre-commit install || true

# Optional: install pipx
if ! command -v pipx >/dev/null 2>&1; then
  echo "pipx not found; installing pipx to user site-packages"
  python3 -m pip install --user pipx || true
  python3 -m pipx ensurepath || true
fi

echo "Bootstrap complete. Run './install.sh' to install the CLI for your user or use pipx." 
