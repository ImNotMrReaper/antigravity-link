# Antigravity Link (AGY-Link) Protocol Specification
## Cross-Machine Peer AI Collaboration Standard (v1.0.0)

---

## 🎯 Architectural Mission
`Antigravity Link` is a zero-dependency, cross-platform protocol designed to connect two independent **Antigravity (AGY)** AI assistants running on remote computers across the internet:
* **Linux Lead Assistant:** Pair-programming with `@Mr-Reaper` (Ubuntu 24.04 LTS / Wayland)
* **Windows Lead Assistant:** Pair-programming with `@Senpai59` (Windows 10/11)

While both human users converse with their respective AI assistants, the two AGYs operate in **Tandem Sync Mode** in the background:
1. Sharing active context (current files, active branch, active task).
2. Preventing conflicts ("stepping on each other's toes").
3. Handing off tasks (e.g., Linux AI drafts core architecture ➜ Windows AI tests on WinMM/DirectInput hardware).
4. Exchanging real-time test logs, code diffs, and review decisions.

---

## 📡 Transport Layer Architecture

### 1. Cloud Relay Mode (Default & Zero-Config)
* **Backend:** Secure, free, unauthenticated HTTPS pub/sub streaming (`https://ntfy.sh`).
* **Firewall Traversal:** 100% outbound HTTPS (Port 443). Bypasses NAT, CGNAT, router firewalls, and dynamic residential IPs. Requires **zero port forwarding**.
* **Channel Architecture:**
  - Shared Room Secret: `agy_link_mrreaper_senpai_8829` (configurable via `config.json`).
  - Directional Sub-channels:
    * Channel 1: `<room>_mr-reaper_to_senpai`
    * Channel 2: `<room>_senpai_to_mr-reaper`
* **Durability & Catch-Up:**
  - When starting up, the client queries `?poll=1` to catch up on any messages sent in the last 12 hours while offline.
  - Then it opens a continuous streaming connection (`/json`) with unique event ID deduplication (`seen_ids`).

### 2. Direct IP Socket Mode (Optional LAN / Tailscale)
* Direct raw TCP socket on configurable port (default: `9988`).
* Suitable for local Wi-Fi pairing or Tailscale encrypted mesh networks (`100.x.y.z`).

---

## 📦 Message Schema (JSON)

Every payload transmitted over the link MUST be valid JSON:

```json
{
  "protocol": "agy-link/1.0",
  "id": "uuid-or-timestamp-hash",
  "sender": "Senpai (Lead Tester)",
  "recipient": "Mr-Reaper (Lead Architect)",
  "role": "windows_lead",
  "type": "progress_update",
  "topic": "WinMM 16-button descriptor fix",
  "timestamp": "2026-09-05 16:15:00",
  "context": {
    "project": "joycon-mouse",
    "branch": "windows",
    "file": "joycon-mouse-windows.py",
    "task": "Testing SL/SR button triggers"
  },
  "content": "Fixed button mask bitshift for SL/SR on Joy-Con R. Raw scancode 0x0020 mapped to right click.",
  "patch": "diff --git a/joycon-mouse-windows.py ...",
  "log": "[WinMM Polling Data...]"
}
```

### Supported Message Types:
| Type | Description |
| :--- | :--- |
| `sync_state` | Broadcasts what the local AI and human are currently doing to prevent overlap. |
| `task_handoff` | Hands off a task to the other AI (e.g. Linux AI hands off Windows testing). |
| `progress_update`| Reports progress, code changes, or milestones completed. |
| `test_report` | Sends hardware test results (PASS/FAIL/BLOCKED) with attached logs. |
| `code_diff` | Proposes a patch or candidate code block for peer AI review. |
| `query` | Asks the peer AI a question or requests advice/clarification. |
| `chat` | Conversational message between humans or AIs. |

---

## 💾 Local AI Integration Standard

When an incoming message is received by the background daemon:
1. **Append to `INBOX.md`:** Formatted as readable GitHub-flavored Markdown.
2. **Overwrite `LATEST.json`:** Contains the raw JSON of the most recent message.
3. **OS Desktop Notification:**
   - **Linux:** Emits via `notify-send -a "Antigravity Link" "<Sender>" "<Message>"`.
   - **Windows:** Emits via native PowerShell / Win32 balloon or toast notification.
4. **Agent Awareness Hook:**
   - Before starting a coding turn, each AGY checks `INBOX.md`.
   - If the peer AI has posted an update or handoff, the agent incorporates it into its immediate context.
   - After completing a task or making file edits, the AGY runs:
     `python agy_link.py send "Completed task X" --topic "..." --type "progress_update"`

---

## 🛡️ Zero-Trust Security Architecture (v1.1.0)

To allow peer prompting while preventing unauthorized remote control or "cross-machine hacking", the protocol enforces three security layers:

### 1. Human-in-the-Loop (HITL) Interactive Approval Gate
* Any peer-summoned task requiring local execution is intercepted before invoking the agent.
* **Windows Station:** Prompts the machine owner via native PowerShell GUI dialog:
  `[Antigravity Link Security Gate] Peer {user} requested task: "{prompt}". Allow execution on your PC? [Yes / No]`
* **Linux Station:** Prompts via native Zenity dialog (or interactive TTY prompt).
* If rejected or timed out (60s), the task is safely denied and an error report is returned to the caller.

### 2. Cryptographic HMAC-SHA256 Packet Signing
* All packets are hashed and signed using a shared secret key:
  $$\text{HMAC-SHA256}(\text{key}, \text{canonical\_payload})$$
* Unauthenticated or spoofed packets are automatically dropped by the listener.

### 3. Execution Permission Sandboxing
* Remote peer summons do not run with `--dangerously-skip-permissions` unless the local machine owner explicitly sets `"allow_unrestricted_remote": true`.

---

## 👑 Role-Based Collaboration & Branch Ownership

To support multi-user pair programming without collisions:
* **Project Lead (`lead`):** Holds the master repository branch (`main`). Possesses ultimate architectural authority over merges, release tags, and project standards.
* **Platform Lead (`platform_lead`):** Direct owner of platform-specific branch (e.g. `windows` branch for Senpai59). Autonomously manages platform testing, builds native executables (`.exe`, `.bat`), and submits proposed diffs/PRs to the Project Lead.
* **Contributors & Testers:** Validate hardware, run benchmarks, and submit test reports without write permissions on protected branches.
