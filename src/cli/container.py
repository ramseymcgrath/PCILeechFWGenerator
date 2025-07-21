#!/usr/bin/env python3
"""container_build - unified VFIO‑aware Podman build runner"""
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

from .vfio import VFIOBinder  # auto‑fix & diagnostics baked in
from .vfio import get_current_driver, restore_driver

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
    # active device configuration
    disable_active_device: bool = False
    active_timer_period: int = 100000
    active_interrupt_mode: str = "msi"
    active_interrupt_vector: int = 0
    active_priority: int = 15
    # output options
    output_template: Optional[str] = None
    donor_template: Optional[str] = None

    def cmd_args(self) -> List[str]:
        """Translate config to build.py flags - only include supported arguments"""
        args = [f"--bdf {self.bdf}", f"--board {self.board}"]

        # Add feature toggles
        if self.advanced_sv:
            args.append("--advanced-sv")
        if self.enable_variance:
            args.append("--enable-variance")

        # Only include arguments that build.py actually supports:
        # --profile (for behavior profiling duration)
        if self.behavior_profile_duration != 30:
            args.append(f"--profile {self.behavior_profile_duration}")

        # --output-template and --donor-template are supported
        if self.output_template:
            args.append(f"--output-template {self.output_template}")
        if self.donor_template:
            args.append(f"--donor-template {self.donor_template}")

        return args


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


def check_podman_available() -> bool:
    """Check if Podman is available and working."""
    if shutil.which("podman") is None:
        return False

    # Try to run a simple podman command to check if it's working
    try:
        shell = Shell()
        shell.run("podman version", timeout=5)
        return True
    except RuntimeError:
        return False


def require_podman() -> None:
    if shutil.which("podman") is None:
        raise EnvError("Podman not found - install it or adjust PATH")


def image_exists(name: str) -> bool:
    try:
        shell = Shell()
        out = shell.run("podman images --format '{{.Repository}}:{{.Tag}}'", timeout=5)
        return any(line.startswith(name) for line in out.splitlines())
    except RuntimeError as e:
        # If podman fails to connect, return False
        if "Cannot connect to Podman" in str(e) or "connection refused" in str(e):
            return False
        raise


def build_image(name: str, tag: str) -> None:
    log_info_safe(logger, "Building container image {name}:{tag}", name=name, tag=tag)
    cmd = f"podman build -t {name}:{tag} -f Containerfile ."
    subprocess.run(cmd, shell=True, check=True)


# ──────────────────────────────────────────────────────────────────────────────
# Public façade
# ──────────────────────────────────────────────────────────────────────────────


def prompt_user_for_local_build() -> bool:
    """Prompt user to confirm local build when Podman is unavailable."""
    print("\n" + "=" * 60)
    print("⚠️  Podman is not available or cannot connect.")
    print("=" * 60)
    print("\nThe build normally runs in a container for consistency.")
    print("However, you can run the build locally on your system.")
    print("\nNote: Local builds require all dependencies to be installed.")
    print("      (Vivado, Python packages, etc.)")
    print()

    while True:
        response = (
            input("Would you like to run the build locally? [y/N]: ").strip().lower()
        )
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no", ""]:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")


