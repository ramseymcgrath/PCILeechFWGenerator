"""Device-specific configuration for SystemVerilog generation."""

from dataclasses import dataclass
from typing import Optional

from src.device_clone.device_config import DeviceClass, DeviceType


@dataclass
class DeviceSpecificLogic:
    """Configuration for device-specific logic generation."""

    device_type: DeviceType = DeviceType.GENERIC
    device_class: DeviceClass = DeviceClass.CONSUMER

    # Device capabilities
    max_payload_size: int = 256
    max_read_request_size: int = 512
    msi_vectors: int = 1
    msix_vectors: int = 0

    # Device-specific features
    enable_dma: bool = False
    enable_interrupt_coalescing: bool = False
    enable_virtualization: bool = False
    enable_sr_iov: bool = False

    # Queue management
    tx_queue_depth: int = 256
    rx_queue_depth: int = 256
    command_queue_depth: int = 64

    # Buffer sizes
    tx_buffer_size_kb: int = 64
    rx_buffer_size_kb: int = 64

    # Timing characteristics
    base_frequency_mhz: float = 100.0
    memory_frequency_mhz: float = 200.0

    def validate(self) -> None:
        """Validate the configuration values."""
        if self.max_payload_size <= 0:
            raise ValueError(f"Invalid max_payload_size: {self.max_payload_size}")

        if self.max_read_request_size <= 0:
            raise ValueError(
                f"Invalid max_read_request_size: {self.max_read_request_size}"
            )

        if self.tx_queue_depth <= 0:
            raise ValueError(f"Invalid tx_queue_depth: {self.tx_queue_depth}")

        if self.rx_queue_depth <= 0:
            raise ValueError(f"Invalid rx_queue_depth: {self.rx_queue_depth}")

        if self.base_frequency_mhz <= 0:
            raise ValueError(f"Invalid base_frequency_mhz: {self.base_frequency_mhz}")
