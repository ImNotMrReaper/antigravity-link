# Antigravity Link (AGY-Link) 🤖⚡🤖
> Zero-dependency peer-to-peer collaboration protocol connecting remote Antigravity (AGY) AI assistants across Linux and Windows.

---

## 🌟 Overview
`antigravity-link` enables two AI assistants running on different machines across the internet to communicate, work in tandem, exchange test logs and code diffs, and prevent conflicting edits ("stepping on each other's toes") while their human operators pair-program.

* **Linux Node:** @Mr-Reaper (Ubuntu 24.04 LTS / Wayland)
* **Windows Node:** @Senpai59 (Windows 10/11)
* **Transport:** Zero-config encrypted HTTPS cloud relay via `ntfy.sh` (or direct TCP sockets).
* **Dependencies:** Pure Python 3 Standard Library (Zero pip installs).

---

## 🚀 Quick Start

### On Linux (@Mr-Reaper):
```bash
# 1. Start the listener daemon in the background:
./run_link_linux.sh

# 2. Or open interactive live terminal chat with Senpai:
./run_link_linux.sh chat

# 3. Send a message or update directly to Senpai's AI:
python3 agy_link.py send "Linux architecture updated. Ready for Windows testing." --topic "Architecture"
```

### On Windows (@Senpai59):
```bat
# 1. Start listener:
python agy_link.py --user Senpai --peer Mr-Reaper listen

# 2. Send progress update to Mr-Reaper's AI:
python agy_link.py --user Senpai --peer Mr-Reaper send "Windows joystick polling verified at 2ms" --topic "Testing"
```

---

## 📖 Architecture & Standards
For message schemas, event hooks, and AI sync rules, see [`PROTOCOL.md`](./PROTOCOL.md).  
For Senpai's AI onboarding prompt, see [`SENPAI_AGY_PROMPT.md`](./SENPAI_AGY_PROMPT.md).
