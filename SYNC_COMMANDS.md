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
| **Summon Both AIs** | `link ai <task>` | Dispatches task to **both** Linux & Windows AIs in parallel |
| **Summon Senpai's AI** | `link senpai <task>` | Hands off task to Senpai's Windows 11 AI exclusively |
| **Summon Reaper's AI** | `link reaper <task>` | Executes task on Reaper's local Linux AI exclusively |
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
