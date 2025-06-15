#!/usr/bin/env python3
"""
Repository Manager

Handles cloning and updating of required Git repositories.
"""

import datetime
import os
import subprocess
from pathlib import Path

# Git repository information
PCILEECH_FPGA_REPO = "https://github.com/ufrisk/pcileech-fpga.git"
REPO_CACHE_DIR = Path(os.path.expanduser("~/.cache/pcileech-fw-generator/repos"))
PCILEECH_FPGA_DIR = REPO_CACHE_DIR / "pcileech-fpga"


class RepoManager:
    """Manages Git repositories required for the build process"""

    @staticmethod
    def run_command(cmd: str, **kwargs) -> subprocess.CompletedProcess:
        """
        Execute a shell command.

        Args:
            cmd (str): The shell command to execute.
            **kwargs: Additional arguments passed to subprocess.run.

        Returns:
            subprocess.CompletedProcess: The result of the command execution.

        Raises:
            subprocess.CalledProcessError: If the command fails.
        """
        print(f"[+] {cmd}")
        return subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True, **kwargs
        )

    @classmethod
    def ensure_git_repo(cls) -> None:
        """
        Ensure that the pcileech-fpga git repository is available.

        Raises:
            RuntimeError: If Git is not available or repository operations fail.
        """
        print("[*] Checking pcileech-fpga repository")

        # Create cache directory if it doesn't exist
        repo_dir = PCILEECH_FPGA_DIR
        os.makedirs(REPO_CACHE_DIR, exist_ok=True)

        # Check if git is available
        try:
            result = cls.run_command("git --version")
            if result.returncode != 0:
                raise RuntimeError("Git not available")
        except (FileNotFoundError, subprocess.CalledProcessError):
            raise RuntimeError("Git not found in PATH")

        # Check if repository already exists
        if os.path.exists(os.path.join(repo_dir, ".git")):
            print(f"[*] PCILeech FPGA repository found at {repo_dir}")

            # Check if repository needs update (older than 7 days)
            try:
                last_update_file = repo_dir / ".last_update"
                update_needed = True

                if last_update_file.exists():
                    with open(last_update_file, "r") as f:
                        try:
                            last_update = datetime.datetime.fromisoformat(
                                f.read().strip()
                            )
                            days_since_update = (
                                datetime.datetime.now() - last_update
                            ).days
                            update_needed = days_since_update >= 7
                        except (ValueError, TypeError):
                            update_needed = True

                if update_needed:
                    print("[*] Updating PCILeech FPGA repository")

                    # Get current directory
                    current_dir = os.getcwd()

                    # Change to repository directory
                    os.chdir(repo_dir)

                    try:
                        # Pull latest changes
                        result = cls.run_command("git pull")

                        # Update last update timestamp
                        with open(last_update_file, "w") as f:
                            f.write(datetime.datetime.now().isoformat())

                        print("[✓] PCILeech FPGA repository updated successfully")
                    except Exception as e:
                        print(f"[!] Warning: Failed to update repository: {str(e)}")
                    finally:
                        # Change back to original directory
                        os.chdir(current_dir)
            except Exception as e:
                print(f"[!] Warning: Error checking repository update status: {str(e)}")
        else:
            # Clone repository
            print(f"[*] Cloning PCILeech FPGA repository to {repo_dir}")

            try:
                result = cls.run_command(f"git clone {PCILEECH_FPGA_REPO} {repo_dir}")

                # Create last update timestamp
                with open(repo_dir / ".last_update", "w") as f:
                    f.write(datetime.datetime.now().isoformat())

                print("[✓] PCILeech FPGA repository cloned successfully")
            except Exception as e:
                raise RuntimeError(
                    f"Failed to clone PCILeech FPGA repository: {str(e)}"
                )

    @classmethod
    def get_board_path(cls, board_type: str) -> Path:
        """
        Get the path to the board directory in the pcileech-fpga repository.

        Args:
            board_type (str): The board type (e.g., "75t", "35t", "100t").

        Returns:
            Path: The path to the board directory.

        Raises:
            RuntimeError: If the board directory doesn't exist.
        """
        # Ensure repository is available
        cls.ensure_git_repo()

        # Board configuration mapping
        board_info = {
            # Original boards
            "35t": PCILEECH_FPGA_DIR / "PCIeSquirrel",
            "75t": PCILEECH_FPGA_DIR / "PCIeEnigmaX1",
            "100t": PCILEECH_FPGA_DIR / "XilinxZDMA",
            # CaptainDMA boards
            "pcileech_75t484_x1": PCILEECH_FPGA_DIR / "CaptainDMA" / "75t484_x1",
            "pcileech_35t484_x1": PCILEECH_FPGA_DIR / "CaptainDMA" / "35t484_x1",
            "pcileech_35t325_x4": PCILEECH_FPGA_DIR / "CaptainDMA" / "35t325_x4",
            "pcileech_35t325_x1": PCILEECH_FPGA_DIR / "CaptainDMA" / "35t325_x1",
            "pcileech_100t484_x1": PCILEECH_FPGA_DIR / "CaptainDMA" / "100t484-1",
            # Other boards
            "pcileech_enigma_x1": PCILEECH_FPGA_DIR / "EnigmaX1",
            "pcileech_squirrel": PCILEECH_FPGA_DIR / "PCIeSquirrel",
            "pcileech_pciescreamer_xc7a35": PCILEECH_FPGA_DIR / "pciescreamer",
        }

        if board_type not in board_info:
            raise RuntimeError(f"Unknown board type: {board_type}")

        board_path = board_info[board_type]
        if not board_path.exists():
            raise RuntimeError(
                f"Board directory not found: {board_path}\n"
                "Make sure the pcileech-fpga repository is properly cloned."
            )

        return board_path

    @classmethod
    def get_board_xdc_files(cls, board_type: str) -> list[Path]:
        """
        Get XDC constraint files for a specific board type.

        Args:
            board_type: The board type identifier (e.g., 'pcileech_75t484_x1')

        Returns:
            List of Path objects pointing to XDC files for the board

        Raises:
            RuntimeError: If the board directory doesn't exist or no XDC files found.
        """
        board_path = cls.get_board_path(board_type)
        
        # Search for XDC files in the board directory and subdirectories
        xdc_files = []
        
        # Common locations for XDC files in PCILeech FPGA repo
        search_paths = [
            board_path,
            board_path / "src",
            board_path / "constraints",
            board_path / "xdc"
        ]
        
        for search_path in search_paths:
            if search_path.exists():
                xdc_files.extend(search_path.glob("*.xdc"))
                # Also search recursively in subdirectories
                xdc_files.extend(search_path.rglob("*.xdc"))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_xdc_files = []
        for xdc_file in xdc_files:
            if xdc_file not in seen:
                seen.add(xdc_file)
                unique_xdc_files.append(xdc_file)
        
        if not unique_xdc_files:
            raise RuntimeError(
                f"No XDC files found for board type: {board_type}\n"
                f"Searched in: {board_path}"
            )
        
        return unique_xdc_files

    @classmethod
    def read_xdc_constraints(cls, board_type: str) -> str:
        """
        Read and combine XDC constraint files for a specific board type.

        Args:
            board_type: The board type identifier (e.g., 'pcileech_75t484_x1')

        Returns:
            Combined content of all XDC files for the board

        Raises:
            RuntimeError: If XDC files cannot be read.
        """
        xdc_files = cls.get_board_xdc_files(board_type)
        
        combined_content = []
        combined_content.append(f"# XDC constraints for board: {board_type}")
        combined_content.append(f"# Source files: {[str(f.name) for f in xdc_files]}")
        combined_content.append("")
        
        for xdc_file in xdc_files:
            try:
                with open(xdc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                combined_content.append(f"# === From {xdc_file.name} ===")
                combined_content.append(content)
                combined_content.append("")
                
            except Exception as e:
                raise RuntimeError(f"Failed to read XDC file {xdc_file}: {e}")
        
        return "\n".join(combined_content)


if __name__ == "__main__":
    # If run directly, ensure the repository is available
    RepoManager.ensure_git_repo()
    print("[✓] Repository check complete")
