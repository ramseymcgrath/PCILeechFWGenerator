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
    
    def __init__(self, module_source_dir: Optional[Path] = None):
        """
        Initialize the donor dump manager
        
        Args:
            module_source_dir: Path to donor_dump source directory
        """
        if module_source_dir is None:
            # Default to src/donor_dump relative to this file
            self.module_source_dir = Path(__file__).parent / "donor_dump"
        else:
            self.module_source_dir = Path(module_source_dir)
            
        self.module_name = "donor_dump"
        self.proc_path = "/proc/donor_dump"
        
    def check_kernel_headers(self) -> Tuple[bool, str]:
        """
        Check if kernel headers are available for the current kernel
        
        Returns:
            Tuple of (headers_available, kernel_version)
        """
        try:
            kernel_version = subprocess.check_output(
                ["uname", "-r"], text=True
            ).strip()
            
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
                text=True
            )
            
            # Install specific kernel headers
            subprocess.run(
                ["sudo", "apt-get", "install", "-y", f"linux-headers-{kernel_version}"],
                check=True,
                capture_output=True,
                text=True
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
            raise ModuleBuildError(f"Module source directory not found: {self.module_source_dir}")
        
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
                    text=True
                )
            
            # Build the module
            result = subprocess.run(
                ["make"],
                cwd=self.module_source_dir,
                check=True,
                capture_output=True,
                text=True
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
            result = subprocess.run(
                ["which", "lsmod"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                # Not on Linux, module loading not supported
                return False
                
            result = subprocess.run(
                ["lsmod"],
                capture_output=True,
                text=True,
                check=True
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
        bdf_pattern = re.compile(r"^[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7]$")
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
                text=True
            )
            
            # Verify module loaded and proc file exists
            if not self.is_module_loaded():
                raise ModuleLoadError("Module load appeared to succeed but module not found in lsmod")
            
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
                text=True
            )
            
            logger.info("Module unloaded successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to unload module: {e}"
            if e.stderr:
                error_msg += f"\nStderr: {e.stderr}"
            raise ModuleLoadError(error_msg)
    
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
            with open(self.proc_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
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
    
    def setup_module(self, bdf: str, auto_install_headers: bool = False) -> Dict[str, str]:
        """
        Complete setup process: check headers, build, load module, and read info
        
        Args:
            bdf: PCI Bus:Device.Function
            auto_install_headers: Automatically install headers if missing
            
        Returns:
            Device information dictionary
        """
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
        return self.read_device_info()


def main():
    """CLI interface for donor dump manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Donor Dump Kernel Module Manager")
    parser.add_argument("--bdf", required=True, help="PCI Bus:Device.Function (e.g., 0000:03:00.0)")
    parser.add_argument("--source-dir", help="Path to donor_dump source directory")
    parser.add_argument("--auto-install-headers", action="store_true", 
                       help="Automatically install kernel headers if missing")
    parser.add_argument("--force-rebuild", action="store_true", 
                       help="Force rebuild of kernel module")
    parser.add_argument("--unload", action="store_true", 
                       help="Unload the module instead of loading")
    parser.add_argument("--status", action="store_true", 
                       help="Show module status")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose logging")
    
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
            auto_install_headers=args.auto_install_headers
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