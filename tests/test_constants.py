"""
Comprehensive tests for src/constants.py - Constants module.

This module tests the constants module including:
- Board parts mapping completeness
- FPGA family patterns
- Validate all constants are properly defined
"""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.device_clone.constants import (
    BOARD_PARTS,
    DEFAULT_FPGA_PART,
    FPGA_FAMILIES,
    IMPLEMENTATION_STRATEGY,
    LEGACY_TCL_FILES,
    MASTER_BUILD_SCRIPT,
    SYNTHESIS_STRATEGY,
    TCL_SCRIPT_FILES,
    VIVADO_OUTPUT_DIR,
    VIVADO_PROJECT_DIR,
    VIVADO_PROJECT_NAME,
)


class TestBoardPartsMapping:
    """Test board to FPGA part mapping."""

    def test_board_parts_not_empty(self):
        """Test that BOARD_PARTS is not empty."""
        assert len(BOARD_PARTS) > 0
        assert isinstance(BOARD_PARTS, dict)

    def test_original_boards_present(self):
        """Test that original board mappings are present."""
        original_boards = ["35t", "75t", "100t"]

        for board in original_boards:
            assert board in BOARD_PARTS
            assert isinstance(BOARD_PARTS[board], str)
            assert len(BOARD_PARTS[board]) > 0

    def test_captaindma_boards_present(self):
        """Test that CaptainDMA board mappings are present."""
        captaindma_boards = [
            "pcileech_75t484_x1",
            "pcileech_35t484_x1",
            "pcileech_35t325_x4",
            "pcileech_35t325_x1",
            "pcileech_100t484_x1",
        ]

        for board in captaindma_boards:
            assert board in BOARD_PARTS
            assert isinstance(BOARD_PARTS[board], str)
            assert len(BOARD_PARTS[board]) > 0

    def test_other_boards_present(self):
        """Test that other board mappings are present."""
        other_boards = [
            "pcileech_enigma_x1",
            "pcileech_squirrel",
            "pcileech_pciescreamer_xc7a35",
        ]

        for board in other_boards:
            assert board in BOARD_PARTS
            assert isinstance(BOARD_PARTS[board], str)
            assert len(BOARD_PARTS[board]) > 0

    def test_fpga_part_format_validity(self):
        """Test that all FPGA parts have valid format."""
        valid_prefixes = ["xc7a", "xc7k", "xc7v", "xczu", "xck", "xcvu"]

        for board, fpga_part in BOARD_PARTS.items():
            # Check that part starts with valid prefix
            assert any(
                fpga_part.lower().startswith(prefix) for prefix in valid_prefixes
            ), f"Board {board} has invalid FPGA part format: {fpga_part}"

            # Check that part contains speed grade
            assert (
                fpga_part.count("-") >= 1
            ), f"Board {board} FPGA part missing speed grade: {fpga_part}"

    def test_artix7_parts_mapping(self):
        """Test specific Artix-7 part mappings."""
        artix7_mappings = {
            "35t": "xc7a35tcsg324-2",
            "75t": "xc7a75tfgg484-2",
            "pcileech_35t325_x4": "xc7a35tcsg324-2",
            "pcileech_35t325_x1": "xc7a35tcsg324-2",
            "pcileech_75t484_x1": "xc7a75tfgg484-2",
        }

        for board, expected_part in artix7_mappings.items():
            assert BOARD_PARTS[board] == expected_part

    def test_zynq_ultrascale_parts_mapping(self):
        """Test Zynq UltraScale+ part mappings."""
        zynq_mappings = {
            "100t": "xczu3eg-sbva484-1-e",
            "pcileech_100t484_x1": "xczu3eg-sbva484-1-e",
        }

        for board, expected_part in zynq_mappings.items():
            assert BOARD_PARTS[board] == expected_part

    def test_no_duplicate_values(self):
        """Test that there are no unexpected duplicate FPGA parts."""
        # Some duplication is expected (multiple boards can use same FPGA)
        # but let's verify the expected duplicates
        part_counts = {}
        for board, part in BOARD_PARTS.items():
            part_counts[part] = part_counts.get(part, 0) + 1

        # xc7a35tcsg324-2 should be used by multiple 35T boards
        assert part_counts.get("xc7a35tcsg324-2", 0) >= 3

        # Each part should be used by at least one board
        assert all(count >= 1 for count in part_counts.values())


