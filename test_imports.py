#!/usr/bin/env python3
"""
Test script to verify module imports in the container
"""
import sys
import os

print("Python version:", sys.version)
print("PYTHONPATH:", os.environ.get("PYTHONPATH", "Not set"))
print("Current directory:", os.getcwd())
print("Directory contents:", os.listdir("."))
print("src directory contents:", os.listdir("./src"))
print("src/device_clone directory contents:", os.listdir("./src/device_clone"))

# Try importing the problematic module
try:
    from src.device_clone.pcileech_generator import PCILeechGenerator

    print("✅ Successfully imported PCILeechGenerator")
except ImportError as e:
    print(f"❌ Import error: {e}")
    # Print the Python module search path
    print("\nPython module search path:")
    for path in sys.path:
        print(f"  - {path}")

    # Check if the file exists
    file_path = "./src/device_clone/pcileech_generator.py"
    if os.path.exists(file_path):
        print(f"\n{file_path} exists")
        # Print the first few lines of the file
        with open(file_path, "r") as f:
            print("\nFirst 10 lines of the file:")
            for i, line in enumerate(f):
                if i >= 10:
                    break
                print(f"{i+1}: {line.rstrip()}")
    else:
        print(f"\n{file_path} does not exist")

# Try importing other modules to see if they work
print("\nTrying to import other modules:")
modules_to_test = [
    "src.device_clone.behavior_profiler",
    "src.templating.tcl_builder",
    "src.cli.vfio_handler",
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f"✅ Successfully imported {module}")
    except ImportError as e:
        print(f"❌ Failed to import {module}: {e}")
