#!/bin/bash

# 컨테이너 내부에서 빌드 실행
podman run --rm --privileged \
    --device=/dev/vfio/12 \
    --device=/dev/vfio/vfio \
    --entrypoint /bin/bash \
    --user root \
    -v /home/muttti/123/output:/app/output \
    -v /lib/modules/$(uname -r)/build:/kernel-headers:ro \
    -it \
    pcileech-fw-generator:latest \
    -c "cd /app && python3 -m src.build --bdf 0000:01:00.0 --board pcileech_75t484_x1"
