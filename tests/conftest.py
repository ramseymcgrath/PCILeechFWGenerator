"""
conftest.py for pcileechfwgenerator.

If you don't know what this is for, just leave it empty.
Read more about conftest.py under:
- https://docs.pytest.org/en/stable/fixture.html
- https://docs.pytest.org/en/stable/writing_plugins.html
"""

from pathlib import Path
from unittest.mock import Mock

import pytest


@pytest.fixture
def sample_pci_device():
    """Sample PCIDevice for testing"""
    try:
        from src.tui.models.device import PCIDevice
    except ImportError:
        pytest.skip("TUI models not available")

    return PCIDevice(
        bdf="0000:01:00.0",
        vendor_id="10de",
        device_id="1234",
        vendor_name="NVIDIA",
        device_name="Test GPU",
        device_class="Display controller",
        subsystem_vendor="10de",
        subsystem_device="1234",
        driver="nvidia",
        iommu_group="1",
        power_state="D0",
        link_speed="8.0 GT/s",
        bars=[],
        suitability_score=0.9,
        compatibility_issues=[],
    )


@pytest.fixture
def config_dialog():
    """Mock configuration dialog for testing"""
    try:
        from src.tui.main import ConfigurationDialog
    except ImportError:
        pytest.skip("TUI main module not available")

    dialog = ConfigurationDialog(Mock(), Mock())
    dialog.app = Mock()
    dialog.app.config_manager = Mock()
    dialog.query_one = Mock()
    dialog.dismiss = Mock()
    return dialog


@pytest.fixture
def mock_textual_app():
    """Mock Textual app for TUI testing"""
    app = Mock()
    app.notify = Mock()
    app.push_screen = Mock()
    app.query_one = Mock()
    app.config_manager = Mock()
    app.device_manager = Mock()
    app.build_orchestrator = Mock()
    app.status_monitor = Mock()
    return app


@pytest.fixture(scope="session", autouse=True)
def explicit_config_dir():
    """Configure a global DeviceConfigManager for tests that expect on-disk
    profiles.

    This fixture sets `src.device_clone.device_config._config_manager` to an
    instance with `config_dir` pointed at `configs/devices` inside the repo
    root when that directory exists. It avoids changing runtime defaults while
    keeping tests passing.
    """
    try:
        import src.device_clone.device_config as dc
    except Exception:
        # If import fails, nothing to configure
        yield
        return

    prev = getattr(dc, "_config_manager", None)
    repo_root = Path(__file__).resolve().parents[1]
    configs_dir = repo_root / "configs" / "devices"

    if configs_dir.exists():
        dc._config_manager = dc.DeviceConfigManager(config_dir=configs_dir)
    else:
        dc._config_manager = None

    yield

    # Restore previous manager
    dc._config_manager = prev
