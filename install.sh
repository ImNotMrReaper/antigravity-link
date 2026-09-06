#!/usr/bin/env bash
# Antigravity Link — Universal Linux 1-Liner Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/ImNotMrReaper/antigravity-link/main/install.sh | bash
set -e

REPO_URL="https://github.com/ImNotMrReaper/antigravity-link.git"
INSTALL_DIR="$HOME/.local/share/antigravity-link"

# If already running inside a cloned repo, use current dir
if [ -f "./agy_link.py" ]; then
    INSTALL_DIR="$(pwd)"
else
    echo "📦 Cloning Antigravity Link to $INSTALL_DIR..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    if [ -d "$INSTALL_DIR/.git" ]; then
        (cd "$INSTALL_DIR" && git pull origin main)
    else
        git clone "$REPO_URL" "$INSTALL_DIR"
    fi
fi

echo "🚀 Running Antigravity Link Linux Installer..."
bash "$INSTALL_DIR/install_linux_shortcuts.sh"
