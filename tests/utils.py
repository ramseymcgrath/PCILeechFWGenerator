"""
Utility functions for PCILeech firmware generator tests.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# GitHub repository information
GITHUB_REPO = "dom0ng/pcileech-wifi-v2"
GITHUB_BRANCH = "main"
GITHUB_BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents"

# Fallback repository if the primary one doesn't have the files we need
FALLBACK_REPOS = [{"repo": "ufrisk/pcileech-fpga",
                   "branch": "master",
                   "sv_paths": ["artix7/pcileech_tlps_a7.sv",
                                "artix7/pcileech_tlps128_bar_a7.sv"],
                   "tcl_paths": ["artix7/vivado_generate_project_a7.tcl"],
                   }]

# Cache directory for downloaded files
CACHE_DIR = Path(os.path.expanduser("~")) / ".pcileech_test_cache"
CACHE_EXPIRY = 86400  # Cache expiry in seconds (24 hours)

# Local example files as a last resort
LOCAL_EXAMPLE_SV = Path(__file__).parent.parent / "external_sv_example.sv"
LOCAL_EXAMPLE_TCL = Path(__file__).parent.parent / "external_tcl_example.tcl"


def ensure_cache_dir() -> Path:
    """Ensure the cache directory exists."""
    if not CACHE_DIR.exists():
        CACHE_DIR.mkdir(parents=True)
    return CACHE_DIR


def get_cache_path(file_path: str) -> Path:
    """Get the cache path for a file."""
    # Convert the file path to a cache-friendly name
    cache_name = file_path.replace("/", "_").replace("\\", "_")
    return ensure_cache_dir() / cache_name


def is_cache_valid(cache_path: Path) -> bool:
    """Check if the cache is still valid."""
    if not cache_path.exists():
        return False

    # Check if the cache has expired
    cache_time = cache_path.stat().st_mtime
    current_time = time.time()
    return (current_time - cache_time) < CACHE_EXPIRY


def save_to_cache(file_path: str, content: str) -> None:
    """Save content to cache."""
    cache_path = get_cache_path(file_path)

    # Save the content and metadata
    cache_data = {
        "file_path": file_path,
        "timestamp": time.time(),
        "content": content}

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f)


def load_from_cache(file_path: str) -> Optional[str]:
    """Load content from cache if valid."""
    cache_path = get_cache_path(file_path)

    if not is_cache_valid(cache_path):
        return None

    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
            return cache_data.get("content")
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def fetch_file_from_github(file_path: str, use_cache: bool = True) -> str:
    """
    Fetch a file from GitHub repository.

    Args:
        file_path: Path to the file in the repository
        use_cache: Whether to use cached version if available

    Returns:
        The content of the file as a string

    Raises:
        ValueError: If the file cannot be fetched
    """
    # Check cache first if enabled
    if use_cache:
        cached_content = load_from_cache(file_path)
        if cached_content is not None:
            logger.info(f"Using cached version of {file_path}")
            return cached_content

    # Construct the URL
    url = f"{GITHUB_BASE_URL}/{file_path}"

    try:
        logger.info(f"Fetching {file_path} from GitHub")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses

        content = response.text

        # Cache the content if caching is enabled
        if use_cache:
            save_to_cache(file_path, content)

        return content
    except requests.RequestException as e:
        error_msg = f"Failed to fetch {file_path} from GitHub: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)


def fetch_directory_listing(directory_path: str) -> list:
    """
    Fetch a listing of files in a directory from GitHub repository.

    Args:
        directory_path: Path to the directory in the repository

    Returns:
        A list of file information dictionaries

    Raises:
        ValueError: If the directory listing cannot be fetched
    """
    # Construct the URL
    url = f"{GITHUB_API_URL}/{directory_path}"

    try:
        logger.info(
            f"Fetching directory listing for {directory_path} from GitHub")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        return response.json()
    except requests.RequestException as e:
        error_msg = f"Failed to fetch directory listing for {directory_path} from GitHub: {
            str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)


def get_pcileech_wifi_file(file_path: str, use_cache: bool = True) -> str:
    """
    Get a file from the pcileech-wifi-v2 repository.

    This is the main function that should be used by tests to fetch files.

    Args:
        file_path: Path to the file in the repository (relative to the repository root)
        use_cache: Whether to use cached version if available

    Returns:
        The content of the file as a string

    Raises:
        ValueError: If the file cannot be fetched
    """
    try:
        return fetch_file_from_github(file_path, use_cache)
    except ValueError as e:
        logger.error(f"Error fetching file: {str(e)}")
        raise


def search_repository_for_file_type(
        extension: str,
        use_cache: bool = True) -> list:
    """
    Search the entire repository for files with a specific extension.

    Args:
        extension: File extension to search for (e.g., ".sv")
        use_cache: Whether to use cached results if available

    Returns:
        List of file paths
    """
    # Check cache first if enabled
    cache_key = f"file_search_{extension}"
    if use_cache:
        cached_content = load_from_cache(cache_key)
        if cached_content is not None:
            try:
                return json.loads(cached_content)
            except json.JSONDecodeError:
                pass

    # Start with common directories to check
    directories_to_check = [
        "",  # Root directory
        "src",
        "pcileech-wifi-DWA-556/src",
        "pcileech-wifi-DWA-556",
        "pcileech-wifi-v2/pcileech-wifi-DWA-556/src",
    ]

    found_files = []

    # Check each directory
    for directory in directories_to_check:
        try:
            files = fetch_directory_listing(directory)

            # Check for files with the specified extension
            for file in files:
                if file.get("type") == "file" and file.get(
                        "name", "").endswith(extension):
                    file_path = (
                        f"{directory}/{file['name']}" if directory else file["name"]
                    )
                    found_files.append(file_path)
                elif file.get("type") == "dir":
                    # Add subdirectories to check
                    subdir = (
                        f"{directory}/{file['name']}" if directory else file["name"]
                    )
                    if subdir not in directories_to_check:
                        directories_to_check.append(subdir)
        except ValueError:
            # Directory might not exist, continue to the next one
            continue

    # Cache the results if caching is enabled
    if use_cache and found_files:
        save_to_cache(cache_key, json.dumps(found_files))

    return found_files


def get_pcileech_wifi_sv_file(use_cache: bool = True) -> str:
    """
    Get a SystemVerilog file from the pcileech-wifi-v2 repository.

    Returns:
        The content of a SystemVerilog file

    Raises:
        ValueError: If no suitable file can be found
    """
    # First, check if local example exists and use it if it does
    if LOCAL_EXAMPLE_SV.exists():
        logger.info(
            f"Using local SystemVerilog example file: {LOCAL_EXAMPLE_SV}")
        return LOCAL_EXAMPLE_SV.read_text()

    # If local example doesn't exist, try to fetch from GitHub
    try:
        # Search for SystemVerilog files in the repository
        sv_files = search_repository_for_file_type(".sv", use_cache)

        if not sv_files:
            # If no .sv files found, try looking for .v files (Verilog)
            v_files = search_repository_for_file_type(".v", use_cache)
            if v_files:
                sv_files = v_files
            else:
                raise ValueError(
                    "No SystemVerilog files found in the repository and no local example available"
                )

        # Get the first SystemVerilog file
        file_path = sv_files[0]
        logger.info(f"Using SystemVerilog file: {file_path}")

        return fetch_file_from_github(file_path, use_cache)
    except ValueError as e:
        # If we can't fetch from the primary repository, try fallback
        # repositories
        for fallback in FALLBACK_REPOS:
            repo = fallback["repo"]
            branch = fallback["branch"]
            for path in fallback["sv_paths"]:
                try:
                    logger.info(
                        f"Trying fallback SystemVerilog file from {repo}: {path}")
                    return fetch_file_from_github_repo(
                        repo, branch, path, use_cache)
                except ValueError:
                    continue

        # If local example exists, use it as a last resort
        if LOCAL_EXAMPLE_SV.exists():
            logger.info(
                f"Using local SystemVerilog example file: {LOCAL_EXAMPLE_SV}")
            return LOCAL_EXAMPLE_SV.read_text()

        logger.error(f"Error fetching SystemVerilog file: {str(e)}")
        raise


def get_pcileech_wifi_tcl_file(use_cache: bool = True) -> str:
    """
    Get a TCL file from the pcileech-wifi-v2 repository.

    Returns:
        The content of a TCL file

    Raises:
        ValueError: If no suitable file can be found
    """
    # First, check if local example exists and use it if it does
    if LOCAL_EXAMPLE_TCL.exists():
        logger.info(f"Using local TCL example file: {LOCAL_EXAMPLE_TCL}")
        return LOCAL_EXAMPLE_TCL.read_text()

    # If local example doesn't exist, try to fetch from GitHub
    try:
        # Search for TCL files in the repository
        tcl_files = search_repository_for_file_type(".tcl", use_cache)

        if not tcl_files:
            raise ValueError(
                "No TCL files found in the repository and no local example available"
            )

        # Get the first TCL file
        file_path = tcl_files[0]
        logger.info(f"Using TCL file: {file_path}")

        return fetch_file_from_github(file_path, use_cache)
    except ValueError as e:
        # If we can't fetch from the primary repository, try fallback
        # repositories
        for fallback in FALLBACK_REPOS:
            repo = fallback["repo"]
            branch = fallback["branch"]
            for path in fallback["tcl_paths"]:
                try:
                    logger.info(
                        f"Trying fallback TCL file from {repo}: {path}")
                    return fetch_file_from_github_repo(
                        repo, branch, path, use_cache)
                except ValueError:
                    continue

        # If local example exists, use it as a last resort
        if LOCAL_EXAMPLE_TCL.exists():
            logger.info(f"Using local TCL example file: {LOCAL_EXAMPLE_TCL}")
            return LOCAL_EXAMPLE_TCL.read_text()

        logger.error(f"Error fetching TCL file: {str(e)}")
        raise


def fetch_file_from_github_repo(
    repo: str, branch: str, file_path: str, use_cache: bool = True
) -> str:
    """
    Fetch a file from a specific GitHub repository.

    Args:
        repo: Repository name (e.g., "user/repo")
        branch: Branch name
        file_path: Path to the file in the repository
        use_cache: Whether to use cached version if available

    Returns:
        The content of the file as a string

    Raises:
        ValueError: If the file cannot be fetched
    """
    # Check cache first if enabled
    cache_key = f"{repo}_{branch}_{file_path}"
    if use_cache:
        cached_content = load_from_cache(cache_key)
        if cached_content is not None:
            logger.info(f"Using cached version of {file_path} from {repo}")
            return cached_content

    # Construct the URL
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{file_path}"

    try:
        logger.info(f"Fetching {file_path} from GitHub repository {repo}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        content = response.text

        # Cache the content if caching is enabled
        if use_cache:
            save_to_cache(cache_key, content)

        return content
    except requests.RequestException as e:
        error_msg = (
            f"Failed to fetch {file_path} from GitHub repository {repo}: {
                str(e)}")
        logger.error(error_msg)
        raise ValueError(error_msg)