class TestDefaultFpgaPart:
    """Test default FPGA part configuration."""

    def test_default_fpga_part_defined(self):
        """Test that DEFAULT_FPGA_PART is defined."""
        assert DEFAULT_FPGA_PART is not None
        assert isinstance(DEFAULT_FPGA_PART, str)
        assert len(DEFAULT_FPGA_PART) > 0

    def test_default_fpga_part_valid_format(self):
        """Test that DEFAULT_FPGA_PART has valid format."""
        valid_prefixes = ["xc7a", "xc7k", "xc7v", "xczu", "xck", "xcvu"]

        assert any(
            DEFAULT_FPGA_PART.lower().startswith(prefix) for prefix in valid_prefixes
        )
        assert DEFAULT_FPGA_PART.count("-") >= 1  # Should have speed grade

    def test_default_fpga_part_in_board_parts(self):
        """Test that DEFAULT_FPGA_PART exists in BOARD_PARTS values."""
        assert DEFAULT_FPGA_PART in BOARD_PARTS.values()

    def test_default_fpga_part_is_conservative(self):
        """Test that default part is a conservative choice (35T)."""
        # Default should be a smaller, more widely available part
        assert "xc7a35t" in DEFAULT_FPGA_PART.lower()


class TestVivadoConfiguration:
    """Test Vivado project configuration constants."""

    def test_vivado_project_name_defined(self):
        """Test that VIVADO_PROJECT_NAME is defined."""
        assert VIVADO_PROJECT_NAME is not None
        assert isinstance(VIVADO_PROJECT_NAME, str)
        assert len(VIVADO_PROJECT_NAME) > 0

    def test_vivado_project_name_valid(self):
        """Test that VIVADO_PROJECT_NAME is valid for Vivado."""
        # Should not contain spaces or special characters that could cause issues
        assert " " not in VIVADO_PROJECT_NAME
        assert all(c.isalnum() or c in "_-" for c in VIVADO_PROJECT_NAME)

    def test_vivado_project_dir_defined(self):
        """Test that VIVADO_PROJECT_DIR is defined."""
        assert VIVADO_PROJECT_DIR is not None
        assert isinstance(VIVADO_PROJECT_DIR, str)
        assert len(VIVADO_PROJECT_DIR) > 0

    def test_vivado_project_dir_relative(self):
        """Test that VIVADO_PROJECT_DIR is a relative path."""
        assert VIVADO_PROJECT_DIR.startswith("./") or not VIVADO_PROJECT_DIR.startswith(
            "/"
        )

    def test_vivado_output_dir_defined(self):
        """Test that VIVADO_OUTPUT_DIR is defined."""
        assert VIVADO_OUTPUT_DIR is not None
        assert isinstance(VIVADO_OUTPUT_DIR, str)


class TestTclScriptFiles:
    """Test TCL script file configuration."""

    def test_tcl_script_files_defined(self):
        """Test that TCL_SCRIPT_FILES is defined."""
        assert TCL_SCRIPT_FILES is not None
        assert isinstance(TCL_SCRIPT_FILES, list)
        assert len(TCL_SCRIPT_FILES) > 0

    def test_tcl_script_files_order(self):
        """Test that TCL script files are in logical build order."""
        expected_order = [
            "01_project_setup.tcl",
            "02_ip_config.tcl",
            "03_add_sources.tcl",
            "04_constraints.tcl",
            "05_synthesis.tcl",
            "06_implementation.tcl",
            "07_bitstream.tcl",
        ]

        assert TCL_SCRIPT_FILES == expected_order

    def test_tcl_script_files_naming_convention(self):
        """Test that TCL script files follow naming convention."""
        for i, script_file in enumerate(TCL_SCRIPT_FILES, 1):
            # Should start with zero-padded number
            assert script_file.startswith(f"{i:02d}_")

            # Should end with .tcl
            assert script_file.endswith(".tcl")

            # Should contain descriptive name
            assert len(script_file) > 10  # More than just number and extension

    def test_tcl_script_files_coverage(self):
        """Test that TCL script files cover all build phases."""
        script_content = " ".join(TCL_SCRIPT_FILES).lower()

        required_phases = [
            "project",
            "setup",
            "ip",
            "config",
            "sources",
            "constraints",
            "synthesis",
            "implementation",
            "bitstream",
        ]

        for phase in required_phases:
            assert phase in script_content, f"Missing phase: {phase}"

    def test_master_build_script_defined(self):
        """Test that MASTER_BUILD_SCRIPT is defined."""
        assert MASTER_BUILD_SCRIPT is not None
        assert isinstance(MASTER_BUILD_SCRIPT, str)
        assert MASTER_BUILD_SCRIPT.endswith(".tcl")

    def test_master_build_script_name(self):
        """Test that master build script has appropriate name."""
        # Should indicate it's a master/main build script
        script_lower = MASTER_BUILD_SCRIPT.lower()
        assert any(
            keyword in script_lower for keyword in ["build", "master", "main", "all"]
        )


