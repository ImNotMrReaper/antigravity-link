---
name: senpai
description: Send messages or delegate tasks directly to Senpai's Windows 11 station in AGY TUI
---

# /senpai — Windows 11 Peer Communication & Task Delegation

You are handling the `/senpai` command inside the Antigravity TUI.

> [!IMPORTANT]
> **STRICT TUI RULE**: Do NOT open any external terminal windows (e.g. Terminator, cmd.exe, wt.exe). All interactions, messages, status reports, and AI handoffs must occur **entirely inside this AGY session**.

## Instructions
When the user types `/senpai <prompt>`:

1. **If it is a task or request for Senpai's AI (e.g. compile, test, verify, code, run)**:
   - Dispatch to Senpai's AI via `python3 agy_link.py summon "<prompt>" --target senpai`.
   - Monitor `INBOX.md` or wait for the report from Senpai's Windows machine.
   - Format and present the complete report directly inside this AGY conversation.

2. **If it is a direct chat message or greeting**:
   - Send the message to Senpai via `python3 agy_link.py send "<prompt>"`.
   - Confirm delivery directly in chat.
