---
name: agy-link
description: Operates the Antigravity Link cross-platform peer synchronization and task delegation tool. Use when checking remote peer status, broadcasting state syncs, delegating tasks between Linux and Windows, or sending agent messages.
---

# Antigravity Link Peer AI Skill

Use this skill when collaborating with the remote peer station (@Senpai59 on Windows 11 or @Mr-Reaper on Ubuntu Linux).

## Primary Commands

### 1. Check Status & Peer State
```bash
python3 agy_link.py status
```

### 2. Broadcast State Sync
```bash
python3 agy_link.py sync --task "<Task Name>" --status "in-progress|completed" --files "<file1,file2>"
```

### 3. Delegate Task to Peer OS
```bash
python3 agy_link.py delegate --title "<Title>" --description "<Instructions>" --target-os "windows|linux" --priority "high"
```

### 4. Send Direct Agent Message
```bash
python3 agy_link.py send "<Message>" --agent
```

### 5. Inspect Inbox
```bash
python3 agy_link.py inbox
```
