## Overview

### What is a Donor Dump?

A donor dump is a comprehensive snapshot of a physical PCI device's configuration and capabilities. The PCILeech Firmware Generator uses this information to create firmware that accurately emulates the donor device's behavior.

**Key Information Captured:**

| Component | Description | Purpose |
|-----------|-------------|---------|
| **Device Identity** | Vendor/Device IDs, Subsystem IDs, Revision | Device identification and driver matching |
| **Configuration Space** | Full 4KB extended PCI configuration | Complete device state and capabilities |
| **Power Management** | MPC/MPR values, power states | Power efficiency and compatibility |
| **Capabilities** | AER, MSI/MSI-X, vendor-specific | Advanced PCI features |
| **Memory Layout** | BAR sizes, Device Serial Number (DSN) | Memory mapping and addressing |
| **Class Information** | 24-bit class code | Device type classification |

### When to Use Manual Process

- **Debugging**: When automated tools fail or produce unexpected results
- **Custom Workflows**: Integration with existing automation or CI/CD pipelines
- **Research**: Understanding the donor extraction process in detail
- **Troubleshooting**: Isolating issues in the firmware generation pipeline

## Prerequisites

### System Requirements

| Requirement | Linux |
|-------------|-------|
| **OS Version** | Any modern distribution | 
| **Privileges** | Root access (`sudo`) | 
| **Shell** | Bash/Zsh |
| **Build Tools** | GCC, Make, Kernel Headers |

### Quick Prerequisite Check

**Linux:**
```bash
# Check if all prerequisites are available
echo "Checking prerequisites..."
command -v gcc >/dev/null 2>&1 && echo "✓ GCC available" || echo "✗ GCC missing"
command -v make >/dev/null 2>&1 && echo "✓ Make available" || echo "✗ Make missing"
[ -d "/lib/modules/$(uname -r)/build" ] && echo "✓ Kernel headers available" || echo "✗ Kernel headers missing"
[ "$EUID" -eq 0 ] && echo "✓ Running as root" || echo "✗ Need root privileges"
```

### Installing Prerequisites

#### Debian/Ubuntu
```bash
sudo apt-get update && sudo apt-get install -y \
    linux-headers-$(uname -r) \
    build-essential \
    dkms
```

#### Fedora/CentOS/RHEL
```bash
sudo dnf install -y \
    kernel-devel-$(uname -r) \
    gcc \
    make \
    dkms
```

#### Arch Linux/Manjaro
```bash
sudo pacman -S --needed \
    linux-headers \
    base-devel \
    dkms
```

#### openSUSE
```bash
sudo zypper install -y \
    kernel-devel-$(uname -r) \
    gcc \
    make \
    dkms
```

## Linux Manual Process

### Step 1: Device Discovery and Validation

#### Find Your Donor Device
```bash
# List all PCI devices with detailed information
lspci -vv

# Filter by device type (example: network controllers)
lspci -vv | grep -A 20 "Ethernet controller"

# Get specific device information
lspci -s 03:00.0 -vv
```

#### Validate Device Accessibility
```bash
# Check if device is bound to a driver
lspci -k -s 03:00.0

# Verify device is not in use by critical services
systemctl status NetworkManager  # For network devices
systemctl status display-manager # For graphics devices
```

#### Extract BDF Information
```bash
# Get BDF with domain information
DEVICE_BDF=$(lspci | grep "Ethernet controller" | head -1 | cut -d' ' -f1)
FULL_BDF="0000:${DEVICE_BDF}"
echo "Using device: ${FULL_BDF}"
```

### Step 2: Build Environment Setup

#### Navigate to Build Directory
```bash
# Ensure we're in the correct directory
cd "$(dirname "$0")/../PCILeechFWGenerator/src/donor_dump" || {
    echo "Error: Cannot find donor_dump directory"
    exit 1
}

# Verify required files exist
[ -f "Makefile" ] || { echo "Error: Makefile not found"; exit 1; }
[ -f "donor_dump.c" ] || { echo "Error: Source file not found"; exit 1; }
```

#### Clean Build Environment
```bash
# Clean any previous builds
make clean

# Verify kernel build environment
make -n 2>&1 | grep -q "No rule to make target" && {
    echo "Error: Kernel build environment not properly configured"
    exit 1
}
```

