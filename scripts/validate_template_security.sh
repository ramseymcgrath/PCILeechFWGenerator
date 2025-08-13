#!/bin/bash
# Script to validate template security enhancements
# This script runs the template security test and reports results

set -e

echo "===================================================="
echo "Running Template Security Validation Tests"
echo "===================================================="

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Make the test script executable
chmod +x "$SCRIPT_DIR/test_template_security.py"

# Run the tests with Python
cd "$PROJECT_ROOT"
python3 "$SCRIPT_DIR/test_template_security.py"

# Check exit code
if [ $? -eq 0 ]; then
    echo "===================================================="
    echo "SUCCESS: All security validation tests passed!"
    echo "===================================================="
    echo "Template system is properly secured against invalid or incomplete data."
    exit 0
else
    echo "===================================================="
    echo "ERROR: Some security validation tests failed!"
    echo "===================================================="
    echo "Please review the security validation failures and fix them before proceeding."
    exit 1
fi