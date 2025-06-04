# Multi-stage build for smaller final image
# Build stage - includes development tools
FROM ubuntu:22.04 AS builder

# Set environment variables for reproducible builds
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Install build dependencies without version pins for compatibility
RUN apt-get update && apt-get install -y \
    build-essential \
    linux-headers-generic \
    make \
    git \
    python3 \
    python3-pip \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy source code for any compilation steps
COPY ./src /build/src
COPY ./generate.py /build/
COPY ./requirements-test.txt /build/
WORKDIR /build

# Pre-compile any Python modules or build kernel modules if needed
RUN cd src/donor_dump && make clean && make

# Runtime stage - minimal runtime environment
FROM ubuntu:22.04 AS runtime

# Set environment variables for reproducible builds
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Install only runtime dependencies without version pins for compatibility
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    pciutils \
    bsdextrautils \
    sudo \
    kmod \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Create non-root user for security (though privileged access needed for PCI operations)
RUN groupadd -r appuser && useradd -r -g appuser -s /bin/bash -m appuser

# Set working directory
WORKDIR /app

# Copy Python requirements first for better layer caching
COPY --chown=appuser:appuser ./requirements.txt /app/
COPY --chown=appuser:appuser ./requirements-tui.txt /app/
COPY --chown=appuser:appuser ./requirements-test.txt /app/

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r /app/requirements.txt && \
    pip3 install --no-cache-dir -r /app/requirements-tui.txt

# Copy application files from builder stage
# This includes all new advanced SystemVerilog modules:
# - manufacturing_variance.py, advanced_sv_*.py, enhanced behavior_profiler.py, enhanced build.py
COPY --from=builder --chown=appuser:appuser /build/src /app/src

# Copy additional root-level files needed for enhanced functionality
COPY --chown=appuser:appuser ./generate.py /app/

# Create output directory with proper permissions
RUN mkdir -p /app/output && chown appuser:appuser /app/output

# Add health check with dependency validation
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import psutil, pydantic; print('Dependencies OK')" || exit 1

# Add container usage documentation
LABEL maintainer="Ramsey McGrath <ramseymcgrath@gmail.com>" \
      description="PCILeech DMA firmware generator container with advanced SystemVerilog features (multi-stage optimized)" \
      version="2.0" \
      usage="podman run --rm -it --cap-add=SYS_RAWIO --cap-add=SYS_ADMIN --device=/dev/vfio/X --device=/dev/vfio/vfio -v ./output:/app/output dma-fw sudo python3 /app/src/build.py --bdf XXXX:XX:XX.X --board XXt [--advanced-sv] [--device-type TYPE] [--enable-variance]" \
      security.notes="Requires privileged mode for PCI device access via VFIO" \
      features="Basic firmware generation, Advanced SystemVerilog features, Manufacturing variance simulation, Device-specific optimizations"

# Create entrypoint script for better container usage
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Display usage information\n\
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then\n\
    echo "PCILeech DMA Firmware Generator Container v2.0"\n\
    echo "Usage: podman run --rm -it --cap-add=SYS_RAWIO --cap-add=SYS_ADMIN \\"\n\
    echo "         --device=/dev/vfio/GROUP --device=/dev/vfio/vfio \\"\n\
    echo "         -v ./output:/app/output dma-fw \\"\n\
    echo "         sudo python3 /app/src/build.py [OPTIONS]"\n\
    echo ""\n\
    echo "Required arguments:"\n\
    echo "  --bdf XXXX:XX:XX.X  PCI Bus:Device.Function (e.g., 0000:03:00.0)"\n\
    echo "  --board XXt         Target board (35t, 75t, or 100t)"\n\
    echo ""\n\
    echo "Advanced SystemVerilog options:"\n\
    echo "  --advanced-sv       Enable advanced SystemVerilog generation"\n\
    echo "  --device-type TYPE  Device type optimization (network, storage, graphics)"\n\
    echo "  --enable-variance   Enable manufacturing variance simulation"\n\
    echo "  --disable-power-management  Disable power management features"\n\
    echo "  --enable-debug      Enable debug features in generated code"\n\
    echo "  --custom-config FILE  Use custom configuration file"\n\
    echo ""\n\
    echo "Basic examples:"\n\
    echo "  # Standard firmware generation"\n\
    echo "  sudo python3 /app/src/build.py --bdf 0000:03:00.0 --board 75t"\n\
    echo ""\n\
    echo "Advanced examples:"\n\
    echo "  # Basic advanced generation"\n\
    echo "  sudo python3 /app/src/build.py --bdf 0000:03:00.0 --board 75t --advanced-sv"\n\
    echo ""\n\
    echo "  # Device-specific with variance"\n\
    echo "  sudo python3 /app/src/build.py --bdf 0000:03:00.0 --board 75t --advanced-sv --device-type network --enable-variance"\n\
    echo ""\n\
    echo "  # Custom configuration"\n\
    echo "  sudo python3 /app/src/build.py --bdf 0000:03:00.0 --board 75t --advanced-sv --device-type storage --disable-power-management"\n\
    echo ""\n\
    echo "Features:"\n\
    echo "  - Basic PCILeech DMA firmware generation"\n\
    echo "  - Advanced SystemVerilog code generation"\n\
    echo "  - Manufacturing variance simulation"\n\
    echo "  - Device-specific optimizations"\n\
    echo "  - Power management controls"\n\
    echo "  - Performance profiling and optimization"\n\
    exit 0\n\
fi\n\
\n\
# Execute the command\n\
exec "$@"\n' > /entrypoint.sh && chmod +x /entrypoint.sh

# Note: Vivado tools should be installed separately or use Xilinx's official container images
# This container provides the optimized base environment for DMA firmware generation

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
