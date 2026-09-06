---
name: inbox
description: View incoming peer messages and AI task reports inside AGY TUI
---

# /inbox — Read Peer Messages & AI Reports

You are handling the `/inbox` command inside the Antigravity TUI.

> [!IMPORTANT]
> **STRICT TUI RULE**: Do NOT open any external terminal windows (e.g. Terminator, cmd.exe, wt.exe). All interactions, messages, status reports, and AI handoffs must occur **entirely inside this AGY session**.

## Instructions
When the user types `/inbox`:

1. Read the latest entries from `INBOX.md` (or run `python3 agy_link.py inbox`).
2. Format the messages and task reports cleanly in markdown.
3. Highlight any unread messages or completed AI task reports from the peer.
