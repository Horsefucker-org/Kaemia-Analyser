#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}    Safety Checker - Website Security Scanner${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
  echo -e "${RED}✗ Python 3 is required but not installed.${NC}"
  echo "Install Python 3.8+ and try again."
  exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"

# Check and install dependencies
echo -e "\n${YELLOW}Checking dependencies...${NC}"
python3 -c "
try:
    import requests
    import bs4
    print('Dependencies OK')
except ImportError:
    exit(1)
" 2>/dev/null || {
  echo -e "${YELLOW}Installing required packages...${NC}"
  python3 -m pip install --user -q -r requirements.txt
  echo -e "${GREEN}✓ Dependencies installed${NC}"
}

echo -e "\n${GREEN}Starting Safety Checker...${NC}\n"

# Always start interactive menu by default, unless CLI args are provided
if [ $# -eq 0 ]; then
  python3 safety_checker.py --menu
else
  python3 safety_checker.py "$@"
fi

EXIT_CODE=$?

# Keep terminal open on error
if [ $EXIT_CODE -ne 0 ]; then
  echo -e "\n${RED}✗ Error occurred (exit code: $EXIT_CODE)${NC}"
  echo -e "Press any key to exit..."
  read -n 1 -s -r || true
fi

exit $EXIT_CODE
