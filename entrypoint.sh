#!/bin/bash
set -e

# Display usage information
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "PCILeech DMA Firmware Generator Container v2.0"
    echo "Usage: podman run --rm -it --cap-add=SYS_RAWIO --cap-add=SYS_ADMIN \\"
    echo "         --device=/dev/vfio/GROUP --device=/dev/vfio/vfio \\"
    echo "         -v ./output:/app/output dma-fw \\"
    echo "         sudo python3 /app/build_wrapper.py [OPTIONS]"
    echo ""
    echo "Required arguments:"
    echo "  --bdf XXXX:XX:XX.X  PCI Bus:Device.Function (e.g., 0000:03:00.0)"
    echo "  --board XXt         Target board (35t, 75t, or 100t)"
    echo ""
    echo "Production mode options (all advanced features enabled by default):"
    echo "  --disable-advanced-sv    Disable advanced SystemVerilog generation"
    echo "  --device-type TYPE       Device type optimization (default: network)"
    echo "  --disable-variance       Disable manufacturing variance simulation"
    echo "  --disable-power-management  Disable power management features"
    echo "  --enable-debug           Enable debug features in generated code"
    echo "  --custom-config FILE     Use custom configuration file"
    echo ""
    echo "Basic examples (production mode with all features enabled):"
    echo "  # Standard production firmware generation"
    echo "  sudo python3 /app/build_wrapper.py --bdf 0000:03:00.0 --board 75t"
    echo ""
    echo "Advanced examples:"
    echo "  # Production build with specific device type"
    echo "  sudo python3 /app/build_wrapper.py --bdf 0000:03:00.0 --board 75t --device-type storage"
    echo ""
    echo "  # Minimal build (disable advanced features)"
    echo "  sudo python3 /app/build_wrapper.py --bdf 0000:03:00.0 --board 75t --disable-advanced-sv --disable-variance"
    echo ""
    echo "  # Custom device type with all production features"
    echo "  sudo python3 /app/build_wrapper.py --bdf 0000:03:00.0 --board 75t --device-type graphics"
    echo ""
    echo "Kernel Module (donor_dump, optional):"
    echo "  To use donor_dump (add --use-donor-dump flag), the module must be built on the host system:"
    echo "  1. Copy /app/src/donor_dump/ to host"
    echo "  2. Install kernel headers: apt-get install linux-headers-\$(uname -r)"
    echo "  3. Build module: cd donor_dump && make"
    echo "  4. Load module: sudo insmod donor_dump.ko bdf=XXXX:XX:XX.X"
    echo ""
    echo "Production Features (enabled by default):"
    echo "  - Advanced SystemVerilog code generation with optimizations"
    echo "  - Manufacturing variance simulation for realistic behavior"
    echo "  - Device-specific optimizations (network, storage, graphics, audio)"
    echo "  - Power management controls and PMCSR support"
    echo "  - Performance profiling and behavior analysis"
    echo "  - MSI-X capability handling and table replication"
    echo "  - Configuration space shadowing and validation"
    echo "  - Option ROM support and management"
    echo "  - Error handling and recovery mechanisms"
    exit 0
fi

# Check if VFIO constants need to be rebuilt at runtime
if [ "${REBUILD_VFIO_CONSTANTS:-false}" = "true" ]; then
    echo "Rebuilding VFIO constants for runtime kernel..."
    if [ -f /app/build_vfio_constants.sh ]; then
        cd /app && ./build_vfio_constants.sh || echo "Warning: VFIO constants rebuild failed"
    else
        echo "Warning: VFIO constants build script not found"
    fi
fi

# Make sure the backend module is present
modprobe -q vfio_iommu_type1 || true

# Enable unsafe-interrupts in *this* mount-NS
echo 1 > /sys/module/vfio_iommu_type1/parameters/allow_unsafe_interrupts 2>/dev/null || true

# (optional) print the value for debugging
printf "vfio_iommu_type1.allow_unsafe_interrupts = %s\n" \
       "$(cat /sys/module/vfio_iommu_type1/parameters/allow_unsafe_interrupts)"

# Execute the command
exec "$@"