# Antigravity Peer AI Collaboration & Tandem Sync Rule

## 1. Conflict Prevention (Don't Step on Toes)
- Before editing any shared codebase files or starting a new feature, check `.agy_link/peer_state.json` or run:
  ```bash
  python3 agy_link.py status
  ```
- If files are currently marked as locked or in-progress by the remote peer station, coordinate with the peer agent before modifying them.

## 2. Real-Time Progression Broadcasting
- Whenever you start, update, or complete a task milestone, broadcast your progress so the peer AI's context updates in real-time:
  ```bash
  python3 agy_link.py sync --task "<Task Title>" --status "in-progress" --files "<Modified Files>"
  ```
- When a task is completed:
  ```bash
  python3 agy_link.py sync --task "<Task Title>" --status "completed" --files "<Modified Files>"
  ```

## 3. Cross-OS Task Delegation
- If a task requires validation on the other OS (e.g. Windows compiling/WinMM testing, or Linux systemd/evdev testing), delegate the task:
  ```bash
  python3 agy_link.py delegate --title "<Title>" --description "<Instructions>" --target-os windows|linux --priority high
  ```

## 4. Live Agent Communication
- Send direct notes, questions, or updates to the peer agent:
  ```bash
  python3 agy_link.py send "<Message text>" --agent
  ```
