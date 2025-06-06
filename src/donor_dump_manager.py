#!/usr/bin/env python3
"""
Donor Dump Kernel Module Manager

Provides functionality to build, load, and manage the donor_dump kernel module
for extracting PCI device parameters.
"""

import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import random

logger = logging.getLogger(__name__)


class DonorDumpError(Exception):
    """Base exception for donor dump operations"""

    pass


class KernelHeadersNotFoundError(DonorDumpError):
    """Raised when kernel headers are not available"""

    pass


class ModuleBuildError(DonorDumpError):
    """Raised when module build fails"""

    pass


class ModuleLoadError(DonorDumpError):
    """Raised when module loading fails"""

    pass


class DonorDumpManager:
    """Manager for donor_dump kernel module operations"""

    def __init__(self, module_source_dir: Optional[Path] = None, donor_info_path: Optional[str] = None):
        """
        Initialize the donor dump manager

        Args:
            module_source_dir: Path to donor_dump source directory
            donor_info_path: Path to donor information JSON file from previous run
        """
        if module_source_dir is None:
            # Default to src/donor_dump relative to this file
            self.module_source_dir = Path(__file__).parent / "donor_dump"
        else:
            self.module_source_dir = Path(module_source_dir)

        self.module_name = "donor_dump"
        self.proc_path = "/proc/donor_dump"
        self.donor_info_path = donor_info_path

    def check_kernel_headers(self) -> Tuple[bool, str]:
        """
        Check if kernel headers are available for the current kernel

        Returns:
            Tuple of (headers_available, kernel_version)
        """
        try:
            kernel_version = subprocess.check_output(["uname", "-r"], text=True).strip()

            headers_path = f"/lib/modules/{kernel_version}/build"
            headers_available = os.path.exists(headers_path)

            return headers_available, kernel_version
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get kernel version: {e}")
            return False, ""

    def install_kernel_headers(self, kernel_version: str) -> bool:
        """
        Attempt to install kernel headers for the specified version

        Args:
            kernel_version: Kernel version string

        Returns:
            True if installation succeeded
        """
        try:
            logger.info(f"Installing kernel headers for {kernel_version}")

            # Update package list first
            subprocess.run(
                ["sudo", "apt-get", "update"],
                check=True,
                capture_output=True,
                text=True,
            )

            # Install specific kernel headers
            subprocess.run(
                ["sudo", "apt-get", "install", "-y", f"linux-headers-{kernel_version}"],
                check=True,
                capture_output=True,
                text=True,
            )

            # Verify installation
            headers_available, _ = self.check_kernel_headers()
            return headers_available

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install kernel headers: {e}")
            return False

    def build_module(self, force_rebuild: bool = False) -> bool:
        """
        Build the donor_dump kernel module

        Args:
            force_rebuild: Force rebuild even if module exists

        Returns:
            True if build succeeded
        """
        if not self.module_source_dir.exists():
            raise ModuleBuildError(
                f"Module source directory not found: {self.module_source_dir}"
            )

        module_ko = self.module_source_dir / f"{self.module_name}.ko"

        # Check if module already exists and we're not forcing rebuild
        if module_ko.exists() and not force_rebuild:
            logger.info("Module already built, skipping build")
            return True

        # Check kernel headers
        headers_available, kernel_version = self.check_kernel_headers()
        if not headers_available:
            raise KernelHeadersNotFoundError(
                f"Kernel headers not found for {kernel_version}. "
                f"Install with: sudo apt-get install linux-headers-{kernel_version}"
            )

        try:
            logger.info("Building donor_dump kernel module...")

            # Clean first if forcing rebuild
            if force_rebuild:
                subprocess.run(
                    ["make", "clean"],
                    cwd=self.module_source_dir,
                    check=True,
                    capture_output=True,
                    text=True,
                )

            # Build the module
            result = subprocess.run(
                ["make"],
                cwd=self.module_source_dir,
                check=True,
                capture_output=True,
                text=True,
            )

            logger.info("Module build completed successfully")
            return True

        except subprocess.CalledProcessError as e:
            error_msg = f"Module build failed: {e}"
            if e.stderr:
                error_msg += f"\nStderr: {e.stderr}"
            raise ModuleBuildError(error_msg)

    def is_module_loaded(self) -> bool:
        """Check if the donor_dump module is currently loaded"""
        try:
            # Check if we're on Linux (lsmod available)
            result = subprocess.run(["which", "lsmod"], capture_output=True, text=True)
            if result.returncode != 0:
                # Not on Linux, module loading not supported
                return False

            result = subprocess.run(
                ["lsmod"], capture_output=True, text=True, check=True
            )
            return self.module_name in result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def load_module(self, bdf: str, force_reload: bool = False) -> bool:
        """
        Load the donor_dump module with specified BDF

        Args:
            bdf: PCI Bus:Device.Function (e.g., "0000:03:00.0")
            force_reload: Unload existing module first if loaded

        Returns:
            True if load succeeded
        """
        # Validate BDF format
        import re

        bdf_pattern = re.compile(
            r"^[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7]$"
        )
        if not bdf_pattern.match(bdf):
            raise ModuleLoadError(f"Invalid BDF format: {bdf}")

        # Check if module is already loaded
        if self.is_module_loaded():
            if force_reload:
                logger.info("Module already loaded, unloading first")
                self.unload_module()
            else:
                logger.info("Module already loaded")
                return True

        # Ensure module is built
        module_ko = self.module_source_dir / f"{self.module_name}.ko"
        if not module_ko.exists():
            logger.info("Module not built, building now...")
            self.build_module()

        try:
            logger.info(f"Loading donor_dump module with BDF {bdf}")
            subprocess.run(
                ["sudo", "insmod", str(module_ko), f"bdf={bdf}"],
                check=True,
                capture_output=True,
                text=True,
            )

            # Verify module loaded and proc file exists
            if not self.is_module_loaded():
                raise ModuleLoadError(
                    "Module load appeared to succeed but module not found in lsmod"
                )

            if not os.path.exists(self.proc_path):
                raise ModuleLoadError(f"Module loaded but {self.proc_path} not created")

            logger.info("Module loaded successfully")
            return True

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to load module: {e}"
            if e.stderr:
                error_msg += f"\nStderr: {e.stderr}"
            raise ModuleLoadError(error_msg)

    def unload_module(self) -> bool:
        """
        Unload the donor_dump module

        Returns:
            True if unload succeeded
        """
        if not self.is_module_loaded():
            logger.info("Module not loaded")
            return True

        try:
            logger.info("Unloading donor_dump module")
            subprocess.run(
                ["sudo", "rmmod", self.module_name],
                check=True,
                capture_output=True,
                text=True,
            )

            logger.info("Module unloaded successfully")
            return True

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to unload module: {e}"
            if e.stderr:
                error_msg += f"\nStderr: {e.stderr}"
            raise ModuleLoadError(error_msg)

    def generate_donor_info(self, device_type: str = "generic") -> Dict[str, str]:
        """
        Generate synthetic donor information for local builds

        Args:
            device_type: Type of device to generate info for (generic, network, storage, etc.)

        Returns:
            Dictionary of synthetic device parameters
        """
        logger.info(f"Generating synthetic donor information for {device_type} device")
        
        # Common device profiles
        device_profiles = {
            "generic": {
                "vendor_id": "0x8086",  # Intel
                "device_id": "0x1533",  # I210 Gigabit Network Connection
                "subvendor_id": "0x8086",
                "subsystem_id": "0x0000",
                "revision_id": "0x03",
                "bar_size": "0x20000",  # 128KB
                "mpc": "0x02",  # Max payload size capability (512 bytes)
                "mpr": "0x02",  # Max read request size (512 bytes)
            },
            "network": {
                "vendor_id": "0x8086",  # Intel
                "device_id": "0x1533",  # I210 Gigabit Network Connection
                "subvendor_id": "0x8086",
                "subsystem_id": "0x0000",
                "revision_id": "0x03",
                "bar_size": "0x20000",  # 128KB
                "mpc": "0x02",  # Max payload size capability (512 bytes)
                "mpr": "0x02",  # Max read request size (512 bytes)
            },
            "storage": {
                "vendor_id": "0x8086",  # Intel
                "device_id": "0x2522",  # NVMe SSD Controller
                "subvendor_id": "0x8086",
                "subsystem_id": "0x0000",
                "revision_id": "0x01",
                "bar_size": "0x40000",  # 256KB
                "mpc": "0x03",  # Max payload size capability (1024 bytes)
                "mpr": "0x03",  # Max read request size (1024 bytes)
            },
        }
        
        # Use the specified device profile or fall back to generic
        profile = device_profiles.get(device_type, device_profiles["generic"])
        
        # Add some randomness to make it look more realistic
        if random.random() > 0.5:
            profile["revision_id"] = f"0x{random.randint(1, 5):02x}"
        
        return profile

    def save_donor_info(self, device_info: Dict[str, str], output_path: str) -> bool:
        """
        Save donor information to a JSON file for future use

        Args:
            device_info: Device information dictionary
            output_path: Path to save the JSON file

        Returns:
            True if data was saved successfully
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            with open(output_path, "w") as f:
                json.dump(device_info, f, indent=2)
            logger.info(f"Saved donor information to {output_path}")
            return True
        except IOError as e:
            logger.error(f"Failed to save donor information: {e}")
            return False

    def read_device_info(self) -> Dict[str, str]:
        """
        Read device information from /proc/donor_dump

        Returns:
            Dictionary of device parameters
        """
        if not os.path.exists(self.proc_path):
            raise DonorDumpError(f"Module not loaded or {self.proc_path} not available")

        try:
            device_info = {}
            with open(self.proc_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if ":" in line:
                        key, value = line.split(":", 1)
                        device_info[key.strip()] = value.strip()

            return device_info

        except IOError as e:
            raise DonorDumpError(f"Failed to read device info: {e}")

    def get_module_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of the donor_dump module

        Returns:
            Dictionary with status information
        """
        headers_available, kernel_version = self.check_kernel_headers()
        module_ko = self.module_source_dir / f"{self.module_name}.ko"

        status = {
            "kernel_version": kernel_version,
            "headers_available": headers_available,
            "module_built": module_ko.exists(),
            "module_loaded": self.is_module_loaded(),
            "proc_available": os.path.exists(self.proc_path),
            "source_dir_exists": self.module_source_dir.exists(),
        }

        if module_ko.exists():
            status["module_path"] = str(module_ko)
            status["module_size"] = module_ko.stat().st_size

        return status
        
    def check_module_installation(self) -> Dict[str, Any]:
        """
        Check if the donor_dump kernel module is installed properly and provide detailed status
        
        Returns:
            Dictionary with detailed status information including:
            - status: overall status (installed, not_installed, built_not_loaded, etc.)
            - details: detailed description of the status
            - issues: list of identified issues
            - fixes: list of suggested fixes for the issues
        """
        # Get basic module status
        status_info = self.get_module_status()
        
        result = {
            "status": "unknown",
            "details": "",
            "issues": [],
            "fixes": [],
            "raw_status": status_info
        }
        
        # Check if module is fully installed and working
        if status_info["module_loaded"] and status_info["proc_available"]:
            result["status"] = "installed"
            result["details"] = "Donor dump kernel module is properly installed and loaded"
            return result
            
        # Check if module is built but not loaded
        if status_info["module_built"] and not status_info["module_loaded"]:
            result["status"] = "built_not_loaded"
            result["details"] = "Module is built but not currently loaded"
            result["issues"].append("Module is not loaded into the kernel")
            result["fixes"].append(f"Load the module with: sudo insmod {status_info.get('module_path', 'donor_dump.ko')} bdf=YOUR_DEVICE_BDF")
            result["fixes"].append("Or use the DonorDumpManager.load_module() function with your device BDF")
            return result
            
        # Check if source exists but module is not built
        if status_info["source_dir_exists"] and not status_info["module_built"]:
            result["status"] = "not_built"
            result["details"] = "Module source exists but has not been built"
            
            # Check if headers are available
            if not status_info["headers_available"]:
                result["issues"].append(f"Kernel headers not found for kernel {status_info['kernel_version']}")
                result["fixes"].append(f"Install kernel headers: sudo apt-get install linux-headers-{status_info['kernel_version']}")
            else:
                result["issues"].append("Module has not been built yet")
                result["fixes"].append(f"Build the module: cd {self.module_source_dir} && make")
                result["fixes"].append("Or use the DonorDumpManager.build_module() function")
            
            return result
            
        # Check if source directory doesn't exist
        if not status_info["source_dir_exists"]:
            result["status"] = "missing_source"
            result["details"] = "Module source directory not found"
            result["issues"].append(f"Source directory not found at {self.module_source_dir}")
            result["fixes"].append("Ensure the PCILeech Firmware Generator is properly installed")
            result["fixes"].append("Check if the donor_dump directory exists in the src directory")
            return result
            
        # Module is loaded but proc file is not available
        if status_info["module_loaded"] and not status_info["proc_available"]:
            result["status"] = "loaded_but_error"
            result["details"] = "Module is loaded but /proc/donor_dump is not available"
            result["issues"].append("Module loaded with errors or incorrect parameters")
            result["fixes"].append("Unload the module: sudo rmmod donor_dump")
            result["fixes"].append("Check kernel logs for errors: dmesg | grep donor_dump")
            result["fixes"].append("Reload with correct BDF: sudo insmod donor_dump.ko bdf=YOUR_DEVICE_BDF")
            return result
            
        # Fallback for any other state
        result["status"] = "unknown_error"
        result["details"] = "Unknown module installation state"
        result["issues"].append("Could not determine module status")
        result["fixes"].append("Check the module source directory and build logs")
        result["fixes"].append("Try rebuilding the module: make clean && make")
        
        return result

    def setup_module(
        self, bdf: str, auto_install_headers: bool = False, save_to_file: Optional[str] = None,
        generate_if_unavailable: bool = False, device_type: str = "generic"
    ) -> Dict[str, str]:
        """
        Complete setup process: check headers, build, load module, and read info

        Args:
            bdf: PCI Bus:Device.Function
            auto_install_headers: Automatically install headers if missing
            save_to_file: Path to save donor information for future use
            generate_if_unavailable: Generate synthetic donor info if module setup fails
            device_type: Type of device to generate info for if needed

        Returns:
            Device information dictionary
        """
        try:
            logger.info(f"Setting up donor_dump module for device {bdf}")

            # Check kernel headers
            headers_available, kernel_version = self.check_kernel_headers()
            if not headers_available:
                if auto_install_headers:
                    logger.info("Kernel headers missing, attempting to install...")
                    if not self.install_kernel_headers(kernel_version):
                        raise KernelHeadersNotFoundError(
                            f"Failed to install kernel headers for {kernel_version}"
                        )
                else:
                    raise KernelHeadersNotFoundError(
                        f"Kernel headers not found for {kernel_version}. "
                        f"Install with: sudo apt-get install linux-headers-{kernel_version}"
                    )

            # Build module
            self.build_module()

            # Load module
            self.load_module(bdf)

            # Read device info
            device_info = self.read_device_info()
            
            # Save to file if requested
            if save_to_file and device_info:
                self.save_donor_info(device_info, save_to_file)
                
            return device_info
            
        except Exception as e:
            logger.error(f"Failed to set up donor_dump module: {e}")
            
            if generate_if_unavailable:
                logger.info("Generating synthetic donor information as fallback")
                device_info = self.generate_donor_info(device_type)
                
                # Save to file if requested
                if save_to_file and device_info:
                    self.save_donor_info(device_info, save_to_file)
                    
                return device_info
            else:
                raise


