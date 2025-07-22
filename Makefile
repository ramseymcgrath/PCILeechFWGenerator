# Makefile for PCILeech Firmware Generator

.PHONY: help clean install install-dev test lint format build build-pypi upload-test upload-pypi release container container-rebuild docker-build build-container vfio-constants vfio-constants-clean

# Default target
help:
	@echo "PCILeech Firmware Generator - Available targets:"
	@echo ""
	@echo "Development:"
	@echo "  install      - Install package in development mode"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run test suite"
	@echo "  test-tui     - Run TUI integration tests only"
	@echo "  test-unit    - Run unit tests only (no hardware/TUI)"
	@echo "  test-all     - Run all tests with coverage"
	@echo "  test-fast    - Run fast tests only"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code with black and isort"
	@echo "  clean        - Clean build artifacts"
	@echo ""
	@echo "Building:"
	@echo "  build        - Build package distributions"
	@echo "  build-pypi   - Full PyPI package generation (recommended)"
	@echo "  build-quick  - Quick build without quality checks"
	@echo ""
	@echo "Publishing:"
	@echo "  upload-test  - Upload to Test PyPI"
	@echo "  upload-pypi  - Upload to PyPI"
	@echo "  release      - Full release process"
	@echo ""
	@echo "Container:"
	@echo "  container         - Build container image (dma-fw) with --no-cache"
	@echo "  container-rebuild - Force rebuild container (alias for container)"
	@echo "  docker-build      - Build container image (default tag) with --no-cache"
	@echo ""
	@echo "Utilities:"
	@echo "  check-deps      - Check system dependencies"
	@echo "  security        - Run security scans"
	@echo "  vfio-constants  - Build and patch VFIO ioctl constants"
	@echo "  vfio-constants-clean - Clean VFIO build artifacts"

# Development targets
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,test,tui]"

test:
	pytest tests/ --cov=src --cov-report=term-missing

test-tui:
	pytest tests/test_tui_integration.py -v -m tui

test-unit:
	pytest tests/ -k "not tui" -m "not hardware" --cov=src --cov-report=term-missing

test-all:
	pytest tests/ -v --cov=src --cov-report=term-missing

test-fast:
	pytest tests/ -x -q -m "not slow and not hardware"

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Building targets
build:
	python -m build

build-pypi:
	@echo "Running full PyPI package generation..."
	python3 scripts/generate_pypi_package.py --skip-upload

build-quick:
	@echo "Running quick PyPI package generation..."
	python3 scripts/generate_pypi_package.py --quick --skip-upload

# Publishing targets
upload-test:
	@echo "Building and uploading to Test PyPI..."
	python3 scripts/generate_pypi_package.py --test-pypi

upload-pypi:
	@echo "Building and uploading to PyPI..."
	python3 scripts/generate_pypi_package.py

release:
	@echo "Running full release process..."
	./scripts/build_release.sh release $(VERSION)

# Utility targets
check-deps:
	@echo "Checking system dependencies..."
	@python3 scripts/generate_pypi_package.py --skip-quality --skip-security --skip-upload --skip-install-test || true

security:
	@echo "Running security scans..."
	bandit -r src/
	safety check

# Container targets
container:
	./scripts/build_container.sh --tag dma-fw

container-rebuild: container

docker-build:
	./scripts/build_container.sh

# Alias for container
build-container: container

# Test package build
test-build:
	@echo "Testing PyPI package build..."
	python3 scripts/test_package_build.py

# Help for specific targets
help-build:
	@echo "Build targets:"
	@echo ""
	@echo "  build        - Basic build using python -m build"
	@echo "  build-pypi   - Full PyPI generation with all checks"
	@echo "  build-quick  - Quick build skipping quality checks"
	@echo ""
	@echo "Options for build-pypi:"
	@echo "  - Runs code quality checks (black, isort, flake8, mypy)"
	@echo "  - Runs security scans (bandit, safety)"
	@echo "  - Runs test suite with coverage"
	@echo "  - Validates package structure"
	@echo "  - Tests installation in virtual environment"
	@echo ""
	@echo "Use 'make build-quick' for faster iteration during development"

help-upload:
	@echo "Upload targets:"
	@echo ""
	@echo "  upload-test  - Upload to Test PyPI (https://test.pypi.org/)"
	@echo "  upload-pypi  - Upload to production PyPI (https://pypi.org/)"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - Configure ~/.pypirc with your API tokens"
	@echo "  - Or set TWINE_USERNAME and TWINE_PASSWORD environment variables"
	@echo ""
	@echo "Test PyPI installation:"
	@echo "  pip install --index-url https://test.pypi.org/simple/ pcileech-fw-generator"
	@echo ""
	@echo "Production PyPI installation:"
	@echo "  pip install pcileech-fw-generator"

# VFIO Constants targets
vfio-constants:
	@echo "Building VFIO constants..."
	./build_vfio_constants.sh

vfio-constants-clean:
	@echo "Cleaning VFIO build artifacts..."
	rm -f vfio_helper vfio_helper.exe
	@echo "VFIO build artifacts cleaned"

# Integration targets - build VFIO constants before container build
container: vfio-constants
	./scripts/build_container.sh --tag dma-fw

build-pypi: vfio-constants
	@echo "Running full PyPI package generation with VFIO constants..."
	python3 scripts/generate_pypi_package.py --skip-upload