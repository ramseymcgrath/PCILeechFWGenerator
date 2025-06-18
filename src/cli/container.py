#!/usr/bin/env python3
"""container_build – unified VFIO‑aware Podman build runner"""
from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from utils.logging import get_logger
from utils.shell import Shell
from .vfio import VFIOBinder  # auto‑fix & diagnostics baked in

logger = get_logger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Exceptions
# ──────────────────────────────────────────────────────────────────────────────
class ContainerError(RuntimeError):
    pass


class VFIOError(RuntimeError):
    pass


class EnvError(RuntimeError):
    pass


# ──────────────────────────────────────────────────────────────────────────────
# Build configuration (thin wrapper over original)
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class BuildConfig:
    bdf: str
    board: str
    # feature toggles
    advanced_sv: bool = False
    device_type: str = "generic"
    enable_variance: bool = False
    disable_power_management: bool = False
    disable_error_handling: bool = False
    disable_performance_counters: bool = False
    behavior_profile_duration: int = 30
    # runtime toggles
    auto_fix: bool = True  # hand to VFIOBinder
    container_tag: str = "latest"
    container_image: str = "pcileech-fw-generator"

    def cmd_args(self) -> List[str]:
        """Translate config to build.py flags"""
        args = [f"--bdf {self.bdf}", f"--board {self.board}"]
        if self.advanced_sv:
            args.append("--advanced-sv")
        if self.device_type != "generic":
            args.append(f"--device-type {self.device_type}")
        if self.enable_variance:
            args.append("--enable-variance")
        if self.disable_power_management:
            args.append("--disable-power-management")
        if self.disable_error_handling:
            args.append("--disable-error-handling")
        if self.disable_performance_counters:
            args.append("--disable-performance-counters")
        if self.behavior_profile_duration != 30:
            args.append(f"--behavior-profile-duration {self.behavior_profile_duration}")
        return args


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


def require_podman() -> None:
    if shutil.which("podman") is None:
        raise EnvError("Podman not found – install it or adjust PATH")


def image_exists(name: str) -> bool:
    shell = Shell()
    out = shell.run("podman images --format '{{.Repository}}:{{.Tag}}'", timeout=5)
    return any(line.startswith(name) for line in out.splitlines())


def build_image(name: str, tag: str) -> None:
    logger.info("Building container image %s:%s", name, tag)
    cmd = f"podman build -t {name}:{tag} -f Containerfile ."
    subprocess.run(cmd, shell=True, check=True)


# tqdm optional ----------------------------------------------------------------
try:
    from tqdm import tqdm  # type: ignore

    def _prog(it, desc):
        return tqdm(it, desc=desc)

except ImportError:

    def _prog(it, desc):  # Keep parameter name consistent
        return it


# ──────────────────────────────────────────────────────────────────────────────
# Public façade
# ──────────────────────────────────────────────────────────────────────────────


def run_build(cfg: BuildConfig) -> None:
    """High‑level orchestration: VFIO bind → container run → cleanup"""
    require_podman()
    if not image_exists(f"{cfg.container_image}:{cfg.container_tag}"):
        build_image(cfg.container_image, cfg.container_tag)

    # Ensure host output dir exists and is absolute
    output_dir = (Path.cwd() / "output").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    with VFIOBinder(cfg.bdf, auto_fix=cfg.auto_fix) as vfio_node:
        logger.info(
            "Launching build container – board=%s, tag=%s", cfg.board, cfg.container_tag
        )

        cmd_args = " ".join(cfg.cmd_args())
        podman_cmd = textwrap.dedent(
            f"""
            podman run --rm --privileged \
              --device={vfio_node} \
              --entrypoint python3 \
              --device=/dev/vfio/vfio \
              -v {output_dir}:/app/output \
              {cfg.container_image}:{cfg.container_tag} \
              /app/src/build.py {cmd_args}
        """
        ).strip()

        logger.debug("Container command: %s", podman_cmd)
        start = time.time()
        try:
            subprocess.run(podman_cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            raise ContainerError(f"Build failed (exit {e.returncode})") from e
        duration = time.time() - start
        logger.info("Build completed in %.1fs", duration)


# ──────────────────────────────────────────────────────────────────────────────
# CLI entry for humans / CI
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="VFIO‑aware Podman build wrapper")
    p.add_argument("bdf", help="PCIe BDF, e.g. 0000:03:00.0")
    p.add_argument("board", help="Target board string")
    p.add_argument("--advanced-sv", action="store_true")
    p.add_argument("--device-type", default="generic")
    p.add_argument("--enable-variance", action="store_true")
    p.add_argument("--auto-fix", action="store_true")
    args = p.parse_args()

    cfg = BuildConfig(
        bdf=args.bdf,
        board=args.board,
        advanced_sv=args.advanced_sv,
        device_type=args.device_type,
        enable_variance=args.enable_variance,
        auto_fix=args.auto_fix,
    )

    run_build(cfg)
