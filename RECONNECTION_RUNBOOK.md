# 🔄 Antigravity Link: Handover & Reconnection Runbook

This guide contains everything you and Senpai need to maintain, reconnect, or cleanly reinstall **Antigravity Link** from scratch without friction.

---

## 🔑 Master Pairing Credentials

Both machines use these cryptographic session tokens to authenticate and link over the zero-port-forwarding Cloud Relay:

| Parameter | Configuration Value | Description |
| :--- | :--- | :--- |
| **Room ID** | `agy_link_mrreaper_senpai_8829` | Directional isolation topic on ntfy.sh relay |
| **Session Secret Key** | `agy_secret_8829_tandem_key` | Used for HMAC-SHA256 wire packet signing |
| **Auth Token** | `agy_token_8829` | Static authentication header check |
| **Local Port** | `7890` | Direct TCP socket fallback (on local LAN) |
| **Web Dashboard** | `http://127.0.0.1:7891` | PyCharm embedded browser monitoring |

> [!IMPORTANT]
> These credentials are permanently saved in `.agy_link/config.json` on both machines.

---

## 🚀 Scenario 1: Zero-Touch Reconnection (When Senpai Gets Home)

If neither of you uninstalled the repository:
1. When Senpai returns home, he simply sits down at his PC, opens **PyCharm**, and launches Antigravity (`agy`).
2. The MCP server automatically starts the background listener and reconnects to the room silently.
3. In his AGY prompt, Senpai can confirm connection by typing:
   ```text
   /link status
   ```
4. Senpai can send a hello directly to your terminal:
   ```text
   /link send Hey Reaper, I'm back from work!
   ```

---

## 🧼 Scenario 2: 100% Clean Fresh Reinstall (Scorched-Earth)

If either of you deletes the folder and wants to re-add everything fresh from GitHub:

### 🐧 For Mr-Reaper (Ubuntu Linux Lead)

```bash
# 1. Remove old plugin registration
agy plugin uninstall antigravity-link 2>/dev/null || true
rm -rf ~/.gemini/config/plugins/antigravity-link

# 2. Delete and re-clone repository fresh from GitHub
cd ~/PycharmProjects
rm -rf antigravity-link
git clone https://github.com/ImNotMrReaper/antigravity-link.git
cd antigravity-link

# 3. Create canonical global plugin symlink
ln -sfn ~/PycharmProjects/antigravity-link ~/.gemini/config/plugins/antigravity-link

# 4. Join room with 1 command (automatically configures credentials and sends handshake)
python3 agy_link.py join --room "agy_link_mrreaper_senpai_8829" --key "agy_secret_8829_tandem_key" --peer "Senpai59"
python3 agy_link.py role linux-lead

# 5. Validate plugin
agy plugin validate .
```

---

### 🪟 For Senpai59 (Windows 11 Platform Lead)

When Senpai returns to his Windows PC:

1. Open PowerShell:
```powershell
# 1. Remove old installation
cd C:\Users\angel
Remove-Item -Recurse -Force antigravity-link

# 2. Clone fresh from GitHub
git clone https://github.com/ImNotMrReaper/antigravity-link.git
cd antigravity-link

# 3. Join room with 1 command (automatically configures credentials and sends handshake)
python agy_link.py join --room "agy_link_mrreaper_senpai_8829" --key "agy_secret_8829_tandem_key" --peer "Mr-Reaper"
python agy_link.py role windows-lead

# 4. Link plugin globally in Antigravity
New-Item -ItemType SymbolicLink -Path "$HOME\.gemini\config\plugins\antigravity-link" -Target "C:\Users\angel\antigravity-link" -Force
```

2. Open PyCharm, launch Antigravity (`agy`), and type:
```text
/link status
```

---

## 📋 Reconnection Verification Checklist

Run these quick checks inside your PyCharm terminal chat to verify complete operational readiness:

1. **Check Node Matrix:**
   ```text
   /link status
   ```
   *Expected Output:* `Cloud Relay: 🟢 READY`, `Peer Node: Senpai59`, status `Online`.

2. **Send Direct Chat:**
   ```text
   /link send Testing fresh install reconnection!
   ```

3. **Check Tandem Summoning:**
   ```text
   /peer Run git status on Windows and report back
   ```

4. **Launch PyCharm Embedded Web Dashboard:**
   ```text
   /link gui
   ```
   *View in PyCharm:* `View` -> `Tool Windows` -> `Web Browser` -> `http://127.0.0.1:7891`.
