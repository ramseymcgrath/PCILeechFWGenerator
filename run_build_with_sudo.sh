#!/bin/bash
# Wrapper script to run build_without_container.py with sudo using the virtual environment

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Use the virtual environment's Python interpreter with sudo
sudo -E "${SCRIPT_DIR}/.venv/bin/python3.11" "${SCRIPT_DIR}/build_without_container.py" "$@"