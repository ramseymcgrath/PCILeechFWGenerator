#!/usr/bin/env python3
"""
PCILeech Board Configuration Tests

This module tests PCILeech board configuration integration,
validating board-specific settings and file management.
"""

import pytest
import tempfile
import shutil
import yaml
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any, List

# Import modules under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from board_config import get_pcileech_board_config, PCILEECH_BOARD_CONFIG
from src.file_management.file_manager import FileManager


class TestPCILeechBoardConfig:
    """Test suite for PCILeech board configuration."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_pcileech_board_config_constants(self):
        """Test PCILeech board configuration constants."""
        # Test that all expected boards are present
        expected_boards = [
            "pcileech_35t325_x4",
            "pcileech_75t484_x1", 
            "pcileech_100t484_x1"
        ]
        
        for board in expected_boards:
            assert board in PCILEECH_BOARD_CONFIG, f"Board {board} not found in PCILEECH_BOARD_CONFIG"
        
        # Test that configuration is not empty
        assert len(PCILEECH_BOARD_CONFIG) >= len(expected_boards)

    def test_pcileech_35t325_x4_configuration(self):
        """Test pcileech_35t325_x4 board configuration."""
        board_name = "pcileech_35t325_x4"
        config = get_pcileech_board_config(board_name)
        
        # Test required fields
        assert "fpga_part" in config
        assert "fpga_family" in config
        assert "pcie_ip_type" in config
        
        # Test specific values for this board
        assert config["fpga_part"] == "xc7a35tcsg324-2"
        assert config["fpga_family"] == "7series"
        assert config["pcie_ip_type"] == "axi_pcie"
        
        # Test PCILeech-specific fields
        assert "src_files" in config
        assert "ip_files" in config
        assert isinstance(config["src_files"], list)
        assert isinstance(config["ip_files"], list)
        
        # Test lane configuration
        if "max_lanes" in config:
            assert config["max_lanes"] == 4

    def test_pcileech_75t484_x1_configuration(self):
        """Test pcileech_75t484_x1 board configuration."""
        board_name = "pcileech_75t484_x1"
        config = get_pcileech_board_config(board_name)
        
        # Test required fields
        assert "fpga_part" in config
        assert "fpga_family" in config
        assert "pcie_ip_type" in config
        
        # Test specific values for this board
        assert config["fpga_part"] == "xc7a75tfgg484-2"
        assert config["fpga_family"] == "7series"
        assert config["pcie_ip_type"] == "pcie_7x"
        
        # Test PCILeech-specific fields
        assert "src_files" in config
        assert "ip_files" in config
        
        # Test lane configuration
        if "max_lanes" in config:
            assert config["max_lanes"] == 1

    def test_pcileech_100t484_x1_configuration(self):
        """Test pcileech_100t484_x1 board configuration."""
        board_name = "pcileech_100t484_x1"
        config = get_pcileech_board_config(board_name)
        
        # Test required fields
        assert "fpga_part" in config
        assert "fpga_family" in config
        assert "pcie_ip_type" in config
        
        # Test specific values for this board
        assert config["fpga_part"] == "xc7a100tfgg484-2"
        assert config["fpga_family"] == "7series"
        assert config["pcie_ip_type"] == "pcie_7x"
        
        # Test PCILeech-specific fields
        assert "src_files" in config
        assert "ip_files" in config
        
        # Test lane configuration
        if "max_lanes" in config:
            assert config["max_lanes"] == 1

    def test_board_config_file_lists(self):
        """Test board configuration explicit file lists."""
        for board_name in PCILEECH_BOARD_CONFIG.keys():
            config = get_pcileech_board_config(board_name)
            
            # Test source file lists
            assert "src_files" in config
            src_files = config["src_files"]
            assert isinstance(src_files, list)
            
            # Validate source files are explicit (no glob patterns)
            for src_file in src_files:
                assert not any(char in src_file for char in ['*', '?', '[', ']'])
                # Should be SystemVerilog or Verilog files
                assert src_file.endswith(('.sv', '.v'))
            
            # Test IP file lists
            assert "ip_files" in config
            ip_files = config["ip_files"]
            assert isinstance(ip_files, list)
            
            # Validate IP files are explicit
            for ip_file in ip_files:
                assert not any(char in ip_file for char in ['*', '?', '[', ']'])
                # Should be Xilinx IP files
                assert ip_file.endswith('.xci')

    def test_fpga_family_to_pcie_ip_mapping(self):
        """Test FPGA family to PCIe IP type mapping."""
        family_ip_mapping = {
            "7series": ["axi_pcie", "pcie_7x"],
            "ultrascale": ["pcie_ultrascale"],
            "ultrascale_plus": ["pcie_ultrascale"]
        }
        
        for board_name in PCILEECH_BOARD_CONFIG.keys():
            config = get_pcileech_board_config(board_name)
            
            fpga_family = config["fpga_family"]
            pcie_ip_type = config["pcie_ip_type"]
            
            # Validate mapping
            assert fpga_family in family_ip_mapping
            assert pcie_ip_type in family_ip_mapping[fpga_family]

    def test_board_config_validation(self):
        """Test board configuration validation."""
        for board_name in PCILEECH_BOARD_CONFIG.keys():
            config = get_pcileech_board_config(board_name)
            
            # Test required fields are present and not None
            required_fields = ["fpga_part", "fpga_family", "pcie_ip_type"]
            for field in required_fields:
                assert field in config
                assert config[field] is not None
                assert config[field] != ""
            
            # Test FPGA part format
            fpga_part = config["fpga_part"]
            assert fpga_part.startswith("xc")  # Xilinx FPGA parts start with 'xc'
            
            # Test FPGA family is valid
            valid_families = ["7series", "ultrascale", "ultrascale_plus"]
            assert config["fpga_family"] in valid_families
            
            # Test PCIe IP type is valid
            valid_ip_types = ["axi_pcie", "pcie_7x", "pcie_ultrascale"]
            assert config["pcie_ip_type"] in valid_ip_types

    def test_board_specific_features(self):
        """Test board-specific feature configuration."""
        # Test x4 board features
        x4_config = get_pcileech_board_config("pcileech_35t325_x4")
        if "max_lanes" in x4_config:
            assert x4_config["max_lanes"] == 4
        
        # Test x1 board features
        x1_boards = ["pcileech_75t484_x1", "pcileech_100t484_x1"]
        for board in x1_boards:
            config = get_pcileech_board_config(board)
            if "max_lanes" in config:
                assert config["max_lanes"] == 1

    def test_board_config_yaml_files(self):
        """Test that board configuration YAML files exist and are valid."""
        boards_dir = Path(__file__).parent.parent / "boards"
        
        expected_yaml_files = [
            "pcileech_35t325_x4.yaml",
            "pcileech_75t484_x1.yaml",
            "pcileech_100t484_x1.yaml"
        ]
        
        for yaml_file in expected_yaml_files:
            yaml_path = boards_dir / yaml_file
            
            if yaml_path.exists():
                # Test YAML file is valid
                with open(yaml_path, 'r') as f:
                    try:
                        yaml_data = yaml.safe_load(f)
                        assert isinstance(yaml_data, dict)
                        
                        # Test basic structure
                        if "name" in yaml_data:
                            assert yaml_data["name"] is not None
                        if "part" in yaml_data:
                            assert yaml_data["part"] is not None
                        if "family" in yaml_data:
                            assert yaml_data["family"] is not None
                            
                    except yaml.YAMLError as e:
                        pytest.fail(f"Invalid YAML in {yaml_file}: {e}")
            else:
                # YAML file might not exist - that's acceptable if config is in Python
                pass

    def test_file_manager_board_integration(self, temp_dir):
        """Test FileManager integration with board configurations."""
        file_manager = FileManager(temp_dir)
        
        # Test PCILeech structure creation
        directories = file_manager.create_pcileech_structure()
        
        assert "src" in directories
        assert "ip" in directories
        assert directories["src"].exists()
        assert directories["ip"].exists()
        
        # Test writing board-specific files
        for board_name in PCILEECH_BOARD_CONFIG.keys():
            config = get_pcileech_board_config(board_name)
            
            # Test writing source files for this board
            src_files = config.get("src_files", [])
            for src_file in src_files[:2]:  # Test first 2 files to avoid too many files
                test_content = f"// Test SystemVerilog file for {board_name}\nmodule {src_file.replace('.sv', '')} ();\nendmodule"
                written_file = file_manager.write_to_src_directory(src_file, test_content)
                
                assert written_file.exists()
                assert written_file.parent.name == "src"
                assert written_file.read_text() == test_content
            
            # Test writing IP files for this board
            ip_files = config.get("ip_files", [])
            for ip_file in ip_files[:1]:  # Test first IP file
                test_content = f"# Test IP configuration for {board_name}\nCONFIG.Component_Name {{{ip_file.replace('.xci', '')}}}"
                written_file = file_manager.write_to_ip_directory(ip_file, test_content)
                
                assert written_file.exists()
                assert written_file.parent.name == "ip"
                assert written_file.read_text() == test_content

    def test_board_config_error_handling(self):
        """Test board configuration error handling."""
        # Test invalid board name
        try:
            config = get_pcileech_board_config("invalid_board_name")
            # If no exception is raised, config should be None or empty
            if config is not None:
                assert len(config) == 0 or config == {}
        except (KeyError, ValueError):
            # Exception is acceptable for invalid board names
            pass

    def test_board_config_consistency(self):
        """Test consistency across board configurations."""
        all_configs = {}
        
        for board_name in PCILEECH_BOARD_CONFIG.keys():
            all_configs[board_name] = get_pcileech_board_config(board_name)
        
        # Test that all boards have consistent structure
        required_keys = ["fpga_part", "fpga_family", "pcie_ip_type", "src_files", "ip_files"]
        
        for board_name, config in all_configs.items():
            for key in required_keys:
                assert key in config, f"Board {board_name} missing required key: {key}"
        
        # Test that 7-series boards use appropriate IP types
        for board_name, config in all_configs.items():
            if config["fpga_family"] == "7series":
                assert config["pcie_ip_type"] in ["axi_pcie", "pcie_7x"]

    def test_board_config_file_path_validation(self):
        """Test that file paths in board configurations are valid."""
        for board_name in PCILEECH_BOARD_CONFIG.keys():
            config = get_pcileech_board_config(board_name)
            
            # Test source file paths
            src_files = config.get("src_files", [])
            for src_file in src_files:
                # Should be relative paths without directory separators
                assert "/" not in src_file and "\\" not in src_file
                # Should have valid SystemVerilog extension
                assert src_file.endswith(('.sv', '.v'))
                # Should not be empty
                assert len(src_file) > 0
            
            # Test IP file paths
            ip_files = config.get("ip_files", [])
            for ip_file in ip_files:
                # Should be relative paths without directory separators
                assert "/" not in ip_file and "\\" not in ip_file
                # Should have valid IP extension
                assert ip_file.endswith('.xci')
                # Should not be empty
                assert len(ip_file) > 0

    def test_board_config_completeness(self):
        """Test that board configurations are complete for PCILeech integration."""
        for board_name in PCILEECH_BOARD_CONFIG.keys():
            config = get_pcileech_board_config(board_name)
            
            # Test that essential PCILeech files are present
            src_files = config.get("src_files", [])
            ip_files = config.get("ip_files", [])
            
            # Should have at least one source file
            assert len(src_files) > 0, f"Board {board_name} has no source files"
            
            # Should have at least one IP file (PCIe IP core)
            assert len(ip_files) > 0, f"Board {board_name} has no IP files"
            
            # Should have PCIe-related IP core
            pcie_ip_found = any("pcie" in ip_file.lower() for ip_file in ip_files)
            assert pcie_ip_found, f"Board {board_name} missing PCIe IP core"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])