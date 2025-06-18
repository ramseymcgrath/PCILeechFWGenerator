#!/usr/bin/env python3
"""
Complete VFIO Binding Script

This script completes the VFIO binding process for your Intel I226-V device
and runs comprehensive diagnostics to verify the setup.
"""

import os
import subprocess
import sys
from pathlib import Path

# Add the src directory to Python path so we can import our VFIO diagnostics
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from cli.vfio_diagnostics import run_vfio_diagnostic
except ImportError:
    print("Warning: Could not import VFIO diagnostics module")
    run_vfio_diagnostic = None


def complete_vfio_binding(device_bdf: str, vendor_id: str, device_id: str):
    """Complete the VFIO binding process for the specified device."""

    print("🔧 Completing VFIO binding process...")
    print(f"📍 Device: {device_bdf} (Intel I226-V [{vendor_id}:{device_id}])")
    print()

    try:
        # Step 1: Verify device is unbound
        driver_path = f"/sys/bus/pci/devices/{device_bdf}/driver"
        if os.path.exists(driver_path):
            current_driver = os.path.basename(os.readlink(driver_path))
            print(f"⚠️  Device still bound to {current_driver}")

            # Unbind if needed
            print("🔄 Unbinding device...")
            subprocess.run(
                ["sudo", "tee", f"/sys/bus/pci/devices/{device_bdf}/driver/unbind"],
                input=device_bdf,
                text=True,
                check=True,
            )
        else:
            print("✅ Device is already unbound")

        # Step 2: Bind to vfio-pci
        print("🔗 Binding device to vfio-pci...")
        subprocess.run(
            ["sudo", "tee", "/sys/bus/pci/drivers/vfio-pci/bind"],
            input=device_bdf,
            text=True,
            check=True,
        )

        print("✅ Device successfully bound to vfio-pci!")
        print()

        # Step 3: Verify binding
        driver_path = f"/sys/bus/pci/devices/{device_bdf}/driver"
        if os.path.exists(driver_path):
            current_driver = os.path.basename(os.readlink(driver_path))
            if current_driver == "vfio-pci":
                print("✅ Verification: Device is now bound to vfio-pci")
            else:
                print(f"❌ Verification failed: Device bound to {current_driver}")
                return False
        else:
            print("❌ Verification failed: No driver binding detected")
            return False

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function to complete VFIO binding and run diagnostics."""

    # Device details from your lspci output
    device_bdf = "0000:03:00.0"
    vendor_id = "8086"
    device_id = "125c"

    print("🚀 Intel I226-V VFIO Setup Completion")
    print("=" * 50)
    print()

    # Complete the binding process
    if complete_vfio_binding(device_bdf, vendor_id, device_id):
        print()
        print("🔍 Running comprehensive VFIO diagnostics...")
        print("=" * 50)

        # Run the full diagnostic suite if available
        if run_vfio_diagnostic:
            result = run_vfio_diagnostic(device_bdf, interactive=False)

            if result.can_proceed:
                print()
                print("🎉 SUCCESS! Your VFIO setup is complete and ready to use.")
                print()
                print("📋 Next steps:")
                print("   1. Your device is now available for VFIO operations")
                print(
                    "   2. You can use this device with PCILeech or other VFIO applications"
                )
                print("   3. The device file is available at /dev/vfio/{group_number}")
                print()
                print("💡 To verify the setup:")
                print(f"   ls -la /sys/bus/pci/devices/{device_bdf}/iommu_group")
                print(f"   ls -la /dev/vfio/")
            else:
                print()
                print("⚠️  Setup completed but diagnostics show issues.")
                print("   Please review the diagnostic report above.")
        else:
            # Manual verification if diagnostics not available
            print()
            print("🎉 VFIO binding completed!")
            print()
            print("📋 Manual verification steps:")
            print(
                f"   1. Check driver binding: ls -la /sys/bus/pci/devices/{device_bdf}/driver"
            )
            print(
                f"   2. Check IOMMU group: ls -la /sys/bus/pci/devices/{device_bdf}/iommu_group"
            )
            print("   3. Check VFIO device files: ls -la /dev/vfio/")
            print()
            print("💡 Your device should now be available for VFIO operations")
    else:
        print()
        print("❌ Failed to complete VFIO binding.")
        print("   Please check the error messages above.")


if __name__ == "__main__":
    main()
