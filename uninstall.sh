#!/usr/bin/env bash
# ==============================================================================
# Antigravity Link (agy-link) Clean Uninstaller
# Remote 1-Liner:
#   curl -fsSL https://raw.githubusercontent.com/ImNotMrReaper/antigravity-link/main/uninstall.sh | bash
# ==============================================================================

set -e

RED="\033[91m"
GREEN="\033[92m"
CYAN="\033[96m"
RESET="\033[0m"

echo -e "${CYAN}>>> Stopping any active Antigravity Link processes...${RESET}"
pkill -f "agy_link.py" 2>/dev/null || true

echo -e "${CYAN}>>> Removing Antigravity Link files...${RESET}"
rm -rf "${HOME}/.gemini/config/plugins/antigravity-link"
rm -rf "${HOME}/.agents/skills/agy-link"

if [ -f "/usr/local/bin/agy-link" ]; then
    if [ -w "/usr/local/bin" ] || [ "$(id -u)" -eq 0 ]; then
        rm -f "/usr/local/bin/agy-link"
    elif command -v sudo >/dev/null 2>&1; then
        sudo rm -f "/usr/local/bin/agy-link"
    fi
fi
rm -f "${HOME}/.local/bin/agy-link"

echo -e "${GREEN}✓ Antigravity Link cleanly uninstalled.${RESET}\n"
