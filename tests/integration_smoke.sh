#!/usr/bin/env bash
set -euo pipefail

MOCK_ROOT="$(pwd)/tests/mock_sysfs"
BUILD_DIR="$(pwd)/tests/build"
BOARD="${BOARD_NAME:-pcileech_35t325_x1}"
BDF="$(cat "$MOCK_ROOT/BDF")"

mkdir -p "$BUILD_DIR"

echo "[host build]"
pip3 install -r requirements.txt --no-cache-dir
pip3 install -r requirements-tui.txt --no-cache-dir

PCILEECH_SYSFS_ROOT="$MOCK_ROOT/sys/bus/pci/devices" \
python pcileech.py build --bdf "$BDF" --board "$BOARD" --build-dir "$BUILD_DIR" --no-synth

test -f "$BUILD_DIR/generated/pcileech_top.sv" || { echo "Missing generated SV"; exit 1; }

echo "[podman build]"
podman build -t pcileechfwgen:ci -f Containerfile .

echo "[podman run]"
podman run --rm \
    -e PCILEECH_SYSFS_ROOT=/mock/sys/bus/pci/devices \
    -v "$MOCK_ROOT":/mock:ro \
    pcileechfwgen:ci build --bdf "$BDF" --board "$BOARD" --build-dir /tmp/build --no-synth

echo "Integration OK."