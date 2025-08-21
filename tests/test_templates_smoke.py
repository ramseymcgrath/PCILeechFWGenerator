import pytest

from src.device_clone.device_config import DeviceClass, DeviceType
from src.templating.advanced_sv_features import (ErrorHandlingConfig,
                                                 PerformanceConfig)
from src.templating.advanced_sv_power import PowerManagementConfig
from src.templating.systemverilog_generator import (AdvancedSVGenerator,
                                                    DeviceSpecificLogic)


def test_advanced_controller_renders():
    """Smoke test: render the advanced controller template end-to-end."""
    g = AdvancedSVGenerator(
        device_config=DeviceSpecificLogic(
            device_type=DeviceType.GENERIC, device_class=DeviceClass.CONSUMER
        ),
        power_config=PowerManagementConfig(),
        perf_config=PerformanceConfig(),
        error_config=ErrorHandlingConfig(),
    )

    result = g.generate_advanced_systemverilog(regs=[], variance_model=None)

    assert result and isinstance(result, str)
    # Basic sanity checks
    assert "module" in result or "//" in result
