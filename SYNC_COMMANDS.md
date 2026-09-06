# Antigravity Link Cheatsheet (Linux & Windows)

---

## 🚀 Quick Setup & Connection

### Network Architecture:
- **Direct TCP Socket:** Port `7890` (Used when both machines are on the same Wi-Fi or connected via Tailscale mesh VPN).
- **Hybrid Cloud Relay:** Automatically active fallback using encrypted HTTPS via `ntfy.sh`. Bypasses home router firewalls, NAT, and CGNAT with zero port forwarding.

---

## ⚡ Ultra-Simple Global Commands (`link`)
Run these from **ANY** terminal window without changing directories:

| Action | Quick Command (No Quotes Needed!) | What it Does |
| :--- | :--- | :--- |
| **Open Chat** | `link` or `link chat` | Launches two-way terminal chat with zero setup |
| **Summon Both AIs** | `link ai <task>` | Dispatches task to **both** peer AIs in parallel |
| **Summon Peer AI** | `link peer <task>` | Hands off task to remote peer AI exclusively (`link senpai` alias) |
| **Execute Local AI** | `link local <task>` | Executes task on local AI exclusively (`link reaper` alias) |
| **Send Message** | `link send <message>` | Sends direct chat alert to peer |
| **Check Peer Status** | `link status` | Displays live network state and active locks |
| **View Peer Inbox** | `link inbox` | Displays latest peer messages and AI reports |
| **Pull Updates** | `link pull` | Runs `git pull origin main` automatically |
| **Open Chat Window** | `link open` | Pops up chat in a new Terminator / Windows Terminal window |

---

## 🔔 Interactive Clickable Notifications
When you receive a chat message, task handoff, or AI report:
* **Linux:** Click the popup banner or select **"Open Chat"** to pop up Terminator with the live chat. Click **"View Inbox"** to open `INBOX.md`.
* **Windows:** Click the balloon notification to immediately pop up Windows Terminal or Command Prompt directly into the chat session!

---

## 🛠️ Full Verbose Syntax Reference

| Action | Linux Full Command | Windows Full Command |
| :--- | :--- | :--- |
| **Start Background Daemon** | `./run_link_linux.sh` | `run_link_windows.bat` (Option 3) |
| **Install Shortcuts & Protocol** | `~/.local/bin/link` | `powershell -File install_windows_shortcuts.ps1` (Option 9) |
| **Broadcast Active Task** | `link sync --task "..."` | `link sync --task "..."` |
| **Delegate Task to Other OS** | `link delegate --title "..."` | `link delegate --title "..."` |

---

## ⚡ Terminal Chat Summon Shortcuts (`python3 agy_link.py chat`)

| Tag | Behavior |
| :--- | :--- |
| `@ai <task>` or `@both <task>` | Wakes up **BOTH** Linux and Windows AIs to execute in parallel and report back |
| `@senpai-ai <task>` | Wakes up Senpai's **Windows AI** agent only to execute on Senpai's PC |
| `@reaper-ai <task>` | Wakes up Reaper's **Linux AI** agent only to execute on Reaper's PC |
| *(normal text)* | Clean human-to-human terminal chat with **zero AI noise** |

---

## 🧩 Antigravity (AGY) Plugin & MCP Integration
The repo includes a native AGY plugin located in `.agents/plugins/antigravity-link`. When installed, Antigravity has native tools and skills to interact with the link directly from inside your AGY coding sessions:

### Exposed MCP Tools (Pure Python stdio JSON-RPC):
- `link_status`: Check peer node connection and active file locks.
- `link_summon`: Summon peer AI (`prompt`, `target: both|senpai|reaper`).
- `link_send`: Send direct message to peer station.
- `link_sync`: Broadcast active task and lock files (`task`, `status`, `files`).
- `link_inbox`: Read recent messages and task handoffs from `INBOX.md`.

### Native AGY TUI Slash Commands:
No external terminals needed! Run these directly inside AGY chat:
- **`/link status`** — Check live link connection & file locks
- **`/link send <msg>`** — Send chat message to peer
- **`/link summon <task>`** — Summon both AIs to work and report back
- **`/senpai <task>`** — Delegate task or question to Senpai's Windows 11 station
- **`/inbox`** — View incoming peer messages & AI task reports
- **`/link sync --task "<name>"`** — Broadcast progress & lock files

### 1-Click Installation:
- **Linux:** Run `./install_linux_shortcuts.sh`
- **Windows:** Run `install_windows_shortcuts.ps1` (or Option `[9]` in `run_link_windows.bat`)
- **Validate:** Run `agy plugin validate ~/.gemini/config/plugins/antigravity-link`


