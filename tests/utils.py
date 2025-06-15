"""
Utility functions for PCILeech FPGA firmware generator tests, now focused solely
on the *official* `ufrisk/pcileech-fpga` repository (no Wi‑Fi forks).
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

import requests

# ─────────────────────────── Logging ────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ───────────────────── GitHub repository info ───────────────────
GITHUB_REPO = "ufrisk/pcileech-fpga"
GITHUB_BRANCH = "master"
GITHUB_BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents"

# Define specific paths for common SystemVerilog and TCL files
SV_PATHS = [
    "artix7/pcileech_tlps_a7.sv",
    "artix7/pcileech_tlps128_bar_a7.sv",
]
TCL_PATHS = ["artix7/vivado_generate_project_a7.tcl"]

# ──────────────────────── Cache settings ────────────────────────
CACHE_DIR = Path(os.path.expanduser("~")) / ".pcileech_test_cache"
CACHE_EXPIRY = 86400  # 24 h

# Local fallbacks (only used if GitHub is unreachable)
LOCAL_EXAMPLE_SV = Path(__file__).parent.parent / "external_sv_example.sv"
LOCAL_EXAMPLE_TCL = Path(__file__).parent.parent / "external_tcl_example.tcl"

# ───────────────────────── Cache helpers ────────────────────────


def ensure_cache_dir() -> Path:
    """Create cache dir if needed and return it."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR


def _cache_path(key: str) -> Path:
    """Map an arbitrary key to a file inside the cache dir."""
    safe_key = key.replace("/", "_").replace("\\", "_")
    return ensure_cache_dir() / safe_key


def _cache_valid(path: Path) -> bool:
    if not path.exists():
        return False
    return (time.time() - path.stat().st_mtime) < CACHE_EXPIRY


def _cache_load(key: str) -> Optional[str]:
    path = _cache_path(key)
    if not _cache_valid(path):
        return None
    try:
        with path.open("r", encoding="utf-8") as fh:
            obj = json.load(fh)
            return obj.get("content")
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def _cache_save(key: str, content: str) -> None:
    path = _cache_path(key)
    data = {"timestamp": time.time(), "content": content}
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh)


# ─────────────────────── GitHub fetchers ────────────────────────


def fetch_file_from_github(file_path: str, *, use_cache: bool = True) -> str:
    """Download a file *once* from the canonical repo (with opt‑in cache)."""
    if use_cache and (cached := _cache_load(file_path)):
        logger.info("Using cached %s", file_path)
        return cached

    url = f"{GITHUB_BASE_URL}/{file_path}"
    logger.info("Fetching %s", url)
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except requests.RequestException as exc:
        msg = f"Failed to fetch {file_path}: {exc}"
        logger.error(msg)
        raise ValueError(msg) from exc

    text = r.text
    if use_cache:
        _cache_save(file_path, text)
    return text


def fetch_directory_listing(directory: str) -> list[dict]:
    """Return GitHub API JSON for files under *directory* (non‑recursive)."""
    url = f"{GITHUB_API_URL}/{directory}"
    logger.info("Listing %s", url)
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as exc:
        msg = f"Failed to list {directory}: {exc}"
        logger.error(msg)
        raise ValueError(msg) from exc


# ─────────────────────── Repo search helpers ────────────────────


def search_repository_for_extension(ext: str, *, use_cache: bool = True) -> list[str]:
    """Recursively locate files with *ext* (e.g. ".sv", ".tcl")."""
    key = f"find::{ext}"
    if use_cache and (cached := _cache_load(key)):
        try:
            return json.loads(cached)
        except json.JSONDecodeError:
            pass

    to_visit: list[str] = [""]  # start at repo root
    found: list[str] = []

    while to_visit:
        directory = to_visit.pop()
        try:
            for entry in fetch_directory_listing(directory):
                typ, name = entry.get("type"), entry.get("name", "")
                path = f"{directory}/{name}".lstrip("/") if directory else name
                if typ == "file" and name.endswith(ext):
                    found.append(path)
                elif typ == "dir":
                    if "wifi" in name.lower():
                        continue
                    to_visit.append(path)
        except ValueError:
            continue  # ignore missing dirs

    if use_cache:
        _cache_save(key, json.dumps(found))
    return found


# ─────────────────────── Public convenience API ─────────────────


def get_pcileech_file(file_path: str, *, use_cache: bool = True) -> str:
    """Fetch *file_path* from the canonical repo, honouring cache."""
    return fetch_file_from_github(file_path, use_cache=use_cache)


def get_pcileech_sv_file(*, use_cache: bool = True) -> str:
    """Return contents of a representative SystemVerilog file.

    Preference order:
      1. First file in `SV_PATHS` list that exists.
      2. First *.sv* file discovered by repo search.
      3. Local fallback `external_sv_example.sv` if present.
    """
    # 1) Try curated list
    for p in SV_PATHS:
        try:
            return fetch_file_from_github(p, use_cache=use_cache)
        except ValueError:
            continue

    # 2) Fallback to search
    sv_files = search_repository_for_extension(".sv", use_cache=use_cache)
    if sv_files:
        return fetch_file_from_github(sv_files[0], use_cache=use_cache)

    # 3) Local example
    if LOCAL_EXAMPLE_SV.exists():
        logger.info("Using local SV example %s", LOCAL_EXAMPLE_SV)
        return LOCAL_EXAMPLE_SV.read_text()

    raise ValueError("No SystemVerilog source found in repository or locally")


def get_pcileech_tcl_file(*, use_cache: bool = True) -> str:
    """Return contents of a representative Vivado TCL script.

    Preference order mirrors `get_pcileech_sv_file()`.
    """
    # 1) Curated list
    for p in TCL_PATHS:
        try:
            return fetch_file_from_github(p, use_cache=use_cache)
        except ValueError:
            continue

    # 2) Search
    tcl_files = search_repository_for_extension(".tcl", use_cache=use_cache)
    if tcl_files:
        return fetch_file_from_github(tcl_files[0], use_cache=use_cache)

    # 3) Local example
    if LOCAL_EXAMPLE_TCL.exists():
        logger.info("Using local TCL example %s", LOCAL_EXAMPLE_TCL)
        return LOCAL_EXAMPLE_TCL.read_text()

    raise ValueError("No TCL script found in repository or locally")


# ───────────────────────── Misc helpers ─────────────────────────


def fetch_file_from_github_repo(
    repo: str, branch: str, file_path: str, *, use_cache: bool = True
) -> str:
    """Generic helper unrelated to PCILeech; left unchanged for completeness."""
    key = f"{repo}@{branch}:{file_path}"
    if use_cache and (cached := _cache_load(key)):
        return cached

    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{file_path}"
    logger.info("Fetching %s", url)
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except requests.RequestException as exc:
        msg = f"Failed to fetch {file_path} from {repo}: {exc}"
        logger.error(msg)
        raise ValueError(msg) from exc

    text = r.text
    if use_cache:
        _cache_save(key, text)
    return text


# ─────────────────────── Function aliases for backward compatibility ─────────────────────


def get_pcileech_wifi_sv_file(*, use_cache: bool = True) -> str:
    """Alias for get_pcileech_sv_file for backward compatibility."""
    return get_pcileech_sv_file(use_cache=use_cache)


def get_pcileech_wifi_tcl_file(*, use_cache: bool = True) -> str:
    """Alias for get_pcileech_tcl_file for backward compatibility."""
    return get_pcileech_tcl_file(use_cache=use_cache)
