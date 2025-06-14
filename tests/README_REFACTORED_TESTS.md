# Refactored Build System Test Suite

This directory contains comprehensive tests for the refactored PCILeech firmware generation build system. The test suite validates all new components and ensures backward compatibility with the existing system.

## Test Structure

### Core Test Modules

1. **`test_template_renderer.py`** - Tests for the Jinja2-based template rendering system
   - Template loading and rendering
   - Custom TCL filters (hex_format, tcl_string_escape, tcl_list_format)
   - Error handling for missing templates
   - Template context variable substitution

2. **`test_build_helpers.py`** - Tests for helper functions
   - `safe_import_with_fallback()` with successful and failed imports
   - `select_pcie_ip_core()` with different FPGA parts
   - `write_tcl_file_with_logging()` functionality
   - FPGA strategy selector functionality

3. **`test_tcl_builder.py`** - Tests for the TCL builder class
   - Each TCL generation method (project_setup, ip_config, sources, etc.)
   - Context preparation and template integration
   - Fallback to legacy methods when templates unavailable
   - `build_all_tcl_scripts()` orchestration method

4. **`test_constants.py`** - Tests for the constants module
   - Board parts mapping completeness
   - FPGA family patterns
   - Validation of all constants

5. **`test_build.py`** (Updated) - Integration tests for the refactored build.py
   - Template-based vs legacy TCL generation
   - Backward compatibility of the API
   - Performance comparisons
   - Migration compatibility

### Support Files

- **`conftest_refactored.py`** - Pytest fixtures and configuration for refactored tests
- **`run_refactored_tests.py`** - Comprehensive test runner with coverage analysis
- **`README_REFACTORED_TESTS.md`** - This documentation file

## Running Tests

### Quick Start

Run all refactored build system tests:

```bash
python tests/run_refactored_tests.py
```

### Individual Test Modules

Run specific test modules:

```bash
# Template renderer tests
pytest tests/test_template_renderer.py -v

# Build helpers tests  
pytest tests/test_build_helpers.py -v

# TCL builder tests
pytest tests/test_tcl_builder.py -v

# Constants tests
pytest tests/test_constants.py -v

# Updated build integration tests
pytest tests/test_build.py::TestRefactoredBuildSystem -v
```

### Test Categories

Run tests by category using markers:

```bash
# Template-related tests
pytest -m template -v

# Helper function tests
pytest -m helpers -v

# TCL builder tests
pytest -m tcl_builder -v

# Constants tests
pytest -m constants -v

# Integration tests
pytest -m integration -v

# Performance tests (slow)
pytest -m performance -v

# Skip slow tests
pytest -m "not slow" -v
```

### Coverage Analysis

Generate coverage report:

```bash
coverage run --source=src/template_renderer.py,src/build_helpers.py,src/tcl_builder.py,src/constants.py -m pytest tests/test_template_renderer.py tests/test_build_helpers.py tests/test_tcl_builder.py tests/test_constants.py
coverage report -m
coverage html --directory=tests/coverage_html
```

## Test Dependencies

Required packages for running tests:

```bash
pip install pytest coverage jinja2
```

Optional packages for enhanced testing:

```bash
pip install pytest-xdist pytest-cov pytest-html psutil
```

## Test Coverage Goals

The test suite aims for comprehensive coverage of:

### Template Renderer (`template_renderer.py`)
- ✅ Template loading and rendering
- ✅ Custom filter functionality
- ✅ Error handling and fallbacks
- ✅ Context variable substitution
- ✅ Template existence checking
- ✅ Template listing functionality

### Build Helpers (`build_helpers.py`)
- ✅ Safe import with fallback logic
- ✅ PCIe IP core selection for all FPGA families
- ✅ TCL file writing with logging
- ✅ FPGA strategy selector patterns
- ✅ Batch file operations
- ✅ FPGA part validation

### TCL Builder (`tcl_builder.py`)
- ✅ Context preparation for all board types
- ✅ Individual TCL script generation methods
- ✅ Template integration and fallback logic
- ✅ Orchestration of complete build process
- ✅ File management and cleanup
- ✅ Error handling and recovery

### Constants (`constants.py`)
- ✅ Board parts mapping completeness
- ✅ FPGA family pattern validation
- ✅ TCL script file definitions
- ✅ Build strategy configurations
- ✅ Type consistency and format validation

### Integration Tests
- ✅ Backward compatibility with existing API
- ✅ Template vs legacy output equivalence
- ✅ Performance comparison
- ✅ Migration path validation
- ✅ Error handling with missing components

## Test Data and Fixtures

### Mock Data
- **`mock_donor_info`** - Sample PCI device information
- **`mock_register_data`** - Sample register definitions with timing
- **`mock_behavior_profile`** - Sample device behavior analysis
- **`performance_test_data`** - Configuration for performance tests

