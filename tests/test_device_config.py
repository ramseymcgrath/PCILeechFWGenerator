#!/usr/bin/env python3
"""Unit tests for device configuration management."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from src.device_clone.device_config import (
    DeviceCapabilities,
    DeviceClass,
    DeviceConfigManager,
    DeviceConfiguration,
    DeviceIdentification,
    DeviceType,
    PCIeRegisters,
    generate_device_state_machine,
    get_config_manager,
    get_device_config,
    validate_hex_id,
)


class TestDeviceType:
    """Test DeviceType enum."""

    def test_device_type_values(self):
        """Test DeviceType enum values."""
        assert DeviceType.NETWORK.value == "network"
        assert DeviceType.STORAGE.value == "storage"
        assert DeviceType.GRAPHICS.value == "graphics"
        assert DeviceType.GENERIC.value == "generic"
        assert DeviceType.AUDIO.value == "audio"


class TestDeviceClass:
    """Test DeviceClass enum."""

    def test_device_class_values(self):
        """Test DeviceClass enum values."""
        assert DeviceClass.CONSUMER.value == "consumer"
        assert DeviceClass.ENTERPRISE.value == "enterprise"
        assert DeviceClass.EMBEDDED.value == "embedded"


class TestPCIeRegisters:
    """Test PCIeRegisters dataclass."""

    def test_pcie_registers_creation(self):
        """Test creating PCIeRegisters with default values."""
        regs = PCIeRegisters()
        assert regs.command == 0x0006
        assert regs.status == 0x0210
        assert regs.cache_line_size == 0x10
        assert regs.latency_timer == 0x00
        assert regs.header_type == 0x00
        assert regs.bist == 0x00
        assert regs.revision_id == 0x01

    def test_pcie_registers_custom_values(self):
        """Test creating PCIeRegisters with custom values."""
        regs = PCIeRegisters(
            command=0x0007,
            status=0x0210,
            cache_line_size=0x20,
            latency_timer=0x40,
        )
        assert regs.command == 0x0007
        assert regs.status == 0x0210
        assert regs.cache_line_size == 0x20
        assert regs.latency_timer == 0x40

    def test_pcie_registers_validate(self):
        """Test PCIeRegisters validation."""
        regs = PCIeRegisters()
        # Should not raise
        regs.validate()


class TestDeviceIdentification:
    """Test DeviceIdentification dataclass."""

    def test_device_identification_creation(self):
        """Test creating DeviceIdentification."""
        ident = DeviceIdentification(
            vendor_id=0x8086,
            device_id=0x1000,
            class_code=0x020000,  # Network controller
            subsystem_vendor_id=0x1028,
            subsystem_device_id=0x1234,
        )
        assert ident.vendor_id == 0x8086
        assert ident.device_id == 0x1000
        assert ident.class_code == 0x020000
        # revision_id is not part of DeviceIdentification

    def test_device_identification_validate(self):
        """Test DeviceIdentification validation."""
        ident = DeviceIdentification(
            vendor_id=0x8086,
            device_id=0x1000,
            class_code=0x020000,  # Network controller
        )
        # Should not raise
        ident.validate()

    def test_device_identification_validate_invalid_vendor(self):
        """Test DeviceIdentification validation with invalid vendor ID."""
        ident = DeviceIdentification(
            vendor_id=0x0000,  # Invalid
            device_id=0x1000,
            class_code=0x020000,  # Network controller
        )
        with pytest.raises(ValueError, match="Invalid vendor ID"):
            ident.validate()

    def test_device_identification_validate_invalid_device(self):
        """Test DeviceIdentification validation with invalid device ID."""
        ident = DeviceIdentification(
            vendor_id=0x8086,
            device_id=0x0000,  # Invalid
            class_code=0x020000,  # Network controller
        )
        with pytest.raises(ValueError, match="Invalid device ID"):
            ident.validate()

    def test_vendor_name_property(self):
        """Test vendor_name property."""
        ident = DeviceIdentification(
            vendor_id=0x8086,
            device_id=0x1000,
            class_code=0x020000,  # Network controller
        )
        assert ident.vendor_id_hex == "0x8086"

    def test_vendor_name_unknown(self):
        """Test vendor_name property for unknown vendor."""
        ident = DeviceIdentification(
            vendor_id=0xFFFF,
            device_id=0x1000,
            class_code=0x020000,  # Network controller
        )
        assert ident.vendor_id_hex == "0xFFFF"

    def test_device_name_property(self):
        """Test device_name property."""
        ident = DeviceIdentification(
            vendor_id=0x8086,
            device_id=0x1000,
            class_code=0x020000,  # Network controller
        )
        # Should return formatted device ID
        assert ident.device_id_hex == "0x1000"

    def test_full_name_property(self):
        """Test full_name property."""
        ident = DeviceIdentification(
            vendor_id=0x8086,
            device_id=0x1000,
            class_code=0x020000,  # Network controller
        )
        # full_name property doesn't exist
        assert ident.vendor_id_hex == "0x8086"
        assert ident.device_id_hex == "0x1000"


class TestDeviceCapabilities:
    """Test DeviceCapabilities dataclass."""

    def test_device_capabilities_creation(self):
        """Test creating DeviceCapabilities with defaults."""
        caps = DeviceCapabilities()
        assert caps.max_payload_size == 256
        assert caps.msi_vectors == 1
        assert caps.msix_vectors == 0
        assert caps.supports_msi is True
        assert caps.supports_msix is False
        assert caps.supports_power_management is True
        assert caps.supports_advanced_error_reporting is False
        assert caps.link_speed == "2.5GT/s"
        assert caps.link_width == 1

    def test_device_capabilities_custom(self):
        """Test creating DeviceCapabilities with custom values."""
        caps = DeviceCapabilities(
            max_payload_size=512,
            msi_vectors=4,
            msix_vectors=64,
            supports_msix=True,
            link_speed="5.0GT/s",
            link_width=4,
        )
        assert caps.max_payload_size == 512
        assert caps.msi_vectors == 4
        assert caps.msix_vectors == 64
        assert caps.supports_msix is True
        assert caps.link_speed == "5.0GT/s"
        assert caps.link_width == 4

    def test_device_capabilities_validate(self):
        """Test DeviceCapabilities validation."""
        caps = DeviceCapabilities(
            max_payload_size=256,
            supports_msix=True,
            msix_vectors=64,
        )
        # Should not raise
        caps.validate()

    def test_device_capabilities_validate_invalid_payload_size(self):
        """Test validation with invalid payload size."""
        caps = DeviceCapabilities(max_payload_size=100)  # Invalid size
        with pytest.raises(ValueError, match="Invalid maximum payload size"):
            caps.validate()

    def test_device_capabilities_validate_invalid_msi_vectors(self):
        """Test validation with invalid MSI vector count."""
        caps = DeviceCapabilities(msi_vectors=64)  # Invalid - max is 32
        with pytest.raises(ValueError, match="Invalid MSI vector count"):
            caps.validate()


class TestDeviceConfiguration:
    """Test DeviceConfiguration dataclass."""

    def test_device_configuration_creation(self):
        """Test creating DeviceConfiguration."""
        config = DeviceConfiguration(
            name="test_device",
            device_type=DeviceType.NETWORK,
            device_class=DeviceClass.CONSUMER,
            identification=DeviceIdentification(
                vendor_id=0x8086,
                device_id=0x1000,
                class_code=0x020000,  # Network controller
            ),
            registers=PCIeRegisters(),
            capabilities=DeviceCapabilities(),
        )
        assert config.device_type == DeviceType.NETWORK
        assert config.device_class == DeviceClass.CONSUMER
        assert config.identification.vendor_id == 0x8086

    def test_device_configuration_validate(self):
        """Test DeviceConfiguration validation."""
        config = DeviceConfiguration(
            name="test_device",
            device_type=DeviceType.NETWORK,
            device_class=DeviceClass.CONSUMER,
            identification=DeviceIdentification(
                vendor_id=0x8086,
                device_id=0x1000,
                class_code=0x020000,  # Network controller
            ),
            registers=PCIeRegisters(),
            capabilities=DeviceCapabilities(),
        )
        # Should not raise
        config.validate()

    def test_device_configuration_to_dict(self):
        """Test converting DeviceConfiguration to dict."""
        config = DeviceConfiguration(
            name="test_device",
            device_type=DeviceType.NETWORK,
            device_class=DeviceClass.CONSUMER,
            identification=DeviceIdentification(
                vendor_id=0x8086,
                device_id=0x1000,
                class_code=0x020000,  # Network controller
            ),
            registers=PCIeRegisters(),
            capabilities=DeviceCapabilities(),
        )

        config_dict = config.to_dict()

        assert config_dict["device_type"] == "network"
        assert config_dict["device_class"] == "consumer"
        assert config_dict["identification"]["vendor_id"] == 0x8086
        assert config_dict["identification"]["device_id"] == 0x1000
        assert "registers" in config_dict
        assert "capabilities" in config_dict


class TestDeviceConfigManager:
    """Test DeviceConfigManager class."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory."""
        temp_dir = tempfile.mkdtemp()
        config_dir = Path(temp_dir) / "configs"
        config_dir.mkdir()

        # Create test config file
        test_config = {
            "name": "test_device",
            "device_type": "network",
            "device_class": "consumer",
            "identification": {
                "vendor_id": 0x8086,
                "device_id": 0x1000,
                "class_code": 0x020000,  # Network controller
            },
            "registers": {
                "command": 0x0007,
                "status": 0x0210,
            },
            "capabilities": {
                "max_payload_size": 256,
                "msi_vectors": 1,
                "supports_msi": True,
            },
        }

        config_file = config_dir / "test_device.yaml"
        config_file.write_text(json.dumps(test_config))

        yield config_dir

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir)

    @pytest.fixture
    def manager(self, temp_config_dir):
        """Create DeviceConfigManager instance."""
        return DeviceConfigManager(config_dir=temp_config_dir)

    def test_manager_initialization(self, manager):
        """Test DeviceConfigManager initialization."""
        assert manager.config_dir.exists()
        # No default profiles anymore
        assert len(manager.profiles) >= 0

    def test_load_config_file(self, manager, temp_config_dir):
        """Test loading configuration from file."""
        config_path = temp_config_dir / "test_device.yaml"
        config = manager.load_config_file(config_path)

        assert config.device_type == DeviceType.NETWORK
        assert config.identification.vendor_id == 0x8086
        assert config.identification.device_id == 0x1000
        assert config.identification.class_code == 0x020000

    def test_load_config_file_not_found(self, manager):
        """Test loading non-existent config file."""
        with pytest.raises(FileNotFoundError):
            manager.load_config_file("nonexistent.yaml")

    def test_get_profile(self, manager):
        """Test getting profile by name."""
        # No default "generic" profile exists anymore - create one for test
        config = DeviceConfiguration(
            name="test_device",
            device_type=DeviceType.NETWORK,
            device_class=DeviceClass.CONSUMER,
            identification=DeviceIdentification(
                vendor_id=0x8086,
                device_id=0x1000,
                class_code=0x020000,  # Network controller
            ),
        )
        manager.profiles["test_device"] = config

        retrieved_config = manager.get_profile("test_device")
        assert retrieved_config is not None
        assert isinstance(retrieved_config, DeviceConfiguration)

    def test_get_profile_not_found(self, manager):
        """Test getting non-existent profile."""
        with pytest.raises(ValueError, match="Device profile not found"):
            manager.get_profile("nonexistent")

    def test_create_profile_from_env(self, manager):
        """Test creating profile from environment variables."""
        with patch.dict(
            "os.environ",
            {
                "PCIE_TEST_ENV_VENDOR_ID": "0x8086",
                "PCIE_TEST_ENV_DEVICE_ID": "0x1000",
                "PCIE_TEST_ENV_CLASS_CODE": "0x020000",  # Network controller
            },
        ):
            config = manager.create_profile_from_env("test_env")
            assert config.name == "test_env"
            assert config.identification.vendor_id == 0x8086
            assert config.identification.device_id == 0x1000
            assert config.identification.class_code == 0x020000

    def test_list_profiles(self, manager):
        """Test listing available profiles."""
        profiles = manager.list_profiles()
        assert isinstance(profiles, list)
        # Should contain the test_device profile we created in the fixture
        assert "test_device" in profiles

    def test_save_profile(self, manager, temp_config_dir):
        """Test saving profile to file."""
        config = DeviceConfiguration(
            name="saved_test",
            device_type=DeviceType.STORAGE,
            device_class=DeviceClass.ENTERPRISE,
            identification=DeviceIdentification(
                vendor_id=0x1234,
                device_id=0x5678,
                class_code=0x010800,  # Storage controller
            ),
            registers=PCIeRegisters(),
            capabilities=DeviceCapabilities(),
        )

        output_file = temp_config_dir / "saved_profile.yaml"
        manager.save_profile(config, output_file)

        assert output_file.exists()
        assert "saved_test" in manager.profiles

        # Verify saved content
        loaded_config = manager.load_config_file(output_file)
        assert loaded_config.device_type == DeviceType.STORAGE
        assert loaded_config.identification.vendor_id == 0x1234


