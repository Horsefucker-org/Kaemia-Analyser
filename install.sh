#!/usr/bin/env bash
set -euo pipefail

# Simple installer for safety_checker
# Prefer pipx (isolated), fallback to pip --user

PROGNAME="safety-checker"
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

usage(){
  cat <<EOF
Usage: $0 [--method pipx|user]

Installs safety_checker. Default method: pipx if available or installable.

--method pipx    Install with pipx (recommended)
--method user    Install with pip --user (adds to ~/.local/bin)
EOF
}

METHOD="auto"
if [ "$#" -gt 0 ]; then
  if [ "$1" = "--method" ] && [ -n "${2-}" ]; then
    METHOD="$2"
  else
    usage
    exit 1
  fi
fi

install_pipx(){
  echo "Installing with pipx..."
  python3 -m pip install --user pipx || true
  python3 -m pipx ensurepath || true
  # reload shell PATH if needed (best-effort)
  export PATH="$HOME/.local/bin:$PATH"
  cd "$HERE"
  pipx install . || pipx install --editable . || python3 -m pip install --user .
}

install_user(){
  echo "Installing with pip --user..."
  cd "$HERE"
  python3 -m pip install --user .
  echo "Ensure ~/.local/bin is on your PATH to run 'safety-checker'"
}

if [ "$METHOD" = "pipx" ]; then
  install_pipx
elif [ "$METHOD" = "user" ]; then
  install_user
else
  # auto: try pipx first
  if command -v pipx >/dev/null 2>&1; then
    install_pipx
  else
    echo "pipx not found — will attempt to install pipx and use it (requires pip)"
    install_pipx
  fi
fi

echo "Installation complete. Run: safety-checker --help"
