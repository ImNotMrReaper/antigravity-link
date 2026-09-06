---
name: link
description: Cross-platform peer AI collaboration and tandem sync in AGY TUI
---

# /link — Antigravity Peer Collaboration

You are handling the `/link` command inside the Antigravity TUI.

> [!IMPORTANT]
> **STRICT TUI RULE**: Do NOT open any external terminal windows (e.g. Terminator, cmd.exe, wt.exe). All interactions, messages, status reports, and AI handoffs must occur **entirely inside this AGY session**.

## Instructions
Parse the user's arguments following `/link`:

1. **`/link status` (or no arguments)**:
   - Check peer connectivity and active file locks using `link_status` MCP tool or running `python3 agy_link.py status`.
   - Render the formatted status matrix directly in this conversation.

2. **`/link send <message>`**:
   - Send the message to the peer station using `link_send` or `python3 agy_link.py send "<message>"`.
   - Confirm transmission directly in chat.

3. **`/link summon <task>` or `/link ai <task>`**:
   - Dispatch the task to the peer AI agent (or both) using `link_summon` or `python3 agy_link.py summon "<task>" --target both`.
   - Wait for the remote report to arrive, and present the formatted report directly in chat.

4. **`/link peer <task>` (or `/link senpai <task>`)**:
   - Dispatch task directly to remote peer machine via `python3 agy_link.py summon "<task>" --target peer`.
   - Wait for the remote peer AI report and display it in this conversation.

5. **`/link local <task>` (or `/link reaper <task>`)**:
   - Execute task on local station via `python3 agy_link.py summon "<task>" --target local`.
   - Report the result in this conversation.

6. **`/link inbox`**:
   - Read the latest messages from `INBOX.md` using `link_inbox` or `python3 agy_link.py inbox`.
   - Render the unread/recent messages directly in chat.

7. **`/link sync --task "<Task>" [--files "<Files>"]`**:
   - Broadcast task progress and lock files using `link_sync` or `python3 agy_link.py sync`.
   - Confirm lock status in chat.

8. **`/link pair`**:
   - Generate and display room pairing credentials and passkey via `python3 agy_link.py pair`.

9. **`/link join --room <ROOM_ID> --key <SECRET_KEY>`**:
   - Connect to a peer session room and test handshake via `python3 agy_link.py join`.

10. **`/link role [lead|platform_lead|contributor|tester]`**:
    - Inspect or set local hierarchy role via `python3 agy_link.py role`.

11. **`/link security [prompt|session_trusted|autonomous|deny]`**:
    - Inspect or configure the Human-in-the-Loop (HITL) security approval gate via `python3 agy_link.py security`.
