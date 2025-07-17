#!/usr/bin/env python3
"""
Flash a LambdaConcept Squirrel/Screamer (Artix-7 75T) with usbloader.

Usage:
    sudo python3 flash_fpga.py output/firmware.bin
Needs:
    • usbloader binary in $PATH  (https://docs.lambdaconcept.com/screamer/programming.html)
    • Board in JTAG/flash-mode (default power-on state)
"""
import argparse
import pathlib
import shutil
import subprocess
import sys


def run(cmd):
    print(f"[flash] {cmd}")
    subprocess.run(cmd, shell=True, check=True)


def main():
    """Main entry point for pcileech-flash command"""
    p = argparse.ArgumentParser(
        description="Flash a LambdaConcept Squirrel/Screamer (Artix-7 75T) with usbloader"
    )
    p.add_argument("bitfile", help=".bin produced by build.py")
    args = p.parse_args()

    if shutil.which("usbloader") is None:
        sys.exit("usbloader not found in PATH. Install it and retry.")

    bit = pathlib.Path(args.bitfile).resolve()
    if not bit.exists():
        sys.exit(f"File not found: {bit}")

    # Screamer/Squirrel default VID:PID = 1d50:6130
    run(f"usbloader --vidpid 1d50:6130 -f {bit}")

    print("[✓] Flash complete - power-cycle or warm-reset the card.")


if __name__ == "__main__":
    main()
