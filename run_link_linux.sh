#!/usr/bin/env bash
# Antigravity Link - Linux Runner
# Runs the live AGY-Link background daemon on Ubuntu / Linux

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=================================================="
echo "🤖 Antigravity Link — Linux Peer Node"
echo "=================================================="

case "$1" in
    chat)
        python3 agy_link.py chat
        ;;
    status)
        python3 agy_link.py status
        ;;
    inbox)
        python3 agy_link.py inbox
        ;;
    summon)
        shift
        python3 agy_link.py summon "$@"
        ;;
    sync)
        shift
        python3 agy_link.py sync "$@"
        ;;
    delegate)
        shift
        python3 agy_link.py delegate "$@"
        ;;
    send)
        shift
        python3 agy_link.py send "$@"
        ;;
    *)
        echo "Starting background sync daemon..."
        echo "Direct Socket : Port 7890 TCP"
        echo "Cloud Relay   : Active Fallback"
        echo "Inbox Ledger  : $DIR/INBOX.md"
        echo "Press Ctrl+C to stop."
        echo ""
        python3 agy_link.py daemon
        ;;
esac
