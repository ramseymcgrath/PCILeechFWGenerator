# Manual Donor Dump Generation Guide

This guide explains how to manually generate a donor dump file for the PCILeech Firmware Generator without using the automated tools. This can be useful for debugging, custom workflows, or when the automated process doesn't work as expected.

## What is a Donor Dump?

A donor dump contains essential PCI device parameters extracted from a physical device. These parameters are used by the PCILeech Firmware Generator to create firmware that accurately emulates the donor device's behavior.

Key information captured includes:
- Max-Payload-Capable (MPC) and Max-ReadReq-InEffect (MPR) values
- Vendor/device IDs, subsystem information, and revision
- 24-bit class code information
- BAR0 size and Device Serial Number (DSN)
- Full 4KB extended configuration space
- Power management, AER, and vendor-specific capabilities

## Prerequisites

Before starting, ensure you have:

1. A Linux system with root access
2. Kernel headers for your current kernel
3. Basic build tools (gcc, make)
4. A PCI device to use as donor (identified by its BDF - Bus:Device.Function)

### Installing Prerequisites

#### Debian/Ubuntu
```bash
sudo apt-get update
sudo apt-get install linux-headers-$(uname -r) build-essential
```

#### Fedora/CentOS/RHEL
```bash
sudo dnf install kernel-devel-$(uname -r) gcc make
```

#### Arch Linux/Manjaro
```bash
sudo pacman -S linux-headers base-devel
```

#### openSUSE
```bash
sudo zypper install kernel-devel-$(uname -r) gcc make
```

## Step 1: Identify Your Donor Device

Find the BDF (Bus:Device.Function) of your donor PCI device:

```bash
lspci
```

This will list all PCI devices. Look for your target device and note its BDF, which appears at the beginning of each line in the format `XX:XX.X`. For example:

```
03:00.0 Ethernet controller: Intel Corporation I210 Gigabit Network Connection
```

In this case, the BDF is `03:00.0`. For PCILeech, you'll need to add the domain (usually 0000) to make it `0000:03:00.0`.

## Step 2: Build the Donor Dump Kernel Module

Navigate to the donor_dump directory in the PCILeech Firmware Generator:

```bash
cd /path/to/PCILeechFWGenerator/src/donor_dump
```

Build the kernel module:

```bash
make
```

Verify the module was built successfully:

```bash
ls -la donor_dump.ko
```

## Step 3: Load the Module with Your Device

Load the donor_dump kernel module with your device's BDF:

```bash
sudo insmod donor_dump.ko bdf=0000:03:00.0
```

Replace `0000:03:00.0` with your actual device's BDF.

Verify the module loaded successfully:

```bash
lsmod | grep donor_dump
```

## Step 4: Extract the Donor Information

Read the donor information from the proc file:

```bash
cat /proc/donor_dump
```

This will display all the extracted device parameters in key:value format.

## Step 5: Save the Donor Information

Save the output to a file for future use:

```bash
cat /proc/donor_dump > donor_info.txt
```

For use with PCILeech Firmware Generator, you can convert this to JSON format:

```bash
# Create a JSON file manually
echo "{" > donor_info.json
cat donor_info.txt | sed 's/\(.*\):\(.*\)/  "\1": "\2",/' >> donor_info.json
# Remove the trailing comma from the last line and close the JSON
sed -i '$ s/,$/\n}/' donor_info.json
```

## Step 6: Unload the Module

When you're done, unload the kernel module:

```bash
sudo rmmod donor_dump
```

## Step 7: Using the Donor Information with PCILeech

You can now use the saved donor information with PCILeech Firmware Generator:

```bash
sudo pcileech-build --bdf 0000:03:00.0 --board 75t --donor-info-file /path/to/donor_info.json
```

## Alternative: Using the Python API

You can also use the Python API provided by the PCILeech Firmware Generator:

