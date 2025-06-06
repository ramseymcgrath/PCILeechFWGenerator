#!/bin/bash
# Install the pcileech sudo wrapper scripts

# Determine the installation directory
INSTALL_DIR="/usr/local/bin"
if [ ! -w "$INSTALL_DIR" ]; then
    # If we don't have write permission to /usr/local/bin, use ~/.local/bin
    INSTALL_DIR="$HOME/.local/bin"
    mkdir -p "$INSTALL_DIR"
fi

# Copy the wrapper scripts to the installation directory
cp pcileech-tui-sudo "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/pcileech-tui-sudo"

cp pcileech-build-sudo "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/pcileech-build-sudo"

echo "Installed pcileech sudo wrappers to $INSTALL_DIR"
echo "You can now run the TUI with sudo using: pcileech-tui-sudo"
echo "You can now run the build with sudo using: pcileech-build-sudo"

# Add the directory to PATH if it's not already there
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "Adding $INSTALL_DIR to your PATH"
    
    # Determine which shell configuration file to use
    SHELL_CONFIG=""
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_CONFIG="$HOME/.bashrc"
    elif [ -f "$HOME/.zshrc" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [ -f "$HOME/.profile" ]; then
        SHELL_CONFIG="$HOME/.profile"
    fi
    
    if [ -n "$SHELL_CONFIG" ]; then
        echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$SHELL_CONFIG"
        echo "Added $INSTALL_DIR to your PATH in $SHELL_CONFIG"
        echo "Please restart your terminal or run 'source $SHELL_CONFIG' to apply changes"
    else
        echo "Could not find a shell configuration file to update PATH"
        echo "Please manually add $INSTALL_DIR to your PATH"
    fi
fi