class TestBuildStrategies:
    """Test synthesis and implementation strategy configuration."""

    def test_synthesis_strategy_defined(self):
        """Test that SYNTHESIS_STRATEGY is defined."""
        assert SYNTHESIS_STRATEGY is not None
        assert isinstance(SYNTHESIS_STRATEGY, str)
        assert len(SYNTHESIS_STRATEGY) > 0

    def test_synthesis_strategy_valid(self):
        """Test that SYNTHESIS_STRATEGY is a valid Vivado strategy."""
        # Common Vivado synthesis strategies
        valid_strategies = [
            "Vivado Synthesis Defaults",
            "Flow_AreaOptimized_high",
            "Flow_AreaOptimized_medium",
            "Flow_AlternateRoutability",
            "Flow_PerfOptimized_high",
            "Flow_RuntimeOptimized",
        ]

        assert SYNTHESIS_STRATEGY in valid_strategies or "Vivado" in SYNTHESIS_STRATEGY

    def test_implementation_strategy_defined(self):
        """Test that IMPLEMENTATION_STRATEGY is defined."""
        assert IMPLEMENTATION_STRATEGY is not None
        assert isinstance(IMPLEMENTATION_STRATEGY, str)
        assert len(IMPLEMENTATION_STRATEGY) > 0

    def test_implementation_strategy_valid(self):
        """Test that IMPLEMENTATION_STRATEGY is a valid Vivado strategy."""
        # Common Vivado implementation strategies
        valid_strategies = [
            "Vivado Implementation Defaults",
            "Performance_Explore",
            "Performance_ExplorePostRoutePhysOpt",
            "Performance_WLBlockPlacement",
            "Performance_WLBlockPlacementFanoutOpt",
            "Performance_EarlyBlockPlacement",
            "Performance_NetDelay_high",
            "Performance_NetDelay_low",
            "Performance_Retiming",
            "Performance_ExtraTimingOpt",
            "Performance_RefinePlacement",
            "Performance_SpreadSLLs",
            "Performance_BalanceSLLs",
            "Performance_BalanceSLRs",
            "Performance_HighUtilSLRs",
            "Congestion_SpreadLogic_high",
            "Congestion_SpreadLogic_medium",
            "Congestion_SpreadLogic_low",
            "Congestion_SSI_SpreadLogic_high",
            "Congestion_SSI_SpreadLogic_low",
            "Area_Explore",
            "Area_ExploreSequential",
            "Area_ExploreWithRemap",
            "Power_DefaultOpt",
            "Power_ExploreArea",
            "Flow_RunPhysOpt",
            "Flow_RunPostRoutePhysOpt",
            "Flow_RuntimeOptimized",
            "Flow_Quick",
        ]

        assert IMPLEMENTATION_STRATEGY in valid_strategies or any(
            keyword in IMPLEMENTATION_STRATEGY
            for keyword in ["Performance", "Area", "Power", "Flow"]
        )


