# Note: Kernel module (donor_dump) should be built on target system, not in container
# The module requires kernel headers matching the host kernel version
# Build instructions are available in src/donor_dump/Makefile

# ---------- build stage for VFIO constants ----------
FROM ubuntu:22.04 AS build

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 LC_ALL=C.UTF-8 TZ=UTC
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# ── base build deps ──────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-pip build-essential \
        linux-headers-generic \
        pciutils kmod ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /src

# ── VFIO constants patching ───────────────────────────────────────────────────
COPY vfio_helper.c patch_vfio_constants.py build_vfio_constants.sh ./
COPY src/cli/vfio_constants.py ./src/cli/
RUN mkdir -p src/cli && \
    chmod +x build_vfio_constants.sh && \
    (./build_vfio_constants.sh && cp src/cli/vfio_constants.py vfio_constants_patched.py) || \
    (echo "⚠ VFIO constants build failed, using original" && cp src/cli/vfio_constants.py vfio_constants_patched.py) && \
    echo "Content of patched file:" && cat vfio_constants_patched.py | grep -A 10 "Ioctl numbers"

# ---------- runtime ----------
FROM ubuntu:22.04 AS runtime

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 LC_ALL=C.UTF-8 TZ=UTC \
    PCILEECH_PRODUCTION_MODE=true \
    PCILEECH_ALLOW_MOCK_DATA=false

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip pciutils bsdextrautils kmod ca-certificates git sudo \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create non-root user and configure sudo
RUN useradd -m -r appuser && \
    echo "appuser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    echo "Defaults !requiretty" >> /etc/sudoers

WORKDIR /app
COPY requirements.txt requirements-tui.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt -r requirements-tui.txt

# Copy only what you need
COPY src ./src
COPY boards ./boards
COPY configs ./configs
COPY generate.py .

# Ensure __init__.py files exist in all directories
RUN find ./src -type d -exec touch {}/__init__.py \; 2>/dev/null || true
COPY entrypoint.sh /usr/local/bin/entrypoint
RUN chmod 755 /usr/local/bin/entrypoint

# Copy the patched VFIO constants file (commented out to use our pre-patched version)
# COPY --from=build /src/vfio_constants_patched.py ./src/cli/vfio_constants.py

ENV PYTHONPATH=/app:/app/src
RUN mkdir -p /app/output && chown appuser /app/output

HEALTHCHECK CMD python3 - <<'PY'\nimport psutil, pydantic, sys; sys.exit(0)\nPY

USER appuser
ENTRYPOINT ["entrypoint"]