#### Build with Error Handling
```bash
# Build the kernel module with verbose output
if ! make V=1; then
    echo "Build failed. Common issues:"
    echo "1. Kernel headers mismatch: $(uname -r) vs $(ls /lib/modules/)"
    echo "2. Missing dependencies: gcc, make, kernel-devel"
    echo "3. Insufficient permissions"
    exit 1
fi

# Verify build artifacts
[ -f "donor_dump.ko" ] || { echo "Error: Module not built"; exit 1; }
echo "✓ Module built successfully: $(ls -lh donor_dump.ko)"
```

### Step 3: Module Loading and Device Binding

#### Pre-load Validation
```bash
# Check if module is already loaded
if lsmod | grep -q donor_dump; then
    echo "Warning: donor_dump module already loaded"
    sudo rmmod donor_dump || {
        echo "Error: Cannot unload existing module"
        exit 1
    }
fi

# Verify device exists and is accessible
if ! lspci -s "${DEVICE_BDF}" >/dev/null 2>&1; then
    echo "Error: Device ${FULL_BDF} not found"
    exit 1
fi
```

#### Load Module with Comprehensive Error Handling
```bash
# Load module with device binding
if ! sudo insmod donor_dump.ko bdf="${FULL_BDF}"; then
    echo "Module load failed. Checking kernel logs..."
    dmesg | tail -20 | grep donor_dump
    exit 1
fi

# Verify module loaded successfully
if ! lsmod | grep -q donor_dump; then
    echo "Error: Module not loaded despite successful insmod"
    exit 1
fi

echo "✓ Module loaded successfully for device ${FULL_BDF}"
```

#### Verify Proc Interface
```bash
# Check if proc file is created and accessible
if [ ! -r "/proc/donor_dump" ]; then
    echo "Error: /proc/donor_dump not accessible"
    echo "Module may have loaded but device binding failed"
    sudo rmmod donor_dump
    exit 1
fi

echo "✓ Proc interface available"
```

### Step 4: Data Extraction and Validation

#### Extract Raw Data
```bash
# Read donor information with error checking
if ! DONOR_DATA=$(cat /proc/donor_dump 2>/dev/null); then
    echo "Error: Cannot read donor information"
    sudo rmmod donor_dump
    exit 1
fi

# Validate data completeness
if [ -z "$DONOR_DATA" ]; then
    echo "Error: No donor data extracted"
    sudo rmmod donor_dump
    exit 1
fi

echo "✓ Donor data extracted ($(echo "$DONOR_DATA" | wc -l) lines)"
```

#### Save Raw Data with Metadata
```bash
# Create output directory with timestamp
OUTPUT_DIR="donor_dumps/$(date +%Y%m%d_%H%M%S)_${DEVICE_BDF//:/_}"
mkdir -p "$OUTPUT_DIR"

# Save raw data with metadata
{
    echo "# Donor dump generated on $(date)"
    echo "# Device: ${FULL_BDF}"
    echo "# Kernel: $(uname -r)"
    echo "# System: $(uname -a)"
    echo ""
    echo "$DONOR_DATA"
} > "${OUTPUT_DIR}/donor_info.txt"

echo "✓ Raw data saved to ${OUTPUT_DIR}/donor_info.txt"
```

