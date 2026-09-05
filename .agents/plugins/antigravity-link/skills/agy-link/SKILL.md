---
name: agy-link
description: Cross-platform peer AI tandem synchronization, state sharing, file locking, and autonomous task summoning between Mr-Reaper (Ubuntu Linux) and Senpai59 (Windows 11).
---

# Antigravity Link Peer AI Skill

Use this skill when collaborating with the remote peer station (@Senpai59 on Windows 11 or @Mr-Reaper on Ubuntu Linux).

## Primary Commands

### 1. Global Fast Commands (From Anywhere)
```bash
# Check link status & active locks:
link status

# Summon both AIs:
link ai <task prompt>

# Summon remote peer AI:
link senpai <task prompt>  # (on Linux)
link reaper <task prompt>  # (on Windows)

# View recent messages & task reports:
link inbox

# Send quick message:
link send <message>

# Open two-way chat terminal:
link chat
```

### 2. Conflict Prevention (Locking Files)
```bash
python agy_link.py sync --task "<Task Name>" --status "in-progress|completed" --files "<file1,file2>"
```

### 3. Task Delegation
```bash
python agy_link.py delegate --title "<Title>" --description "<Instructions>" --target-os "windows|linux" --priority "high"
```
