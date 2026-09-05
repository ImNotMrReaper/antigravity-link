#!/usr/bin/env bash
# Antigravity Link - Linux Runner
# Runs the live AGY-Link background daemon on Ubuntu / Linux

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=================================================="
echo "🤖 Antigravity Link — Linux Lead Node (Mr-Reaper)"
echo "=================================================="

if [ "$1" == "chat" ]; then
    python3 agy_link.py --user "Mr-Reaper" --peer "Senpai" chat
elif [ "$1" == "inbox" ]; then
    python3 agy_link.py inbox
else
    echo "Starting background listener daemon..."
    echo "Logs and incoming messages will sync to: $DIR/INBOX.md"
    echo "Press Ctrl+C to stop."
    echo ""
    python3 agy_link.py --user "Mr-Reaper" --peer "Senpai" listen
fi
