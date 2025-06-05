#!/usr/bin/env python3
"""
Test script to verify PyPI package generation works correctly.
This script performs a quick validation of the package build process.
"""

import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

def run_command(cmd: str) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result

def test_package_build():
    """Test the package build process."""
    print("Testing PyPI package generation...")
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    import os
    os.chdir(project_root)
    
    # Run quick build (skip tests and uploads)
    result = run_command("python3 scripts/generate_pypi_package.py --quick --skip-upload")
    
    if result.returncode != 0:
        print(f"Build failed: {result.stderr}")
        return False
    
    # Check if distributions were created
    dist_dir = project_root / "dist"
    if not dist_dir.exists():
        print("No dist directory found")
        return False
    
    wheel_files = list(dist_dir.glob("*.whl"))
    if not wheel_files:
        print("No wheel files found")
        return False
    
    # Check wheel contents
    wheel_file = wheel_files[0]
    print(f"Checking wheel file: {wheel_file.name}")
    
    with zipfile.ZipFile(wheel_file, 'r') as zf:
        files = zf.namelist()
        
        # Check that src files are included
        src_files = [f for f in files if f.startswith('src/')]
        if not src_files:
            print("No src files found in wheel")
            return False
        
        # Check that test files are NOT included
        test_files = [f for f in files if 'test' in f.lower() and f.endswith('.py')]
        if test_files:
            print(f"ERROR: Test files found in wheel: {test_files}")
            return False
        
        print(f"✓ Wheel contains {len(src_files)} source files")
        print("✓ No test files found in wheel")
    
    print("✓ Package build test passed!")
    return True

if __name__ == "__main__":
    success = test_package_build()
    sys.exit(0 if success else 1)