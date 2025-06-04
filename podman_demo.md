# Podman Demo for PCILeech Firmware Generator

This guide demonstrates how to use Podman to containerize and run the PCILeech DMA firmware generator application.

## What is Podman?

Podman is a daemonless container engine for developing, managing, and running OCI containers. Unlike Docker, Podman:
- Runs containers without a daemon
- Can run containers as a non-root user
- Has a command-line interface compatible with Docker
- Supports pods (groups of containers)

## Prerequisites

- Podman installed on your system
- Basic understanding of container concepts
- PCILeech firmware generator source code

## 1. Installing Podman

### On Fedora/RHEL/CentOS:
```bash
sudo dnf install podman
```

### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install podman
```

### On macOS (using Homebrew):
```bash
brew install podman
podman machine init
podman machine start
```

## 2. Building the Container Image

Navigate to the directory containing the Containerfile and run:

```bash
# Build the image with a tag
podman build -t pcileech-fw-generator:latest -f Containerfile .
```

This builds a multi-stage container that:
1. Compiles necessary components in a builder stage
2. Creates a minimal runtime image with only required dependencies
3. Sets up proper permissions and an entrypoint script

## 3. Running the Container

### Basic Run Command

```bash
podman run --rm -it pcileech-fw-generator:latest
```

This starts the container in interactive mode and removes it when you exit.

### Running with Specific Capabilities for PCI Operations

```bash
podman run --rm -it \
  --cap-add=SYS_RAWIO --cap-add=SYS_ADMIN \
  --device=/dev/vfio/10 --device=/dev/vfio/vfio \
  -v ./output:/app/output \
  pcileech-fw-generator:latest \
  sudo python3 /app/src/build.py --bdf 0000:03:00.0 --board 75t
```

This command:
- Grants specific capabilities (SYS_RAWIO, SYS_ADMIN) instead of full privileged access
- Maps specific VFIO devices into the container
- Mounts a local `output` directory to store generated files
- Runs the firmware generator with specific parameters

### Alternative: Running with Privileged Access (Less Secure)

```bash
podman run --rm -it --privileged \
  --device=/dev/vfio/10 --device=/dev/vfio/vfio \
  -v ./output:/app/output \
  pcileech-fw-generator:latest \
  sudo python3 /app/src/build.py --bdf 0000:03:00.0 --board 75t
```

### Running with Advanced SystemVerilog Features

```bash
podman run --rm -it \
  --cap-add=SYS_RAWIO --cap-add=SYS_ADMIN \
  --device=/dev/vfio/10 --device=/dev/vfio/vfio \
  -v ./output:/app/output \
  pcileech-fw-generator:latest \
  sudo python3 /app/src/build.py --bdf 0000:03:00.0 --board 75t \
  --advanced-sv --device-type network --enable-variance
```

## 4. Viewing Container Help Information

```bash
podman run --rm pcileech-fw-generator:latest --help
```

This displays the built-in help information from the container's entrypoint script.

## Managing Containers

### List Running Containers

```bash
podman ps
```

### List All Containers (including stopped ones)

```bash
podman ps -a
```

### Stop a Running Container

```bash
podman stop <container_id>
```

### Remove a Container

```bash
podman rm <container_id>
```

## 6. Working with Container Images

### List Available Images

```bash
podman images
```

### Remove an Image

```bash
podman rmi pcileech-fw-generator:latest
```

### Tag an Image

```bash
podman tag pcileech-fw-generator:latest pcileech-fw-generator:v2.0
```

## 7. Advanced Podman Features

### Running Rootless Containers

Podman allows running containers as a non-root user:

```bash
# No sudo needed
podman run --rm -it pcileech-fw-generator:latest bash
```

Note: For PCI operations that require privileged access, you may still need to use sudo or configure proper permissions.

### Creating a Pod

Pods allow you to group containers together:

```bash
# Create a pod
podman pod create --name pcileech-pod

# Run containers in the pod
podman run --pod pcileech-pod -d pcileech-fw-generator:latest
```

## Best Practices for PCILeech Container

1. **Mount Output Directory**: Always mount an output directory to preserve generated files
   ```bash
   -v ./output:/app/output
   ```

2. **Device Access**: For PCI operations, map the specific VFIO devices needed
   ```bash
   --device=/dev/vfio/X --device=/dev/vfio/vfio
   ```

3. **Security**: Use specific capabilities instead of --privileged when possible
   ```bash
   --cap-add=SYS_RAWIO --cap-add=SYS_ADMIN
   ```

4. **Resource Limits**: Set memory and CPU limits for better resource management
   ```bash
   --memory 2g --cpus 2
   ```

5. **Environment Variables**: Pass configuration through environment variables
   ```bash
   -e DEBUG=1 -e OPTIMIZATION_LEVEL=high
   ```

6. **Container Labels**: Add custom labels for better organization
   ```bash
   --label "purpose=firmware-generation" --label "project=pcileech"
   ```

## Scripts Common Operations

```bash
#!/bin/bash
# podman_pcileech_demo.sh

# Build the image
echo "Building PCILeech container image..."
podman build -t pcileech-fw-generator:latest -f Containerfile .

# Create output directory
mkdir -p ./output
chmod 777 ./output

# Run basic firmware generation
echo "Running basic firmware generation..."
podman run --rm -it \
  --cap-add=SYS_RAWIO --cap-add=SYS_ADMIN \
  --device=/dev/vfio/10 --device=/dev/vfio/vfio \
  -v ./output:/app/output \
  pcileech-fw-generator:latest \
  sudo python3 /app/src/build.py --bdf 0000:03:00.0 --board 75t

# Run advanced firmware generation
echo "Running advanced firmware generation..."
podman run --rm -it \
  --cap-add=SYS_RAWIO --cap-add=SYS_ADMIN \
  --device=/dev/vfio/10 --device=/dev/vfio/vfio \
  -v ./output:/app/output \
  pcileech-fw-generator:latest \
  sudo python3 /app/src/build.py --bdf 0000:03:00.0 --board 75t \
  --advanced-sv --device-type network --enable-variance

# List generated files
echo "Generated files:"
ls -la ./output
```

Make this script executable with `chmod +x podman_pcileech_demo.sh` and run it with `./podman_pcileech_demo.sh`.