#### Convert to JSON with Validation
```bash
# Enhanced JSON conversion with validation
convert_to_json() {
    local input_file="$1"
    local output_file="$2"
    
    # Create JSON with proper escaping and validation
    {
        echo "{"
        echo "  \"metadata\": {"
        echo "    \"generated_at\": \"$(date -Iseconds)\","
        echo "    \"device_bdf\": \"${FULL_BDF}\","
        echo "    \"kernel_version\": \"$(uname -r)\","
        echo "    \"generator_version\": \"manual-v1.0\""
        echo "  },"
        echo "  \"device_info\": {"
        
        # Process each line, handling special characters
        grep -v '^#' "$input_file" | while IFS=':' read -r key value; do
            if [ -n "$key" ] && [ -n "$value" ]; then
                # Escape special characters in JSON
                key=$(echo "$key" | sed 's/"/\\"/g' | xargs)
                value=$(echo "$value" | sed 's/"/\\"/g' | xargs)
                echo "    \"$key\": \"$value\","
            fi
        done | sed '$ s/,$//'  # Remove trailing comma
        
        echo "  }"
        echo "}"
    } > "$output_file"
    
    # Validate JSON syntax
    if command -v python3 >/dev/null 2>&1; then
        if ! python3 -m json.tool "$output_file" >/dev/null 2>&1; then
            echo "Warning: Generated JSON may be invalid"
            return 1
        fi
    fi
    
    return 0
}

# Convert to JSON
JSON_FILE="${OUTPUT_DIR}/donor_info.json"
if convert_to_json "${OUTPUT_DIR}/donor_info.txt" "$JSON_FILE"; then
    echo "✓ JSON file created: $JSON_FILE"
else
    echo "⚠ JSON conversion completed with warnings"
fi
```

### Step 5: Cleanup and Verification

#### Safe Module Unloading
```bash
# Unload module with verification
cleanup_module() {
    if lsmod | grep -q donor_dump; then
        if sudo rmmod donor_dump; then
            echo "✓ Module unloaded successfully"
        else
            echo "Warning: Module unload failed"
            echo "Check: lsmod | grep donor_dump"
            echo "Force remove: sudo rmmod -f donor_dump"
        fi
    fi
}

# Set trap for cleanup on script exit
trap cleanup_module EXIT
```

#### Verify Output Quality
```bash
# Comprehensive output validation
validate_donor_dump() {
    local json_file="$1"
    
    echo "Validating donor dump quality..."
    
    # Check required fields
    local required_fields=("vendor_id" "device_id" "class_code")
    for field in "${required_fields[@]}"; do
        if ! grep -q "\"$field\"" "$json_file"; then
            echo "Warning: Missing required field: $field"
        fi
    done
    
    # Check file size (should be reasonable)
    local file_size=$(stat -f%z "$json_file" 2>/dev/null || stat -c%s "$json_file" 2>/dev/null)
    if [ "$file_size" -lt 100 ]; then
        echo "Warning: Donor dump seems too small ($file_size bytes)"
    elif [ "$file_size" -gt 10000 ]; then
        echo "Warning: Donor dump seems unusually large ($file_size bytes)"
    else
        echo "✓ Donor dump size looks reasonable ($file_size bytes)"
    fi
}

validate_donor_dump "$JSON_FILE"
```

## Validation and Testing

### Donor Dump Quality Validation

