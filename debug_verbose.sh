#!/bin/bash

# 더 자세한 로그와 함께 빌드 실행
podman run --rm --privileged \
    --device=/dev/vfio/12 \
    --device=/dev/vfio/vfio \
    --entrypoint python3 \
    --user root \
    -v /home/muttti/123/output:/app/output \
    -v /lib/modules/$(uname -r)/build:/kernel-headers:ro \
    pcileech-fw-generator:latest \
    -m src.build --bdf 0000:01:00.0 --board pcileech_75t484_x1 --verbose
