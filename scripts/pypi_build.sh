#!/bin/bash
# Simple wrapper script for PyPI package generation

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}PCILeech Firmware Generator - PyPI Package Builder${NC}"
echo "=================================================="

# Change to project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Run the Python script with all arguments
python3 scripts/generate_pypi_package.py "$@"

echo -e "${GREEN}Build process completed!${NC}"