def run_local_build(cfg: BuildConfig) -> None:
    """Run build locally without container."""
    import sys

    log_info_safe(
        logger,
        "Running local build - board={board}",
        board=cfg.board,
        prefix="LOCAL",
    )

    # Ensure output directory exists
    output_dir = Path.cwd() / "output"
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Add src to path if needed
    src_path = Path(__file__).parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # Import build module
    try:
        from src.build import main as build_main
    except ImportError:
        # Try alternative import path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        try:
            from src.build import main as build_main
        except ImportError:
            log_error_safe(
                logger,
                "Failed to import build module - cannot run local build",
                prefix="LOCAL",
            )
            raise ImportError("Cannot run local build - missing build module")

    # Process the command arguments properly
    build_args = []

    # Add core arguments directly
    build_args.append("--bdf")
    build_args.append(cfg.bdf)
    build_args.append("--board")
    build_args.append(cfg.board)

    # Add boolean flags
    if cfg.advanced_sv:
        build_args.append("--advanced-sv")
    if cfg.enable_variance:
        build_args.append("--enable-variance")

    # Add other parameters that build.py supports
    if cfg.behavior_profile_duration != 30:
        build_args.append("--profile")
        build_args.append(str(cfg.behavior_profile_duration))

    if cfg.output_template:
        build_args.append("--output-template")
        build_args.append(cfg.output_template)

    if cfg.donor_template:
        build_args.append("--donor-template")
        build_args.append(cfg.donor_template)

    log_info_safe(
        logger,
        "Executing local build with args: {args}",
        args=" ".join(build_args),
        prefix="LOCAL",
    )

    # Run the build
    start = time.time()
    try:
        result = build_main(build_args)
        if result != 0:
            raise RuntimeError(f"Local build failed with exit code {result}")

        elapsed = time.time() - start
        log_info_safe(
            logger,
            "Local build completed in {elapsed:.1f}s ✓",
            elapsed=elapsed,
            prefix="LOCAL",
        )
    except Exception as e:
        elapsed = time.time() - start

        # Check if this is a platform compatibility error to reduce redundant logging
        error_str = str(e)
        is_platform_error = (
            "requires Linux" in error_str
            or "Current platform:" in error_str
            or "only available on Linux" in error_str
            or "platform incompatibility" in error_str
        )

        if is_platform_error:
            # For platform errors, log at a lower level since the detailed error was already logged
            log_info_safe(
                logger,
                "Local build skipped due to platform incompatibility (see details above)",
                prefix="LOCAL",
            )
        else:
            log_error_safe(
                logger,
                "Local build failed after {elapsed:.1f}s: {error}",
                elapsed=elapsed,
                error=error_str,
                prefix="LOCAL",
            )
        raise


def run_build(cfg: BuildConfig) -> None:
    """High‑level orchestration: VFIO bind → container run → cleanup"""
    # Check if Podman is available and working
    podman_available = check_podman_available()

    if not podman_available:
        log_warning_safe(
            logger,
            "Podman not available or cannot connect",
            prefix="BUILD",
        )

        # Prompt user for local build
        if prompt_user_for_local_build():
            run_local_build(cfg)
        else:
            log_info_safe(
                logger,
                "Build cancelled by user",
                prefix="BUILD",
            )
            sys.exit(1)
        return

    # Try container build first
    try:
        require_podman()
        if not image_exists(f"{cfg.container_image}:{cfg.container_tag}"):
            build_image(cfg.container_image, cfg.container_tag)
    except (EnvError, RuntimeError) as e:
        if "Cannot connect to Podman" in str(e) or "connection refused" in str(e):
            log_warning_safe(
                logger,
                "Podman connection failed: {error}",
                error=str(e),
                prefix="BUILD",
            )

            # Prompt user for local build
            if prompt_user_for_local_build():
                run_local_build(cfg)
            else:
                log_info_safe(
                    logger,
                    "Build cancelled by user",
                    prefix="BUILD",
                )
                sys.exit(1)
            return
        raise

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
            "Launching build container - board={board}, tag={tag}",
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
                if cfg.bdf:  # This is sufficient since bdf is a required field
                    log_info_safe(
                        logger,
                        "Ensuring VFIO cleanup for device {bdf}",
                        bdf=cfg.bdf,
                        prefix="CLEA",
                    )
                    # Get original driver if possible
                    try:
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
    p.add_argument("--enable-variance", action="store_true")
    p.add_argument("--auto-fix", action="store_true")
    args = p.parse_args()

    cfg = BuildConfig(
        bdf=args.bdf,
        board=args.board,
        advanced_sv=args.advanced_sv,
        enable_variance=args.enable_variance,
        auto_fix=args.auto_fix,
    )

    run_build(cfg)
