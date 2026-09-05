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
