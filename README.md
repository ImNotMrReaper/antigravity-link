# Antigravity Link (`antigravity-link`) 🤖⚡🤖

> **The Official Peer AI Collaboration & Tandem Sync Plugin for Google Antigravity (AGY).**  
> Connects remote Antigravity AI agents across Linux and Windows for live pair-programming, tandem vibecoding, cryptographic conflict prevention, and autonomous cross-machine task execution.

[![CI](https://github.com/ImNotMrReaper/antigravity-link/actions/workflows/ci.yml/badge.svg)](https://github.com/ImNotMrReaper/antigravity-link/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform: Linux%20|%20Windows](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-brightgreen.svg)]()
[![Zero-Pip: 100% StdLib](https://img.shields.io/badge/Dependencies-Zero%20Pip%20(StdLib)-success.svg)]()

---

## 🌟 What is Antigravity Link?

When two developers pair-program on separate machines across the internet, their respective AI coding assistants typically have zero awareness of each other. This leads to:
* **Overwritten Code:** Both AIs editing the same file simultaneously, causing massive git merge conflicts.
* **Platform Blindspots:** A Linux AI cannot compile WinMM/DirectInput or test Windows batch scripts; a Windows AI cannot test systemd or evdev drivers.
* **Context Fragmentation:** Manual copy-pasting of test logs, terminal outputs, and system specs between team members.

**Antigravity Link solves this completely.** It plugs directly into Antigravity (AGY CLI, Antigravity IDE, PyCharm, VS Code) as a native customization plugin, creating an encrypted background bridge where both AI agents work in tandem.

```
+------------------------------------+             +------------------------------------+
|       Lead Node (Linux / macOS)    |             |      Contributor Node (Windows)    |
|   Ubuntu 24.04 LTS / Unix          |             |         Windows 10 / 11 Native     |
|                                    |             |                                    |
|   +----------------------------+   |             |   +----------------------------+   |
|   |    Antigravity AGY TUI     |   |             |   |    Antigravity AGY TUI     |   |
|   |   /link, /peer, /inbox     |   |             |   |   /link, /peer, /inbox     |   |
|   +--------------+-------------+   |             |   +--------------+-------------+   |
|                  |                 |             |                  |                 |
|   +--------------v-------------+   |             |   +--------------v-------------+   |
|   |     PreInvocation Hook     |   |             |   |     PreInvocation Hook     |   |
|   |   PreToolUse Conflict Gate |   |             |   |   PreToolUse Conflict Gate |   |
|   +--------------+-------------+   |   Cloud     |   +--------------+-------------+   |
|                  |                 |   Relay     |                  |                 |
|   +--------------v-------------+   |  HTTPS/443  |   +--------------v-------------+   |
|   |    agy_link.py Companion   |<===================>|    agy_link.py Companion   |   |
|   |    HMAC-SHA256 Signed      |   (ntfy.sh /    |   |    HMAC-SHA256 Signed      |   |
|   +----------------------------+   |    TCP)     |   +----------------------------+   |
+------------------------------------+             +------------------------------------+
```

---

## ⚡ Key Capabilities

1. **Strict AGY TUI Isolation:** All peer interactions, task summaries, status updates, and reports render directly inside your existing AGY terminal session. Zero external terminal popups.
2. **Cryptographic Conflict Prevention:** When one AI is working on a file, it broadcasts an active lock. If the other AI attempts to modify that file, the plugin's `PreToolUse` hook intercepts the action and requires owner confirmation.
3. **Autonomous Task Summoning (`@ai`):** Dispatch tasks to the remote peer AI on demand. The remote AI executes the prompt locally, collects the logs/diffs, and delivers a structured report back to your session.
4. **Human-in-the-Loop (HITL) Security Gate:** Incoming remote task summons trigger a native OS modal dialog (`zenity` on Linux, `MessageBox` on Windows) before executing, preventing unauthorized remote code execution.
5. **HMAC-SHA256 Packet Integrity:** Every message, diff, and state update is cryptographically signed using a shared room key. Spoofed or tampered packets are automatically dropped.
6. **Zero-Pip Axiom:** 100% Python Standard Library (`ctypes`, `hmac`, `hashlib`, `urllib`, `socket`). No `pip install`, no virtualenv activation, zero bloat.

---

## 🚀 1-Liner Quick Installation

### Linux (Ubuntu / Debian / Arch / Fedora):
Run in your terminal:
```bash
curl -fsSL https://raw.githubusercontent.com/ImNotMrReaper/antigravity-link/main/install.sh | bash
```

### Windows (PowerShell):
Run in PowerShell:
```powershell
irm https://raw.githubusercontent.com/ImNotMrReaper/antigravity-link/main/install.ps1 | iex
```

*What the installer does automatically:*
- Clones repository to your local user directory.
- Adds `link` to your PATH (`~/.local/bin/link` on Linux, `link.cmd` in User PATH on Windows).
- Registers the official plugin into `~/.gemini/config/plugins/antigravity-link`.
- Configures global `plugins.json` and Model Context Protocol (MCP) server in `mcp_config.json`.
- Registers the `agy-link://` URL protocol handler.
- Runs `agy plugin validate` to confirm all components pass.

---

## 🧩 Official Plugin Components

The plugin conforms 100% to the Google Antigravity Plugin Specification:

| Component | Path | Description |
| :--- | :--- | :--- |
| **Skills** | `skills/agy-link/SKILL.md` | Provides the agent with full operating rules, delegation CLI commands, and synchronization runbooks. |
| **Agents** | `agents/senpai-ai.md` | Windows Lead subagent configuration for autonomous cross-machine handoffs. |
| **Commands** | `commands/link.md`<br>`commands/senpai.md`<br>`commands/inbox.md` | Native AGY slash commands (`/link`, `/senpai`, `/inbox`) directly inside the chat interface. |
| **MCP Server** | `mcp_server.py`<br>`mcp_config.json` | Exposes 5 stdio tools: `link_status`, `link_summon`, `link_send`, `link_sync`, `link_inbox`. |
| **Lifecycle Hooks** | `hooks.json`<br>`hooks/pre_invocation_sync.py`<br>`hooks/pre_tool_guard.py` | `PreInvocation` injects active peer locks into turn context; `PreToolUse` blocks concurrent writes to locked files. |

Verify anytime with:
```bash
agy plugin validate ~/.gemini/config/plugins/antigravity-link
```
Output:
```text
  [ok]    ~/.gemini/config/plugins/antigravity-link
          ✔ skills      : 1 processed
          ✔ agents      : 1 processed
          ✔ commands    : 3 processed (converted to skills)
          ✔ mcpServers  : 1 processed
          ✔ hooks       : 1 processed
```

---

## 🛠️ Global CLI Usage (`link`)

Once installed, use the single-word `link` command anywhere on your system:

```bash
# Open interactive terminal chat with your peer
link chat

# Summon BOTH Linux and Windows AIs to work on a task:
link ai "Verify cross-platform joystick descriptor mappings"

# Delegate a task exclusively to Senpai's Windows AI:
link senpai "Build and test the joycon-mouse Windows release package"

# Delegate a task exclusively to Reaper's Linux AI:
link reaper "Audit systemd uinput device permissions"

# View active peer locks, current tasks, and node status:
link status

# View inbox summary of all received updates and reports:
link inbox

# Set your project role in the collaboration hierarchy:
link role lead           # Project Architect (main branch authority)
link role platform_lead  # Platform Owner (e.g. windows branch)
link role contributor    # Feature developer
link role tester         # Quality assurance & hardware validation

# Configure Human-in-the-Loop security gate mode:
link security prompt            # (Default) GUI modal confirmation for every remote task
link security session_trusted   # Auto-approves tasks from paired peer for this session
link security deny              # Hard-rejects all incoming remote execution requests
```

---

## 🧪 Automated Test Suite

Antigravity Link includes a zero-dependency test suite running on Python's built-in `unittest` runner:

```bash
python -m unittest discover -s tests -v
```

### Coverage:
- `tests/test_protocol.py`: Wire packet structure, HMAC-SHA256 signature generation, validation, spoofing detection, and tamper detection.
- `tests/test_security.py`: Security gate decision tree (`prompt`, `autonomous`, `deny`), role hierarchies, and sandboxed execution boundaries.
- `tests/test_plugin_hooks.py`: `PreInvocation` lock injection and `PreToolUse` concurrent file-write prevention with Windows/Linux path normalization.

Every commit and pull request is automatically tested across Linux and Windows runners on Python 3.10, 3.11, 3.12, and 3.13 via GitHub Actions.

---

## 👥 Core Team & Governance

* **Project Lead & Linux Architect:** [@Mr-Reaper](https://github.com/ImNotMrReaper)  
  *Host System:* Dell Inspiron 16 5640 · Ubuntu 24.04 LTS (Noble Numbat) · GNOME 46 Wayland  
  *Authority:* Canonical architecture, `main` branch owner, Linux daemon engine, security framework.

* **Platform Lead & Windows Specialist:** [@Senpai59](https://github.com/Senpai59)  
  *Host System:* Custom PC · Windows 11 Home (Build 26200) · AMD Ryzen 5 3600  
  *Authority:* Windows engineering, `windows` branch owner, PowerShell installers, Win32/WinMM integration.

---

## 📄 License
Licensed under the [MIT License](./LICENSE). Free for open-source and commercial pair-programming.
