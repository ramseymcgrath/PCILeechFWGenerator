#!/usr/bin/env python3
"""
PCI Capability Rule Engine

This module provides a configurable rule system for categorizing PCI capabilities
based on emulation feasibility. It replaces the hardcoded categorization logic
with a flexible, data-driven approach that supports device-type specific rules
and capability versions.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

try:
    from ..string_utils import safe_format
except ImportError:
    # Fallback for script execution
    import sys
    from pathlib import Path

    src_dir = Path(__file__).parent.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    from string_utils import safe_format

from .constants import PCI_DEVICE_ID_OFFSET, PCI_VENDOR_ID_OFFSET
from .core import ConfigSpace
from .types import (CapabilityInfo, CapabilityType, EmulationCategory,
                    PCICapabilityID, PCIExtCapabilityID)

logger = logging.getLogger(__name__)


class CapabilityRule:
    """
    Individual capability rule for determining emulation category.

    A rule defines conditions under which a capability should be assigned
    a specific emulation category. Rules can be based on capability ID,
    version, device type, or other criteria.
    """

    def __init__(
        self,
        cap_id: int,
        cap_type: CapabilityType,
        category: EmulationCategory,
        conditions: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        Initialize a capability rule.

        Args:
            cap_id: Capability ID this rule applies to
            cap_type: Type of capability (standard or extended)
            category: Emulation category to assign if rule matches
            conditions: Optional conditions for rule matching
            description: Human-readable description of the rule
        """
        self.cap_id = cap_id
        self.cap_type = cap_type
        self.category = category
        self.conditions = conditions or {}
        self.description = (
            description or f"Rule for {cap_type.value} capability 0x{cap_id:02x}"
        )

    def matches(
        self,
        cap_info: CapabilityInfo,
        config_space: Optional[ConfigSpace] = None,
        device_context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Check if this rule matches the given capability.

        Args:
            cap_info: Capability information to check
            config_space: Configuration space for additional checks
            device_context: Device context information (VID/DID, etc.)

        Returns:
            True if the rule matches, False otherwise
        """
        # Basic capability ID and type check
        if cap_info.cap_id != self.cap_id or cap_info.cap_type != self.cap_type:
            return False

        # Check additional conditions
        for condition, expected_value in self.conditions.items():
            if not self._check_condition(
                condition, expected_value, cap_info, config_space, device_context
            ):
                return False

        return True

    def _check_condition(
        self,
        condition: str,
        expected_value: Any,
        cap_info: CapabilityInfo,
        config_space: Optional[ConfigSpace],
        device_context: Optional[Dict[str, Any]],
    ) -> bool:
        """Check a specific condition."""
        if condition == "version":
            return cap_info.version == expected_value

        elif condition == "min_version":
            return cap_info.version >= expected_value

        elif condition == "max_version":
            return cap_info.version <= expected_value

        elif condition == "vendor_id" and device_context:
            return device_context.get("vendor_id") == expected_value

        elif condition == "device_id" and device_context:
            return device_context.get("device_id") == expected_value

        elif condition == "vendor_ids" and device_context:
            return device_context.get("vendor_id") in expected_value

        elif condition == "device_ids" and device_context:
            return device_context.get("device_id") in expected_value

        else:
            logger.warning(f"Unknown condition '{condition}' in rule")
            return True  # Unknown conditions are ignored

    def __repr__(self) -> str:
        return safe_format(
            "CapabilityRule(cap_id=0x{cap_id:02x}, type={cap_type}, category={category})",
            cap_id=self.cap_id,
            cap_type=self.cap_type.value,
            category=self.category.name,
        )


class RuleEngine:
    """
    Rule engine for processing capability categorization rules.

    The RuleEngine manages a collection of CapabilityRule objects and
    provides methods to determine the appropriate emulation category
    for capabilities based on the configured rules.
    """

    def __init__(self) -> None:
        """Initialize the rule engine with default rules."""
        self.rules: List[CapabilityRule] = []
        self._load_default_rules()

    def add_rule(self, rule: CapabilityRule) -> None:
        """
        Add a rule to the engine.

        Args:
            rule: CapabilityRule to add
        """
        self.rules.append(rule)
        logger.debug(f"Added rule: {rule}")

    def remove_rules(self, cap_id: int, cap_type: CapabilityType) -> int:
        """
        Remove all rules for a specific capability.

        Args:
            cap_id: Capability ID
            cap_type: Capability type

        Returns:
            Number of rules removed
        """
        initial_count = len(self.rules)
        self.rules = [
            rule
            for rule in self.rules
            if not (rule.cap_id == cap_id and rule.cap_type == cap_type)
        ]
        removed_count = initial_count - len(self.rules)

        if removed_count > 0:
            logger.debug(
                f"Removed {removed_count} rules for {cap_type.value} capability 0x{cap_id:02x}"
            )

        return removed_count

    def categorize_capability(
        self,
        cap_info: CapabilityInfo,
        config_space: Optional[ConfigSpace] = None,
        device_context: Optional[Dict[str, Any]] = None,
    ) -> EmulationCategory:
        """
        Determine the emulation category for a capability.

        Args:
            cap_info: Capability information
            config_space: Configuration space for additional checks
            device_context: Device context information

        Returns:
            EmulationCategory for the capability
        """
        # Extract device context from config space if not provided
        if device_context is None and config_space is not None:
            device_context = self._extract_device_context(config_space)

        # Find matching rules (first match wins)
        for rule in self.rules:
            if rule.matches(cap_info, config_space, device_context):
                logger.debug(
                    safe_format(
                        "Rule matched for {cap_type} capability 0x{cap_id:02x} at offset 0x{offset:02x}: {category}",
                        cap_type=cap_info.cap_type.value,
                        cap_id=cap_info.cap_id,
                        offset=cap_info.offset,
                        category=rule.category.name,
                    )
                )
                return rule.category

        # Default to UNSUPPORTED if no rules match
        logger.debug(
            safe_format(
                "No rules matched for {cap_type} capability 0x{cap_id:02x} at offset 0x{offset:02x}, defaulting to UNSUPPORTED",
                cap_type=cap_info.cap_type.value,
                cap_id=cap_info.cap_id,
                offset=cap_info.offset,
            )
        )
        return EmulationCategory.UNSUPPORTED

    def categorize_capabilities(
        self,
        capabilities: Dict[int, CapabilityInfo],
        config_space: Optional[ConfigSpace] = None,
        device_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[int, EmulationCategory]:
        """
        Categorize multiple capabilities.

        Args:
            capabilities: Dictionary mapping offsets to CapabilityInfo
            config_space: Configuration space for additional checks
            device_context: Device context information

        Returns:
            Dictionary mapping offsets to EmulationCategory
        """
        categories = {}

        for offset, cap_info in capabilities.items():
            categories[offset] = self.categorize_capability(
                cap_info, config_space, device_context
            )

        return categories

    def load_rules_from_file(self, file_path: Union[str, Path]) -> None:
        """
        Load rules from a YAML or JSON configuration file.

        Args:
            file_path: Path to the configuration file

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is invalid
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Rule configuration file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.suffix.lower() in [".yaml", ".yml"]:
                    config = yaml.safe_load(f)
                elif file_path.suffix.lower() == ".json":
                    config = json.load(f)
                else:
                    raise ValueError(f"Unsupported file format: {file_path.suffix}")

            self._load_rules_from_config(config)
            logger.info(f"Loaded rules from {file_path}")

        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid configuration file format: {e}") from e

    def save_rules_to_file(
        self, file_path: Union[str, Path], format_type: str = "yaml"
    ) -> None:
        """
        Save current rules to a configuration file.

        Args:
            file_path: Path to save the configuration file
            format_type: File format ("yaml" or "json")
        """
        file_path = Path(file_path)
        config = self._rules_to_config()

        with open(file_path, "w", encoding="utf-8") as f:
            if format_type.lower() == "yaml":
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            elif format_type.lower() == "json":
                json.dump(config, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format_type}")

        logger.info(f"Saved {len(self.rules)} rules to {file_path}")

    def _load_default_rules(self) -> None:
        """Load the default rule configuration that matches current behavior."""
        # Standard capability rules
        standard_rules = [
            # Fully supported capabilities
            CapabilityRule(
                PCICapabilityID.MSI.value,
                CapabilityType.STANDARD,
                EmulationCategory.FULLY_SUPPORTED,
                description="MSI capability - fully supported",
            ),
            CapabilityRule(
                PCICapabilityID.MSI_X.value,
                CapabilityType.STANDARD,
                EmulationCategory.FULLY_SUPPORTED,
                description="MSI-X capability - fully supported",
            ),
            # Partially supported capabilities
            CapabilityRule(
                PCICapabilityID.POWER_MANAGEMENT.value,
                CapabilityType.STANDARD,
                EmulationCategory.PARTIALLY_SUPPORTED,
                description="Power Management capability - partially supported",
            ),
            CapabilityRule(
                PCICapabilityID.PCI_EXPRESS.value,
                CapabilityType.STANDARD,
                EmulationCategory.PARTIALLY_SUPPORTED,
                description="PCI Express capability - partially supported",
            ),
            # Unsupported capabilities
            CapabilityRule(
                PCICapabilityID.AGP.value,
                CapabilityType.STANDARD,
                EmulationCategory.UNSUPPORTED,
                description="AGP capability - unsupported",
            ),
            CapabilityRule(
                PCICapabilityID.VPD.value,
                CapabilityType.STANDARD,
                EmulationCategory.UNSUPPORTED,
                description="VPD capability - unsupported",
            ),
            CapabilityRule(
                PCICapabilityID.SLOT_ID.value,
                CapabilityType.STANDARD,
                EmulationCategory.UNSUPPORTED,
                description="Slot ID capability - unsupported",
            ),
            CapabilityRule(
                PCICapabilityID.PCI_X.value,
                CapabilityType.STANDARD,
                EmulationCategory.UNSUPPORTED,
                description="PCI-X capability - unsupported",
            ),
            CapabilityRule(
                PCICapabilityID.AF.value,
                CapabilityType.STANDARD,
                EmulationCategory.UNSUPPORTED,
                description="Advanced Features capability - unsupported",
            ),
            CapabilityRule(
                PCICapabilityID.VENDOR_SPECIFIC.value,
                CapabilityType.STANDARD,
                EmulationCategory.UNSUPPORTED,
                description="Vendor Specific capability - unsupported",
            ),
        ]

        # Extended capability rules
        extended_rules = [
            # Partially supported capabilities
            CapabilityRule(
                PCIExtCapabilityID.ADVANCED_ERROR_REPORTING.value,
                CapabilityType.EXTENDED,
                EmulationCategory.PARTIALLY_SUPPORTED,
                description="Advanced Error Reporting - partially supported",
            ),
            CapabilityRule(
                PCIExtCapabilityID.ACCESS_CONTROL_SERVICES.value,
                CapabilityType.EXTENDED,
                EmulationCategory.PARTIALLY_SUPPORTED,
                description="Access Control Services - partially supported",
            ),
            CapabilityRule(
                PCIExtCapabilityID.DOWNSTREAM_PORT_CONTAINMENT.value,
                CapabilityType.EXTENDED,
                EmulationCategory.PARTIALLY_SUPPORTED,
                description="Downstream Port Containment - partially supported",
            ),
            CapabilityRule(
                PCIExtCapabilityID.RESIZABLE_BAR.value,
                CapabilityType.EXTENDED,
                EmulationCategory.PARTIALLY_SUPPORTED,
                description="Resizable BAR - partially supported",
            ),
        ]

        # Add all rules
        for rule in standard_rules + extended_rules:
            self.add_rule(rule)

        logger.info(f"Loaded {len(self.rules)} default rules")

    def _extract_device_context(self, config_space: ConfigSpace) -> Dict[str, Any]:
        """Extract device context from configuration space."""
        context = {}

        try:
            if config_space.has_data(PCI_VENDOR_ID_OFFSET, 2):
                context["vendor_id"] = config_space.read_word(PCI_VENDOR_ID_OFFSET)

            if config_space.has_data(PCI_DEVICE_ID_OFFSET, 2):
                context["device_id"] = config_space.read_word(PCI_DEVICE_ID_OFFSET)

        except (IndexError, ValueError) as e:
            logger.warning(f"Failed to extract device context: {e}")

        return context

    def _load_rules_from_config(self, config: Dict[str, Any]) -> None:
        """Load rules from configuration dictionary."""
        rules_config = config.get("rules", [])

        for rule_config in rules_config:
            try:
                rule = self._create_rule_from_config(rule_config)
                self.add_rule(rule)
            except (KeyError, ValueError) as e:
                logger.error(f"Failed to load rule from config: {e}")

    def _create_rule_from_config(self, rule_config: Dict[str, Any]) -> CapabilityRule:
        """Create a CapabilityRule from configuration dictionary."""
        cap_id = rule_config["cap_id"]
        cap_type = CapabilityType(rule_config["cap_type"])
        category = EmulationCategory[rule_config["category"]]
        conditions = rule_config.get("conditions", {})
        description = rule_config.get("description")

        return CapabilityRule(cap_id, cap_type, category, conditions, description)

    def _rules_to_config(self) -> Dict[str, Any]:
        """Convert current rules to configuration dictionary."""
        rules_config = []

        for rule in self.rules:
            rule_config = {
                "cap_id": rule.cap_id,
                "cap_type": rule.cap_type.value,
                "category": rule.category.name,
            }

            if rule.conditions:
                rule_config["conditions"] = rule.conditions

            if rule.description:
                rule_config["description"] = rule.description

            rules_config.append(rule_config)

        return {"rules": rules_config}
