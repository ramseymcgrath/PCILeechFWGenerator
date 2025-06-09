# Windows Donor Dump Script for PCILeech Firmware Generator
# This script extracts PCI device parameters similar to the Linux donor_dump kernel module
# Run with administrator privileges for full access to device information

param (
    [Parameter(Mandatory=$true)]
    [string]$BDF,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputFile = "donor_info.json",
    
    [Parameter(Mandatory=$false)]
    [switch]$ExtendedInfo = $true
)

# Function to convert BDF format (0000:00:00.0) to Windows device path format
function Convert-BDFToDevicePath {
    param (
        [string]$BDF
    )
    
    if ($BDF -match "([0-9a-fA-F]{4}):([0-9a-fA-F]{2}):([0-9a-fA-F]{2})\.([0-7])") {
        $Domain = [Convert]::ToInt32($Matches[1], 16)
        $Bus = [Convert]::ToInt32($Matches[2], 16)
        $Device = [Convert]::ToInt32($Matches[3], 16)
        $Function = [Convert]::ToInt32($Matches[4], 16)
        
        return "PCI\VEN_*&DEV_*&SUBSYS_*&REV_*&BUS_$($Bus.ToString("X2"))&DEV_$($Device.ToString("X2"))&FUNC_$($Function.ToString("X"))"
    }
    else {
        throw "Invalid BDF format. Expected format: 0000:00:00.0"
    }
}

# Function to get PCI device information using WMI
function Get-PCIDeviceInfo {
    param (
        [string]$DevicePath
    )
    
    $Devices = Get-WmiObject -Class Win32_PnPEntity | Where-Object { $_.DeviceID -like $DevicePath }
    
    if ($Devices.Count -eq 0) {
        throw "No PCI device found matching $DevicePath"
    }
    
    return $Devices
}

