"""Test SystemVerilog generator validation for critical fields."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.templating.systemverilog_generator import AdvancedSVGenerator
from src.exceptions import TemplateRenderError


class TestSystemVerilogGeneratorValidation:
    """Test validation of critical fields in SystemVerilog generator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_device_config = Mock()
        self.mock_device_config.device_type = Mock(value="network")
        self.mock_device_config.device_class = Mock(value="ethernet")
        self.mock_device_config.enable_dma = True
        self.mock_device_config.max_payload_size = 256
        self.mock_device_config.max_read_request_size = 512
        self.mock_device_config.tx_queue_depth = 1024
        self.mock_device_config.rx_queue_depth = 1024
        self.mock_device_config.command_queue_depth = 256

        self.mock_error_config = Mock()
        self.mock_error_config.enable_ecc = True
        self.mock_perf_config = Mock()
        self.mock_perf_config.enable_transaction_counters = True
        self.mock_power_config = Mock()

        # Create generator instance
        self.generator = AdvancedSVGenerator(
            device_config=self.mock_device_config,
            error_config=self.mock_error_config,
            perf_config=self.mock_perf_config,
            power_config=self.mock_power_config,
        )

        # Mock the renderer
        self.generator.renderer = Mock()
        self.generator.renderer.render_template = Mock(return_value="rendered_content")

    def test_device_signature_missing_raises_error(self):
        """Test that missing device_signature raises TemplateRenderError."""
        # Create template context WITHOUT device_signature
        template_context = {
            "device_config": {
                "vendor_id": "10EC",
                "device_id": "8168",
                "class_code": "020000",
                "revision_id": "01",
            },
            "msix_config": {},
            "bar_config": {},
            "interrupt_config": {},
            # device_signature is intentionally missing
        }

        # Should raise TemplateRenderError due to missing device_signature
        with pytest.raises(TemplateRenderError) as exc_info:
            self.generator.generate_pcileech_modules(template_context)

        assert "device_signature is missing" in str(exc_info.value)
        assert "security" in str(exc_info.value).lower()

    def test_device_signature_none_raises_error(self):
        """Test that None device_signature raises TemplateRenderError."""
        # Create template context with device_signature as None
        template_context = {
            "device_config": {
                "vendor_id": "10EC",
                "device_id": "8168",
                "class_code": "020000",
                "revision_id": "01",
            },
            "device_signature": None,  # Explicitly set to None
            "msix_config": {},
            "bar_config": {},
            "interrupt_config": {},
        }

        # Should raise TemplateRenderError due to None device_signature
        with pytest.raises(TemplateRenderError) as exc_info:
            self.generator.generate_pcileech_modules(template_context)

        assert "device_signature is None or empty" in str(exc_info.value)
        assert "security requirement" in str(exc_info.value).lower()

    def test_device_signature_empty_raises_error(self):
        """Test that empty device_signature raises TemplateRenderError."""
        # Create template context with empty device_signature
        template_context = {
            "device_config": {
                "vendor_id": "10EC",
                "device_id": "8168",
                "class_code": "020000",
                "revision_id": "01",
            },
            "device_signature": "",  # Empty string
            "msix_config": {},
            "bar_config": {},
            "interrupt_config": {},
        }

        # Should raise TemplateRenderError due to empty device_signature
        with pytest.raises(TemplateRenderError) as exc_info:
            self.generator.generate_pcileech_modules(template_context)

        assert "device_signature is None or empty" in str(exc_info.value)
        assert "no fallback values are allowed" in str(exc_info.value).lower()

    def test_valid_device_signature_succeeds(self):
        """Test that valid device_signature allows generation to proceed."""
        # Create template context with valid device_signature
        template_context = {
            "device_config": {
                "vendor_id": "10EC",
                "device_id": "8168",
                "class_code": "020000",
                "revision_id": "01",
            },
            "device_signature": "0xDEADBEEF",  # Valid signature
            "msix_config": {},
            "bar_config": {},
            "interrupt_config": {},
            "config_space_data": {},
            "timing_config": {},
            "pcileech_config": {},
            "generation_metadata": {},
        }

        # Should succeed without raising an error
        result = self.generator.generate_pcileech_modules(template_context)

        # Verify modules were generated
        assert isinstance(result, dict)
        assert "pcileech_tlps128_bar_controller" in result
        assert "pcileech_fifo" in result
        assert "top_level_wrapper" in result
        assert "pcileech_cfgspace.coe" in result

        # Verify renderer was called with device_signature
        calls = self.generator.renderer.render_template.call_args_list
        for call in calls:
            context = call[0][1]  # Second argument is the context
            assert context["device_signature"] == "0xDEADBEEF"

    def test_create_context_preserves_device_signature(self):
        """Test that _create_context properly preserves device_signature."""
        template_context = {
            "device_config": {"vendor_id": "10EC", "device_id": "8168"},
            "device_signature": "0x12345678",
        }

        device_config = {"vendor_id": "10EC", "device_id": "8168"}

        # Call _create_context
        enhanced_context = self.generator._create_context(
            template_context, device_config
        )

        # Verify device_signature is preserved
        assert enhanced_context["device_signature"] == "0x12345678"

    def test_create_context_fails_without_device_signature(self):
        """Test that _create_context fails when device_signature is missing."""
        template_context = {
            "device_config": {"vendor_id": "10EC", "device_id": "8168"}
            # device_signature is missing
        }

        device_config = {"vendor_id": "10EC", "device_id": "8168"}

        # Should raise KeyError due to direct dictionary access
        with pytest.raises(KeyError) as exc_info:
            self.generator._create_context(template_context, device_config)

        assert "device_signature" in str(exc_info.value)

    def test_no_fallback_policy_enforcement(self):
        """Test that no-fallback policy is enforced for device_signature."""
        # This test verifies that the code follows the no-fallback policy
        # by using direct dictionary access instead of .get() with defaults

        template_context = {
            "device_config": {"vendor_id": "10EC", "device_id": "8168"},
            "device_signature": "0xCAFEBABE",
            "msix_config": {},
            "bar_config": {},
        }

        device_config = {"vendor_id": "10EC", "device_id": "8168"}

        # Create context
        enhanced_context = self.generator._create_context(
            template_context, device_config
        )

        # Verify that optional fields use .get() with defaults
        assert enhanced_context["msix_config"] == {}
        assert enhanced_context["bar_config"] == {}

        # Verify that critical field (device_signature) uses direct access
        assert enhanced_context["device_signature"] == "0xCAFEBABE"

        # Verify the implementation doesn't use .get() for device_signature
        # by checking that missing device_signature raises KeyError
        del template_context["device_signature"]
        with pytest.raises(KeyError):
            self.generator._create_context(template_context, device_config)
