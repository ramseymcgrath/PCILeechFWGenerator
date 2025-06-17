"""vivado_utils.py — Light‑weight helpers for locating and invoking Xilinx Vivado

✔ Linux & macOS only (Windows intentionally unsupported)
✔ Single source‑of‑truth for search paths (DRY)
✔ pathlib throughout, minimal branching
✔ Uses `logging` instead of `print` for debug output

Usage examples
--------------
```python
from vivado_handling import find_vivado_installation, run_vivado_command

info = find_vivado_installation()
print(info)

run_vivado_command("-version")
```
"""

from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

LOG = logging.getLogger(__name__)
if not LOG.handlers:

    class ColoredFormatter(logging.Formatter):
        """A logging formatter that adds ANSI color codes to log messages."""

        # ANSI color codes
        COLORS = {"RED": "\033[91m", "YELLOW": "\033[93m", "RESET": "\033[0m"}

        def __init__(self, fmt=None, datefmt=None):
            super().__init__(fmt, datefmt)
            # Only use colors for TTY outputs
            import sys

            self.use_colors = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

        def format(self, record):
            formatted = super().format(record)
            if self.use_colors:
                if record.levelno >= logging.ERROR:
                    return f"{self.COLORS['RED']}{formatted}{self.COLORS['RESET']}"
                elif record.levelno >= logging.WARNING:
                    return f"{self.COLORS['YELLOW']}{formatted}{self.COLORS['RESET']}"
            return formatted

    colored_formatter = ColoredFormatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(colored_formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[console_handler],
    )

# ───────────────────────── Constants ──────────────────────────
IS_LINUX = platform.system().lower() == "linux"
IS_MAC = platform.system().lower() == "darwin"

DEFAULT_BASES: List[Path] = []
if IS_LINUX:
    DEFAULT_BASES = [
        Path("/opt/Xilinx/Vivado"),
        Path("/tools/Xilinx/Vivado"),
        Path("/usr/local/Xilinx/Vivado"),
        Path.home() / "Xilinx" / "Vivado",
    ]
elif IS_MAC:
    DEFAULT_BASES = [
        Path("/Applications/Xilinx/Vivado"),
        Path.home() / "Xilinx" / "Vivado",
    ]
else:
    # Windows deliberately unsupported (keep interface minimal)
    pass

TOOLS_ROOT = Path("/tools/Xilinx")  # pattern: /tools/Xilinx/<version>/Vivado

# ───────────────────────── Internals ──────────────────────────


def _iter_candidate_dirs():
    """Yield all plausible Vivado install roots.*Not* the *bin* dir."""
    # 1) PATH — fast path
    if vivado := shutil.which("vivado"):
        yield Path(vivado).parent.parent  # bin/ -> Vivado/

    # 2) Environment variable
    if env := os.getenv("XILINX_VIVADO"):
        yield Path(env)

    # 3) Standard locations
    yield from DEFAULT_BASES

    # 4) /tools/Xilinx/<ver>/Vivado pattern
    if TOOLS_ROOT.exists():
        for child in TOOLS_ROOT.iterdir():
            if child.is_dir() and child.name[0].isdigit() and "." in child.name:
                candidate = child / "Vivado"
                yield candidate


def _vivado_executable(dir_: Path) -> Optional[Path]:
    """Return the vivado executable inside *dir_* if it exists."""
    exe = dir_ / "bin" / "vivado"
    return exe if exe.is_file() else None


def _detect_version(dir_: Path) -> str:
    """Infer version string from directory name (fallback to runtime query)."""
    for part in dir_.parts:
        if part[0].isdigit() and "." in part:
            return part
    return "unknown"


# ───────────────────────── Public API ──────────────────────────


def find_vivado_installation() -> Optional[Dict[str, str]]:
    """Return a dict with keys *path, bin_path, executable, version* or *None*."""
    for root in _iter_candidate_dirs():
        exe = _vivado_executable(root)
        if not exe:
            continue
        version = get_vivado_version(str(exe)) or _detect_version(root)
        LOG.debug("Vivado candidate: %s (v%s)", exe, version)
        return {
            "path": str(root),
            "bin_path": str(root / "bin"),
            "executable": str(exe),
            "version": version,
        }
    return None


