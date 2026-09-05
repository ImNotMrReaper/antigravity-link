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
| **Send Agent Message** | `python3 agy_link.py send "..." --agent` | `python agy_link.py send "..." --agent` |
| **View Peer Inbox** | `python3 agy_link.py inbox` | `python agy_link.py inbox` |