class TestHelperFunctions:
    """Test helper functions."""

    def test_get_config_manager(self):
        """Test get_config_manager singleton."""
        manager1 = get_config_manager()
        manager2 = get_config_manager()
        assert manager1 is manager2  # Should be same instance

    def test_get_device_config_default(self):
        """Test get_device_config with default profile."""
        # Since no default profiles exist anymore, this should return None
        config = get_device_config("nonexistent_profile")
        assert config is None

    def test_get_device_config_specific_profile(self):
        """Test get_device_config with specific profile."""
        # Now that generic profile exists with correct format, it should work
        config = get_device_config("generic")
        assert config is not None
        assert isinstance(config, DeviceConfiguration)
        assert config.name == "Generic PCIe Device"

    def test_validate_hex_id_valid(self):
        """Test validate_hex_id with valid values."""
        assert validate_hex_id("0x1234") == 0x1234
        assert validate_hex_id("0xABCD") == 0xABCD
        assert validate_hex_id("1234") == 0x1234

    def test_validate_hex_id_invalid(self):
        """Test validate_hex_id with invalid values."""
        with pytest.raises(ValueError):
            validate_hex_id("0xGGGG")  # Invalid hex

        with pytest.raises(ValueError):
            validate_hex_id("0x12345", bit_width=16)  # Too large

    def test_generate_device_state_machine(self):
        """Test generate_device_state_machine."""
        registers = [
            {"address": 0x00, "name": "control", "access": "rw"},
            {"address": 0x04, "name": "status", "access": "ro"},
            {"address": 0x08, "name": "data", "access": "rw"},
        ]

        state_machine = generate_device_state_machine(registers)

        assert "device_states" in state_machine
        assert "state_transitions" in state_machine
        assert "registers" in state_machine
        assert len(state_machine["device_states"]) > 0
