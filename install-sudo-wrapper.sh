#!/bin/bash
# Install the pcileech sudo wrapper script
# Note: This installs the updated wrapper that uses the unified pcileech.py entrypoint

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required files exist
check_files() {
    local missing_files=()
    
    if [ ! -f "pcileech-build-sudo" ]; then
        missing_files+=("pcileech-build-sudo")
    fi
    
    if [ ${#missing_files[@]} -ne 0 ]; then
        log_error "Missing required files:"
        for file in "${missing_files[@]}"; do
            log_error "  - $file"
        done
        log_error "Please run this script from the PCILeechFWGenerator root directory"
        return 1
    fi
    
    return 0
}

# Determine the installation directory
INSTALL_DIR="/usr/local/bin"
if [ ! -w "$INSTALL_DIR" ]; then
    # If we don't have write permission to /usr/local/bin, use ~/.local/bin
    INSTALL_DIR="$HOME/.local/bin"
    mkdir -p "$INSTALL_DIR"
    log_info "Using user installation directory: $INSTALL_DIR"
else
    log_info "Using system installation directory: $INSTALL_DIR"
fi

# Check if required files exist
if ! check_files; then
    exit 1
fi

# Copy the wrapper script to the installation directory
log_info "Installing pcileech-build-sudo..."
cp pcileech-build-sudo "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/pcileech-build-sudo"

log_info "Installed pcileech sudo wrapper to $INSTALL_DIR"
log_info "You can now run builds with sudo using: pcileech-build-sudo build --bdf <device> --board <board>"
log_warning "Note: The wrapper now uses the unified pcileech.py entrypoint"
log_warning "Legacy usage is supported but consider using: sudo python3 pcileech.py build ..."

# Add the directory to PATH if it's not already there
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    log_info "Adding $INSTALL_DIR to your PATH"
    
    # Determine which shell configuration file to use
    SHELL_CONFIG=""
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        SHELL_CONFIG="$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        SHELL_CONFIG="$HOME/.bash_profile"
    elif [ -f "$HOME/.profile" ]; then
        SHELL_CONFIG="$HOME/.profile"
    fi
    
    if [ -n "$SHELL_CONFIG" ]; then
        # Check if the PATH export already exists to avoid duplicates
        if ! grep -q "export PATH.*$INSTALL_DIR" "$SHELL_CONFIG"; then
            echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$SHELL_CONFIG"
            log_info "Added $INSTALL_DIR to your PATH in $SHELL_CONFIG"
            log_info "Please restart your terminal or run 'source $SHELL_CONFIG' to apply changes"
        else
            log_info "$INSTALL_DIR already exists in $SHELL_CONFIG"
        fi
    else
        log_warning "Could not find a shell configuration file to update PATH"
        log_warning "Please manually add $INSTALL_DIR to your PATH"
        log_info "Add this line to your shell configuration file:"
        log_info "  export PATH=\"\$PATH:$INSTALL_DIR\""
    fi
else
    log_info "$INSTALL_DIR is already in your PATH"
fi

log_info "Installation complete!"
log_info ""
log_info "Usage examples:"
log_info "  pcileech-build-sudo build --bdf 0000:03:00.0 --board pcileech_35t325_x1"
log_info "  pcileech-build-sudo tui"
log_info "  pcileech-build-sudo check --device 0000:03:00.0"
log_info ""
log_info "Alternative (recommended):"
log_info "  sudo python3 pcileech.py build --bdf 0000:03:00.0 --board pcileech_35t325_x1"