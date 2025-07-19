PCILeech Firmware Generator
===========================

Generate authentic PCIe DMA firmware from real donor hardware with a single command. This tool extracts donor configurations from a local device and generates unique PCILeech FPGA bitstreams (and optionally flashes a DMA card over USB-JTAG).

Key Features
------------

- **Donor Hardware Analysis**: Extract real PCIe device configurations and register maps from live hardware via VFIO
- **Full 4KB Config-Space Shadow**: Complete configuration space emulation with BRAM-based overlay memory
- **MSI-X Table Replication**: Exact replication of MSI-X tables from donor devices with interrupt delivery logic
- **Deterministic Variance Seeding**: Consistent hardware variance based on device serial number for unique firmware
- **Advanced SystemVerilog Generation**: Comprehensive PCIe device controller with modular template architecture
- **Active Device Interrupts**: MSI-X interrupt controller with timer-based and event-driven interrupt generation
- **Memory Overlay Mapping**: BAR dispatcher with configurable memory regions and custom PIO windows
- **Interactive TUI**: Modern Textual-based interface with real-time device monitoring and guided workflows
- **Containerized Build Pipeline**: Podman-based synthesis environment with automated VFIO setup
- **Automated Testing and Validation**: Comprehensive test suite with SystemVerilog assertions and Python unit tests
- **USB-JTAG Flashing**: Direct firmware deployment to DMA boards via integrated flash utilities

For the complete documentation, installation instructions, and detailed usage guides, please visit the project repository.

Quick Start
-----------

Installation::

   # Install with TUI support (recommended)
   pip install pcileechfwgenerator[tui]

   # Load required kernel modules
   sudo modprobe vfio vfio-pci

Requirements
~~~~~~~~~~~~

- **Python ≥ 3.9**
- **Donor PCIe card** (any inexpensive NIC, sound, or capture card)
- **Linux OS** (Required)

Optional Requirements
~~~~~~~~~~~~~~~~~~~~~

- **Podman** (required for proper PCIe device mounting)
- **DMA board** (pcileech_75t484_x1, pcileech_35t325_x4, or pcileech_100t484_x1)
- **Vivado Studio** (2022.2+ for synthesis and bitstream generation)
