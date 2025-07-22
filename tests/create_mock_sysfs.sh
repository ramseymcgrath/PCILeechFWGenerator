#!/usr/bin/env bash
set -euo pipefail

ROOT="$1"
BDF="0000:03:00.0"
DEV_DIR="$ROOT/sys/bus/pci/devices/$BDF"

mkdir -p "$DEV_DIR"

echo -n "0x8086" > "$DEV_DIR/vendor"
echo -n "0x100e" > "$DEV_DIR/device"
echo -n "0x0000" > "$DEV_DIR/subsystem_vendor"
echo -n "0x0000" > "$DEV_DIR/subsystem_device"

head -c 256 /dev/zero > "$DEV_DIR/config"

printf "%s\n" "$BDF" > "$ROOT/BDF"

echo "[mock_sysfs] Created fake device at $DEV_DIR"
