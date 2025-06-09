# PCILeech FPGA Firmware Generator Release Plan

This document outlines the release plan for version 0.3.0 of the PCILeech FPGA firmware generator, which integrates all the implemented features:

1. Full 4 KB config-space shadow in BRAM
2. Auto-replicate MSI-X table exactly
3. Prune capabilities that can't be faithfully emulated
4. Deterministic variance seeding

## Table of Contents

1. [Release Timeline](#release-timeline)
2. [Pre-Release Tasks](#pre-release-tasks)
3. [Testing Strategy](#testing-strategy)
4. [Deployment Steps](#deployment-steps)
5. [Post-Release Monitoring](#post-release-monitoring)
6. [Rollback Plan](#rollback-plan)
7. [Risk Assessment](#risk-assessment)
8. [Communication Plan](#communication-plan)

## Release Timeline

| Date | Milestone |
|------|-----------|
| June 10, 2025 | Feature freeze - all features integrated |
| June 11, 2025 | Complete integration testing |
| June 12, 2025 | Documentation review and finalization |
| June 13, 2025 | Release candidate 1 (RC1) |
| June 14, 2025 | Community testing of RC1 |
| June 15, 2025 | Address feedback and fix issues |
| June 16, 2025 | Release candidate 2 (RC2) if needed |
| June 17, 2025 | Final review and approval |
| June 18, 2025 | Official release of v0.3.0 |

## Pre-Release Tasks

### Code Preparation

- [x] Integrate all features into the main codebase
- [x] Create comprehensive integration tests
- [x] Update documentation for all features
- [x] Update CHANGELOG.md with release notes
- [ ] Update version number in `src/__version__.py`
- [ ] Update package metadata in `pyproject.toml` and `setup.py`
- [ ] Ensure all dependencies are correctly specified
- [ ] Run code quality checks (linting, formatting, type checking)
- [ ] Address any technical debt or known issues

### Documentation

- [x] Create comprehensive integration documentation
- [x] Update feature-specific documentation with integration details
- [x] Update README.md with new features
- [x] Create release plan document
- [ ] Prepare release announcement
- [ ] Update installation and usage instructions
- [ ] Create or update troubleshooting guide

### Testing

- [x] Create integration tests for all features
- [ ] Run full test suite on multiple platforms (Linux, macOS, Windows)
- [ ] Test with different donor device types
- [ ] Test with different FPGA board types
- [ ] Test with different Python versions
- [ ] Test installation from PyPI
- [ ] Test containerized builds
- [ ] Perform regression testing for existing features

## Testing Strategy

### Unit Testing

- Run existing unit tests for each feature
- Run new integration tests for all features combined
- Ensure test coverage is maintained or improved

### Integration Testing

- Test all features working together with different donor device types:
  - Network controllers
  - Storage controllers
  - Graphics controllers
  - Generic devices
- Test with different FPGA board types:
  - 35t (PCIeSquirrel)
  - 75t (PCIeEnigmaX1)
  - 100t (XilinxZDMA)
  - CaptainDMA boards

### Performance Testing

- Measure build time with all features enabled
- Measure memory usage during build
- Measure FPGA resource utilization
- Compare with previous versions to ensure no significant regressions

### Compatibility Testing

- Test with Python 3.9, 3.10, 3.11, and 3.12
- Test on Ubuntu 22.04, 24.04
- Test on Fedora 39, 40
- Test on macOS Ventura, Sonoma
- Test on Windows 10, 11 with WSL2

## Deployment Steps

### PyPI Release

1. Update version number in `src/__version__.py`
2. Update package metadata in `pyproject.toml` and `setup.py`
3. Build the package:
   ```bash
   python -m build
   ```
4. Upload to PyPI:
   ```bash
   python -m twine upload dist/*
   ```
5. Verify installation from PyPI:
   ```bash
   pip install pcileech-fw-generator==0.3.0
   ```

### GitHub Release

1. Create a new tag for the release:
   ```bash
   git tag -a v0.3.0 -m "Version 0.3.0"
   git push origin v0.3.0
   ```
2. Create a new release on GitHub with release notes
3. Upload built packages as release assets
4. Update documentation on GitHub Pages if applicable

### Container Release

1. Build the container image with the new version:
   ```bash
   ./scripts/build_container.sh 0.3.0
   ```
2. Test the container image
3. Push the container image to the registry:
   ```bash
   podman push pcileech-fw-generator:0.3.0
   ```
4. Update container documentation with new version

## Post-Release Monitoring

### Metrics to Monitor

- PyPI download statistics
- GitHub issue tracker for bug reports
- Community forum activity
- Container image pulls
- Build success rate

### Support Plan

- Monitor GitHub issues for bug reports
- Provide timely responses to user questions
- Prepare hotfix releases if critical issues are discovered
- Document common issues and solutions in the troubleshooting guide

## Rollback Plan

In case of critical issues discovered after release:

1. Identify the issue and its severity
2. Determine if a hotfix is possible or if a rollback is necessary
3. If a hotfix is possible:
   - Develop and test the fix
   - Release a patch version (0.3.1)
4. If a rollback is necessary:
   - Communicate the rollback to users
   - Remove the problematic version from PyPI
   - Revert the GitHub release
   - Update documentation to reflect the rollback

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Integration issues between features | Medium | High | Comprehensive integration testing with different device types |
| Performance degradation | Low | Medium | Performance testing and comparison with previous versions |
| Compatibility issues with different platforms | Medium | Medium | Testing on multiple platforms and Python versions |
| Dependency conflicts | Low | High | Careful management of dependencies and testing with different environments |
| Documentation gaps | Medium | Medium | Thorough documentation review and user feedback |
| Container build failures | Low | Medium | Automated container testing and validation |

## Communication Plan

### Pre-Release Communication

- Announce upcoming release on GitHub repository
- Share release candidate with key community members for testing
- Publish release timeline and feature highlights

### Release Communication

- Publish release announcement on GitHub
- Update documentation with new features and changes
- Send notification to mailing list or community forum
- Update social media channels if applicable

### Post-Release Communication

- Gather user feedback on new features
- Address questions and issues in community forums
- Share success stories and use cases
- Begin planning for next release based on feedback

## Feature Integration Details

### Full 4 KB Config-Space Shadow in BRAM

The configuration space shadow BRAM implementation provides a complete 4 KB PCI Express configuration space in block RAM (BRAM) on the FPGA. This feature is integrated with:

- **MSI-X Table Replication**: The config space shadow provides the configuration space data to the MSI-X capability parser.
- **Capability Pruning**: The config space shadow provides the configuration space data to the capability pruning module.
- **Deterministic Variance Seeding**: The config space shadow can extract the DSN from the configuration space for deterministic variance seeding.

### Auto-Replicate MSI-X Table

The MSI-X table replication feature extends the PCILeech FPGA firmware generator to accurately replicate the MSI-X capability structure from donor devices. This feature is integrated with:

- **Config Space Shadow**: The MSI-X capability parser extracts MSI-X table parameters from the configuration space.
- **Capability Pruning**: The capability pruning module preserves the MSI-X capability during pruning.
- **BAR Controller**: The BAR controller routes MSI-X table and PBA accesses to the appropriate memory regions.

### Capability Pruning

The PCI capability pruning feature extends the PCILeech FPGA firmware generator to analyze and selectively modify or remove PCI capabilities that cannot be faithfully emulated. This feature is integrated with:

- **Config Space Shadow**: The capability pruning module modifies the configuration space data before it is used to initialize the config space shadow.
- **MSI-X Table Replication**: The capability pruning module preserves the MSI-X capability during pruning.
- **Build Process**: The capability pruning module is integrated into the build process to apply pruning rules before generating the firmware.

### Deterministic Variance Seeding

The manufacturing variance simulation module provides realistic hardware variance simulation for PCIe device firmware generation. The deterministic variance seeding feature ensures that two builds of the same donor at the same commit fall in the same timing band. This feature is integrated with:

- **Config Space Shadow**: The deterministic variance seeding module can extract the DSN from the configuration space.
- **Build Process**: The deterministic variance seeding module is integrated into the build process to generate variance parameters based on the DSN and build revision.
- **SystemVerilog Generation**: The deterministic variance seeding module provides variance parameters to the SystemVerilog generation process.