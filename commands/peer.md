---
name: peer
description: Send messages or delegate tasks directly to your remote peer station in AGY TUI
---

# /peer — Remote Peer Communication & Task Delegation

You are handling the `/peer` command inside the Antigravity TUI.

> [!IMPORTANT]
> **STRICT TUI RULE**: Do NOT open any external terminal windows (e.g. Terminator, cmd.exe, wt.exe). All interactions, messages, status reports, and AI handoffs must occur **entirely inside this AGY session**.

## Instructions
When the user types `/peer <prompt>`:

1. **If it is a task or request for the peer AI (e.g. compile, test, verify, code, run)**:
   - Dispatch to the peer AI via `python3 agy_link.py summon "<prompt>" --target peer`.
   - Monitor `INBOX.md` or wait for the report from the remote peer machine.
   - Format and present the complete report directly inside this AGY conversation.

2. **If it is a direct chat message or greeting**:
   - Send the message to the peer via `python3 agy_link.py send "<prompt>"`.
   - Confirm delivery directly in chat.