#### Comprehensive Validation Script
```bash
#!/bin/bash
# validate_donor_dump.sh - Comprehensive donor dump validation

validate_donor_dump() {
    local json_file="$1"
    local errors=0
    local warnings=0
    
    echo "=== Donor Dump Validation Report ==="
    echo "File: $json_file"
    echo "Generated: $(date)"
    echo ""
    
    # Check file existence and readability
    if [ ! -f "$json_file" ]; then
        echo "❌ ERROR: File does not exist"
        return 1
    fi
    
    if [ ! -r "$json_file" ]; then
        echo "❌ ERROR: File is not readable"
        return 1
    fi
    
    # Validate JSON syntax
    if command -v jq >/dev/null 2>&1; then
        if ! jq empty "$json_file" 2>/dev/null; then
            echo "❌ ERROR: Invalid JSON syntax"
            ((errors++))
        else
            echo "✓ JSON syntax valid"
        fi
    else
        echo "⚠ WARNING: jq not available, skipping JSON validation"
        ((warnings++))
    fi
    
    # Check required fields
    local required_fields=(
        ".device_info.vendor_id"
        ".device_info.device_id"
        ".metadata.device_bdf"
    )
    
    for field in "${required_fields[@]}"; do
        if command -v jq >/dev/null 2>&1; then
            if [ "$(jq -r "$field // empty" "$json_file")" = "" ]; then
                echo "❌ ERROR: Missing required field: $field"
                ((errors++))
            else
                echo "✓ Required field present: $field"
            fi
        fi
    done
    
    # Validate field formats
    if command -v jq >/dev/null 2>&1; then
        # Check vendor_id format (4 hex digits)
        vendor_id=$(jq -r '.device_info.vendor_id // empty' "$json_file")
        if [[ ! "$vendor_id" =~ ^[0-9A-Fa-f]{4}$ ]]; then
            echo "❌ ERROR: Invalid vendor_id format: $vendor_id"
            ((errors++))
        fi
        
        # Check device_id format (4 hex digits)
        device_id=$(jq -r '.device_info.device_id // empty' "$json_file")
        if [[ ! "$device_id" =~ ^[0-9A-Fa-f]{4}$ ]]; then
            echo "❌ ERROR: Invalid device_id format: $device_id"
            ((errors++))
        fi
        
        # Check BDF format
        bdf=$(jq -r '.metadata.device_bdf // empty' "$json_file")
        if [[ ! "$bdf" =~ ^[0-9A-Fa-f]{4}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}\.[0-9A-Fa-f]$ ]]; then
            echo "⚠ WARNING: Unusual BDF format: $bdf"
            ((warnings++))
        fi
    fi
    
    # File size checks
    local file_size=$(stat -f%z "$json_file" 2>/dev/null || stat -c%s "$json_file" 2>/dev/null)
    if [ "$file_size" -lt 200 ]; then
        echo "⚠ WARNING: File seems small ($file_size bytes) - may be incomplete"
        ((warnings++))
    elif [ "$file_size" -gt 50000 ]; then
        echo "⚠ WARNING: File seems large ($file_size bytes) - may contain unexpected data"
        ((warnings++))
    fi
    
    echo ""
    echo "=== Validation Summary ==="
    echo "Errors: $errors"
    echo "Warnings: $warnings"
    
    if [ "$errors" -eq 0 ]; then
        echo "✅ Validation PASSED"
        return 0
    else
        echo "❌ Validation FAILED"
        return 1
    fi
}

# Usage: validate_donor_dump "path/to/donor_info.json"
```

### Integration Testing

#### Test with PCILeech Generator
```bash
#!/bin/bash
# test_donor_integration.sh - Test donor dump with PCILeech

test_donor_integration() {
    local donor_file="$1"
    local test_board="${2:-pcileech_35t325_x1}"
    local test_bdf="${3:-0000:03:00.0}"
    
    echo "Testing donor dump integration..."
    
    # Validate donor file first
    if ! validate_donor_dump "$donor_file"; then
        echo "❌ Donor dump validation failed"
        return 1
    fi
    
    # Test dry-run with PCILeech generator
    if command -v pcileech-generate >/dev/null 2>&1; then
        echo "Testing with PCILeech generator (dry-run)..."
        if pcileech-generate \
            --bdf "$test_bdf" \
            --board "$test_board" \
            --donor-info-file "$donor_file" \
            --dry-run; then
            echo "✅ Integration test PASSED"
            return 0
        else
            echo "❌ Integration test FAILED"
            return 1
        fi
    else
        echo "⚠ PCILeech generator not available, skipping integration test"
        return 0
    fi
}
```

## Troubleshooting

### Common Issues and Solutions

#### Linux-Specific Issues

**1. Kernel Headers Mismatch**
```bash
# Problem: Headers don't match running kernel
# Solution: Install correct headers or use DKMS

# Check current kernel vs available headers
echo "Running kernel: $(uname -r)"
echo "Available headers:"
ls /lib/modules/*/build 2>/dev/null || echo "No headers found"

# Fix with DKMS (recommended)
sudo apt-get install dkms
sudo dkms add ./donor_dump
sudo dkms build donor_dump/1.0
sudo dkms install donor_dump/1.0
```

**2. Module Loading Failures**
```bash
# Comprehensive module debugging
debug_module_load() {
    local module_path="$1"
    local bdf="$2"
    
    echo "Debugging module load for $module_path with BDF $bdf"
    
    # Check module dependencies
    echo "Module info:"
    modinfo "$module_path"
    
    # Check for conflicting modules
    echo "Checking for conflicts:"
    lsmod | grep -E "(pci|donor)"
    
    # Attempt load with verbose logging
    echo "Loading with verbose logging:"
    sudo insmod "$module_path" bdf="$bdf" debug=1
    
    # Check kernel logs
    echo "Recent kernel messages:"
    dmesg | tail -20
}
```

