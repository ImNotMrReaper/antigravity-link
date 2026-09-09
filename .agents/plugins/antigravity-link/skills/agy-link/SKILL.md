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
| **`/peer <task or message>`** | Directly communicates with or delegates a task to the remote peer AI station. |
| **`/senpai <task or message>`** | Directly communicates with or delegates a task to Senpai's Windows 11 station. |
| **`/inbox`** | Displays recent peer messages, task handoffs, and AI execution reports from `INBOX.md`. |
| **`/link sync --task "<name>"`** | Broadcasts active task progress and locks files to prevent overlapping edits. |
| **`/link open <file>`** | Opens a file directly in PyCharm editor tabs at an optional line/column. |
| **`/link gui`** | Displays URL and instructions for the PyCharm embedded collaborative web GUI. |

---

## 🛠️ Model Context Protocol (MCP) Tools

When writing code or orchestrating tasks, the agent can call these tools directly:

* **`link_status`**: Queries connection health and active locks.
* **`link_summon`**: Summons peer AI with arguments `prompt` and `target` (`both`, `senpai`, `reaper`).
* **`link_send`**: Dispatches a text message to the peer.
* **`link_sync`**: Broadcasts progression milestones and locks files.
* **`link_inbox`**: Fetches the latest peer communication from `INBOX.md`.
* **`link_open`**: Opens a file in PyCharm editor tabs (`file`, optional `line`, `column`).
* **`link_gui`**: Retrieves PyCharm collaborative web dashboard URL (`http://127.0.0.1:7891`).


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

---

## 🛡️ Human-in-the-Loop (HITL) Security Approval Gate
- Protects against unauthorized remote code execution (RCE).
- When a peer AI asks to execute an autonomous task on your machine, a native GUI confirmation dialog prompts the machine owner (`[Yes / No]`).
- Configure security mode:
  ```bash
  python3 agy_link.py security prompt          # (Default) Explicit approval required
  python3 agy_link.py security session_trusted # Temporarily trust peer for active session
  python3 agy_link.py security deny            # Auto-deny all remote execution
  ```

---

## 👑 Role-Based Collaboration Hierarchy
- **Project Lead (`lead`):** Holds overall architectural authority and default branch (`main`).
- **Platform Lead (`platform_lead`):** Owns platform-specific branch (e.g. `windows`) and native builds.
- **Contributor / Tester:** Validates hardware and submits candidate diffs/PRs to the lead.
- Set role:
  ```bash
  python3 agy_link.py role lead
  python3 agy_link.py role platform_lead
  ```

---

## 🔗 Session Room Pairing & Secret Keys
- View credentials:
  ```bash
  python3 agy_link.py pair
  ```
- Join a collaborator's room:
  ```bash
  python3 agy_link.py join --room <ROOM_ID> --key <SECRET_KEY> --peer <PEER_NAME>
  ```
- All packets are cryptographically signed with HMAC-SHA256 to ensure authenticity.

---

## ⚖️ Work-Done Budgeting & Quota Protection Protocol

To protect against Antigravity compute exhaustion when collaborating with remote peer AIs or running tandem turns:

### 1. The Work-Done Metric & 7-Day Lockout Defense
* **Compute Units:** Antigravity usage is calculated on compute effort (Work Done): **250 units / 5 hours** rolling reset, coupled with a **2,800 units / 7-day hard ceiling**.
* **The 7-Day Lockout Trap:** If the 2,800 weekly cap is breached, your station is locked out for 3 to 7 days regardless of the 5-hour rolling timer.
* **Model Compute Multipliers:**
  * **Gemini Flash:** ~10x fewer units than Sonnet; up to 800x cheaper than Opus. Used for fast-mode planning, micro-tasks, and initial scaffolding.
  * **Sonnet (Fast Mode):** Balanced baseline for core systems engineering (40–80 hours active compute/week).
  * **Claude Opus:** 8x multiplier over Sonnet. Can exhaust your entire 7-day quota in ~3 hours. Strictly restricted to high-complexity architectural design.

### 2. Lean Token-Diet & Micro-Payload Architecture
To prevent swarm token drain and protect our station when interacting with remote peer agents:
1. **Delta-Only Pre-Invocation:** Output 0 tokens unless an active file lock or urgent conflict exists.
2. **Micro-Payload Formatting:** All peer machine handoffs and remote tasks must use compact structured JSON (`{"action":"...", "cmd":"..."}`) or concise summaries under 120 characters. Reject conversational pleasantries or natural language chatter between agents.
3. **Single-Round Task Handoff:** Follow strict single-turn cycles: `Request -> Execute -> Machine Result -> Terminate Turn`. Never allow autonomous conversational ping-pong loops.
4. **Failure-Only Diagnostics:**
   * On success (`exit 0`): Return a 1-line structured confirmation.
   * On failure (`exit != 0`): Truncate diagnostic output strictly to the last 10 lines of standard error.
5. **Tail-Inbox Fetching:** Read unconsumed message deltas (`peek=1`) rather than swallowing entire historical thread logs.

### 3. Modular Architecture Blueprint (Complex Multi-Agent Projects)
When building complex systems (e.g. trading bots, driver suites, daemon frameworks), decompose the project into decoupled modules before generating code:
```
project/
├── data_feed/          # Ingestion / async stream handlers
├── core_engine/        # Mathematical / model / logic processing
├── strategy/           # Decision / state evaluation rules
├── execution/          # Simulator / paper-trading router & live dispatch
├── risk/               # Drawdown guards, circuit breakers, hard limits
├── tests/              # Isolated unit test harnesses with mock fixtures
└── SESSION_STATE.md    # Lean state handoff preventing full-transcript crawls
```

### 4. State Handoff Engineering (`SESSION_STATE.md`)
* Maintain a compact markdown handoff file (`SESSION_STATE.md`) tracking active milestones, completed components, and next actionable steps.
* Always use strict file pinning (`@file` or exact paths) rather than scanning or crawling entire repositories, preserving our compute quota.
* Build all modules with mock fixtures (`pytest`, `unittest.mock`) to prevent recursive agent debugging loops.

