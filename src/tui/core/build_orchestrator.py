"""
Build Orchestrator

Orchestrates the build process with real-time monitoring and progress tracking.
"""

import argparse
import asyncio
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import psutil

from ..models.config import BuildConfiguration
from ..models.device import PCIDevice
from ..models.progress import BuildProgress, BuildStage


class BuildOrchestrator:
    """Orchestrates the build process with real-time monitoring"""

    def __init__(self):
        self._current_progress: Optional[BuildProgress] = None
        self._build_process: Optional[asyncio.subprocess.Process] = None
        self._progress_callback: Optional[Callable[[BuildProgress], None]] = None
        self._is_building = False
        self._should_cancel = False

    async def start_build(
        self,
        device: PCIDevice,
        config: BuildConfiguration,
        progress_callback: Optional[Callable[[BuildProgress], None]] = None,
    ) -> bool:
        """Start build with progress monitoring"""
        if self._is_building:
            raise RuntimeError("Build already in progress")

        self._is_building = True
        self._should_cancel = False
        self._progress_callback = progress_callback

        # Initialize progress tracking
        self._current_progress = BuildProgress(
            stage=BuildStage.ENVIRONMENT_VALIDATION,
            completion_percent=0.0,
            current_operation="Initializing build process",
        )

        try:
            # Stage 1: Environment Validation
            await self._update_progress(
                BuildStage.ENVIRONMENT_VALIDATION, 0, "Validating environment"
            )
            await self._validate_environment()

            # Check donor_dump module status if needed
            if config.donor_dump and not config.local_build:
                await self._update_progress(
                    BuildStage.ENVIRONMENT_VALIDATION,
                    50,
                    "Checking donor_dump module status",
                )
                await self._check_donor_module(config)

            await self._update_progress(
                BuildStage.ENVIRONMENT_VALIDATION,
                100,
                "Environment validation complete",
            )
            self._current_progress.mark_stage_complete(
                BuildStage.ENVIRONMENT_VALIDATION
            )

            if self._should_cancel:
                return False

            # Stage 2: Device Analysis
            await self._update_progress(
                BuildStage.DEVICE_ANALYSIS, 0, "Analyzing device configuration"
            )
            await self._analyze_device(device)
            await self._update_progress(
                BuildStage.DEVICE_ANALYSIS, 100, "Device analysis complete"
            )
            self._current_progress.mark_stage_complete(BuildStage.DEVICE_ANALYSIS)

            if self._should_cancel:
                return False

            # Stage 3: Register Extraction
            await self._update_progress(
                BuildStage.REGISTER_EXTRACTION, 0, "Extracting device registers"
            )
            await self._extract_registers(device)
            await self._update_progress(
                BuildStage.REGISTER_EXTRACTION, 100, "Register extraction complete"
            )
            self._current_progress.mark_stage_complete(BuildStage.REGISTER_EXTRACTION)

            if self._should_cancel:
                return False

            # Stage 4: Behavior Profiling (if enabled)
            if config.behavior_profiling:
                await self._update_progress(
                    BuildStage.BEHAVIOR_PROFILING, 0, "Starting behavior profiling"
                )
                await self._run_behavior_profiling(device)
                await self._update_progress(
                    BuildStage.BEHAVIOR_PROFILING, 100, "Behavior profiling complete"
                )
                self._current_progress.mark_stage_complete(
                    BuildStage.BEHAVIOR_PROFILING
                )

                if self._should_cancel:
                    return False

            # Stage 5: SystemVerilog Generation
            await self._update_progress(
                BuildStage.SYSTEMVERILOG_GENERATION, 0, "Generating SystemVerilog"
            )
            await self._generate_systemverilog(device, config)
            await self._update_progress(
                BuildStage.SYSTEMVERILOG_GENERATION,
                100,
                "SystemVerilog generation complete",
            )
            self._current_progress.mark_stage_complete(
                BuildStage.SYSTEMVERILOG_GENERATION
            )

            if self._should_cancel:
                return False

            # Stage 5: Vivado Synthesis
            await self._update_progress(
                BuildStage.VIVADO_SYNTHESIS, 0, "Starting Vivado synthesis"
            )
            await self._run_vivado_synthesis(device, config)
            await self._update_progress(
                BuildStage.VIVADO_SYNTHESIS, 100, "Vivado synthesis complete"
            )
            self._current_progress.mark_stage_complete(BuildStage.VIVADO_SYNTHESIS)

            if self._should_cancel:
                return False

            # Stage 6: Bitstream Generation
            await self._update_progress(
                BuildStage.BITSTREAM_GENERATION, 0, "Generating bitstream"
            )
            await self._generate_bitstream(config)
            await self._update_progress(
                BuildStage.BITSTREAM_GENERATION, 100, "Bitstream generation complete"
            )
            self._current_progress.mark_stage_complete(BuildStage.BITSTREAM_GENERATION)

            # Build complete
            self._current_progress.completion_percent = 100.0
            self._current_progress.current_operation = "Build completed successfully"
            await self._notify_progress()

            return True

        except Exception as e:
            if self._current_progress:
                self._current_progress.add_error(f"Build failed: {str(e)}")
                await self._notify_progress()
            raise
        finally:
            self._is_building = False

    async def cancel_build(self) -> None:
        """Cancel the current build"""
        self._should_cancel = True
        if self._build_process:
            try:
                self._build_process.terminate()
                # Wait a bit for graceful termination
                await asyncio.sleep(2)
                if self._build_process.returncode is None:
                    self._build_process.kill()
            except Exception:
                pass

    def get_current_progress(self) -> Optional[BuildProgress]:
        """Get current build progress"""
        return self._current_progress

    def is_building(self) -> bool:
        """Check if build is in progress"""
        return self._is_building

    async def _update_progress(
        self, stage: BuildStage, percent: float, operation: str
    ) -> None:
        """Update progress and notify callback"""
        if self._current_progress:
            self._current_progress.stage = stage
            self._current_progress.completion_percent = percent
            self._current_progress.current_operation = operation

            # Update resource usage
            await self._update_resource_usage()

            await self._notify_progress()

    async def _notify_progress(self) -> None:
        """Notify progress callback"""
        if self._progress_callback and self._current_progress:
            try:
                self._progress_callback(self._current_progress)
            except Exception:
                pass  # Don't let callback errors break the build

    async def _update_resource_usage(self) -> None:
        """Update system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            if self._current_progress:
                self._current_progress.update_resource_usage(
                    cpu=cpu_percent,
                    memory=memory.used / (1024**3),  # GB
                    disk_free=disk.free / (1024**3),  # GB
                )
        except Exception:
            pass  # Resource monitoring is optional

    async def _validate_environment(self) -> None:
        """Validate build environment"""
        # Get current configuration
        app = self._get_app()
        config = getattr(app, "current_config", None)
        local_build = config and config.local_build

        # For local builds, we have more relaxed requirements
        if not local_build:
            # Check if running as root (only needed for non-local builds)
            if os.geteuid() != 0:
                raise RuntimeError("Root privileges required for device binding")

            # Check if Podman is available (only needed for non-local builds)
            try:
                result = await self._run_command("podman --version")
                if result.returncode != 0:
                    raise RuntimeError("Podman not available")
            except FileNotFoundError:
                raise RuntimeError("Podman not found in PATH")

            # Check if container image exists
            result = await self._run_command(
                "podman images dma-fw --format '{{.Repository}}'"
            )
            if "dma-fw" not in result.stdout:
                # Container image not found, try to build it
                if self._current_progress:
                    self._current_progress.current_operation = (
                        "Building container image 'dma-fw'"
                    )
                    await self._notify_progress()

                try:
                    print("[*] Container image 'dma-fw' not found. Building it now...")
                    build_result = await self._run_command("podman build -t dma-fw .")
                    if build_result.returncode != 0:
                        raise RuntimeError(
                            f"Failed to build container image: {build_result.stderr}"
                        )
                    print("[✓] Container image built successfully")
                except Exception as e:
                    raise RuntimeError(
                        f"Container image 'dma-fw' not found and build failed: {str(e)}"
                    )
        else:
            # For local builds, just check if Python and build.py are available
            if not Path("src/build.py").exists():
                raise RuntimeError("build.py not found in src directory")

            # Check if donor info file exists if specified
            if (
                config
                and config.donor_info_file
                and not Path(config.donor_info_file).exists()
            ):
                if self._current_progress:
                    self._current_progress.add_warning(
                        f"Donor info file not found: {config.donor_info_file}"
                    )

        # Check output directory
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

    async def _check_donor_module(self, config: BuildConfiguration) -> None:
        """
        Check if donor_dump kernel module is properly installed

        Args:
            config: Current build configuration
        """
        # Skip check if donor_dump is disabled or using local build
        if not config.donor_dump or config.local_build:
            return

        try:
            # Import donor_dump_manager
            import sys
            from pathlib import Path

            sys.path.append(str(Path(__file__).parent.parent.parent.parent))
            from donor_dump_manager import DonorDumpManager

            # Create manager and check status
            manager = DonorDumpManager()
            module_status = manager.check_module_installation()

            # Update progress with module status
            if self._current_progress:
                status = module_status.get("status", "unknown")
                details = module_status.get("details", "")

                if status != "installed":
                    # Add warning about module status
                    self._current_progress.add_warning(
                        f"Donor module status: {details}"
                    )

                    # Add first issue and fix to progress
                    issues = module_status.get("issues", [])
                    fixes = module_status.get("fixes", [])

                    if issues:
                        self._current_progress.add_warning(f"Issue: {issues[0]}")
                    if fixes:
                        self._current_progress.add_warning(f"Suggested fix: {fixes[0]}")

                    # If auto_install_headers is enabled, try to fix common issues
                    if (
                        config.auto_install_headers
                        and status == "not_built"
                        and "headers" in str(issues)
                    ):
                        self._current_progress.current_operation = (
                            "Attempting to install kernel headers"
                        )
                        await self._notify_progress()

                        # Get kernel version
                        kernel_version = module_status.get("raw_status", {}).get(
                            "kernel_version", ""
                        )
                        if kernel_version:
                            # Try to install headers
                            try:
                                result = await self._run_command(
                                    f"sudo apt-get install -y linux-headers-{kernel_version}"
                                )
                                if result.returncode == 0:
                                    self._current_progress.add_warning(
                                        "Kernel headers installed successfully"
                                    )

                                    # Try to build module
                                    self._current_progress.current_operation = (
                                        "Building donor_dump module"
                                    )
                                    await self._notify_progress()

                                    # Build module
                                    manager.build_module(force_rebuild=True)
                                    self._current_progress.add_warning(
                                        "Donor module built successfully"
                                    )
                                else:
                                    self._current_progress.add_error(
                                        f"Failed to install kernel headers: {result.stderr}"
                                    )
                            except Exception as e:
                                self._current_progress.add_error(
                                    f"Failed to install kernel headers: {str(e)}"
                                )
                else:
                    # Module is properly installed
                    self._current_progress.current_operation = (
                        "Donor module is properly installed"
                    )
                    await self._notify_progress()

        except Exception as e:
            # Log error but continue with build
            if self._current_progress:
                self._current_progress.add_error(
                    f"Failed to check donor module status: {str(e)}"
                )
                await self._notify_progress()

    def _get_app(self):
        """Get the parent app instance"""
        # Find the app instance in the widget tree
        widget = getattr(self, "_progress_callback", None)
        while widget and not isinstance(widget, object):
            widget = getattr(widget, "app", None)

        return widget

    async def _analyze_device(self, device: PCIDevice) -> None:
        """Analyze device configuration"""
        # Import existing functions
        import sys

        sys.path.append(str(Path(__file__).parent.parent.parent.parent))
        from generate import get_current_driver, get_iommu_group

        # Get current device state
        current_driver = await asyncio.get_event_loop().run_in_executor(
            None, get_current_driver, device.bdf
        )

        iommu_group = await asyncio.get_event_loop().run_in_executor(
            None, get_iommu_group, device.bdf
        )

        # Validate VFIO device path
        vfio_device = f"/dev/vfio/{iommu_group}"
        if not os.path.exists(vfio_device) and self._current_progress:
            self._current_progress.add_warning(f"VFIO device {vfio_device} not found")

    async def _extract_registers(self, device: PCIDevice) -> None:
        """Extract device registers"""
        # This would integrate with existing register extraction logic
        await asyncio.sleep(1)  # Simulate register extraction

    async def _run_behavior_profiling(self, device: PCIDevice) -> None:
        """Run behavior profiling on the device"""
        # Import behavior profiler
        import sys
        from pathlib import Path

        sys.path.append(str(Path(__file__).parent.parent.parent))
        from behavior_profiler import BehaviorProfiler

        # Log the start of profiling
        if self._current_progress:
            self._current_progress.current_operation = f"Profiling device {device.bdf}"
            await self._notify_progress()

        # Run the profiling in a separate thread to avoid blocking the event loop
        def run_profiling():
            try:
                profiler = BehaviorProfiler(bdf=device.bdf, debug=True)
                profile = profiler.capture_behavior_profile(duration=30.0)
                return profile
            except Exception as e:
                if self._current_progress:
                    self._current_progress.add_error(
                        f"Behavior profiling failed: {str(e)}"
                    )
                return None

        # Execute profiling in a thread pool
        loop = asyncio.get_event_loop()
        profile = await loop.run_in_executor(None, run_profiling)

        # Update progress with results
        if profile and self._current_progress:
            self._current_progress.current_operation = (
                f"Analyzed {profile.total_accesses} register accesses"
            )
            self._current_progress.add_warning(
                f"Found {len(profile.timing_patterns)} timing patterns"
            )
            self._current_progress.add_warning(
                f"Identified {len(profile.state_transitions)} state transitions"
            )

    async def _generate_systemverilog(
        self, device: PCIDevice, config: BuildConfiguration
    ) -> None:
        """Generate SystemVerilog code"""
        # This would integrate with existing SystemVerilog generation
        await asyncio.sleep(2)  # Simulate SystemVerilog generation

    async def _run_vivado_synthesis(
        self, device: PCIDevice, config: BuildConfiguration
    ) -> None:
        """Run Vivado synthesis in container or locally"""
        # Convert config to CLI args
        cli_args = config.to_cli_args()

        # Build command parts
        build_cmd_parts = [
            f"python3 src/build.py --bdf {device.bdf} --board {config.board_type}"
        ]

        if cli_args.get("advanced_sv"):
            build_cmd_parts.append("--advanced-sv")
        if cli_args.get("device_type") != "generic":
            build_cmd_parts.append(f"--device-type {cli_args['device_type']}")
        if cli_args.get("enable_variance"):
            build_cmd_parts.append("--enable-variance")
        if cli_args.get("enable_behavior_profiling"):
            build_cmd_parts.append("--enable-behavior-profiling")
            build_cmd_parts.append(
                f"--profile-duration {cli_args['behavior_profile_duration']}"
            )

        # Add donor dump options
        if cli_args.get("skip_donor_dump"):
            build_cmd_parts.append("--skip-donor-dump")
        # Only add donor_info_file when explicitly provided and not empty
        donor_info_file = cli_args.get("donor_info_file")
        if (
            donor_info_file
            and isinstance(donor_info_file, str)
            and donor_info_file.strip()
        ):
            build_cmd_parts.append(f"--donor-info-file {donor_info_file}")
        if cli_args.get("skip_board_check"):
            build_cmd_parts.append("--skip-board-check")

        build_cmd = " ".join(build_cmd_parts)

        if config.local_build:
            # Run locally
            if self._current_progress:
                self._current_progress.current_operation = "Running local build"
                await self._notify_progress()

            # Run the build command directly
            await self._run_monitored_command(build_cmd.split())
        else:
            # Run in container
            # Get IOMMU group for VFIO device
            import sys

            sys.path.append(str(Path(__file__).parent.parent.parent.parent))
            from generate import get_iommu_group

            iommu_group = await asyncio.get_event_loop().run_in_executor(
                None, get_iommu_group, device.bdf
            )
            vfio_device = f"/dev/vfio/{iommu_group}"

            # Construct container command
            container_cmd = [
                "podman",
                "run",
                "--rm",
                "-it",
                "--privileged",
                f"--device={vfio_device}",
                "--device=/dev/vfio/vfio",
                "-v",
                f"{os.getcwd()}/output:/app/output",
                "dma-fw",
                f"sudo python3 /app/build.py --bdf {device.bdf} --board {config.board_type}",
            ]

            # Add the same options to the container command
            for option in build_cmd_parts[
                1:
            ]:  # Skip the first part (python3 src/build.py)
                container_cmd.append(option)

            # Run container with progress monitoring
            await self._run_monitored_command(container_cmd)

    async def _generate_bitstream(self, config: BuildConfiguration) -> None:
        """Generate final bitstream"""
        # This would be part of the Vivado synthesis step
        await asyncio.sleep(1)  # Simulate bitstream generation

    async def _run_command(self, cmd: str) -> subprocess.CompletedProcess:
        """Run a shell command and return the result"""
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        return subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode if process.returncode is not None else 0,
            stdout=stdout.decode("utf-8"),
            stderr=stderr.decode("utf-8"),
        )

    async def _run_monitored_command(self, cmd_parts: list) -> None:
        """Run a command with progress monitoring"""
        cmd = " ".join(cmd_parts) if isinstance(cmd_parts, list) else cmd_parts

        self._build_process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Monitor process output for progress updates
        while True:
            if self._build_process.stdout:
                line = await self._build_process.stdout.readline()
                if not line:
                    break

                line_str = line.decode("utf-8").strip()
                if line_str:
                    # Update progress based on output
                    if "Running synthesis" in line_str:
                        await self._update_progress(
                            BuildStage.VIVADO_SYNTHESIS, 25, "Running synthesis"
                        )
                    elif "Running implementation" in line_str:
                        await self._update_progress(
                            BuildStage.VIVADO_SYNTHESIS, 50, "Running implementation"
                        )
                    elif "Generating bitstream" in line_str:
                        await self._update_progress(
                            BuildStage.VIVADO_SYNTHESIS, 75, "Generating bitstream"
                        )

            # Check if process has completed
            if self._build_process.returncode is not None:
                break

            await asyncio.sleep(0.1)

        # Wait for process to complete
        await self._build_process.wait()

        if self._build_process.returncode != 0:
            error_msg = ""
            if self._build_process.stderr:
                stderr = await self._build_process.stderr.read()
                error_msg = stderr.decode("utf-8")
            if self._current_progress:
                self._current_progress.add_error(f"Build command failed: {error_msg}")
            raise RuntimeError(
                f"Build command failed with code {self._build_process.returncode}"
            )
