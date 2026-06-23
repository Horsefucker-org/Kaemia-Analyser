#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
METHOD="${1:---method auto}"

echo "════════════════════════════════════════"
echo "  Safety Checker Installation Script"
echo "════════════════════════════════════════"

# Extract method
if [[ "$METHOD" == "--method" ]]; then
  INSTALL_METHOD="${2:-auto}"
else
  INSTALL_METHOD="auto"
fi

install_with_pipx() {
  echo "Installing with pipx (recommended)..."
  
  # Check if pipx is available
  if ! command -v pipx >/dev/null 2>&1; then
    echo "pipx not found. Installing pipx..."
    python3 -m pip install --user --quiet pipx
    export PATH="$HOME/.local/bin:$PATH"
  fi
  
  cd "$SCRIPT_DIR"
  echo "Installing safety-checker..."
  pipx install . --force
  echo "✓ Installation complete!"
}

install_with_pip() {
  echo "Installing with pip --user..."
  cd "$SCRIPT_DIR"
  python3 -m pip install --user --quiet .
  
  if [ -d "$HOME/.local/bin" ]; then
    echo "✓ Installation complete!"
    echo "Make sure \$HOME/.local/bin is in your PATH:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
  fi
}

# Main installation
case "$INSTALL_METHOD" in
  pipx)
    install_with_pipx
    ;;
  user)
    install_with_pip
    ;;
  auto)
    if command -v pipx >/dev/null 2>&1; then
      install_with_pipx
    else
      install_with_pip
    fi
    ;;
  *)
    echo "Unknown method: $INSTALL_METHOD"
    echo "Usage: $0 [--method pipx|user|auto]"
    exit 1
    ;;
esac

echo ""
echo "Usage: safety-checker https://example.com --aggressive"
echo "For help: safety-checker --help"
