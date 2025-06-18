#!/usr/bin/env python3
"""vfio_handler – context‑managed VFIO binding with built‑in health checks."""
from __future__ import annotations

import logging
import os
import re
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

# ────────────────────────────────────────────────
# Bring in vfio_assist diagnostics
# ────────────────────────────────────────────────
try:
    from vfio_assist import Diagnostics, remediation_script, Status, colour, Fore  # type: ignore
except ImportError:  # fallback – minimal stubs if user omitted vfio_assist

    class Status:  # noqa: D101 – tiny shim
        OK = "ok"
        WARNING = "warning"
        ERROR = "error"

    class Diagnostics:  # noqa: D101 – minimal always‑OK shim
        def __init__(self, *_, **__):
            pass

        def run(self):  # noqa: D401 – stub
            from dataclasses import dataclass, field

            @dataclass
            class _R:  # noqa: D401
                overall: str = Status.OK
                can_proceed: bool = True
                checks: list = field(default_factory=list)

            return _R()

    def remediation_script(_):  # noqa: D401 – noop
        return "#!/bin/sh\necho stub remediation\n"

    def colour(x, *_):  # noqa: D401 – pass‑through
        return x

    class Fore:  # noqa: D401 – dummy colours
        CYAN = ""


log = logging.getLogger("vfio-handler")
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

# Bring in original utils ------------------------------------------------------
from utils.logging import get_logger  # type: ignore   # your local helper
from utils.shell import Shell  # type: ignore

logger = get_logger(__name__)

# ────────────────────────────────────────────────
# Helper utilities (mostly unchanged)
# ────────────────────────────────────────────────
BDF_RE = re.compile(r"^[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7]$")


def validate_bdf_format(bdf: str) -> bool:
    return bool(BDF_RE.match(bdf))


def check_linux() -> None:
    import platform

    if platform.system().lower() != "linux":
        raise RuntimeError("VFIO requires Linux – current OS: %s" % platform.system())


def get_current_driver(bdf: str) -> Optional[str]:
    drv_link = Path(f"/sys/bus/pci/devices/{bdf}/driver")
    return os.path.basename(drv_link.resolve()) if drv_link.exists() else None


def get_iommu_group(bdf: str) -> str:
    return os.path.basename(Path(f"/sys/bus/pci/devices/{bdf}/iommu_group").resolve())


def read_ids(bdf: str) -> tuple[str, str]:
    dev_path = Path(f"/sys/bus/pci/devices/{bdf}")
    return (
        dev_path.joinpath("vendor").read_text().strip().lstrip("0x"),
        dev_path.joinpath("device").read_text().strip().lstrip("0x"),
    )


# ────────────────────────────────────────────────
# Pre‑flight check wrapper
# ────────────────────────────────────────────────


def ensure_vfio_ready(device_bdf: Optional[str] = None, *, auto_fix: bool = True):
    """Run Diagnostics; optionally auto‑apply fixes.

    Raises RuntimeError if blockers remain after (optional) fixing.
    """
    diag = Diagnostics(device_bdf)
    rep = diag.run()

    if rep.overall == Status.OK:
        log.debug("VFIO pre‑flight: all good")
        return

    # show quick summary (don’t spam full coloured report – that’s handled elsewhere)
    log.warning("VFIO pre‑flight found issues – status: %s", rep.overall)

    if not auto_fix:
        raise RuntimeError(
            "VFIO environment not ready – run 'vfio_assist fix' or set auto_fix=True"
        )

    log.info(colour("Attempting automatic remediation…", Fore.CYAN))
    script = remediation_script(rep)
    temp = Path("/tmp/vfio_auto_fix.sh")
    temp.write_text(script)
    temp.chmod(0o755)
    try:
        subprocess.run(["sudo", str(temp)], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Remediation script failed: {e}") from e

    # re‑run
    rep = Diagnostics(device_bdf).run()
    if not rep.can_proceed:
        raise RuntimeError("Issues remain after remediation – aborting")
    log.info("VFIO environment healthy after remediation")


def _write(path: Path, data: str):
    Shell().write_file(path.as_posix(), data)


def bind_to_vfio(bdf: str):
    vendor, device = read_ids(bdf)
    if get_current_driver(bdf) == "vfio-pci":
        log.info("%s already bound to vfio-pci", bdf)
        return
    _write(Path("/sys/bus/pci/drivers/vfio-pci/new_id"), f"{vendor} {device}\n")
    cur_drv = get_current_driver(bdf)
    if cur_drv:
        _write(Path(f"/sys/bus/pci/devices/{bdf}/driver/unbind"), f"{bdf}\n")
    _write(Path("/sys/bus/pci/drivers/vfio-pci/bind"), f"{bdf}\n")
    if get_current_driver(bdf) != "vfio-pci":
        raise RuntimeError(f"Failed to bind {bdf} to vfio-pci")


def restore_driver(bdf: str, original: Optional[str]):
    if original and get_current_driver(bdf) != original:
        _write(Path(f"/sys/bus/pci/drivers/{original}/bind"), f"{bdf}\n")


# ────────────────────────────────────────────────
# Public context manager
# ────────────────────────────────────────────────
@contextmanager
def VFIOBinder(bdf: str, *, auto_fix: bool = False) -> Generator[Path, None, None]:
    """Yield `/dev/vfio/<group>` with automatic cleanup.

    *auto_fix* will attempt to run remediation script automatically.
    """
    check_linux()
    if not validate_bdf_format(bdf):
        raise ValueError(f"Invalid BDF: {bdf}")

    ensure_vfio_ready(bdf, auto_fix=auto_fix)

    original_driver = get_current_driver(bdf)
    iommu_group = get_iommu_group(bdf)
    vfio_node = Path(f"/dev/vfio/{iommu_group}")

    log.info("Binding %s (IOMMU grp %s) to vfio-pci", bdf, iommu_group)
    bind_to_vfio(bdf)
    if not vfio_node.exists():
        raise RuntimeError(f"VFIO node {vfio_node} missing after bind")
    try:
        yield vfio_node
    finally:
        log.info("Restoring %s to %s", bdf, original_driver or "<none>")
        restore_driver(bdf, original_driver)
        log.info("Cleanup complete")
        if vfio_node.exists():
            log.info(
                "VFIO node %s still exists – manual cleanup may be needed", vfio_node
            )
        else:
            log.info("VFIO node %s removed successfully", vfio_node)


# at end of vfio_handler.py
from .vfio import get_current_driver as get_current_driver  # re-export
