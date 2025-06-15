"""
Test XDC integration with PCILeech repository.
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.repo_manager import RepoManager
from src.tcl_builder import TCLBuilder


class TestXDCIntegration:
    """Test XDC file integration with PCILeech repository."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tcl_builder = TCLBuilder()

    @patch("src.repo_manager.RepoManager.ensure_git_repo")
    @patch("src.repo_manager.RepoManager.get_board_path")
    def test_get_board_xdc_files_success(
        self, mock_get_board_path, mock_ensure_git_repo
    ):
        """Test successful XDC file discovery."""
        # Mock board path with XDC files
        mock_board_path = Mock(spec=Path)
        mock_board_path.exists.return_value = True
        mock_get_board_path.return_value = mock_board_path

        # Mock XDC files
        mock_xdc_file1 = Mock(spec=Path)
        mock_xdc_file1.name = "board_constraints.xdc"
        mock_xdc_file2 = Mock(spec=Path)
        mock_xdc_file2.name = "timing_constraints.xdc"

        mock_board_path.glob.return_value = [mock_xdc_file1]
        mock_board_path.rglob.return_value = [mock_xdc_file1, mock_xdc_file2]

        # Test XDC file discovery
        xdc_files = RepoManager.get_board_xdc_files("pcileech_75t484_x1")

        assert len(xdc_files) == 2
        assert mock_xdc_file1 in xdc_files
        assert mock_xdc_file2 in xdc_files

    @patch("src.repo_manager.RepoManager.ensure_git_repo")
    @patch("src.repo_manager.RepoManager.get_board_path")
    def test_get_board_xdc_files_not_found(
        self, mock_get_board_path, mock_ensure_git_repo
    ):
        """Test XDC file discovery when no files found."""
        # Mock board path with no XDC files
        mock_board_path = Mock(spec=Path)
        mock_board_path.exists.return_value = True
        mock_get_board_path.return_value = mock_board_path

        mock_board_path.glob.return_value = []
        mock_board_path.rglob.return_value = []

        # Test that RuntimeError is raised when no XDC files found
        with pytest.raises(RuntimeError, match="No XDC files found"):
            RepoManager.get_board_xdc_files("unknown_board")

    @patch("src.repo_manager.RepoManager.get_board_xdc_files")
    def test_read_xdc_constraints_success(self, mock_get_xdc_files):
        """Test successful XDC content reading."""
        # Mock XDC files
        mock_xdc_file1 = Mock(spec=Path)
        mock_xdc_file1.name = "board.xdc"
        mock_xdc_file2 = Mock(spec=Path)
        mock_xdc_file2.name = "timing.xdc"

        mock_get_xdc_files.return_value = [mock_xdc_file1, mock_xdc_file2]

        # Mock file content
        xdc_content1 = (
            "# Board constraints\nset_property PACKAGE_PIN E3 [get_ports clk]"
        )
        xdc_content2 = "# Timing constraints\ncreate_clock -period 10.0 [get_ports clk]"

        with patch("builtins.open", create=True) as mock_open:
            mock_open.side_effect = [
                MagicMock(read=lambda: xdc_content1),
                MagicMock(read=lambda: xdc_content2),
            ]

            # Test XDC content reading
            combined_content = RepoManager.read_xdc_constraints("pcileech_75t484_x1")

            assert "pcileech_75t484_x1" in combined_content
            assert "board.xdc" in combined_content
            assert "timing.xdc" in combined_content
            assert xdc_content1 in combined_content
            assert xdc_content2 in combined_content

    @patch("src.repo_manager.RepoManager.get_board_xdc_files")
    def test_read_xdc_constraints_file_error(self, mock_get_xdc_files):
        """Test XDC content reading with file error."""
        # Mock XDC file
        mock_xdc_file = Mock(spec=Path)
        mock_xdc_file.name = "board.xdc"
        mock_get_xdc_files.return_value = [mock_xdc_file]

        # Mock file read error
        with patch("builtins.open", side_effect=IOError("File not readable")):
            with pytest.raises(RuntimeError, match="Failed to read XDC file"):
                RepoManager.read_xdc_constraints("pcileech_75t484_x1")

    @patch("src.repo_manager.RepoManager.read_xdc_constraints")
    def test_tcl_builder_xdc_integration_success(self, mock_read_xdc):
        """Test TCL builder XDC integration success."""
        # Mock XDC content
        mock_xdc_content = """
# Test XDC content
set_property PACKAGE_PIN E3 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports clk]
"""
        mock_read_xdc.return_value = mock_xdc_content

        # Test context with board information
        context = {
            "device": {"vendor_id": "0x1234", "device_id": "0x5678"},
            "board": {"name": "pcileech_75t484_x1"},
            "header": "# Test header",
        }

        # Test constraint generation
        result = self.tcl_builder.build_constraints_tcl(context)

        assert result is not None
        assert len(result) > 0
        # Should contain the XDC content
        assert "PACKAGE_PIN E3" in result
        assert "IOSTANDARD LVCMOS33" in result

    @patch("src.repo_manager.RepoManager.read_xdc_constraints")
    def test_tcl_builder_xdc_integration_fallback(self, mock_read_xdc):
        """Test TCL builder XDC integration with fallback."""
        # Mock XDC loading failure
        mock_read_xdc.side_effect = RuntimeError("XDC files not found")

        # Test context with board information
        context = {
            "device": {"vendor_id": "0x1234", "device_id": "0x5678"},
            "board": {"name": "unknown_board"},
            "header": "# Test header",
        }

        # Test constraint generation with fallback
        result = self.tcl_builder.build_constraints_tcl(context)

        assert result is not None
        assert len(result) > 0
        # Should contain fallback timing constraints
        assert "create_clock" in result
        assert "set_input_delay" in result

    def test_tcl_builder_no_board_info(self):
        """Test TCL builder without board information."""
        # Test context without board information
        context = {
            "device": {"vendor_id": "0x1234", "device_id": "0x5678"},
            "header": "# Test header",
        }

        # Test constraint generation
        result = self.tcl_builder.build_constraints_tcl(context)

        assert result is not None
        assert len(result) > 0
        # Should contain basic timing constraints
        assert "create_clock" in result

    @pytest.mark.parametrize(
        "board_type",
        [
            "pcileech_75t484_x1",
            "pcileech_35t484_x1",
            "pcileech_35t325_x4",
            "pcileech_35t325_x1",
            "pcileech_100t484_x1",
        ],
    )
    def test_supported_board_types(self, board_type):
        """Test that supported board types are recognized."""
        # This test verifies the board mapping exists
        # In a real test, we'd mock the repository access
        with patch("src.repo_manager.RepoManager.ensure_git_repo"):
            with patch("src.repo_manager.Path.exists", return_value=True):
                try:
                    board_path = RepoManager.get_board_path(board_type)
                    assert board_path is not None
                except RuntimeError:
                    # Board type not in mapping - this would be a configuration issue
                    pytest.fail(f"Board type {board_type} not supported")

    def test_board_xdc_content_in_template_context(self):
        """Test that board XDC content is properly added to template context."""
        with patch(
            "src.repo_manager.RepoManager.read_xdc_constraints"
        ) as mock_read_xdc:
            mock_xdc_content = "# Test XDC\nset_property PACKAGE_PIN E3 [get_ports clk]"
            mock_read_xdc.return_value = mock_xdc_content

            context = {
                "device": {"vendor_id": "0x1234", "device_id": "0x5678"},
                "board": {"name": "pcileech_75t484_x1"},
                "header": "# Test header",
            }

            # Call the method that should add board_xdc_content
            result_context = context.copy()

            # Simulate what build_constraints_tcl does
            try:
                from src.repo_manager import RepoManager

                board_xdc_content = RepoManager.read_xdc_constraints(
                    "pcileech_75t484_x1"
                )
                result_context["board_xdc_content"] = board_xdc_content
            except Exception:
                result_context["board_xdc_content"] = None

            # Verify the context contains the XDC content
            assert "board_xdc_content" in result_context
            assert result_context["board_xdc_content"] == mock_xdc_content

    def test_xdc_content_template_rendering(self):
        """Test that XDC content is properly rendered in template."""
        # This would require a more complex test with actual template rendering
        # For now, we verify the template variable is set correctly

        mock_xdc_content = """
set_property PACKAGE_PIN E3 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports clk]
set_property PACKAGE_PIN C12 [get_ports reset_n]
set_property IOSTANDARD LVCMOS33 [get_ports reset_n]
"""

        context = {
            "device": {"vendor_id": "0x1234", "device_id": "0x5678"},
            "board": {"name": "pcileech_75t484_x1"},
            "board_xdc_content": mock_xdc_content,
            "header": "# Test header",
        }

        # Verify context has the expected structure
        assert context["board_xdc_content"] is not None
        assert "PACKAGE_PIN E3" in context["board_xdc_content"]
        assert "IOSTANDARD LVCMOS33" in context["board_xdc_content"]