class TestFpgaFamilies:
    """Test FPGA family detection patterns."""

    def test_fpga_families_defined(self):
        """Test that FPGA_FAMILIES is defined."""
        assert FPGA_FAMILIES is not None
        assert isinstance(FPGA_FAMILIES, dict)
        assert len(FPGA_FAMILIES) > 0

    def test_fpga_families_coverage(self):
        """Test that FPGA_FAMILIES covers expected families."""
        expected_families = ["ZYNQ_ULTRASCALE", "ARTIX7_35T", "ARTIX7_75T", "KINTEX7"]

        for family in expected_families:
            assert family in FPGA_FAMILIES

    def test_fpga_families_patterns_valid(self):
        """Test that FPGA family patterns are valid."""
        for family_name, pattern in FPGA_FAMILIES.items():
            assert isinstance(pattern, str)
            assert len(pattern) > 0

            # Pattern should be a valid FPGA part prefix
            assert pattern.startswith("xc")

    def test_fpga_families_pattern_uniqueness(self):
        """Test that FPGA family patterns are unique."""
        patterns = list(FPGA_FAMILIES.values())
        assert len(patterns) == len(set(patterns))

    def test_fpga_families_match_board_parts(self):
        """Test that FPGA family patterns match actual board parts."""
        for family_name, pattern in FPGA_FAMILIES.items():
            # Find board parts that should match this pattern
            matching_parts = [
                part
                for part in BOARD_PARTS.values()
                if part.lower().startswith(pattern.lower())
            ]

            # Each family pattern should match at least one board part
            assert (
                len(matching_parts) > 0
            ), f"No board parts match family {family_name} pattern {pattern}"

    def test_specific_family_patterns(self):
        """Test specific family pattern mappings."""
        expected_patterns = {
            "ZYNQ_ULTRASCALE": "xczu",
            "ARTIX7_35T": "xc7a35t",
            "ARTIX7_75T": "xc7a75t",
            "KINTEX7": "xc7k",
        }

        for family, expected_pattern in expected_patterns.items():
            assert FPGA_FAMILIES[family] == expected_pattern


class TestLegacyTclFiles:
    """Test legacy TCL files configuration."""

    def test_legacy_tcl_files_defined(self):
        """Test that LEGACY_TCL_FILES is defined."""
        assert LEGACY_TCL_FILES is not None
        assert isinstance(LEGACY_TCL_FILES, list)

    def test_legacy_tcl_files_format(self):
        """Test that legacy TCL files have proper format."""
        for legacy_file in LEGACY_TCL_FILES:
            assert isinstance(legacy_file, str)
            assert legacy_file.endswith(".tcl")
            assert len(legacy_file) > 4  # More than just .tcl

    def test_legacy_tcl_files_not_overlap_current(self):
        """Test that legacy files don't overlap with current script files."""
        current_files = set(TCL_SCRIPT_FILES + [MASTER_BUILD_SCRIPT])
        legacy_files = set(LEGACY_TCL_FILES)

        # No overlap between current and legacy files
        assert len(current_files.intersection(legacy_files)) == 0

    def test_legacy_tcl_files_naming_patterns(self):
        """Test that legacy files follow expected naming patterns."""
        legacy_content = " ".join(LEGACY_TCL_FILES).lower()

        # Should contain build-related keywords
        build_keywords = ["build", "unified", "firmware"]
        assert any(keyword in legacy_content for keyword in build_keywords)


class TestConstantsConsistency:
    """Test consistency between different constants."""

    def test_default_fpga_part_has_family_pattern(self):
        """Test that DEFAULT_FPGA_PART matches one of the family patterns."""
        default_part_lower = DEFAULT_FPGA_PART.lower()

        matching_families = [
            family
            for family, pattern in FPGA_FAMILIES.items()
            if default_part_lower.startswith(pattern.lower())
        ]

        assert (
            len(matching_families) > 0
        ), f"Default FPGA part {DEFAULT_FPGA_PART} doesn't match any family pattern"

    def test_board_parts_cover_all_families(self):
        """Test that board parts cover all defined FPGA families."""
        for family_name, pattern in FPGA_FAMILIES.items():
            matching_boards = [
                board
                for board, part in BOARD_PARTS.items()
                if part.lower().startswith(pattern.lower())
            ]

            assert (
                len(matching_boards) > 0
            ), f"No boards use FPGA family {family_name} (pattern: {pattern})"

    def test_tcl_script_count_reasonable(self):
        """Test that number of TCL scripts is reasonable."""
        # Should have enough scripts to cover build phases but not be excessive
        assert 5 <= len(TCL_SCRIPT_FILES) <= 10

    def test_vivado_project_name_matches_context(self):
        """Test that Vivado project name is appropriate for PCILeech."""
        project_name_lower = VIVADO_PROJECT_NAME.lower()
        assert any(
            keyword in project_name_lower for keyword in ["pcileech", "firmware", "pci"]
        )