def main():
    """CLI interface for donor dump manager"""
    import argparse

    parser = argparse.ArgumentParser(description="Donor Dump Kernel Module Manager")
    parser.add_argument(
        "--bdf", required=True, help="PCIe Bus:Device.Function (e.g., 0000:03:00.0)"
    )
    parser.add_argument("--source-dir", help="Path to donor_dump source directory")
    parser.add_argument(
        "--auto-install-headers",
        action="store_true",
        help="Automatically install kernel headers if missing",
    )
    parser.add_argument(
        "--force-rebuild", action="store_true", help="Force rebuild of kernel module"
    )
    parser.add_argument(
        "--unload", action="store_true", help="Unload the module instead of loading"
    )
    parser.add_argument("--status", action="store_true", help="Show module status")
    parser.add_argument(
        "--save-to", help="Save donor information to specified file"
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate synthetic donor information if module setup fails",
    )
    parser.add_argument(
        "--device-type",
        choices=["generic", "network", "storage"],
        default="generic",
        help="Device type for synthetic donor information",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    try:
        manager = DonorDumpManager(args.source_dir)

        if args.status:
            status = manager.get_module_status()
            print("Donor Dump Module Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
            return

        if args.unload:
            manager.unload_module()
            print("Module unloaded successfully")
            return

        # Setup and read device info
        device_info = manager.setup_module(
            args.bdf,
            auto_install_headers=args.auto_install_headers,
            save_to_file=args.save_to,
            generate_if_unavailable=args.generate,
            device_type=args.device_type
        )

        print(f"Device information for {args.bdf}:")
        for key, value in device_info.items():
            print(f"  {key}: {value}")

    except DonorDumpError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
