#!/usr/bin/env python3
"""
File Management Module

Handles file operations, cleanup, and validation for PCILeech firmware building.
"""

import fnmatch
import hashlib
import json
import logging
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List

from ..device_clone.constants import (PCILEECH_BUILD_SCRIPT,
                                      PCILEECH_PROJECT_SCRIPT)

logger = logging.getLogger(__name__)
try:
    from ..string_utils import log_info_safe, log_warning_safe, safe_format
except ImportError:
    try:
        from string_utils import log_info_safe, log_warning_safe, safe_format
    except ImportError:
        # Fallback implementations if string_utils not available
        def log_info_safe(logger, template, **kwargs):
            try:
                message = template.format(**kwargs) if kwargs else template
                logger.info(message)
            except Exception:
                logger.info(template)

        def log_warning_safe(logger, template, **kwargs):
            try:
                message = template.format(**kwargs) if kwargs else template
                logger.warning(message)
            except Exception:
                logger.warning(template)

        def safe_format(template, **kwargs):
            try:
                return template.format(**kwargs)
            except Exception:
                return template


class FileManager:
    """Manages file operations for PCILeech firmware building."""

    def __init__(
        self,
        output_dir: Path,
        min_bitstream_size_mb: float = 0.5,
        max_bitstream_size_mb: float = 10.0,
    ):
        self.output_dir = output_dir
        self.min_bitstream_size_mb = min_bitstream_size_mb
        self.max_bitstream_size_mb = max_bitstream_size_mb

    def create_pcileech_structure(
        self, src_dir: str = "src", ip_dir: str = "ip"
    ) -> Dict[str, Path]:
        """
        Create PCILeech directory structure with src/ and ip/ directories.

        Args:
            src_dir: Name of the source directory (default: "src")
            ip_dir: Name of the IP directory (default: "ip")

        Returns:
            Dictionary mapping directory names to Path objects
        """
        directories = {}

        # Create source directory
        src_path = self.output_dir / src_dir
        src_path.mkdir(parents=True, exist_ok=True)
        directories["src"] = src_path

        # Create IP directory
        ip_path = self.output_dir / ip_dir
        ip_path.mkdir(parents=True, exist_ok=True)
        directories["ip"] = ip_path

        logger.info(f"Created PCILeech directory structure:")
        logger.info(f"  Source directory: {src_path}")
        logger.info(f"  IP directory: {ip_path}")

        return directories

    def write_to_src_directory(
        self, filename: str, content: str, src_dir: str = "src"
    ) -> Path:
        """
        Write content to a file in the PCILeech src directory.

        Args:
            filename: Name of the file to write
            content: Content to write to the file
            src_dir: Name of the source directory (default: "src")

        Returns:
            Path to the written file
        """
        src_path = self.output_dir / src_dir
        src_path.mkdir(parents=True, exist_ok=True)

        file_path = src_path / filename
        with open(file_path, "w") as f:
            f.write(content)

        logger.info(f"Written file to src directory: {filename}")
        return file_path

    def write_to_ip_directory(
        self, filename: str, content: str, ip_dir: str = "ip"
    ) -> Path:
        """
        Write content to a file in the PCILeech ip directory.

        Args:
            filename: Name of the file to write
            content: Content to write to the file
            ip_dir: Name of the IP directory (default: "ip")

        Returns:
            Path to the written file
        """
        ip_path = self.output_dir / ip_dir
        ip_path.mkdir(parents=True, exist_ok=True)

        file_path = ip_path / filename
        with open(file_path, "w") as f:
            f.write(content)

        logger.info(f"Written file to ip directory: {filename}")
        return file_path

    def cleanup_intermediate_files(self) -> List[str]:
        """Clean up intermediate files, keeping only final outputs and logs."""
        preserved_files = []
        cleaned_files = []

        # Define patterns for files to preserve
        preserve_patterns = [
            "*.bit",  # Final bitstream
            "*.mcs",  # Flash memory file
            "*.ltx",  # Debug probes
            "*.dcp",  # Design checkpoint
            "*.log",  # Log files
            "*.rpt",  # Report files
            "build_firmware.tcl",  # Final TCL build script
            "*.tcl",  # All TCL files (preserve in-place)
            "*.sv",  # SystemVerilog source files (needed for build)
            "*.v",  # Verilog source files (needed for build)
            "*.xdc",  # Constraint files (needed for build)
            "*.hex",
        ]

        # Define patterns for files/directories to clean
        cleanup_patterns = [
            "vivado_project/",  # Vivado project directory
            "project_dir/",  # Alternative project directory
            "*.json",  # JSON files (intermediate)
            "*.jou",  # Vivado journal files
            "*.str",  # Vivado strategy files
            ".Xil/",  # Xilinx temporary directory
        ]

        logger.info("Starting cleanup of intermediate files...")

        try:
            # Get all files in output directory
            all_files = list(self.output_dir.rglob("*"))

            for file_path in all_files:
                should_preserve = False

                # Check if file should be preserved
                for pattern in preserve_patterns:
                    if fnmatch.fnmatch(file_path.name, pattern):
                        should_preserve = True
                        preserved_files.append(str(file_path))
                        break

                # If not preserved, check if it should be cleaned
                if not should_preserve:
                    # Handle cleanup patterns
                    for pattern in cleanup_patterns:
                        if pattern.endswith("/"):
                            # Directory pattern
                            if file_path.is_dir() and fnmatch.fnmatch(
                                file_path.name + "/", pattern
                            ):
                                try:
                                    shutil.rmtree(file_path)
                                    cleaned_files.append(str(file_path))
                                    log_info_safe(
                                        logger,
                                        "Cleaned directory: {filename}",
                                        filename=file_path.name,
                                    )
                                except PermissionError as e:
                                    log_warning_safe(
                                        logger,
                                        "Permission denied while cleaning directory {filename} (path: {filepath}): {error}",
                                        filename=file_path.name,
                                        filepath=file_path,
                                        error=e,
                                    )
                                except FileNotFoundError as e:
                                    log_warning_safe(
                                        logger,
                                        "Directory not found during cleanup {filename} (path: {filepath}): {error}",
                                        filename=file_path.name,
                                        filepath=file_path,
                                        error=e,
                                    )
                                except Exception as e:
                                    log_warning_safe(
                                        logger,
                                        "Unexpected error while cleaning directory {filename} (path: {filepath}): {error}",
                                        filename=file_path.name,
                                        filepath=file_path,
                                        error=e,
                                    )
                                break
                        else:
                            # File pattern
                            if file_path.is_file() and fnmatch.fnmatch(
                                file_path.name, pattern
                            ):
                                try:
                                    file_path.unlink()
                                    cleaned_files.append(str(file_path))
                                    logger.debug(f"Cleaned file: {file_path.name}")
                                except Exception as e:
                                    log_warning_safe(
                                        logger,
                                        "Could not clean file {filename} (path: {filepath}): {error}",
                                        filename=file_path.name,
                                        filepath=file_path,
                                        error=e,
                                    )
                                break

            log_info_safe(
                logger,
                "Cleanup completed: preserved {preserved_count} files, cleaned {cleaned_count} items",
                preserved_count=len(preserved_files),
                cleaned_count=len(cleaned_files),
            )

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

        return preserved_files

    def validate_final_outputs(self) -> Dict[str, Any]:
        """Validate and provide information about final output files."""
        validation_results = {
            "bitstream_info": None,
            "flash_file_info": None,
            "debug_file_info": None,
            "tcl_file_info": None,
            "reports_info": [],
            "validation_status": "unknown",
            "file_sizes": {},
            "checksums": {},
            "build_mode": "unknown",
        }

        try:
            # Check for TCL build file (main output when Vivado not available)
            # First check for legacy files for backward compatibility
            tcl_files = list(self.output_dir.glob("build_firmware.tcl"))
            if not tcl_files:
                # Also check for fallback TCL file name
                tcl_files = list(self.output_dir.glob("build_all.tcl"))

            # If no legacy files found, check for PCILeech script names
            if not tcl_files:
                tcl_files = list(self.output_dir.glob(PCILEECH_BUILD_SCRIPT))
            if not tcl_files:
                tcl_files = list(self.output_dir.glob(PCILEECH_PROJECT_SCRIPT))
            if tcl_files:
                tcl_file = tcl_files[0]
                file_size = tcl_file.stat().st_size

                with open(tcl_file, "r") as f:
                    content = f.read()
                    file_hash = hashlib.sha256(content.encode()).hexdigest()

                # Check if TCL script contains hex generation commands
                has_hex_generation = (
                    "write_cfgmem" in content
                    and "format hex" in content
                    and ".hex" in content
                ) or "07_bitstream.tcl" in content

                # For master build scripts, check for sourcing of individual scripts
                # rather than direct commands
                has_device_config = (
                    "CONFIG.Device_ID" in content
                    or "02_ip_config.tcl" in content
                    or "Device:" in content
                )

                has_synthesis = (
                    "launch_runs synth_1" in content or "05_synthesis.tcl" in content
                )

                has_implementation = (
                    "launch_runs impl_1" in content
                    or "06_implementation.tcl" in content
                )

                validation_results["tcl_file_info"] = {
                    "filename": tcl_file.name,
                    "size_bytes": file_size,
                    "size_kb": round(file_size / 1024, 2),
                    "sha256": file_hash,
                    "has_device_config": has_device_config,
                    "has_synthesis": has_synthesis,
                    "has_implementation": has_implementation,
                    "has_hex_generation": has_hex_generation,
                }
                validation_results["file_sizes"][tcl_file.name] = file_size
                validation_results["checksums"][tcl_file.name] = file_hash

                # Check for actual hex files (only if Vivado was run)
                hex_files = list(self.output_dir.glob("*.hex"))
                if hex_files:
                    hex_file = hex_files[0]
                    hex_size = hex_file.stat().st_size
                    validation_results["tcl_file_info"]["hex_file"] = {
                        "filename": hex_file.name,
                        "size_bytes": hex_size,
                        "size_kb": round(hex_size / 1024, 2),
                    }
                    validation_results["file_sizes"][hex_file.name] = hex_size
                else:
                    # For TCL-only builds, check if hex generation commands are present
                    validation_results["tcl_file_info"]["hex_file"] = has_hex_generation

            # Check for bitstream file (only if Vivado was run)
            bitstream_files = list(self.output_dir.glob("*.bit"))
            if bitstream_files:
                bitstream_file = bitstream_files[0]
                file_size = bitstream_file.stat().st_size

                # Calculate checksum
                with open(bitstream_file, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()

                validation_results["bitstream_info"] = {
                    "filename": bitstream_file.name,
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "sha256": file_hash,
                    "created": bitstream_file.stat().st_mtime,
                }
                validation_results["file_sizes"][bitstream_file.name] = file_size
                validation_results["checksums"][bitstream_file.name] = file_hash
                validation_results["build_mode"] = "full_vivado"
            else:
                validation_results["build_mode"] = "tcl_only"

            # Check for MCS flash file
            mcs_files = list(self.output_dir.glob("*.mcs"))
            if mcs_files:
                mcs_file = mcs_files[0]
                file_size = mcs_file.stat().st_size

                with open(mcs_file, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()

                validation_results["flash_file_info"] = {
                    "filename": mcs_file.name,
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "sha256": file_hash,
                }
                validation_results["file_sizes"][mcs_file.name] = file_size
                validation_results["checksums"][mcs_file.name] = file_hash

            # Check for debug file
            ltx_files = list(self.output_dir.glob("*.ltx"))
            if ltx_files:
                ltx_file = ltx_files[0]
                file_size = ltx_file.stat().st_size

                validation_results["debug_file_info"] = {
                    "filename": ltx_file.name,
                    "size_bytes": file_size,
                }
                validation_results["file_sizes"][ltx_file.name] = file_size

            # Check for report files
            report_files = list(self.output_dir.glob("*.rpt"))
            for report_file in report_files:
                file_size = report_file.stat().st_size
                validation_results["reports_info"].append(
                    {
                        "filename": report_file.name,
                        "size_bytes": file_size,
                        "type": self._determine_report_type(report_file.name),
                    }
                )
                validation_results["file_sizes"][report_file.name] = file_size

            # Determine overall validation status
            if validation_results["tcl_file_info"]:
                if validation_results["build_mode"] == "full_vivado":
                    # Full Vivado build - check bitstream
                    if validation_results["bitstream_info"]:
                        if (
                            validation_results["bitstream_info"]["size_bytes"] > 1000000
                        ):  # > 1MB
                            validation_results["validation_status"] = (
                                "success_full_build"
                            )
                        else:
                            validation_results["validation_status"] = (
                                "warning_small_bitstream"
                            )
                    else:
                        validation_results["validation_status"] = "failed_no_bitstream"
                else:
                    # TCL-only build - check TCL file quality (this is the main output)
                    tcl_info = validation_results["tcl_file_info"]
                    if tcl_info["has_device_config"] and tcl_info["size_bytes"] > 1000:
                        validation_results["validation_status"] = "success_tcl_ready"
                    else:
                        validation_results["validation_status"] = (
                            "warning_incomplete_tcl"
                        )
                    # Check if hex generation commands are present in TCL script
                    if not tcl_info.get("has_hex_generation", False):
                        validation_results["validation_status"] = "warning_missing_hex"
            else:
                validation_results["validation_status"] = "failed_no_tcl"

        except Exception as e:
            logger.error(f"Error during output validation: {e}")
            validation_results["validation_status"] = "error"

        return validation_results

    def _determine_report_type(self, filename: str) -> str:
        """Determine the type of report based on filename."""
        if "timing" in filename.lower():
            return "timing_analysis"
        elif "utilization" in filename.lower():
            return "resource_utilization"
        elif "power" in filename.lower():
            return "power_analysis"
        elif "drc" in filename.lower():
            return "design_rule_check"
        else:
            return "general"

    def generate_project_file(
        self, device_info: Dict[str, Any], board: str
    ) -> Dict[str, Any]:
        """Generate project configuration file."""
        return {
            "project_name": "pcileech_firmware",
            "board": board,
            "device_info": device_info,
            "build_timestamp": time.time(),
            "build_version": "1.0.0",
            "features": {
                "advanced_sv": False,  # Will be updated by caller if needed
                "manufacturing_variance": False,  # Will be updated by caller if needed
                "behavior_profiling": False,  # Will be updated by caller if needed
            },
        }

    def generate_file_manifest(
        self, device_info: Dict[str, Any], board: str
    ) -> Dict[str, Any]:
        """Generate a manifest of all files for verification."""
        manifest = {
            "project_info": {
                "device": f"{device_info['vendor_id']}:{device_info['device_id']}",
                "board": board,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "files": {
                "systemverilog": [],
                "verilog": [],
                "constraints": [],
                "tcl_scripts": [],
                "generated": [],
            },
            "validation": {
                "required_files_present": True,
                "top_module_identified": False,
                "build_script_ready": False,
            },
        }

        # Check for files in output directory
        output_files = list(self.output_dir.glob("*"))

        for file_path in output_files:
            if file_path.suffix == ".sv":
                manifest["files"]["systemverilog"].append(file_path.name)
                if "top" in file_path.name.lower():
                    manifest["validation"]["top_module_identified"] = True
            elif file_path.suffix == ".v":
                manifest["files"]["verilog"].append(file_path.name)
            elif file_path.suffix == ".xdc":
                manifest["files"]["constraints"].append(file_path.name)
            elif file_path.suffix == ".tcl":
                manifest["files"]["tcl_scripts"].append(file_path.name)
                if "build" in file_path.name:
                    manifest["validation"]["build_script_ready"] = True
            elif file_path.suffix == ".json":
                manifest["files"]["generated"].append(file_path.name)

        return manifest

    def copy_pcileech_sources(self, board: str) -> Dict[str, List[str]]:
        """Copy PCILeech source files to output directory."""
        copied_files = {
            "systemverilog": [],
            "verilog": [],
            "packages": [],
            "constraints": [],
            "ip_files": [],
        }

        try:
            # Import repo manager
            from ..file_management.repo_manager import RepoManager

            # Ensure PCILeech repository is available
            repo_path = RepoManager.ensure_repo()
            logger.info(f"Using PCILeech repository at: {repo_path}")

            # Get board-specific path
            board_path = RepoManager.get_board_path(board, repo_root=repo_path)
            logger.info(f"Board path: {board_path}")

            # Create source directory structure
            src_dir = self.output_dir / "src"
            src_dir.mkdir(parents=True, exist_ok=True)

            # Copy board-specific source files
            if board_path.exists():
                # Look for SystemVerilog/Verilog files in board directory
                for pattern in ["*.sv", "*.v"]:
                    for src_file in board_path.rglob(pattern):
                        if src_file.is_file():
                            dest_file = src_dir / src_file.name
                            shutil.copy2(src_file, dest_file)

                            if src_file.suffix == ".sv":
                                copied_files["systemverilog"].append(str(dest_file))
                            else:
                                copied_files["verilog"].append(str(dest_file))

                            logger.info(f"Copied source file: {src_file.name}")

                # Copy package files
                for pkg_file in board_path.rglob("*_pkg.sv*"):
                    if pkg_file.is_file():
                        dest_file = src_dir / pkg_file.name
                        shutil.copy2(pkg_file, dest_file)
                        copied_files["packages"].append(str(dest_file))
                        logger.info(f"Copied package file: {pkg_file.name}")

            # Copy local PCILeech files from project directory
            local_pcileech_dir = Path(__file__).parent.parent.parent / "pcileech"
            if local_pcileech_dir.exists():
                logger.info(f"Copying local PCILeech files from: {local_pcileech_dir}")

                # Copy package files
                for pkg_file in local_pcileech_dir.glob("*.svh"):
                    dest_file = src_dir / pkg_file.name
                    shutil.copy2(pkg_file, dest_file)
                    copied_files["packages"].append(str(dest_file))
                    logger.info(f"Copied local package: {pkg_file.name}")

                # Copy RTL files
                rtl_dir = local_pcileech_dir / "rtl"
                if rtl_dir.exists():
                    for rtl_file in rtl_dir.glob("*.sv"):
                        dest_file = src_dir / rtl_file.name
                        shutil.copy2(rtl_file, dest_file)
                        copied_files["systemverilog"].append(str(dest_file))
                        logger.info(f"Copied local RTL: {rtl_file.name}")

            # Copy constraint files using repo manager
            try:
                xdc_files = RepoManager.get_xdc_files(board, repo_root=repo_path)
                constraints_dir = self.output_dir / "constraints"
                constraints_dir.mkdir(parents=True, exist_ok=True)

                for xdc_file in xdc_files:
                    dest_file = constraints_dir / xdc_file.name
                    shutil.copy2(xdc_file, dest_file)
                    copied_files["constraints"].append(str(dest_file))
                    logger.info(f"Copied constraint file: {xdc_file.name}")

            except Exception as e:
                logger.warning(f"Could not copy constraint files: {e}")

            # Log summary
            total_files = sum(len(files) for files in copied_files.values())
            logger.info(f"Successfully copied {total_files} PCILeech source files")

        except ImportError as e:
            logger.error(f"Could not import repo manager: {e}")
        except Exception as e:
            logger.error(f"Error copying PCILeech sources: {e}")

        return copied_files

    def get_source_file_lists(self) -> Dict[str, List[str]]:
        """Get lists of source files in the output directory for TCL generation."""
        file_lists = {
            "systemverilog_files": [],
            "verilog_files": [],
            "constraint_files": [],
            "package_files": [],
            "ip_files": [],
        }

        # Scan source directory
        src_dir = self.output_dir / "src"
        if src_dir.exists():
            # SystemVerilog files
            for sv_file in src_dir.glob("*.sv"):
                file_lists["systemverilog_files"].append(f"src/{sv_file.name}")

            # Verilog files
            for v_file in src_dir.glob("*.v"):
                file_lists["verilog_files"].append(f"src/{v_file.name}")

            # Package files
            for pkg_file in src_dir.glob("*_pkg.sv*"):
                file_lists["package_files"].append(f"src/{pkg_file.name}")

        # Scan constraints directory
        constraints_dir = self.output_dir / "constraints"
        if constraints_dir.exists():
            for xdc_file in constraints_dir.glob("*.xdc"):
                file_lists["constraint_files"].append(f"constraints/{xdc_file.name}")

        # Scan IP directory
        ip_dir = self.output_dir / "ip"
        if ip_dir.exists():
            for ip_file in ip_dir.glob("*"):
                if ip_file.is_file():
                    file_lists["ip_files"].append(f"ip/{ip_file.name}")

        return file_lists

        # Validate required files
        required_files = ["device_config.sv", "pcileech_top.sv"]
        manifest["validation"]["required_files_present"] = all(
            f.lower() in [file.lower() for file in manifest["files"]["systemverilog"]]
            for f in required_files
        )

        return manifest

    def print_final_output_info(self, validation_results: Dict[str, Any]):
        """Print detailed information about final output files."""
        logger.info("=" * 80)
        logger.info("FINAL BUILD OUTPUT VALIDATION")
        logger.info("=" * 80)

        build_mode = validation_results["build_mode"]
        status = validation_results["validation_status"]

        # Display build status
        if status == "success_full_build":
            logger.info("BUILD STATUS: SUCCESS (Full Vivado Build)")
        elif status == "success_tcl_ready":
            logger.info("BUILD STATUS: SUCCESS (TCL Build Script Ready)")
        elif status == "warning_small_bitstream":
            logger.warning("BUILD STATUS: WARNING - Bitstream file is unusually small")
        elif status == "warning_incomplete_tcl":
            logger.warning("BUILD STATUS: WARNING - TCL script may be incomplete")
        elif status == "warning_missing_hex":
            logger.warning(
                "BUILD STATUS: WARNING - No hex file generated in TCL script"
            )
        elif status == "failed_no_bitstream":
            logger.error("BUILD STATUS: FAILED - No bitstream file generated")
        elif status == "failed_no_tcl":
            logger.error("BUILD STATUS: FAILED - No TCL build script generated")
        else:
            logger.error("BUILD STATUS: ERROR - Validation failed")

        logger.info(f"BUILD MODE: {build_mode.replace('_', ' ').title()}")

        # TCL file information (always show if present)
        if validation_results.get("tcl_file_info"):
            info = validation_results["tcl_file_info"]
            print("\n📜 BUILD SCRIPT:")
            print(f"   File: {info['filename']}")
            print(
                safe_format(
                    "   Size: {size_kb} KB ({size_bytes:,} bytes)",
                    size_kb=info["size_kb"],
                    size_bytes=info["size_bytes"],
                )
            )
            print(f"   SHA256: {info['sha256'][:16]}...")

            # TCL script validation
            features = []
            if info["has_device_config"]:
                features.append("✅ Device-specific configuration")
            else:
                features.append("❌ Missing device configuration")

            if info["has_synthesis"]:
                features.append("✅ Synthesis commands")
            else:
                features.append("⚠️  No synthesis commands")

            if info["has_implementation"]:
                features.append("✅ Implementation commands")
            else:
                features.append("⚠️  No implementation commands")

            if info.get("has_hex_generation", False):
                features.append("✅ Hex file generation commands")
            else:
                features.append("⚠️  No hex file generation commands")

            print("   Features:")
            for feature in features:
                print(f"     {feature}")

        # Bitstream information (only if Vivado was run)
        if validation_results.get("bitstream_info"):
            info = validation_results["bitstream_info"]
            print("\n📁 BITSTREAM FILE:")
            print(f"   File: {info['filename']}")
            print(
                safe_format(
                    "   Size: {size_mb} MB ({size_bytes:,} bytes)",
                    size_mb=info["size_mb"],
                    size_bytes=info["size_bytes"],
                )
            )
            print(f"   SHA256: {info['sha256'][:16]}...")

            # Validate bitstream size
            if info["size_mb"] < self.min_bitstream_size_mb:
                print(
                    f"   ⚠️  WARNING: Bitstream is very small (less than {self.min_bitstream_size_mb} MB), may be incomplete"
                )
            elif info["size_mb"] > self.max_bitstream_size_mb:
                print(
                    f"   ⚠️  WARNING: Bitstream is very large (greater than {self.max_bitstream_size_mb} MB), check for issues"
                )
            else:
                print("   ✅ Bitstream size looks normal")

        # Flash file information
        if validation_results.get("flash_file_info"):
            info = validation_results["flash_file_info"]
            print("\n💾 FLASH FILE:")
            print(f"   File: {info['filename']}")
            print(
                safe_format(
                    "   Size: {size_mb} MB ({size_bytes:,} bytes)",
                    size_mb=info["size_mb"],
                    size_bytes=info["size_bytes"],
                )
            )
            print(f"   SHA256: {info['sha256'][:16]}...")

        # Debug file information
        if validation_results.get("debug_file_info"):
            info = validation_results["debug_file_info"]
            print("\n🔍 DEBUG FILE:")
            print(f"   File: {info['filename']}")
            print(f"   Size: {info['size_bytes']:,} bytes")

        # Report files
        if validation_results.get("reports_info"):
            print("\n📊 ANALYSIS REPORTS:")
            for report in validation_results["reports_info"]:
                print(
                    f"   {report['filename']} ({report['type']}) - {report['size_bytes']:,} bytes"
                )

        # File checksums
        if validation_results.get("checksums"):
            print("\n🔐 FILE CHECKSUMS (for verification):")
            for filename, checksum in validation_results["checksums"].items():
                print(f"   {filename}: {checksum[:16]}...")  # Show first 16 characters

        print("\n" + "=" * 80)
        if build_mode == "tcl_only":
            print("TCL build script is ready! Run with Vivado to generate bitstream.")
        else:
            print("Build output files are ready for deployment!")
        print("=" * 80 + "\n")