class TestConstantsTypes:
    """Test that all constants have correct types."""

    def test_string_constants_types(self):
        """Test that string constants are actually strings."""
        string_constants = [
            DEFAULT_FPGA_PART,
            VIVADO_PROJECT_NAME,
            VIVADO_PROJECT_DIR,
            VIVADO_OUTPUT_DIR,
            MASTER_BUILD_SCRIPT,
            SYNTHESIS_STRATEGY,
            IMPLEMENTATION_STRATEGY,
        ]

        for constant in string_constants:
            assert isinstance(constant, str)
            assert len(constant) > 0

    def test_dict_constants_types(self):
        """Test that dictionary constants are actually dictionaries."""
        dict_constants = [BOARD_PARTS, FPGA_FAMILIES]

        for constant in dict_constants:
            assert isinstance(constant, dict)
            assert len(constant) > 0

    def test_list_constants_types(self):
        """Test that list constants are actually lists."""
        list_constants = [TCL_SCRIPT_FILES, LEGACY_TCL_FILES]

        for constant in list_constants:
            assert isinstance(constant, list)

    def test_nested_types_consistency(self):
        """Test that nested types are consistent."""
        # BOARD_PARTS should have string keys and values
        for key, value in BOARD_PARTS.items():
            assert isinstance(key, str)
            assert isinstance(value, str)

        # FPGA_FAMILIES should have string keys and values
        for key, value in FPGA_FAMILIES.items():
            assert isinstance(key, str)
            assert isinstance(value, str)

        # TCL_SCRIPT_FILES should contain only strings
        for script_file in TCL_SCRIPT_FILES:
            assert isinstance(script_file, str)

        # LEGACY_TCL_FILES should contain only strings
        for legacy_file in LEGACY_TCL_FILES:
            assert isinstance(legacy_file, str)


class TestConstantsCompleteness:
    """Test that constants provide complete coverage."""

    def test_all_expected_constants_present(self):
        """Test that all expected constants are present in the module."""
        expected_constants = [
            "BOARD_PARTS",
            "DEFAULT_FPGA_PART",
            "VIVADO_PROJECT_NAME",
            "VIVADO_PROJECT_DIR",
            "VIVADO_OUTPUT_DIR",
            "TCL_SCRIPT_FILES",
            "MASTER_BUILD_SCRIPT",
            "SYNTHESIS_STRATEGY",
            "IMPLEMENTATION_STRATEGY",
            "FPGA_FAMILIES",
            "LEGACY_TCL_FILES",
        ]

        # Import the module to check what's available
        import src.device_clone.constants as constants

        for constant_name in expected_constants:
            assert hasattr(
                constants, constant_name
            ), f"Missing constant: {constant_name}"

    def test_no_unexpected_none_values(self):
        """Test that no constants have None values unexpectedly."""
        import src.device_clone.constants as constants

        # Get all module attributes that look like constants (uppercase)
        constant_attrs = [
            attr
            for attr in dir(constants)
            if attr.isupper() and not attr.startswith("_")
        ]

        for attr_name in constant_attrs:
            attr_value = getattr(constants, attr_name)
            assert attr_value is not None, f"Constant {attr_name} is None"

    def test_constants_not_empty(self):
        """Test that collection constants are not empty."""
        collection_constants = [
            (BOARD_PARTS, "BOARD_PARTS"),
            (TCL_SCRIPT_FILES, "TCL_SCRIPT_FILES"),
            (FPGA_FAMILIES, "FPGA_FAMILIES"),
        ]

        for constant_value, constant_name in collection_constants:
            assert len(constant_value) > 0, f"Constant {constant_name} is empty"