### Template Data
- **`sample_tcl_templates`** - Example Jinja2 templates for testing
- **`mock_template_context`** - Complete template context for rendering
- **`sample_fpga_configurations`** - FPGA-specific configuration data

### Utility Functions
- **`generate_test_registers(count)`** - Generate large register sets for performance testing
- **`assert_tcl_content_valid(content)`** - Validate TCL output format
- **`assert_systemverilog_content_valid(content)`** - Validate SystemVerilog output
- **`assert_fpga_part_valid(part)`** - Validate FPGA part string format

## Performance Testing

Performance tests validate that the refactored system:

1. **TCL Generation Performance**
   - Template-based generation should not be >2x slower than legacy
   - Memory usage should not increase >50% over legacy
   - Large register sets (1000+ registers) should complete within 2 seconds

2. **Memory Usage**
   - Template caching should not cause excessive memory growth
   - Large datasets should be processed within memory limits
   - Garbage collection should properly clean up temporary objects

3. **Scalability**
   - System should handle boards with 100+ registers efficiently
   - Batch operations should scale linearly with input size
   - Template rendering should cache efficiently for repeated use

## Integration Testing

Integration tests ensure:

1. **API Compatibility**
   - All existing `build.py` functions remain callable
   - Function signatures are unchanged
   - Return value formats are consistent

2. **Output Equivalence**
   - Template-based TCL generation produces equivalent results to legacy
   - SystemVerilog output remains functionally identical
   - File organization and naming conventions are preserved

3. **Migration Support**
   - Both legacy and refactored systems can coexist
   - Gradual migration path is supported
   - Configuration migration is handled gracefully

## Error Handling Tests

Error handling tests cover:

1. **Missing Dependencies**
   - Graceful fallback when Jinja2 is not available
   - Safe import handling for optional components
   - Clear error messages for missing requirements

2. **Template Errors**
   - Missing template files trigger fallback methods
   - Template syntax errors are caught and reported
   - Invalid template context is handled gracefully

3. **File System Errors**
   - Permission errors during file writing
   - Missing directories are created automatically
   - Disk space issues are handled appropriately

4. **Configuration Errors**
   - Invalid FPGA parts trigger warnings and defaults
   - Malformed board configurations are validated
   - Missing constants use sensible fallbacks

## Continuous Integration

For CI/CD integration, use:

```bash
# Fast test suite (excludes slow performance tests)
pytest tests/test_template_renderer.py tests/test_build_helpers.py tests/test_tcl_builder.py tests/test_constants.py -m "not slow" --tb=short

# Full test suite with coverage
python tests/run_refactored_tests.py
```

## Debugging Test Failures

### Common Issues

1. **Import Errors**
   - Ensure `src/` directory is in Python path
   - Check that all required dependencies are installed
   - Verify module names match file names

2. **Template Errors**
   - Check that template files exist in expected locations
   - Verify Jinja2 syntax is correct
   - Ensure template context contains all required variables

3. **File Permission Errors**
   - Ensure test directories are writable
   - Check that temporary directories can be created
   - Verify file cleanup is working properly

### Debug Mode

Run tests with verbose output and debugging:

```bash
pytest tests/test_template_renderer.py -v -s --tb=long --capture=no
```

### Test Isolation

Run individual test methods for debugging:

```bash
pytest tests/test_template_renderer.py::TestTemplateRendering::test_render_template_success -v -s
```

## Contributing

When adding new tests:

1. Follow the existing naming conventions
2. Use appropriate pytest markers
3. Include both positive and negative test cases
4. Add performance tests for new functionality
5. Update this README with new test descriptions
6. Ensure tests are isolated and don't depend on external state

## Test Results Interpretation

### Success Criteria
- All tests pass (100% success rate)
- Coverage >90% for all refactored modules
- Performance tests meet timing requirements
- No memory leaks in long-running tests

### Failure Analysis
- Review test output for specific failure reasons
- Check coverage report for untested code paths
- Analyze performance test results for regressions
- Verify integration test compatibility

## Future Enhancements

Planned test improvements:

1. **Hardware-in-the-Loop Testing**
   - Integration with actual FPGA boards
   - Real Vivado tool validation
   - End-to-end bitstream generation testing

2. **Fuzzing Tests**
   - Random input generation for robustness testing
   - Edge case discovery through automated testing
   - Stress testing with malformed inputs

3. **Regression Testing**
   - Automated comparison with known good outputs
   - Version compatibility testing
   - Performance regression detection

4. **Documentation Testing**
   - Docstring example validation
   - API documentation accuracy verification
   - Tutorial and example testing