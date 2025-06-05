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

# Note: Kernel module (donor_dump) should be built on target system, not in container
# The module requires kernel headers matching the host kernel version
# Build instructions are available in src/donor_dump/Makefile

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
LABEL maintainer="Ramsey McGrath <ramsey@voltcyclone.info>" \
      description="PCILeech DMA firmware generator container with advanced SystemVerilog features (multi-stage optimized)" \
      version="2.0" \
      usage="podman run --rm -it --cap-add=SYS_RAWIO --cap-add=SYS_ADMIN --device=/dev/vfio/X --device=/dev/vfio/vfio -v ./output:/app/output dma-fw sudo python3 /app/src/build.py --bdf XXXX:XX:XX.X --board XXt [--advanced-sv] [--device-type TYPE] [--enable-variance]" \
      security.notes="Requires privileged mode for PCI device access via VFIO" \
      features="Basic firmware generation, Advanced SystemVerilog features, Manufacturing variance simulation, Device-specific optimizations"

# Copy the pre-created entrypoint script
COPY entrypoint.sh /entrypoint.sh

# Note: Vivado tools should be installed separately or use Xilinx's official container images
# This container provides the optimized base environment for DMA firmware generation

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