```python
from src.donor_dump_manager import DonorDumpManager

# Initialize the manager
manager = DonorDumpManager()

# Build and load the module for your device
manager.build_module()
manager.load_module("0000:03:00.0")

# Read the device information
device_info = manager.read_device_info()

# Save to a file
manager.save_donor_info(device_info, "donor_info.json")

# Unload the module
manager.unload_module()
```

## Troubleshooting

### Kernel Headers Not Found

If you see an error about missing kernel headers:

```
Error: Kernel headers not found at /lib/modules/$(uname -r)/build
```

Install the appropriate headers for your distribution as shown in the Prerequisites section.

### Module Build Fails

If the module fails to build:

1. Ensure you have the correct kernel headers installed
2. Check for compiler errors in the output
3. Try cleaning and rebuilding:
   ```bash
   make clean
   make
   ```

### Module Load Fails

If the module fails to load:

1. Verify the BDF format is correct (e.g., `0000:03:00.0`)
2. Check if the device exists: `lspci -s 03:00.0`
3. Check kernel logs for errors: `dmesg | grep donor_dump`
4. Ensure you have root privileges

### Device Not Found or Invalid BDF

If you see "PCI device not found" or "Invalid BDF format":

1. Double-check the BDF with `lspci`
2. Ensure you're using the full format with domain: `0000:XX:XX.X`
3. Verify the device is present and enabled in your system

### Secure Boot Issues

If you're using Secure Boot, you may need to:

1. Temporarily disable Secure Boot in your BIOS/UEFI settings
2. Or sign the module (advanced, distribution-specific)

## Conclusion

By following this guide, you've manually generated a donor dump file that can be used with the PCILeech Firmware Generator. This process gives you more control and insight into the donor information extraction process, which can be helpful for debugging or custom workflows.

For most users, the automated process using `pcileech-build` or the TUI is recommended, but this manual approach provides an alternative when needed.

## Windows Support

While the donor_dump kernel module is Linux-specific, we also provide a PowerShell script for Windows users to extract similar donor information.

### Prerequisites for Windows

1. Windows 10 or later with PowerShell 5.1+
2. Administrator privileges
3. For full functionality: inpoutx64.dll (for direct hardware access)

### Using the Windows Donor Dump Script

1. Open PowerShell as Administrator
2. Navigate to the PCILeech Firmware Generator directory
3. Identify your donor device using Device Manager or the following PowerShell command:

```powershell
Get-WmiObject -Class Win32_PnPEntity | Where-Object { $_.PNPClass -eq "Net" -or $_.PNPClass -eq "Display" } | Format-Table Name, DeviceID
```

4. Note the device's location (e.g., PCI bus 3, device 0, function 0)
5. Run the donor dump script:

```powershell
.\scripts\windows_donor_dump.ps1 -BDF "0000:03:00.0" -OutputFile "donor_info.json"
```

Replace `0000:03:00.0` with your device's BDF.

### Windows Script Capabilities

The Windows script provides:
- Basic device identification (vendor/device IDs, subsystem info)
- PCI configuration space extraction (when inpoutx64.dll is available)
- JSON output compatible with PCILeech Firmware Generator

### Limitations on Windows

The Windows script has some limitations compared to the Linux kernel module:
- Some advanced PCI capabilities may not be accessible
- Full configuration space access requires inpoutx64.dll
- Some values may be estimated rather than directly read

### Using Windows Donor Info with PCILeech

After generating the donor info file on Windows, you can use it with PCILeech Firmware Generator on Linux:

```bash
sudo pcileech-build --bdf 0000:03:00.0 --board 75t --donor-info-file /path/to/donor_info.json
```

### Troubleshooting Windows Donor Dump

- **Access Denied**: Ensure you're running PowerShell as Administrator
- **Device Not Found**: Verify the BDF format and check Device Manager
- **Limited Information**: Download inpoutx64.dll from http://www.highrez.co.uk/downloads/inpout32/ and place it in the scripts directory