**3. Device Access Issues**
```bash
# Check device binding and driver conflicts
check_device_binding() {
    local bdf="$1"
    
    echo "Device binding status for $bdf:"
    
    # Check current driver
    if [ -d "/sys/bus/pci/devices/$bdf" ]; then
        echo "Device exists in sysfs"
        
        if [ -L "/sys/bus/pci/devices/$bdf/driver" ]; then
            current_driver=$(readlink "/sys/bus/pci/devices/$bdf/driver" | xargs basename)
            echo "Current driver: $current_driver"
            
            # Suggest unbinding if necessary
            echo "To unbind: echo '$bdf' | sudo tee /sys/bus/pci/devices/$bdf/driver/unbind"
        else
            echo "No driver bound"
        fi
    else
        echo "❌ Device not found in sysfs"
    fi
}
```

### Performance Optimization

#### Batch Processing Multiple Devices
```bash
#!/bin/bash
# batch_donor_dump.sh - Process multiple devices efficiently

batch_donor_dump() {
    local device_list="$1"  # File with one BDF per line
    local output_dir="$2"
    
    mkdir -p "$output_dir"
    
    # Build module once
    echo "Building donor_dump module..."
    if ! make -C src/donor_dump; then
        echo "❌ Module build failed"
        return 1
    fi
    
    # Process each device
    while IFS= read -r bdf; do
        [ -z "$bdf" ] && continue
        [[ "$bdf" =~ ^#.*$ ]] && continue  # Skip comments
        
        echo "Processing device: $bdf"
        
        # Create device-specific output directory
        device_dir="$output_dir/${bdf//:/_}"
        mkdir -p "$device_dir"
        
        # Load module for this device
        if sudo insmod src/donor_dump/donor_dump.ko bdf="$bdf"; then
            # Extract data
            cat /proc/donor_dump > "$device_dir/donor_info.txt"
            
            # Convert to JSON
            convert_to_json "$device_dir/donor_info.txt" "$device_dir/donor_info.json"
            
            # Unload module
            sudo rmmod donor_dump
            
            echo "✓ Completed: $bdf"
        else
            echo "❌ Failed: $bdf"
        fi
        
        # Brief pause to avoid overwhelming the system
        sleep 1
    done < "$device_list"
}
```

## Advanced Usage

### Custom Data Extraction

#### Extended Information Gathering
```bash
# Enhanced donor dump with additional system context
create_extended_donor_dump() {
    local bdf="$1"
    local output_file="$2"
    
    # Standard donor dump
    cat /proc/donor_dump > "${output_file}.raw"
    
    # Add system context
    {
        echo "=== EXTENDED DONOR DUMP ==="
        echo "Generated: $(date -Iseconds)"
        echo "System: $(uname -a)"
        echo "BDF: $bdf"
        echo ""
        
        echo "=== DEVICE INFORMATION ==="
        lspci -vvv -s "${bdf#0000:}"
        echo ""
        
        echo "=== SYSTEM PCI TREE ==="
        lspci -tv
        echo ""
        
        echo "=== IOMMU GROUPS ==="
        find /sys/kernel/iommu_groups/ -name "*" -type l | \
            xargs -I {} sh -c 'echo "Group $(basename $(dirname {})): $(basename $(readlink {}))"' | \
            grep "$bdf" || echo "No IOMMU group found"
        echo ""
        
        echo "=== DONOR DUMP DATA ==="
        cat "${output_file}.raw"
        
    } > "$output_file"
}
```

### Automation Integration

#### CI/CD Pipeline Integration
```yaml
# .github/workflows/donor-dump-validation.yml
name: Donor Dump Validation

on:
  push:
    paths:
      - 'donor_dumps/**'
      - 'src/donor_dump/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y jq
          
      - name: Validate donor dumps
        run: |
          for dump in donor_dumps/*.json; do
            echo "Validating $dump"
            ./scripts/validate_donor_dump.sh "$dump"
          done
```

### Security Considerations

#### Safe Module Handling
```bash
# Secure module loading with verification
secure_module_load() {
    local module_path="$1
```

### Automation Integration

