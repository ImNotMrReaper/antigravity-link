#!/usr/bin/env bash
# Antigravity Link - Linux Shortcuts, Protocol, & AGY Plugin Installer
# Run once on Linux to enable 'link' in PATH, clickable notifications, and AGY plugin.

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$HOME/.local/bin"
mkdir -p "$HOME/.local/share/applications"

echo "============================================================"
echo "🤖 Installing Antigravity Link Linux Shortcuts & AGY Plugin"
echo "============================================================"

# 1. Install global 'link' command in ~/.local/bin/link
cat << 'EOF' > "$HOME/.local/bin/link"
#!/usr/bin/env bash
REPO_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/../../PycharmProjects/antigravity-link" 2>/dev/null && pwd)"
if [ ! -f "$REPO_DIR/agy_link.py" ]; then
    REPO_DIR="$HOME/PycharmProjects/antigravity-link"
fi

if [ $# -eq 0 ]; then
    exec python3 "$REPO_DIR/agy_link.py" chat
fi

case "$1" in
    chat)
        exec python3 "$REPO_DIR/agy_link.py" chat
        ;;
    ai|both)
        shift
        exec python3 "$REPO_DIR/agy_link.py" summon "$*" --target both
        ;;
    senpai|remote)
        shift
        exec python3 "$REPO_DIR/agy_link.py" summon "$*" --target senpai
        ;;
    reaper|local)
        shift
        exec python3 "$REPO_DIR/agy_link.py" summon "$*" --target reaper
        ;;
    pull)
        cd "$REPO_DIR" && git pull origin main
        ;;
    open)
        xdg-open "$REPO_DIR" >/dev/null 2>&1 &
        ;;
    *)
        exec python3 "$REPO_DIR/agy_link.py" "$@"
        ;;
esac
EOF
chmod +x "$HOME/.local/bin/link"
echo "[✓] Installed global 'link' command in $HOME/.local/bin/link"

# Ensure python symlink exists in ~/.local/bin
if ! command -v python &>/dev/null; then
    ln -sf "$(which python3)" "$HOME/.local/bin/python"
    echo "[✓] Symlinked python -> python3 in $HOME/.local/bin"
fi

# 2. Register 'agy-link://' URL protocol desktop launcher
cat << EOF > "$HOME/.local/share/applications/agy-link.desktop"
[Desktop Entry]
Name=Antigravity Link Chat
Comment=Open live terminal chat with peer AI station
Exec=terminator -u -T "Antigravity Link Chat" -x "$HOME/.local/bin/link" chat
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Development;Utility;
MimeType=x-scheme-handler/agy-link;
NoDisplay=true
EOF

update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
xdg-mime default agy-link.desktop x-scheme-handler/agy-link 2>/dev/null || true
echo "[✓] Registered 'agy-link://' protocol handler and desktop launcher"

# 3. Install AGY Plugin Globally in ~/.gemini/config/plugins/
GEMINI_CONFIG="$HOME/.gemini/config"
PLUGINS_DIR="$GEMINI_CONFIG/plugins"
TARGET_PLUGIN="$PLUGINS_DIR/antigravity-link"
SOURCE_PLUGIN="$REPO_DIR/.agents/plugins/antigravity-link"

mkdir -p "$PLUGINS_DIR"
rm -rf "$TARGET_PLUGIN"
cp -r "$SOURCE_PLUGIN" "$TARGET_PLUGIN"
echo "$REPO_DIR" > "$TARGET_PLUGIN/repo_path.txt"

# Configure global plugins.json
cat << EOF > "$GEMINI_CONFIG/plugins.json"
{
  "entries": [
    {
      "path": "~/.gemini/config/plugins/antigravity-link"
    }
  ]
}
EOF
echo "[✓] Installed AGY Plugin to $TARGET_PLUGIN"
echo "[✓] Configured global plugins registry in $GEMINI_CONFIG/plugins.json"

# Validate plugin
if command -v agy &>/dev/null; then
    echo "🔍 Validating AGY plugin with agy CLI..."
    agy plugin validate "$TARGET_PLUGIN"
fi

echo ""
echo "🎉 Linux installation complete! You can now:"
echo "   1. Type 'link' or 'link chat' from any terminal."
echo "   2. Type 'link ai <task>' to summon both AIs."
echo "   3. Click incoming desktop notifications to pop up Terminator chat."
echo "   4. Use AGY Link directly inside Antigravity (AGY) sessions via native tools/skills!"
