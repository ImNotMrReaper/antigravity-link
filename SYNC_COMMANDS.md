# Antigravity Link Cheatsheet (Linux & Windows)

---

## 🚀 Quick Setup & Connection

### Network Architecture:
- **Direct TCP Socket:** Port `7890` (Used when both machines are on the same Wi-Fi or connected via Tailscale mesh VPN).
- **Hybrid Cloud Relay:** Automatically active fallback using encrypted HTTPS via `ntfy.sh`. Bypasses home router firewalls, NAT, and CGNAT with zero port forwarding.

---

## 🛠️ Essential Commands

| Action | Linux Command (@Mr-Reaper) | Windows Command (@Senpai59) |
| :--- | :--- | :--- |
| **Check Peer Status** | `python3 agy_link.py status` | `python agy_link.py status` |
| **Start Background Daemon** | `./run_link_linux.sh` | Double-click `run_link_windows.bat` (Option 3) |
| **Interactive Terminal Chat** | `python3 agy_link.py chat` | `python agy_link.py chat` (Option 1) |
| **Broadcast Active Task** | `python3 agy_link.py sync --task "..."` | `python agy_link.py sync --task "..."` |
| **Delegate Task to Other OS** | `python3 agy_link.py delegate --title "..." --target-os windows` | `python agy_link.py delegate --title "..." --target-os linux` |
| **View Peer Inbox** | `python3 agy_link.py inbox` | `python agy_link.py inbox` |
| **Summon Both AI Agents** | `python3 agy_link.py summon "..." --target both` | `python agy_link.py summon "..." --target both` (Option 8) |
| **Summon Remote AI Only** | `python3 agy_link.py summon "..." --target remote` | `python agy_link.py summon "..." --target remote` |

---

## ⚡ Terminal Chat Summon Shortcuts (`python3 agy_link.py chat`)

| Tag | Behavior |
| :--- | :--- |
| `@ai <task>` or `@both <task>` | Wakes up **BOTH** Linux and Windows AIs to execute in parallel and report back |
| `@senpai-ai <task>` | Wakes up Senpai's **Windows AI** agent only to execute on Senpai's PC |
| `@reaper-ai <task>` | Wakes up Reaper's **Linux AI** agent only to execute on Reaper's PC |
| *(normal text)* | Clean human-to-human terminal chat with **zero AI noise** |
