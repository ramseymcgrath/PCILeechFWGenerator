# Note: Kernel module (donor_dump) should be built on target system, not in container
# The module requires kernel headers matching the host kernel version
# Build instructions are available in src/donor_dump/Makefile
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
COPY utils ./utils
COPY generate.py .
COPY entrypoint.sh /usr/local/bin/entrypoint
RUN chmod 755 /usr/local/bin/entrypoint

ENV PYTHONPATH=/app:/app/src
RUN mkdir -p /app/output && chown appuser /app/output

HEALTHCHECK CMD python3 - <<'PY'\nimport psutil, pydantic, sys; sys.exit(0)\nPY

USER appuser
ENTRYPOINT ["entrypoint"]