def get_vivado_search_paths() -> List[str]:
    """Return *human‑readable* list of search locations (for diagnostics)."""
    paths: List[str] = ["System PATH"]
    paths.extend(str(p) for p in DEFAULT_BASES)
    if TOOLS_ROOT.exists():
        paths.append("/tools/Xilinx/<version>/Vivado")
    paths.append(f"XILINX_VIVADO={os.getenv('XILINX_VIVADO', '<not set>')}")
    return paths


def get_vivado_version(vivado_exec: str) -> str:
    """Call *vivado -version* with a 5‑second timeout to parse the version."""
    try:
        res = subprocess.run(
            [vivado_exec, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
            check=False,
        )
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if "vivado" in line.lower() and "v" in line:
                    for tok in line.split():
                        if tok.startswith("v") and "." in tok:
                            return tok.lstrip("v")
    except (subprocess.SubprocessError, FileNotFoundError, PermissionError):
        pass
    return "unknown"


def run_vivado_command(
    args: str | List[str],
    *,
    tcl_file: Optional[str] = None,
    cwd: Optional[str | Path] = None,
    timeout: Optional[int] = None,
    use_discovered: bool = True,
    enable_error_reporting: bool = True,
) -> subprocess.CompletedProcess:
    """Invoke Vivado with *args* (string or list). Enhanced with error reporting."""
    exe: Optional[str] = None
    if use_discovered:
        info = find_vivado_installation()
        if info:
            exe = info["executable"]
    exe = exe or shutil.which("vivado")
    if not exe:
        raise FileNotFoundError(
            "Vivado executable not found. Ensure it is in PATH or set XILINX_VIVADO."
        )

    cmd: List[str] = [exe]
    cmd.extend(args.split() if isinstance(args, str) else args)
    if tcl_file:
        cmd.extend(["-source", str(tcl_file)])

    LOG.info("Running: %s", " ".join(cmd))

    if enable_error_reporting:
        try:
            # Try to import and use the error reporter
            from .vivado_error_reporter import VivadoErrorReporter

            # Run with enhanced error reporting
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=cwd,
            )

            reporter = VivadoErrorReporter(use_colors=True)
            return_code, errors, warnings = reporter.monitor_vivado_process(process)

            # Generate report if there were issues
            if errors or warnings:
                output_dir = Path(cwd) if cwd else Path(".")
                report = reporter.generate_error_report(
                    errors,
                    warnings,
                    "Vivado Command",
                    output_dir / "vivado_error_report.txt",
                )
                reporter.print_summary(errors, warnings)

            # Create a CompletedProcess-like object
            result = subprocess.CompletedProcess(
                cmd,
                return_code,
                stdout="",
                stderr="",  # Output was already printed by monitor
            )

            if return_code != 0:
                result.check_returncode()

            return result

        except ImportError:
            LOG.warning(
                "Error reporter not available, falling back to standard execution"
            )

    # Fallback to standard execution
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
        timeout=timeout,
        check=True,
    )


def get_vivado_executable() -> Optional[str]:
    """Return the Vivado binary path or *None*."""
    info = find_vivado_installation()
    return info["executable"] if info else None


# ───────────────────────── Diagnostics ─────────────────────────


def debug_vivado_search() -> None:
    """Pretty print search logic and detection results (stdout‑only)."""
    print("# Vivado detection report ({}):".format(time.strftime("%F %T")))
    print("Search order:")
    for p in get_vivado_search_paths():
        print("  •", p)
    print()
    info = find_vivado_installation()
    if info:
        print("✔ Vivado found ->")
        for k, v in info.items():
            print(f"    {k:10}: {v}")
    else:
        print("✘ Vivado not located — check PATH or XILINX_VIVADO.")


if __name__ == "__main__":
    debug_vivado_search()
