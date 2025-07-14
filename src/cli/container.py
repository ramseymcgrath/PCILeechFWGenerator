#!/usr/bin/env python3
"""container_build – unified VFIO‑aware Podman build runner"""
from __future__ import annotations

import shutil
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from log_config import get_logger
from shell import Shell

from .vfio_handler import VFIOBinder  # auto‑fix & diagnostics baked in

# Import safe logging functions
try:
    from ..string_utils import (
        log_debug_safe,
        log_error_safe,
        log_info_safe,
        log_warning_safe,
    )
except ImportError:
    # Fallback implementations
    def log_info_safe(logger, template, **kwargs):
        logger.info(template.format(**kwargs))

    def log_error_safe(logger, template, **kwargs):
        logger.error(template.format(**kwargs))

    def log_warning_safe(logger, template, **kwargs):
        logger.warning(template.format(**kwargs))

    def log_debug_safe(logger, template, **kwargs):
        logger.debug(template.format(**kwargs))


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
    # fallback control options
    fallback_mode: str = "none"  # "none", "prompt", or "auto"
    allowed_fallbacks: List[str] = field(default_factory=list)
    denied_fallbacks: List[str] = field(default_factory=list)

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

        # Add fallback control arguments
        if self.fallback_mode != "none":
            args.append(f"--fallback-mode {self.fallback_mode}")
        if self.allowed_fallbacks:
            args.append(f"--allow-fallbacks {','.join(self.allowed_fallbacks)}")
        if self.denied_fallbacks:
            args.append(f"--deny-fallbacks {','.join(self.denied_fallbacks)}")

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
    log_info_safe(logger, "Building container image {name}:{tag}", name=name, tag=tag)
    cmd = f"podman build -t {name}:{tag} -f Containerfile ."
    subprocess.run(cmd, shell=True, check=True)


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

    try:
        # Bind without keeping the FD (call the context manager only long
        # enough to flip the drivers)
        binder = VFIOBinder(cfg.bdf, attach=False)
        with binder:
            # enter/exit immediately → binds device
            pass

        # Get the group device path as a string (safe, just a string)
        from .vfio_handler import _get_iommu_group

        group_id = _get_iommu_group(cfg.bdf)
        group_dev = f"/dev/vfio/{group_id}"

        log_info_safe(
            logger,
            "Launching build container – board={board}, tag={tag}",
            board=cfg.board,
            tag=cfg.container_tag,
            prefix="CONT",
        )

        cmd_args = " ".join(cfg.cmd_args())
        podman_cmd = textwrap.dedent(
            f"""
            podman run --rm --privileged \
              --device={group_dev} \
              --device=/dev/vfio/vfio \
              --entrypoint python3 \
              --user root \
              -v {output_dir}:/app/output \
              -v /lib/modules/$(uname -r)/build:/kernel-headers:ro \
              {cfg.container_image}:{cfg.container_tag} \
              -m src.build {cmd_args}
            """
        ).strip()

        log_debug_safe(
            logger, "Container command: {cmd}", cmd=podman_cmd, prefix="CONT"
        )
        start = time.time()
        try:
            subprocess.run(podman_cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            raise ContainerError(f"Build failed (exit {e.returncode})") from e
        except KeyboardInterrupt:
            log_warning_safe(
                logger,
                "Build interrupted by user - cleaning up...",
                prefix="CONT",
            )
            # Get the container ID if possible
            try:
                container_id = (
                    subprocess.check_output(
                        "podman ps -q --filter ancestor=pcileech-fw-generator:latest",
                        shell=True,
                    )
                    .decode()
                    .strip()
                )
                if container_id:
                    log_info_safe(
                        logger,
                        "Stopping container {container_id}",
                        container_id=container_id,
                        prefix="CONT",
                    )
                    subprocess.run(
                        f"podman stop {container_id}", shell=True, check=False
                    )
            except Exception as e:
                log_warning_safe(
                    logger,
                    "Failed to clean up container: {error}",
                    error=str(e),
                    prefix="CONT",
                )

            # Ensure VFIO cleanup
            try:
                from .vfio import restore_driver

                if hasattr(cfg, "bdf") and cfg.bdf:
                    log_info_safe(
                        logger,
                        "Ensuring VFIO cleanup for device {bdf}",
                        bdf=cfg.bdf,
                        prefix="CLEA",
                    )
                    # Get original driver if possible
                    try:
                        from .vfio import get_current_driver

                        original_driver = get_current_driver(cfg.bdf)
                        restore_driver(cfg.bdf, original_driver)
                    except Exception:
                        # Just try to unbind from vfio-pci
                        try:
                            with open(
                                f"/sys/bus/pci/drivers/vfio-pci/unbind", "w"
                            ) as f:
                                f.write(f"{cfg.bdf}\n")
                        except Exception:
                            pass
            except Exception as e:
                log_warning_safe(
                    logger,
                    "VFIO cleanup after interrupt failed: {error}",
                    error=str(e),
                    prefix="CLEA",
                )

            raise KeyboardInterrupt("Build interrupted by user")
        duration = time.time() - start
        log_info_safe(
            logger,
            "Build completed in {duration:.1f}s",
            duration=duration,
            prefix="CONT",
        )
    except RuntimeError as e:
        if "VFIO" in str(e):
            # VFIO binding failed, diagnostics have already been run
            log_error_safe(
                logger,
                "Build aborted due to VFIO issues: {error}",
                error=str(e),
                prefix="VFIO",
            )
            from .vfio_diagnostics import Diagnostics, render

            # Run diagnostics one more time to ensure user sees the report
            diag = Diagnostics(cfg.bdf)
            report = diag.run()
            if not report.can_proceed:
                log_error_safe(
                    logger,
                    "VFIO diagnostics indicate system is not ready for VFIO operations",
                    prefix="VFIO",
                )
                log_error_safe(
                    logger,
                    "Please fix the issues reported above and try again",
                    prefix="VFIO",
                )
            sys.exit(1)
        else:
            # Re-raise other runtime errors
            raise


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
