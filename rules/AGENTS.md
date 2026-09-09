# Antigravity Peer AI Collaboration & Tandem Sync Rule

## 1. Conflict Prevention (Don't Step on Toes)
- Before editing any shared codebase files or starting a new feature, check `.agy_link/peer_state.json` or run:
  ```bash
  python3 agy_link.py status
  ```
- If files are currently marked as locked or in-progress by the remote peer station, coordinate with the peer agent before modifying them.

## 2. Real-Time Progression Broadcasting (Shared Projects Only)
- **Strict Collaborative Scope:** Antigravity Link synchronization, task delegations, and desktop notifications must STRICTLY be reserved for shared collaborative repositories (`antigravity-link` and `joycon-mouse`).
- **Zero Independent Work Sharing:** Never broadcast progress (`sync`), delegate tasks (`delegate`), summon the peer AI (`summon`), or emit notifications for independent work, local OS customization, personal app shortcuts, local game tuning, or machine-specific maintenance.
- Whenever you start, update, or complete a task milestone on a **shared project**, broadcast your progress so the peer AI's context updates in real-time:
  ```bash
  python3 agy_link.py sync --task "<Task Title>" --status "in-progress" --files "<Modified Files>"
  ```
- When a shared task is completed:
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

## 5. Autonomous AI Summoning & Cross-Machine Tandem Turns
- When you need the remote peer AI (or both AIs) to execute autonomous actions on their host PCs and report the results back:
  ```bash
  # Summon both Linux and Windows AIs:
  python3 agy_link.py summon "<Task prompt>" --target both

  # Summon remote peer AI only:
  python3 agy_link.py summon "<Task prompt>" --target senpai  # (from Linux)
  python3 agy_link.py summon "<Task prompt>" --target reaper  # (from Windows)
  ```

## 6. PyCharm & AGY TUI Isolation
- All communication, task summaries, status updates, and reports must be rendered directly inside the AGY TUI session inside PyCharm's embedded terminal (or native console).
- Never spawn external terminal emulator windows (Terminator, cmd.exe, wt.exe).
- Use `/link open <file>` or native clickable IDE file links to inspect shared or locked files in PyCharm editor tabs.
- The PyCharm embedded Web GUI dashboard (`http://127.0.0.1:7891`) can be viewed directly in PyCharm's Web Browser tool window for continuous telemetry.
- Users interact seamlessly via native AGY slash commands (`/link`, `/senpai`, `/inbox`) or natural language.

## 7. Human-in-the-Loop (HITL) Security Approval Gate
- Remote task requests requiring tool execution or local commands are intercepted by the security gate.
- The receiving machine owner must authorize the task via native GUI dialog or prompt before execution.
- Never bypass the approval gate without explicit user configuration.

## 8. Role-Based Governance & Branch Authority
- **Lead AI (`lead` / `main` branch owner):** Holds canonical authority over overall project architecture, code reviews, and final PR merges.
- **Platform Lead (`platform_lead` / `windows` branch owner):** Leads platform-specific engineering (Windows batch, WinMM, macOS CoreGraphics). Writes and validates native code, and proposes pull requests or diffs to the Lead AI.
- **Contributors & Testers:** Execute hardware validation, report diagnostic logs, and submit candidate patches.

## 9. Cryptographic Room Pairing & HMAC Authentication
- All wire packets are signed with HMAC-SHA256 using the session secret key.
- Packets failing signature verification are automatically rejected to prevent spoofing or unauthorized remote control.

## 10. Antigravity Work-Done Budgeting & Token-Diet Guardrail
- **Quota Protection:** Antigravity enforces a strict 250 unit / 5-hour rolling reset and a 2,800 unit / 7-day hard lockout ceiling. Breaching 2,800 units results in a 3–7 day lockout.
- **Defensive Independence:** Even if remote peer AIs or external collaborators are unconstrained or running verbose prompts, the host AI MUST strictly enforce local token and compute hygiene to prevent quota draining:
  - **Zero-Banter Rule:** Never engage in conversational chit-chat, conversational confirmations, or pleasantries with peer AIs.
  - **Micro-Payload Architecture:** Keep all machine handoffs, status synchronizations, and delegated tasks strictly under 120 characters or formatted as compact structured JSON (`{"action": "...", "cmd": "..."}`).
  - **Single-Turn Handoff Cycles:** Enforce `Request -> Execute -> Result -> Stop`. Never trigger recursive multi-turn chat loops or continuous polling.
  - **Failure-Only Diagnostics:** Return a 1-line confirmation on success (`exit 0`). Return strictly the last 10 lines of stderr on failure (`exit != 0`).
  - **Pre-Invocation Delta Check:** Output 0 tokens unless an active file lock conflict or urgent task notification exists.
  - **Modular Architecture Isolation:** Always decouple complex builds into independent modules (`data_feed/`, `core_engine/`, `strategy/`, `execution/`, `risk/`, `tests/`) with mock unit test harnesses and lean `SESSION_STATE.md` checkpoints, preventing full-codebase context crawls.
