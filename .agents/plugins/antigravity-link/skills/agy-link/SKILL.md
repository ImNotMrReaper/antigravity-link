---
name: agy-link
description: Cross-platform peer AI tandem synchronization, state sharing, file locking, and autonomous task summoning between Mr-Reaper (Ubuntu Linux) and Senpai59 (Windows 11) exclusively inside AGY TUI.
---

# Antigravity Link Peer AI Skill

Use this skill when collaborating with the remote peer station (@Senpai59 on Windows 11 or @Mr-Reaper on Ubuntu Linux).

> [!IMPORTANT]
> **STRICT TUI RULE**: All peer coordination, chatting, and task execution must occur **exclusively inside the AGY TUI session**. Do NOT spawn external terminal windows (e.g. Terminator, cmd.exe, wt.exe). Everything is displayed directly in markdown in this conversation.

---

## ⚡ Native AGY Slash Commands (TUI Mode)

Use these commands directly in the AGY chat input:

| Slash Command | What it Does |
| :--- | :--- |
| **`/link status`** | Displays live link connectivity (Direct Socket & Cloud Relay) and active file locks. |
| **`/link send <message>`** | Sends a direct chat message or technical note to the peer station. |
| **`/link summon <task>`** | Summons both AI agents to autonomously execute a task and report back. |
| **`/senpai <task or message>`** | Directly communicates with or delegates a task to Senpai's Windows 11 station. |
| **`/inbox`** | Displays recent peer messages, task handoffs, and AI execution reports from `INBOX.md`. |
| **`/link sync --task "<name>"`** | Broadcasts active task progress and locks files to prevent overlapping edits. |

---

## 🛠️ Model Context Protocol (MCP) Tools

When writing code or orchestrating tasks, the agent can call these tools directly:

* **`link_status`**: Queries connection health and active locks.
* **`link_summon`**: Summons peer AI with arguments `prompt` and `target` (`both`, `senpai`, `reaper`).
* **`link_send`**: Dispatches a text message to the peer.
* **`link_sync`**: Broadcasts progression milestones and locks files.
* **`link_inbox`**: Fetches the latest peer communication from `INBOX.md`.

---

## 🔒 Conflict Prevention & Lock Etiquette

1. Before starting a feature or editing shared files, check status:
   ```bash
   python3 agy_link.py status
   ```
2. If files are marked as locked by the peer station, coordinate with the peer agent before modifying them.
3. When starting work, broadcast locks:
   ```bash
   python3 agy_link.py sync --task "Feature X" --status "in-progress" --files "file1.py,file2.py"
   ```
4. When finished, broadcast completion:
   ```bash
   python3 agy_link.py sync --task "Feature X" --status "completed"
   ```

---

## 🛡️ Human-in-the-Loop (HITL) Security Approval Gate
- Protects against unauthorized remote code execution (RCE).
- When a peer AI asks to execute an autonomous task on your machine, a native GUI confirmation dialog prompts the machine owner (`[Yes / No]`).
- Configure security mode:
  ```bash
  python3 agy_link.py security prompt          # (Default) Explicit approval required
  python3 agy_link.py security session_trusted # Temporarily trust peer for active session
  python3 agy_link.py security deny            # Auto-deny all remote execution
  ```

---

## 👑 Role-Based Collaboration Hierarchy
- **Project Lead (`lead`):** Holds overall architectural authority and default branch (`main`).
- **Platform Lead (`platform_lead`):** Owns platform-specific branch (e.g. `windows`) and native builds.
- **Contributor / Tester:** Validates hardware and submits candidate diffs/PRs to the lead.
- Set role:
  ```bash
  python3 agy_link.py role lead
  python3 agy_link.py role platform_lead
  ```

---

## 🔗 Session Room Pairing & Secret Keys
- View credentials:
  ```bash
  python3 agy_link.py pair
  ```
- Join a collaborator's room:
  ```bash
  python3 agy_link.py join --room <ROOM_ID> --key <SECRET_KEY> --peer <PEER_NAME>
  ```
- All packets are cryptographically signed with HMAC-SHA256 to ensure authenticity.
