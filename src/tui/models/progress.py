"""
Build Progress Data Model

Build progress tracking for real-time monitoring.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class BuildStage(Enum):
    """Build stages for progress tracking."""

    ENVIRONMENT_VALIDATION = "Environment Validation"
    DEVICE_ANALYSIS = "Device Analysis"
    REGISTER_EXTRACTION = "Register Extraction"
    SYSTEMVERILOG_GENERATION = "SystemVerilog Generation"
    VIVADO_SYNTHESIS = "Vivado Synthesis"
    BITSTREAM_GENERATION = "Bitstream Generation"


@dataclass
class ValidationResult:
    """Validation result for PCI configuration values."""

    field: str
    expected: Any
    actual: Any
    status: str = "mismatch"  # mismatch, missing, invalid


@dataclass
class BuildProgress:
    """Build progress tracking."""

    stage: BuildStage
    completion_percent: float
    current_operation: str
    estimated_remaining: Optional[float] = None
    resource_usage: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    stage_completion: Dict[BuildStage, bool] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize stage completion tracking."""
        if not self.stage_completion:
            self.stage_completion = {stage: False for stage in BuildStage}

    @property
    def completed_stages(self) -> int:
        """Number of completed stages."""
        return sum(1 for completed in self.stage_completion.values() if completed)

    @property
    def total_stages(self) -> int:
        """Total number of stages."""
        return len(BuildStage)

    @property
    def overall_progress(self) -> float:
        """Overall progress percentage across all stages."""
        # Use fixed total_stages value for calculation
        total = self.total_stages
        stage_progress = self.completed_stages / total
        current_stage_progress = self.completion_percent / 100.0 / total
        return min(100.0, (stage_progress + current_stage_progress) * 100.0)

    @property
    def status_text(self) -> str:
        """Human-readable status text."""
        if (
            self.completion_percent == 100.0
            and self.completed_stages == self.total_stages
        ):
            return "Build Complete"
        elif self.errors:
            return f"Error in {self.stage.value}"
        elif self.warnings:
            return f"Warning in {self.stage.value}"
        else:
            return f"Running: {self.current_operation}"

    @property
    def progress_bar_text(self) -> str:
        """Progress bar text with stage information."""
        return f"{self.overall_progress:.1f}% ({self.completed_stages}/{self.total_stages} stages)"

    def mark_stage_complete(self, stage: BuildStage) -> None:
        """Mark a stage as complete."""
        self.stage_completion[stage] = True

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        if message not in self.warnings:
            self.warnings.append(message)

    def add_error(self, message: str) -> None:
        """Add an error message."""
        if message not in self.errors:
            self.errors.append(message)

    def update_resource_usage(
        self, cpu: float, memory: float, disk_free: float
    ) -> None:
        """Update resource usage metrics."""
        self.resource_usage = {"cpu": cpu, "memory": memory, "disk_free": disk_free}

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "stage": self.stage.value,
            "completion_percent": self.completion_percent,
            "current_operation": self.current_operation,
            "estimated_remaining": self.estimated_remaining,
            "resource_usage": self.resource_usage,
            "warnings": self.warnings,
            "errors": self.errors,
            "stage_completion": {
                stage.value: completed
                for stage, completed in self.stage_completion.items()
            },
            "overall_progress": self.overall_progress,
            "status_text": self.status_text,
        }
