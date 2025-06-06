# 🛠️ Development Guide

[![PyPI version](https://badge.fury.io/py/pcileech-fw-generator.svg)](https://badge.fury.io/py/pcileech-fw-generator)
[![Python Support](https://img.shields.io/pypi/pyversions/pcileech-fw-generator.svg)](https://pypi.org/project/pcileech-fw-generator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This document provides instructions for setting up a development environment for the PCILeech Firmware Generator project.

---

## 📑 Table of Contents

- [🚀 Development Setup](#-development-setup)
- [📦 Building from Source](#-building-from-source)
- [🤝 Contributing](#-contributing)
- [🧪 Testing](#-testing)
- [📝 Code Style](#-code-style)
- [⚠️ Disclaimer](#️-disclaimer)

---

## 🚀 Development Setup

```bash
# Clone repository
git clone https://github.com/ramseymcgrath/PCILeechFWGenerator
cd PCILeechFWGenerator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/
```

## 📦 Building from Source

```bash
# Build distributions
python -m build

# Install locally
pip install dist/*.whl

# Test installation
pcileech-generate --help
```

## 🤝 Contributing

We welcome contributions! Please see [`CONTRIBUTING.md`](../CONTRIBUTING.md) for detailed guidelines.

**Quick Start:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'feat: add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 🧪 Testing

The project uses pytest for testing. Run the test suite with:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_specific_module.py

# Run with coverage
pytest --cov=src tests/
```

## 📝 Code Style

This project follows these coding standards:

- PEP 8 for Python code style
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

Pre-commit hooks are configured to enforce these standards.

## ⚠️ Disclaimer

This tool is intended for educational research and legitimate PCIe development purposes only. Users are responsible for ensuring compliance with all applicable laws and regulations. The authors assume no liability for misuse of this software.

---

**Version 0.1.6** - Major release with TUI interface and professional packaging