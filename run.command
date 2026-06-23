#!/usr/bin/env bash
# run.command - macOS version

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
    if ! command -v python >/dev/null 2>&1; then
        echo "Python 3 not found. Install from python.org or via Homebrew:"
        echo "  brew install python3"
        exit 1
    fi
    PYTHON=python
else
    PYTHON=python3
fi

$PYTHON -c "import requests, bs4" 2>/dev/null || {
    echo "Installing dependencies..."
    $PYTHON -m pip install -q -r requirements.txt
}

echo "Starting Safety Checker..."
echo ""

if [ $# -eq 0 ]; then
    $PYTHON safety_checker.py --menu
else
    $PYTHON safety_checker.py "$@"
fi