#### CI/CD Pipeline Integration
```yaml
# .github/workflows/donor-dump-validation.yml
name: Donor Dump Validation

on:
  push:
    paths:
      - 'donor_dumps/**'
      - 'src/donor_dump/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y jq
          
      - name: Validate donor dumps
        run: |
          for dump in donor_dumps/*.json; do
            echo "Validating $dump"
            ./scripts/validate_donor_dump.sh "$dump"
          done
```

### Security Considerations

#### Safe Module Handling
```bash
# Secure module loading with verification
secure_module_load() {
    local module_path="$1"
    local bdf="$2"
    
    # Verify module signature (if available)
    if command -v modinfo >/dev/null 2>&1; then
        modinfo "$module_path" | grep -q "signature" && echo "✓ Module is signed"
    fi
    
    # Check module for suspicious content
    if command -v strings >/dev/null 2>&1; then
        if strings "$module_path" | grep -qE "(rm -rf|format|delete)"; then
            echo "⚠ WARNING: Module contains potentially dangerous strings"
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            [[ ! $REPLY =~ ^[Yy]$ ]] && return 1
        fi
    fi
    
    # Load with restricted permissions
    sudo insmod "$module_path" bdf="$bdf"
}
```

#### Privilege Management
```bash
# Check and minimize required privileges
check_privileges() {
    if [ "$EUID" -ne 0 ]; then
        echo "This script requires root privileges for:"
        echo "- Loading kernel modules"
        echo "- Accessing PCI configuration space"
        echo "- Reading /proc interfaces"
        echo ""
        echo "Run with: sudo $0"
        exit 1
    fi
    
    # Drop privileges where possible
    if command -v sudo >/dev/null 2>&1; then
        ORIGINAL_USER="${SUDO_USER:-$USER}"
        echo "Running as root, will drop privileges where possible"
    fi
}
```

## Best Practices Summary

### Development Workflow
1. **Always validate prerequisites** before starting
2. **Use version control** for donor dump files
3. **Document device-specific quirks** in metadata
4. **Test with multiple board types** when possible
5. **Maintain backup copies** of working donor dumps

### Production Deployment
1. **Automate validation** in CI/CD pipelines
2. **Use secure module signing** in production
3. **Monitor for kernel compatibility** issues
4. **Implement rollback procedures** for failed dumps
5. **Log all operations** for audit trails

### Performance Optimization
1. **Batch process multiple devices** when possible
2. **Cache build artifacts** to avoid rebuilds
3. **Use parallel processing** for validation
4. **Minimize module load/unload cycles**
5. **Implement smart retry logic** for transient failures

## Conclusion

This enhanced manual donor dump generation guide provides:

- **Comprehensive error handling** for robust operation
- **Cross-platform support** for Linux and Windows
- **Validation and testing frameworks** for quality assurance
- **Performance optimizations** for batch processing
- **Security considerations** for safe operation
- **Integration examples** for automation workflows

The manual process gives you complete control over donor dump generation, making it ideal for:
- **Debugging** automated tool failures
- **Research and development** of new features
- **Custom integration** with existing workflows
- **Educational purposes** to understand the process

For most users, the automated [`pcileech.py`](../PCILeechFWGenerator/pcileech.py) command or [TUI interface](tui-readme.md) remains the recommended approach, but this manual process provides a powerful alternative when needed.

## Quick Reference

### Essential Commands

**Linux:**
```bash
# Quick donor dump
cd PCILeechFWGenerator/src/donor_dump
make && sudo insmod donor_dump.ko bdf=0000:03:00.0
cat /proc/donor_dump > donor_info.txt
sudo rmmod donor_dump
```

### File Locations
- **Linux module source**: [`src/donor_dump/`](../PCILeechFWGenerator/src/donor_dump/)
- **Validation tools**: [`scripts/validate_donor_dump.sh`](../PCILeechFWGenerator/scripts/validate_donor_dump.sh)
- **Output directory**: `donor_dumps/YYYYMMDD_HHMMSS_BDF/`

### Support Resources
- **Main documentation**: [Home](Home.md)
- **TUI guide**: [TUI README](tui-readme.md)
- **Development guide**: [Development](Development.md)
- **Firmware uniqueness**: [Firmware Uniqueness](firmware-uniqueness.md)