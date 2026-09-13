#!/usr/bin/env bash
# ==============================================================================
# Antigravity Link (agy-link) - Peer AI Collaboration & Tandem Sync Installer
# Remote 1-Liner:
#   curl -fsSL https://raw.githubusercontent.com/ImNotMrReaper/antigravity-link/main/install.sh | bash
# ==============================================================================

set -e

# ANSI Styling
BOLD="\033[1m"
CYAN="\033[96m"
PURPLE="\033[95m"
GREEN="\033[92m"
YELLOW="\033[93m"
RESET="\033[0m"

echo -e "${PURPLE}================================================================${RESET}"
echo -e "${BOLD} 🤖⚡🤖 Antigravity Link: Peer AI Collaboration & Tandem Sync${RESET}"
echo -e "${PURPLE}================================================================${RESET}\n"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"

# Auto-clone repository if executed directly from curl/pipe
if [ ! -f "${SCRIPT_DIR}/agy_link.py" ]; then
    echo -e "${CYAN}>>> Running from remote pipe. Cloning latest repository...${RESET}"
    TMP_CLONE="$(mktemp -d /tmp/antigravity-link-install.XXXXXX)"
    if ! command -v git >/dev/null 2>&1; then
        echo ">>> Installing git..."
        if command -v apt-get >/dev/null 2>&1; then
            if [ "$(id -u)" -eq 0 ]; then apt-get update -qq && apt-get install -y -qq git; else sudo apt-get update -qq && sudo apt-get install -y -qq git; fi
        elif command -v dnf >/dev/null 2>&1; then
            if [ "$(id -u)" -eq 0 ]; then dnf install -y git; else sudo dnf install -y git; fi
        elif command -v pacman >/dev/null 2>&1; then
            if [ "$(id -u)" -eq 0 ]; then pacman -Sy --needed --noconfirm git; else sudo pacman -Sy --needed --noconfirm git; fi
        elif command -v zypper >/dev/null 2>&1; then
            if [ "$(id -u)" -eq 0 ]; then zypper --non-interactive install git; else sudo zypper --non-interactive install git; fi
        fi
    fi
    git clone --depth 1 https://github.com/ImNotMrReaper/antigravity-link.git "${TMP_CLONE}"
    SCRIPT_DIR="${TMP_CLONE}"
    trap "rm -rf '${TMP_CLONE}'" EXIT
fi

# Ensure Python 3 is installed (100% Python Standard Library, Zero pip dependencies)
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${YELLOW}>>> Python 3 not found. Installing Python 3...${RESET}"
    if command -v apt-get >/dev/null 2>&1; then
        if [ "$(id -u)" -eq 0 ]; then apt-get update -qq && apt-get install -y -qq python3; else sudo apt-get update -qq && sudo apt-get install -y -qq python3; fi
    elif command -v dnf >/dev/null 2>&1; then
        if [ "$(id -u)" -eq 0 ]; then dnf install -y python3; else sudo dnf install -y python3; fi
    elif command -v pacman >/dev/null 2>&1; then
        if [ "$(id -u)" -eq 0 ]; then pacman -Sy --needed --noconfirm python; else sudo pacman -Sy --needed --noconfirm python; fi
    elif command -v zypper >/dev/null 2>&1; then
        if [ "$(id -u)" -eq 0 ]; then zypper --non-interactive install python3; else sudo zypper --non-interactive install python3; fi
    fi
fi

PLUGIN_DIR="${HOME}/.gemini/config/plugins/antigravity-link"
SKILLS_DIR="${HOME}/.agents/skills/agy-link"

echo -e "${CYAN}>>> Installing Antigravity Link Plugin & Rules...${RESET}"
mkdir -p "${PLUGIN_DIR}"
cp -r "${SCRIPT_DIR}/"* "${PLUGIN_DIR}/" 2>/dev/null || true

if [ -d "${SCRIPT_DIR}/skills/agy-link" ]; then
    mkdir -p "${SKILLS_DIR}"
    cp -r "${SCRIPT_DIR}/skills/agy-link/"* "${SKILLS_DIR}/" 2>/dev/null || true
    echo -e "    ${GREEN}✓ Installed Agent Skill:${RESET} ${SKILLS_DIR}"
fi

# Install CLI binary wrapper (agy-link)
echo -e "\n${CYAN}>>> Installing CLI tool (agy-link)...${RESET}"
CLI_TARGET=""
if [ -w "/usr/local/bin" ] || [ "$(id -u)" -eq 0 ]; then
    CLI_TARGET="/usr/local/bin/agy-link"
elif command -v sudo >/dev/null 2>&1; then
    sudo mkdir -p /usr/local/bin
    CLI_TARGET="/usr/local/bin/agy-link"
else
    mkdir -p "${HOME}/.local/bin"
    CLI_TARGET="${HOME}/.local/bin/agy-link"
fi

cat << 'EOF_WRAPPER' > /tmp/agy-link-wrapper
#!/usr/bin/env bash
LINK_SCRIPT="${HOME}/.gemini/config/plugins/antigravity-link/agy_link.py"
if [ -f "$LINK_SCRIPT" ]; then
    exec python3 "$LINK_SCRIPT" "$@"
else
    echo "Error: agy_link.py not found at $LINK_SCRIPT" >&2
    exit 1
fi
EOF_WRAPPER
chmod +x /tmp/agy-link-wrapper

if [ -w "$(dirname "$CLI_TARGET")" ]; then
    mv /tmp/agy-link-wrapper "$CLI_TARGET"
else
    sudo mv /tmp/agy-link-wrapper "$CLI_TARGET"
fi
echo -e "    ${GREEN}✓ Installed CLI Tool:${RESET} ${CLI_TARGET}"

echo -e "\n${GREEN}================================================================${RESET}"
echo -e "${GREEN} 🎉 ANTIGRAVITY LINK INSTALLED SUCCESSFULLY!${RESET}"
echo -e "${GREEN}================================================================${RESET}"
echo -e "Components active:"
echo -e "  • Plugin Directory:  ${PLUGIN_DIR}"
echo -e "  • Agent Skill:       ${SKILLS_DIR}"
echo -e "  • Terminal CLI Tool: ${CLI_TARGET}"
echo -e "  • Web Telemetry HUD: http://127.0.0.1:7891"
echo -e ""
echo -e "Quick Commands:"
echo -e "  ${PURPLE}agy-link status${RESET}                     - View tandem mesh connection & peer status"
echo -e "  ${PURPLE}agy-link send \"Hello peer!\" --agent${RESET}  - Send direct message to peer AI"
echo -e "  ${PURPLE}agy-link summon \"Run tests\"${RESET}         - Summon remote peer AI for autonomous action\n"