# Function to get PCI configuration space data
function Get-PCIConfigSpace {
    param (
        [string]$BDF
    )
    
    # Parse BDF components
    if ($BDF -match "([0-9a-fA-F]{4}):([0-9a-fA-F]{2}):([0-9a-fA-F]{2})\.([0-7])") {
        $Domain = [Convert]::ToInt32($Matches[1], 16)
        $Bus = [Convert]::ToInt32($Matches[2], 16)
        $Device = [Convert]::ToInt32($Matches[3], 16)
        $Function = [Convert]::ToInt32($Matches[4], 16)
    }
    else {
        throw "Invalid BDF format. Expected format: 0000:00:00.0"
    }
    
    # Load the required C# code for direct hardware access
    # Note: This requires administrator privileges
    $PciConfigCode = @"
using System;
using System.Runtime.InteropServices;

public class PciConfig
{
    [DllImport("advapi32.dll", SetLastError = true)]
    public static extern IntPtr GetCurrentProcess();

    [DllImport("advapi32.dll", SetLastError = true)]
    public static extern bool OpenProcessToken(IntPtr ProcessHandle, uint DesiredAccess, out IntPtr TokenHandle);

    [DllImport("advapi32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern bool LookupPrivilegeValue(string lpSystemName, string lpName, ref LUID lpLuid);

    [DllImport("advapi32.dll", SetLastError = true)]
    public static extern bool AdjustTokenPrivileges(IntPtr TokenHandle, bool DisableAllPrivileges, ref TOKEN_PRIVILEGES NewState, uint BufferLength, IntPtr PreviousState, IntPtr ReturnLength);

    [DllImport("inpoutx64.dll", EntryPoint = "MapPhysToLin", SetLastError = true)]
    public static extern IntPtr MapPhysToLin(ulong PhysAddr, uint PhysSize, out IntPtr PhysicalMemoryHandle);

    [DllImport("inpoutx64.dll", EntryPoint = "UnmapPhysicalMemory", SetLastError = true)]
    public static extern bool UnmapPhysicalMemory(IntPtr PhysicalMemoryHandle, IntPtr LinAddr);

    [DllImport("inpoutx64.dll", EntryPoint = "DlPortReadPortUchar", SetLastError = true)]
    public static extern byte DlPortReadPortUchar(ushort PortAddress);

    [DllImport("inpoutx64.dll", EntryPoint = "DlPortWritePortUchar", SetLastError = true)]
    public static extern void DlPortWritePortUchar(ushort PortAddress, byte Value);

    [DllImport("inpoutx64.dll", EntryPoint = "DlPortReadPortUshort", SetLastError = true)]
    public static extern ushort DlPortReadPortUshort(ushort PortAddress);

    [DllImport("inpoutx64.dll", EntryPoint = "DlPortWritePortUshort", SetLastError = true)]
    public static extern void DlPortWritePortUshort(ushort PortAddress, ushort Value);

    [DllImport("inpoutx64.dll", EntryPoint = "DlPortReadPortUlong", SetLastError = true)]
    public static extern uint DlPortReadPortUlong(ushort PortAddress);

    [DllImport("inpoutx64.dll", EntryPoint = "DlPortWritePortUlong", SetLastError = true)]
    public static extern void DlPortWritePortUlong(ushort PortAddress, uint Value);

    [StructLayout(LayoutKind.Sequential)]
    public struct LUID
    {
        public uint LowPart;
        public int HighPart;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct LUID_AND_ATTRIBUTES
    {
        public LUID Luid;
        public uint Attributes;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct TOKEN_PRIVILEGES
    {
        public uint PrivilegeCount;
        public LUID_AND_ATTRIBUTES Privileges;
    }

    public const uint SE_PRIVILEGE_ENABLED = 0x00000002;
    public const uint TOKEN_ADJUST_PRIVILEGES = 0x00000020;
    public const uint TOKEN_QUERY = 0x00000008;

    public static bool EnablePrivilege(string lpszPrivilege)
    {
        IntPtr hToken = IntPtr.Zero;
        LUID luid = new LUID();
        TOKEN_PRIVILEGES tp = new TOKEN_PRIVILEGES();

        if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, out hToken))
            return false;

        if (!LookupPrivilegeValue(null, lpszPrivilege, ref luid))
            return false;

        tp.PrivilegeCount = 1;
        tp.Privileges.Luid = luid;
        tp.Privileges.Attributes = SE_PRIVILEGE_ENABLED;

        if (!AdjustTokenPrivileges(hToken, false, ref tp, 0, IntPtr.Zero, IntPtr.Zero))
            return false;

        return true;
    }

    // PCI Configuration Space Access
    public const ushort PCI_CONFIG_ADDRESS = 0xCF8;
    public const ushort PCI_CONFIG_DATA = 0xCFC;

    public static uint ReadPciConfig(byte bus, byte device, byte function, byte offset)
    {
        uint address = (uint)(0x80000000 | (bus << 16) | (device << 11) | (function << 8) | (offset & 0xFC));
        DlPortWritePortUlong(PCI_CONFIG_ADDRESS, address);
        return DlPortReadPortUlong(PCI_CONFIG_DATA);
    }

    public static void WritePciConfig(byte bus, byte device, byte function, byte offset, uint value)
    {
        uint address = (uint)(0x80000000 | (bus << 16) | (device << 11) | (function << 8) | (offset & 0xFC));
        DlPortWritePortUlong(PCI_CONFIG_ADDRESS, address);
        DlPortWritePortUlong(PCI_CONFIG_DATA, value);
    }

    public static byte[] ReadPciConfigSpace(byte bus, byte device, byte function, int size = 4096)
    {
        byte[] configSpace = new byte[size];
        
        // Enable access to hardware
        EnablePrivilege("SeSystemProfilePrivilege");
        
        for (int offset = 0; offset < size; offset += 4)
        {
            uint value;
            
            if (offset < 256) {
                // First 256 bytes can be accessed directly through standard PCI config space
                value = ReadPciConfig(bus, device, function, (byte)(offset & 0xFF));
            } else {
                // For extended config space (beyond 256 bytes), we need to use a different approach
                // This is a simplified implementation and may not work on all systems
                // For real hardware access, a more sophisticated approach might be needed
                
                // Check if we're in extended config space range
                if (offset >= 4096) {
                    // Fill with 0xFF for out of range
                    value = 0xFFFFFFFF;
                } else {
                    try {
                        // Try to access extended config space
                        // This is a simplified approach - in reality, extended config space
                        // access is more complex and hardware-dependent
                        value = ReadPciConfig(bus, device, function, (byte)(0xE0 + ((offset >> 8) & 0x0F)));
                        value = ReadPciConfig(bus, device, function, (byte)(offset & 0xFF));
                    } catch {
                        // If access fails, fill with 0xFF
                        value = 0xFFFFFFFF;
                    }
                }
            }
            
            // Convert uint to bytes and store in array
            configSpace[offset] = (byte)(value & 0xFF);
            if (offset + 1 < size) configSpace[offset + 1] = (byte)((value >> 8) & 0xFF);
            if (offset + 2 < size) configSpace[offset + 2] = (byte)((value >> 16) & 0xFF);
            if (offset + 3 < size) configSpace[offset + 3] = (byte)((value >> 24) & 0xFF);
        }
        
        return configSpace;
    }
}
"@

    # Check if inpoutx64.dll is available
    $InpOutDllPath = "$PSScriptRoot\inpoutx64.dll"
    if (-not (Test-Path $InpOutDllPath)) {
        Write-Warning "inpoutx64.dll not found at $InpOutDllPath"
        Write-Warning "Extended PCI configuration space access will be limited"
        Write-Warning "Download inpoutx64.dll from http://www.highrez.co.uk/downloads/inpout32/ and place it in the script directory"
        
        # Return empty config space as we can't access it without the DLL
        return @{
            "ConfigSpace" = [byte[]]::new(0)
            "HasFullAccess" = $false
        }
    }
    
    try {
        Add-Type -TypeDefinition $PciConfigCode -Language CSharp
        
        # Read PCI configuration space (full 4KB)
        $ConfigSpace = [PciConfig]::ReadPciConfigSpace($Bus, $Device, $Function, 4096)
        
        return @{
            "ConfigSpace" = $ConfigSpace
            "HasFullAccess" = $true
            "Size" = 4096
        }
    }
    catch {
        Write-Warning "Error accessing PCI configuration space: $_"
        Write-Warning "Limited PCI information will be available"
        
        return @{
            "ConfigSpace" = [byte[]]::new(0)
            "HasFullAccess" = $false
        }
    }
}

# Function to extract device parameters from configuration space
function Extract-DeviceParameters {
    param (
        [byte[]]$ConfigSpace,
        [bool]$HasFullAccess,
        [object]$WmiDevice
    )
    
    $DeviceInfo = @{}
    
    # If we have full access to config space
    if ($HasFullAccess -and $ConfigSpace.Length -ge 256) {
        # Extract vendor and device IDs
        $VendorID = [BitConverter]::ToUInt16($ConfigSpace, 0)
        $DeviceID = [BitConverter]::ToUInt16($ConfigSpace, 2)
        $Command = [BitConverter]::ToUInt16($ConfigSpace, 4)
        $Status = [BitConverter]::ToUInt16($ConfigSpace, 6)
        $RevisionID = $ConfigSpace[8]
        $ClassCode = ($ConfigSpace[11] -shl 16) -bor ($ConfigSpace[10] -shl 8) -bor $ConfigSpace[9]
        $SubsystemVendorID = [BitConverter]::ToUInt16($ConfigSpace, 44)
        $SubsystemID = [BitConverter]::ToUInt16($ConfigSpace, 46)
        
        # Extract capabilities pointer
        $CapPtr = $ConfigSpace[52]
        
        # Extract Max Payload Size and Max Read Request Size
        $MPC = 0
        $MPR = 0
        
        # Walk capability list to find PCIe capability
        $CurrentPtr = $CapPtr
        while ($CurrentPtr -ne 0 -and $CurrentPtr -lt $ConfigSpace.Length) {
            $CapID = $ConfigSpace[$CurrentPtr]
            $NextPtr = $ConfigSpace[$CurrentPtr + 1]
            
            # PCIe capability ID is 0x10
            if ($CapID -eq 0x10) {
                # PCIe capability structure
                # DevCap is at offset 4 from capability start
                $DevCap = [BitConverter]::ToUInt32($ConfigSpace, $CurrentPtr + 4)
                # DevCtl is at offset 8 from capability start
                $DevCtl = [BitConverter]::ToUInt32($ConfigSpace, $CurrentPtr + 8)
                
                # Extract MPC from DevCap (bits 0-2)
                $MPC = $DevCap -band 0x7
                
                # Extract MPR from DevCtl (bits 5-7)
                $MPR = ($DevCtl -shr 5) -band 0x7
                
                break
            }
            
            # Move to next capability
            $CurrentPtr = $NextPtr
        }
        
        # Populate device info
        $DeviceInfo["vendor_id"] = "0x" + $VendorID.ToString("X4")
        $DeviceInfo["device_id"] = "0x" + $DeviceID.ToString("X4")
        $DeviceInfo["subvendor_id"] = "0x" + $SubsystemVendorID.ToString("X4")
        $DeviceInfo["subsystem_id"] = "0x" + $SubsystemID.ToString("X4")
        $DeviceInfo["revision_id"] = "0x" + $RevisionID.ToString("X2")
        $DeviceInfo["class_code"] = "0x" + $ClassCode.ToString("X6")
        $DeviceInfo["mpc"] = "0x" + $MPC.ToString("X")
        $DeviceInfo["mpr"] = "0x" + $MPR.ToString("X")
        
        # Convert config space to hex string
        $ConfigHex = [System.BitConverter]::ToString($ConfigSpace).Replace("-", "").ToLower()
        $DeviceInfo["extended_config"] = $ConfigHex
        
        # Save config space in a format suitable for $readmemh
        $ConfigHexPath = Join-Path (Split-Path -Parent $OutputFile) "config_space_init.hex"
        Save-ConfigSpaceHex -ConfigSpace $ConfigSpace -OutputPath $ConfigHexPath
    }
    else {
        # Extract from WMI if available
        if ($WmiDevice) {
            # Parse device ID to extract vendor and device IDs
            if ($WmiDevice.DeviceID -match "PCI\\VEN_([0-9A-F]{4})&DEV_([0-9A-F]{4})&SUBSYS_([0-9A-F]{8})&REV_([0-9A-F]{2})") {
                $VendorID = $Matches[1]
                $DeviceID = $Matches[2]
                $Subsys = $Matches[3]
                $RevisionID = $Matches[4]
                
                $SubsystemVendorID = $Subsys.Substring(4, 4)
                $SubsystemID = $Subsys.Substring(0, 4)
                
                $DeviceInfo["vendor_id"] = "0x" + $VendorID
                $DeviceInfo["device_id"] = "0x" + $DeviceID
                $DeviceInfo["subvendor_id"] = "0x" + $SubsystemVendorID
                $DeviceInfo["subsystem_id"] = "0x" + $SubsystemID
                $DeviceInfo["revision_id"] = "0x" + $RevisionID
                
                # Default values for MPC and MPR
                $DeviceInfo["mpc"] = "0x2"  # Default to 512 bytes
                $DeviceInfo["mpr"] = "0x2"  # Default to 512 bytes
                
                # Try to get class code from WMI
                if ($WmiDevice.PNPClass -eq "Net") {
                    $DeviceInfo["class_code"] = "0x020000"  # Network controller
                }
                elseif ($WmiDevice.PNPClass -eq "HDC") {
                    $DeviceInfo["class_code"] = "0x010000"  # Storage controller
                }
                elseif ($WmiDevice.PNPClass -eq "Display") {
                    $DeviceInfo["class_code"] = "0x030000"  # Display controller
                }
                else {
                    $DeviceInfo["class_code"] = "0x000000"  # Unknown
                }
            }
        }
        else {
            # Default values if no information is available
            $DeviceInfo["vendor_id"] = "0x8086"  # Intel
            $DeviceInfo["device_id"] = "0x1533"  # I210 Gigabit Network Connection
            $DeviceInfo["subvendor_id"] = "0x8086"
            $DeviceInfo["subsystem_id"] = "0x0000"
            $DeviceInfo["revision_id"] = "0x03"
            $DeviceInfo["class_code"] = "0x020000"  # Network controller
            $DeviceInfo["mpc"] = "0x2"  # Default to 512 bytes
            $DeviceInfo["mpr"] = "0x2"  # Default to 512 bytes
        }
    }
    
    # Add additional fields required by PCILeech
    $DeviceInfo["bar_size"] = "0x20000"  # Default to 128KB
    $DeviceInfo["dsn_hi"] = "0x0"
    $DeviceInfo["dsn_lo"] = "0x0"
    $DeviceInfo["power_mgmt"] = "0x0"
    $DeviceInfo["aer_caps"] = "0x0"
    $DeviceInfo["vendor_caps"] = "0x0"
    
    return $DeviceInfo
}

# Function to save configuration space in a format suitable for $readmemh
function Save-ConfigSpaceHex {
    param (
        [byte[]]$ConfigSpace,
        [string]$OutputPath
    )
    
    # Create directory if it doesn't exist
    $OutputDir = Split-Path -Parent $OutputPath
    if (-not (Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }
    
    # Format the hex data for $readmemh (32-bit words, one per line)
    $Lines = @()
    for ($i = 0; $i -lt $ConfigSpace.Length; $i += 4) {
        if ($i + 4 <= $ConfigSpace.Length) {
            # Extract 4 bytes
            $Bytes = $ConfigSpace[$i..($i+3)]
            
            # Convert to little-endian format (reverse byte order)
            $LeBytes = $Bytes[3], $Bytes[2], $Bytes[1], $Bytes[0]
            
            # Convert to hex string
            $HexString = [System.BitConverter]::ToString($LeBytes).Replace("-", "").ToLower()
            $Lines += $HexString
        }
    }
    
    # Write to file
    $Lines | Out-File -FilePath $OutputPath -Encoding ascii
    
    Write-Host "Saved configuration space hex data to: $OutputPath" -ForegroundColor Green
}

# Main script execution
try {
    Write-Host "Windows Donor Dump Script for PCILeech Firmware Generator" -ForegroundColor Cyan
    Write-Host "Extracting PCI device parameters for BDF: $BDF" -ForegroundColor Cyan
    
    # Check if running as administrator
    $IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $IsAdmin) {
        Write-Warning "This script requires administrator privileges for full functionality"
        Write-Warning "Some features may be limited"
    }
    
    # Convert BDF to Windows device path format
    $DevicePath = Convert-BDFToDevicePath -BDF $BDF
    Write-Host "Looking for device matching: $DevicePath" -ForegroundColor Gray
    
    # Get device information from WMI
    $WmiDevice = $null
    try {
        $WmiDevice = Get-PCIDeviceInfo -DevicePath $DevicePath
        Write-Host "Found device: $($WmiDevice.Name)" -ForegroundColor Green
    }
    catch {
        Write-Warning "Could not find device using WMI: $_"
        Write-Warning "Will attempt to continue with limited information"
    }
    
    # Get PCI configuration space data
    $ConfigResult = $null
    if ($ExtendedInfo) {
        Write-Host "Attempting to read PCI configuration space..." -ForegroundColor Gray
        $ConfigResult = Get-PCIConfigSpace -BDF $BDF
        
        if ($ConfigResult.HasFullAccess) {
            Write-Host "Successfully read PCI configuration space" -ForegroundColor Green
        }
    }
    
    # Extract device parameters
    $DeviceInfo = Extract-DeviceParameters -ConfigSpace $ConfigResult.ConfigSpace -HasFullAccess $ConfigResult.HasFullAccess -WmiDevice $WmiDevice
    
    # Display extracted information
    Write-Host "`nExtracted Device Parameters:" -ForegroundColor Cyan
    foreach ($Key in $DeviceInfo.Keys | Sort-Object) {
        Write-Host "$Key : $($DeviceInfo[$Key])" -ForegroundColor Yellow
    }
    
    # Save to JSON file
    $DeviceInfo | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputFile -Encoding utf8
    Write-Host "`nDonor information saved to: $OutputFile" -ForegroundColor Green
    
    # Save configuration space in hex format for $readmemh
    $ConfigHexPath = Join-Path (Split-Path -Parent $OutputFile) "config_space_init.hex"
    if (Test-Path $ConfigHexPath) {
        Write-Host "Configuration space hex data saved to: $ConfigHexPath" -ForegroundColor Green
    }
    
    # Instructions for using with PCILeech
    Write-Host "`nTo use this donor information with PCILeech Firmware Generator:" -ForegroundColor Cyan
    Write-Host "sudo pcileech-build --bdf $BDF --board 75t --skip-donor-dump --donor-info-file $OutputFile" -ForegroundColor White
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}