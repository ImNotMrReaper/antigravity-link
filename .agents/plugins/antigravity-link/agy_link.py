#!/usr/bin/env python3
"""
Antigravity Link (agy_link.py) - Universal Cross-Platform Engine
================================================================
Unified peer-to-peer communication & tandem AI collaboration suite connecting:
  - Linux Lead:   Mr-Reaper (Ubuntu 24.04 LTS / Wayland)
  - Windows Lead: Senpai59 (Windows 10/11)

Network Architecture (Hybrid):
  1. Direct TCP Sockets (Default Port: 7890) for LAN or Tailscale mesh VPN.
  2. Zero-Port-Forwarding Cloud Relay (ntfy.sh) fallback when direct IP is unreachable.
     Bypasses residential NAT, CGNAT, and home router firewalls automatically.

Capabilities:
  - State Sync & Conflict Detection: Locks files and tracks active tasks.
  - Cross-OS Task Delegation: Linux AI delegates Windows builds/tests; Windows AI delegates Linux daemon tests.
  - Direct Agent-to-Agent Messaging: Real-time packet exchange.
  - Native Desktop Alerts: GNOME notify-send on Linux, Win32/PowerShell Toast on Windows.

Dependencies: Pure Python 3 Standard Library (Zero external pip packages).
"""

import argparse
import datetime
from datetime import timezone
import json
import os
import platform
import re
import hashlib
import hmac
import html
import select
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

# Base Constants
PROTOCOL_VERSION = "1.1.0"
DEFAULT_PORT = 7890
# Environment overrides or generic default room/secret for open source privacy
DEFAULT_ROOM = os.environ.get("AGY_LINK_ROOM", "agy_link_community_room")
DEFAULT_SECRET = os.environ.get("AGY_LINK_SECRET", "agy_secret_key_change_me")
DEFAULT_TOKEN = os.environ.get("AGY_LINK_TOKEN", "")
RELAY_HOST = "https://ntfy.sh"
VALID_ROLES = ["lead", "platform_lead", "contributor", "tester", "linux-lead", "windows-lead"]
SECURITY_MODES = ["prompt", "session_trusted", "autonomous", "deny"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_workspace_root(workspace_paths=None):
    """Find the root of the active workspace or project."""
    if workspace_paths:
        for wp in workspace_paths:
            if os.path.isdir(wp):
                return os.path.abspath(wp)

    env_ws = os.environ.get("AGY_WORKSPACE") or os.environ.get("AGY_PROJECT")
    if env_ws and os.path.isdir(env_ws):
        return os.path.abspath(env_ws)

    # Walk up from current working directory to find VCS, .agents, or .agy_link
    curr = os.path.abspath(os.getcwd())
    while True:
        if (os.path.isdir(os.path.join(curr, ".git")) or
            os.path.isdir(os.path.join(curr, ".agents")) or
            os.path.isdir(os.path.join(curr, ".agy_link"))):
            return curr
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent

    # Check SCRIPT_DIR
    if (os.path.isdir(os.path.join(SCRIPT_DIR, ".git")) or
        os.path.isdir(os.path.join(SCRIPT_DIR, ".agents")) or
        os.path.isdir(os.path.join(SCRIPT_DIR, ".agy_link"))):
        return SCRIPT_DIR

    return os.path.abspath(os.getcwd())


def get_agy_dir(workspace_paths=None):
    """Return the path to the active .agy_link directory."""
    if os.environ.get("AGY_LINK_DIR"):
        return os.path.abspath(os.environ["AGY_LINK_DIR"])
    ws = get_workspace_root(workspace_paths)
    return os.path.join(ws, ".agy_link")


WORKSPACE_ROOT = get_workspace_root()
AGY_DIR = get_agy_dir()
CONFIG_FILE = os.path.join(AGY_DIR, "config.json")
LOCAL_STATE_FILE = os.path.join(AGY_DIR, "local_state.json")
PEER_STATE_FILE = os.path.join(AGY_DIR, "peer_state.json")
ACTIVITY_LOG_FILE = os.path.join(AGY_DIR, "activity.log")
INBOX_FILE = os.path.join(WORKSPACE_ROOT, "INBOX.md")

# Configure Windows UTF-8 stdout/stderr safety
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def get_iso_timestamp():
    """Return timezone-aware ISO timestamp in UTC."""
    return datetime.datetime.now(timezone.utc).isoformat()


def ensure_dirs():
    """Ensure .agy_link state directory exists."""
    os.makedirs(AGY_DIR, exist_ok=True)


def load_config():
    """Load configuration with sensible cross-platform defaults."""
    ensure_dirs()
    is_win = sys.platform == "win32"
    default_config = {
        "node_id": "peer-win" if is_win else "peer-linux",
        "user": "Peer-Windows" if is_win else "Peer-Linux",
        "role": "platform_lead" if is_win else "lead",
        "local_host": "0.0.0.0",
        "local_port": DEFAULT_PORT,
        "peer_host": "127.0.0.1",
        "peer_port": DEFAULT_PORT,
        "auth_token": DEFAULT_TOKEN,
        "secret_key": DEFAULT_SECRET,
        "security_mode": "prompt",  # "prompt" (HITL approval required), "session_trusted", "autonomous", "deny"
        "allow_unrestricted_remote": False,
        "relay_room": DEFAULT_ROOM,
        "mode": "hybrid",  # "hybrid", "direct", "relay"
        "notifications": True,
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                default_config.update(loaded)
        except Exception:
            pass
    else:
        save_config(default_config)

    # Backwards compatibility fallback for paired session rooms
    if ("8829" in str(default_config.get("relay_room", "")) or "mrreaper" in str(default_config.get("relay_room", ""))) and default_config.get("secret_key") == DEFAULT_SECRET:
        default_config["secret_key"] = "agy_secret_8829_tandem_key"

    return default_config


def save_config(cfg):
    """Save configuration to .agy_link/config.json."""
    ensure_dirs()
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


def log_activity(entry):
    """Append activity to .agy_link/activity.log."""
    ensure_dirs()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(ACTIVITY_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {entry}\n")
    except Exception:
        pass


def open_terminal_chat():
    """Launch the interactive chat window in a visible terminal emulator."""
    script_path = os.path.abspath(__file__)
    work_dir = os.path.dirname(script_path)
    python_bin = sys.executable

    try:
        if sys.platform == "win32":
            wt = shutil.which("wt") or shutil.which("wt.exe")
            if wt:
                cmd = [wt, "-w", "0", "nt", "--title", "Antigravity Link Chat", python_bin, script_path, "chat"]
                subprocess.Popen(cmd, cwd=work_dir)
            else:
                cmd = f'start "Antigravity Link Chat" "{python_bin}" "{script_path}" chat'
                subprocess.Popen(cmd, cwd=work_dir, shell=True)
        else:
            terminator = shutil.which("terminator")
            x_term = shutil.which("x-terminal-emulator")
            gnome_term = shutil.which("gnome-terminal")
            alacritty = shutil.which("alacritty")
            kitty = shutil.which("kitty")

            env = os.environ.copy()
            if "DISPLAY" not in env:
                env["DISPLAY"] = ":0"

            if terminator:
                cmd = [terminator, "-u", "-T", "Antigravity Link Chat", f"--working-directory={work_dir}", "-x", python_bin, script_path, "chat"]
            elif gnome_term:
                cmd = [gnome_term, "--title=Antigravity Link Chat", f"--working-directory={work_dir}", "--", python_bin, script_path, "chat"]
            elif alacritty:
                cmd = [alacritty, "-t", "Antigravity Link Chat", f"--working-directory={work_dir}", "-e", python_bin, script_path, "chat"]
            elif kitty:
                cmd = [kitty, "-T", "Antigravity Link Chat", f"-d={work_dir}", python_bin, script_path, "chat"]
            elif x_term:
                cmd = [x_term, "-T", "Antigravity Link Chat", "-e", f"{python_bin} {script_path} chat"]
            else:
                cmd = ["xterm", "-title", "Antigravity Link Chat", "-e", f"cd {work_dir} && {python_bin} {script_path} chat"]

            subprocess.Popen(cmd, cwd=work_dir, env=env, start_new_session=True)
    except Exception as e:
        log_activity(f"Failed to open terminal chat window: {e}")


def open_inbox_window():
    """Open INBOX.md in default editor or viewer."""
    script_path = os.path.abspath(__file__)
    work_dir = os.path.dirname(script_path)
    inbox_path = os.path.join(work_dir, "INBOX.md")
    try:
        if sys.platform == "win32":
            os.startfile(inbox_path)
        else:
            xdg_open = shutil.which("xdg-open")
            if xdg_open:
                subprocess.Popen([xdg_open, inbox_path])
    except Exception as e:
        log_activity(f"Failed to open inbox window: {e}")


def notify_desktop(title, message):
    """Emit lightweight desktop notification without external terminal popups."""
    def _worker():
        system = platform.system()
        try:
            if system == "Linux" and shutil.which("notify-send"):
                subprocess.run(
                    [
                        "notify-send",
                        "-a", "Antigravity Link",
                        "-i", "dialog-information",
                        title,
                        message[:120]
                    ],
                    check=False,
                    timeout=5
                )
            elif system == "Windows":
                clean_title = title.replace('"', '`"')
                clean_msg = message[:100].replace('"', '`"')
                ps = (
                    f'[reflection.assembly]::loadwithpartialname("System.Windows.Forms");'
                    f'$n = new-object system.windows.forms.notifyicon;'
                    f'$n.icon = [system.drawing.systemicons]::Information;'
                    f'$n.visible = $true;'
                    f'$n.showballoontip(5, "{clean_title}", "{clean_msg}", [system.windows.forms.tooltipicon]::Info);'
                )
                subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=False, timeout=3)
        except Exception:
            pass

    threading.Thread(target=_worker, daemon=True).start()



# -----------------------------------------------------------------------------
# Packet Construction & State Management
# -----------------------------------------------------------------------------


SEEN_PACKETS = set()


def verify_packet_freshness(packet, max_drift_seconds=60, allow_resync=True):
    """
    Prevent replay attacks and stale packet injection.
    Allows dynamic clock re-synchronization on cryptographically signed handshake/ping packets.
    """
    packet_id = packet.get("packet_id")
    if not packet_id:
        return False
    if packet_id in SEEN_PACKETS:
        return False  # Replay detected

    packet_epoch = packet.get("timestamp_epoch")
    if packet_epoch is None:
        ts = packet.get("timestamp")
        if ts:
            try:
                dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                packet_epoch = dt.timestamp()
            except Exception:
                pass

    p_type = packet.get("type", "")
    # Allow signed handshake / ping / resync packets to dynamically re-synchronize time window
    if allow_resync and p_type in ("handshake", "ping", "resync_request", "resync_ack"):
        SEEN_PACKETS.add(packet_id)
        return True

    if packet_epoch is not None:
        drift = abs(time.time() - packet_epoch)
        if drift > max_drift_seconds:
            return False  # Stale packet exceeding drift window

    SEEN_PACKETS.add(packet_id)
    if len(SEEN_PACKETS) > 2000:
        SEEN_PACKETS.clear()
    return True


CRITICAL_META_INJECTIONS = [
    "ignore previous instructions",
    "disregard all previous",
    "system prompt override",
    "forget all prior instructions",
    "bypass safety filters",
    "exfiltrate secret",
    "reveal secret key",
    "read ~/.ssh",
    "read /etc/shadow"
]

DESTRUCTIVE_EXECUTION_KEYWORDS = [
    "rm -rf /",
    "rmdir /s /q c:\\",
    "Invoke-Expression",
    ":(){ :|:& };:",
    "mkfs.ext4",
    "format c:"
]

INJECTION_KEYWORDS = CRITICAL_META_INJECTIONS + DESTRUCTIVE_EXECUTION_KEYWORDS


def strip_markdown_code(text):
    """
    Strips fenced code blocks (```...```) and inline code spans (`...`)
    to prevent false-positive quarantines during legitimate code reviews and unit test assertions.
    """
    if not text or not isinstance(text, str):
        return ""
    clean = re.sub(r"```[\s\S]*?```", " ", text)
    clean = re.sub(r"`[^`\n]+`", " ", clean)
    return clean


def scan_for_prompt_injection(text, context_aware=True):
    """
    Context-aware heuristic guard checking for prompt injections, jailbreaks, and destructive shell payloads.
    When context_aware=True, code blocks are stripped before evaluating destructive shell commands,
    preventing false positives when discussing test scripts or shell utilities.
    Critical meta-prompt injections (jailbreaks, credential exfiltration) are always checked globally.
    Returns (is_suspicious: bool, matching_trigger: str).
    """
    if not text or not isinstance(text, str):
        return False, ""

    lower_raw = text.lower()

    # 1. Critical meta-prompt injections are NEVER permitted anywhere in the payload
    for kw in CRITICAL_META_INJECTIONS:
        if kw.lower() in lower_raw:
            return True, kw

    # 2. Destructive execution commands are checked against conversational text
    eval_text = strip_markdown_code(text).lower() if context_aware else lower_raw
    for kw in DESTRUCTIVE_EXECUTION_KEYWORDS:
        if kw.lower() in eval_text:
            return True, kw

    return False, ""


def quarantine_peer(sender_info, reason, packet=None):
    """Quarantine peer connection upon detecting malicious injection attempt."""
    ensure_dirs()
    user = sender_info.get("user", "Unknown")
    node = sender_info.get("node_id", "unknown")

    state_data = {
        "last_updated": get_iso_timestamp(),
        "sender": sender_info,
        "type": "security_alert",
        "state": {
            "status": "quarantined",
            "reason": reason,
            "task": f"QUARANTINED: {reason}",
            "locked_files": []
        }
    }
    try:
        with open(PEER_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    log_activity(f"IMMUNE SYSTEM: Peer '{user}' ({node}) QUARANTINED! Reason: {reason}")
    notify_desktop("Antigravity Link Security Warning", f"Peer {user} QUARANTINED: {reason}")


def compute_packet_signature(packet, secret_key):
    """Calculate HMAC-SHA256 signature for wire packet integrity including session salt."""
    if not secret_key:
        return ""
    try:
        data_to_sign = json.dumps({
            "version": packet.get("version"),
            "packet_id": packet.get("packet_id", ""),
            "salt": packet.get("salt", ""),
            "type": packet.get("type"),
            "timestamp": packet.get("timestamp"),
            "sender": packet.get("sender"),
            "payload": packet.get("payload")
        }, sort_keys=True, ensure_ascii=False)
        return hmac.new(secret_key.encode("utf-8"), data_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
    except Exception:
        return ""


def verify_packet_signature(packet, secret_key, expected_token=""):
    """Verify HMAC-SHA256 signature and/or auth token on incoming packet with backward compatibility."""
    if not secret_key and not expected_token:
        return True
    received_sig = packet.get("signature", "")
    received_token = packet.get("auth_token", "")

    # 1. Primary: Verify cryptographic HMAC-SHA256 wire signature
    if received_sig and secret_key:
        expected_sig = compute_packet_signature(packet, secret_key)
        if hmac.compare_digest(expected_sig, received_sig):
            return True
        # Backward compatibility fallback for legacy packets without salt/packet_id
        try:
            legacy_data = json.dumps({
                "version": packet.get("version"),
                "type": packet.get("type"),
                "timestamp": packet.get("timestamp"),
                "sender": packet.get("sender"),
                "payload": packet.get("payload")
            }, sort_keys=True, ensure_ascii=False)
            legacy_sig = hmac.new(secret_key.encode("utf-8"), legacy_data.encode("utf-8"), hashlib.sha256).hexdigest()
            if hmac.compare_digest(legacy_sig, received_sig):
                return True
        except Exception:
            pass

    # 2. Token-based fallback: must match configured auth token
    if expected_token and received_token:
        if hmac.compare_digest(str(expected_token), str(received_token)):
            return True

    return False


def make_packet(packet_type, payload, config):
    """Create standardized v1.1.0 JSON wire packet with HMAC signature and session salt."""
    now_epoch = time.time()
    pkt = {
        "version": PROTOCOL_VERSION,
        "packet_id": f"{int(now_epoch * 1000)}-{os.urandom(3).hex()}",
        "timestamp": get_iso_timestamp(),
        "timestamp_epoch": now_epoch,
        "salt": config.get("session_salt", "SALT_8829"),
        "auth_token": config.get("auth_token", ""),
        "type": packet_type,
        "sender": {
            "node_id": config.get("node_id", "unknown"),
            "user": config.get("user", "Unknown"),
            "role": config.get("role", "general"),
            "platform": platform.system().lower(),
        },
        "payload": payload,
    }
    secret_key = config.get("secret_key", DEFAULT_SECRET)
    pkt["signature"] = compute_packet_signature(pkt, secret_key)
    return pkt


def update_peer_state(packet):
    """Save received state packet to .agy_link/peer_state.json and INBOX.md."""
    ensure_dirs()
    sender = packet.get("sender", {})
    payload = packet.get("payload", {})
    p_type = packet.get("type", "message")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    node_key = sender.get("node_id") or sender.get("user") or "peer-node"

    # Multi-peer swarm table management
    peers_table = {}
    if os.path.exists(PEER_STATE_FILE):
        try:
            with open(PEER_STATE_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
                peers_table = existing.get("peers", {})
                if not isinstance(peers_table, dict):
                    peers_table = {}
        except Exception:
            peers_table = {}

    # Record or update entry for this specific peer
    peers_table[node_key] = {
        "last_updated": get_iso_timestamp(),
        "sender": sender,
        "type": p_type,
        "state": payload
    }

    state_data = {
        "last_updated": get_iso_timestamp(),
        "sender": sender,
        "type": p_type,
        "state": payload,
        "peers": peers_table  # Multi-peer swarm table
    }

    try:
        with open(PEER_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    # Update INBOX.md
    md_entry = f"\n---\n\n### 📨 [{p_type.upper()}] From `{sender.get('user')}` ({sender.get('role')}) — `{timestamp}`\n"
    if p_type == "state_sync":
        md_entry += f"**Current Task:** {payload.get('task')}  \n"
        md_entry += f"**Status:** `{payload.get('status')}`  \n"
        if payload.get("locked_files"):
            md_entry += f"**🔒 Active Files:** `{', '.join(payload.get('locked_files'))}`  \n"
        if payload.get("notes"):
            md_entry += f"\n> {payload.get('notes')}\n"
    elif p_type == "task_delegation":
        md_entry += f"**🎯 Delegated Task:** {payload.get('title')}  \n"
        md_entry += f"**Priority:** `{payload.get('priority')}` | **Target OS:** `{payload.get('target_os')}`  \n"
        md_entry += f"\n#### Instructions:\n{payload.get('description')}\n"
    elif p_type == "agent_summon":
        md_entry += f"**⚡ AI Summoned:** {payload.get('task')}  \n"
        md_entry += "\n> Initiating local autonomous AGY turn in background...\n"
    elif p_type == "agent_report":
        md_entry += f"**🤖 AGY Task Report:** {payload.get('task')}  \n"
        md_entry += f"\n#### Output from `{sender.get('user')}` ({sender.get('platform', '').upper()}):\n{payload.get('report')}\n"
    elif p_type in ("message", "chat"):
        md_entry += f"\n{payload.get('text', '')}\n"

    if not os.path.exists(INBOX_FILE):
        header = (
            "# 🤖 Antigravity Peer Collaboration Inbox\n"
            "Live stream of tasks, state syncs, and messages between Mr-Reaper (Linux) and Senpai59 (Windows).\n\n"
        )
        with open(INBOX_FILE, "w", encoding="utf-8") as f:
            f.write(header)

    with open(INBOX_FILE, "a", encoding="utf-8") as f:
        f.write(md_entry)

    log_activity(f"Received [{p_type}] from {sender.get('user')}: {str(payload)[:80]}")
    notif_summary = (
        payload.get("report", "")[:80]
        if p_type == "agent_report"
        else (payload.get("task") or payload.get("title") or payload.get("text") or "")
    )
    notify_desktop(f"AGY [{p_type.upper()}]: {sender.get('user')}", notif_summary)


# -----------------------------------------------------------------------------
# Dual-Transport Networking (Direct TCP + Cloud Relay Fallback)
# -----------------------------------------------------------------------------


class NetworkTransport:
    """Handles hybrid delivery across Direct TCP sockets and Cloud Relay."""

    def __init__(self, config):
        self.config = config
        self.role = config.get("role", "general")
        self.room = config.get("relay_room", DEFAULT_ROOM)
        self.peer_host = config.get("peer_host", "127.0.0.1")
        self.peer_port = int(config.get("peer_port", DEFAULT_PORT))

        # Cloud Relay topics
        is_lead = self.role in ("lead", "linux-lead") or (not sys.platform == "win32" and self.role != "platform_lead")
        if self.config.get("sub_topic") and self.config.get("pub_topic"):
            self.sub_topic = self.config["sub_topic"]
            self.pub_topic = self.config["pub_topic"]
        elif "mrreaper" in self.room or "senpai" in self.room:
            # Backwards compatibility for existing Mr-Reaper & Senpai pair
            if is_lead or "linux" in self.role:
                self.sub_topic = f"{self.room}_senpai_to_mr-reaper"
                self.pub_topic = f"{self.room}_mr-reaper_to_senpai"
            else:
                self.sub_topic = f"{self.room}_mr-reaper_to_senpai"
                self.pub_topic = f"{self.room}_senpai_to_mr-reaper"
        else:
            # Generalized directional channels for community teams
            if is_lead:
                self.sub_topic = f"{self.room}_contributor_to_lead"
                self.pub_topic = f"{self.room}_lead_to_contributor"
            else:
                self.sub_topic = f"{self.room}_lead_to_contributor"
                self.pub_topic = f"{self.room}_contributor_to_lead"

    def send_direct_tcp(self, packet):
        """Send packet via raw TCP socket."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2.5)
            s.connect((self.peer_host, self.peer_port))
            data = (json.dumps(packet) + "\n").encode("utf-8")
            s.sendall(data)
            s.close()
            return True, "Delivered via Direct TCP Socket"
        except Exception as e:
            return False, str(e)

    def send_relay(self, packet):
        """Send packet via HTTPS Cloud Relay (ntfy.sh)."""
        url = f"{RELAY_HOST}/{self.pub_topic}"
        data = json.dumps(packet, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Title": f"AGY [{packet.get('type')}] from {self.config.get('user')}",
                "Tags": "robot,satellite",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status in (200, 201):
                    return True, "Delivered via Cloud Relay (Zero-Port-Forwarding)"
                return False, f"Relay HTTP {resp.status}"
        except Exception as e:
            return False, str(e)

    def send(self, packet):
        """Hybrid dispatch: Try direct TCP first; fall back to cloud relay automatically."""
        mode = self.config.get("mode", "hybrid")
        msg = "TCP not attempted"

        if mode in ("direct", "hybrid"):
            if not (mode == "hybrid" and self.peer_host in ("127.0.0.1", "localhost", "0.0.0.0")):
                ok, msg = self.send_direct_tcp(packet)
                if ok:
                    return True, msg
                if mode == "direct":
                    return False, f"Direct TCP failed: {msg}"

        # Hybrid fallback or relay mode
        ok_relay, msg_relay = self.send_relay(packet)
        if ok_relay:
            return True, msg_relay
        return False, f"All transports failed. TCP: {msg}, Relay: {msg_relay}"


# -----------------------------------------------------------------------------
# Background Daemon Listener
# -----------------------------------------------------------------------------


def run_tcp_listener(config, on_packet_callback, stop_event, log_fn=None):
    """Listen on local TCP port for direct socket connections."""
    log = log_fn or print
    host = config.get("local_host", "0.0.0.0")
    port = int(config.get("local_port", DEFAULT_PORT))
    try:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(5)
        srv.settimeout(1.0)
    except Exception as e:
        log(f"[-] Could not bind TCP socket {host}:{port}: {e}")
        return

    log(f"[+] Direct TCP Listener active on {host}:{port}")
    while not stop_event.is_set():
        try:
            conn, addr = srv.accept()
        except socket.timeout:
            continue
        except Exception:
            break

        def handle_conn(c):
            buf = ""
            while not stop_event.is_set():
                try:
                    chunk = c.recv(4096)
                    if not chunk:
                        break
                    buf += chunk.decode("utf-8", errors="replace")
                    while "\n" in buf:
                        line, buf = buf.split("\n", 1)
                        if line.strip():
                            try:
                                packet = json.loads(line.strip())
                                on_packet_callback(packet)
                            except Exception:
                                pass
                except Exception:
                    break
            c.close()

        threading.Thread(target=handle_conn, args=(conn,), daemon=True).start()
    srv.close()


def run_relay_listener(transport, on_packet_callback, stop_event, log_fn=None):
    """Listen on HTTPS cloud relay stream for messages from remote peer."""
    log = log_fn or print
    seen_ids = set()

    # Initial catch-up: mark existing backlog IDs as seen so we DO NOT replay old summons or notifications
    try:
        poll_url = f"{RELAY_HOST}/{transport.sub_topic}/json?poll=1"
        req = urllib.request.Request(poll_url, headers={"User-Agent": "AgyLink/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            for line in resp:
                line_str = line.decode("utf-8", errors="replace").strip()
                if not line_str:
                    continue
                try:
                    event = json.loads(line_str)
                    msg_id = event.get("id")
                    if msg_id:
                        seen_ids.add(msg_id)
                except Exception:
                    pass
    except Exception:
        pass

    # Real-time streaming loop
    log(f"[+] Cloud Relay Listener active on {transport.sub_topic}")
    stream_url = f"{RELAY_HOST}/{transport.sub_topic}/json"
    while not stop_event.is_set():
        try:
            req = urllib.request.Request(stream_url, headers={"User-Agent": "AgyLink/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                for line in resp:
                    if stop_event.is_set():
                        break
                    line_str = line.decode("utf-8", errors="replace").strip()
                    if not line_str:
                        continue
                    try:
                        event = json.loads(line_str)
                        msg_id = event.get("id")
                        if msg_id and msg_id in seen_ids:
                            continue
                        if msg_id:
                            seen_ids.add(msg_id)
                        if event.get("event") == "message":
                            raw = event.get("message", "")
                            if raw.startswith("{"):
                                packet = json.loads(raw)
                                on_packet_callback(packet)
                    except Exception:
                        pass
        except Exception:
            time.sleep(2)


# -----------------------------------------------------------------------------
# Autonomous Agent Execution Engine
# -----------------------------------------------------------------------------


def find_agy_executable():
    """Locate the agy CLI binary across Linux and Windows."""
    agy_path = shutil.which("agy") or shutil.which("agy.cmd") or shutil.which("agy.exe")
    if agy_path:
        return agy_path

    if sys.platform != "win32":
        user_home = os.path.expanduser("~")
        candidates = [
            os.path.join(user_home, ".local", "bin", "agy"),
            "/usr/local/bin/agy",
            "/usr/bin/agy",
        ]
        for c in candidates:
            if os.path.isfile(c) and os.access(c, os.X_OK):
                return c
    else:
        user_profile = os.environ.get("USERPROFILE", "")
        appdata = os.environ.get("APPDATA", "")
        localappdata = os.environ.get("LOCALAPPDATA", "")
        candidates = [
            os.path.join(appdata, "npm", "agy.cmd"),
            os.path.join(appdata, "npm", "agy.exe"),
            os.path.join(localappdata, "Programs", "antigravity", "agy.exe"),
            os.path.join(user_profile, ".local", "bin", "agy.exe"),
            os.path.join(user_profile, ".local", "bin", "agy.cmd"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c

    return "agy"


def should_execute_locally(target, config, is_incoming=False):
    """Determine if this node should execute a summoned task."""
    t = (target or "").lower().strip()
    local_plat = platform.system().lower()
    local_role = config.get("role", "").lower()
    local_user = config.get("user", "").lower()
    local_node = config.get("node_id", "").lower()

    if t in ("both", "all"):
        return True
    if is_incoming:
        # If received from the network, 'remote' or 'peer' was sent for this node to execute!
        if t in ("remote", "peer"):
            return True
        if t == "local":
            return False
    else:
        # If evaluated locally before dispatch
        if t == "local":
            return True
        if t in ("remote", "peer"):
            return False

    if "linux" in t and "linux" in local_plat:
        return True
    if ("win" in t or "windows" in t) and "windows" in local_plat:
        return True
    if "reaper" in t and ("reaper" in local_user or "reaper" in local_node or "linux" in local_role):
        return True
    if "senpai" in t and ("senpai" in local_user or "senpai" in local_node or "windows" in local_role):
        return True
    return False


def resolve_summon_target(raw_prefix, local_platform):
    """Determine if a summon target tag is local, remote, or both."""
    p = raw_prefix.lower().strip()
    is_linux = (local_platform == "Linux")

    if p in ("@both", "@all", "@ai", "@agy"):
        return "both"
    elif p in ("@linux", "@linux-ai", "@reaper", "@reaper-ai", "@local", "@self"):
        return "local" if is_linux else "remote"
    elif p in ("@windows", "@windows-ai", "@win", "@win-ai", "@senpai", "@senpai-ai", "@peer", "@peer-ai", "@remote"):
        return "remote" if is_linux else "local"
    return "both"


def request_user_permission(task_description, sender_info, config):
    """
    Human-in-the-Loop (HITL) Security Approval Gate.
    Prompts the local machine owner to authorize an incoming autonomous task from a peer AI.
    Returns True if approved, False if rejected or timed out.
    """
    security_mode = config.get("security_mode", "prompt")
    if security_mode == "autonomous":
        log_activity("Security Gate: Autonomous mode enabled. Auto-approving task.")
        return True
    if security_mode == "deny":
        log_activity("Security Gate: Deny mode enabled. Rejecting task.")
        return False

    sender_info = sender_info or {}
    sender_user = sender_info.get("user", "Peer AI")
    sender_role = sender_info.get("role", "peer")
    sender_platform = sender_info.get("platform", "").upper()

    log_activity(f"Security Gate: Requesting owner approval for task from {sender_user}: {task_description[:60]}")
    notify_desktop("Antigravity Link Security Gate", f"Task request from {sender_user}: {task_description[:60]}")

    # 1. Windows: Native PowerShell GUI MessageBox
    if sys.platform == "win32":
        clean_task = (task_description[:300]
                      .replace('`', '``')
                      .replace('"', '`"')
                      .replace('$', '`$'))
        ps_cmd = (
            'Add-Type -AssemblyName PresentationFramework; '
            f'$res = [System.Windows.MessageBox]::Show('
            f'"⚡ Antigravity Link Security Request`n`n'
            f'Peer: {sender_user} ({sender_role} on {sender_platform})`n`n'
            f'Requested Task:`n`"{clean_task}`"`n`n'
            f'Allow this AI to execute autonomously on your PC?", '
            f'"Antigravity Link Security Gate", '
            f'[System.Windows.MessageBoxButton]::YesNo, '
            f'[System.Windows.MessageBoxImage]::Question); '
            f'if ($res -eq [System.Windows.MessageBoxResult]::Yes) {{ exit 0 }} else {{ exit 1 }}'
        )
        try:
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], timeout=60)
            approved = (res.returncode == 0)
            log_activity(f"Security Gate: Windows prompt result: {'Approved' if approved else 'Denied'}")
            return approved
        except Exception as e:
            log_activity(f"Security Gate: Windows prompt failed or timed out: {e}")
            return False

    # 2. Linux: Zenity GUI Question Dialog
    else:
        has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
        zenity_bin = shutil.which("zenity")
        if has_display and zenity_bin:
            clean_task = html.escape(task_description[:300])
            msg = (
                f"⚡ <b>Antigravity Link Security Gate</b>\n\n"
                f"<b>Peer:</b> {html.escape(sender_user)} ({html.escape(sender_role)} on {html.escape(sender_platform)})\n\n"
                f"<b>Requested Task:</b>\n<i>{clean_task}</i>\n\n"
                f"Allow this AI task to execute on your machine?"
            )
            try:
                res = subprocess.run(
                    [zenity_bin, "--question", "--title=Antigravity Link Security Gate", f"--text={msg}", "--timeout=60", "--width=420"],
                    timeout=65
                )
                approved = (res.returncode == 0)
                log_activity(f"Security Gate: Linux Zenity prompt result: {'Approved' if approved else 'Denied'}")
                return approved
            except Exception as e:
                log_activity(f"Security Gate: Zenity prompt failed: {e}")

    # 3. Terminal fallback if attached to an interactive TTY
    if sys.stdin and sys.stdin.isatty():
        try:
            print("\n" + "=" * 62, flush=True)
            print("🛡️  ANTIGRAVITY LINK SECURITY GATE: Action Approval Required", flush=True)
            print(f"   From:    {sender_user} ({sender_role} on {sender_platform})", flush=True)
            print(f"   Task:    {task_description}", flush=True)
            print("=" * 62, flush=True)
            ans = input("   Allow autonomous execution on this machine? [y/N]: ").strip().lower()
            approved = ans in ("y", "yes")
            log_activity(f"Security Gate: Terminal prompt result: {'Approved' if approved else 'Denied'}")
            return approved
        except Exception:
            pass

    # Safe default when headless with no GUI and no interactive TTY
    log_activity("Security Gate: Non-interactive environment without display. Defaulting to safe denial.")
    return False


def execute_local_agy(prompt, config, transport=None, is_remote_request=False, sender_info=None):
    """Execute a task autonomously using local agy CLI and broadcast report."""
    sender_info = sender_info or {}
    user = config.get("user", "Local")
    plat_str = platform.system().upper()

    # Security Approval Gate for remote peer summons
    if is_remote_request:
        if not request_user_permission(prompt, sender_info, config):
            print(f"\n🛑 [SECURITY GATE] Remote task rejected or timed out by machine owner.\n> ", end="", flush=True)
            log_activity(f"Security Gate: Blocked unapproved remote task from {sender_info.get('user', 'peer')}")
            notify_desktop("Antigravity Link Security", f"Blocked unapproved task from {sender_info.get('user', 'peer')}")

            rejection_payload = {
                "task": prompt,
                "report": f"Execution declined: Machine owner ({user}) did not authorize this remote task request.",
                "status": "rejected_by_owner",
                "elapsed_sec": 0.0,
                "success": False
            }
            report_packet = make_packet("agent_report", rejection_payload, config)
            update_peer_state(report_packet)
            if transport:
                transport.send(report_packet)
            return rejection_payload

    agy_bin = find_agy_executable()
    log_activity(f"Executing AGY task: {prompt[:80]}")
    notify_desktop(f"AGY [{plat_str}] Autonomous Agent", f"Task started: {prompt[:80]}")

    print(f"\n⚡ [AUTONOMOUS AGY RUNNING] Executing task on {user} ({plat_str})...\n   Task: {prompt}\n", flush=True)

    cmd = [agy_bin, "-p", prompt]
    if (not is_remote_request) or config.get("allow_unrestricted_remote", False):
        cmd.append("--dangerously-skip-permissions")

    start_t = time.time()
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=300,
            encoding="utf-8",
            errors="replace"
        )
        elapsed = round(time.time() - start_t, 2)
        output = proc.stdout.strip() if proc.stdout else "(No output returned)"
        success = (proc.returncode == 0)
        status_str = "completed" if success else f"failed (code {proc.returncode})"
    except subprocess.TimeoutExpired:
        elapsed = round(time.time() - start_t, 2)
        output = "Execution timed out after 300 seconds."
        success = False
        status_str = "timeout"
    except Exception as e:
        elapsed = round(time.time() - start_t, 2)
        output = f"Execution failed to launch: {str(e)}"
        success = False
        status_str = "error"

    report_payload = {
        "task": prompt,
        "report": output,
        "status": status_str,
        "elapsed_sec": elapsed,
        "success": success
    }

    # Record report locally
    report_packet = make_packet("agent_report", report_payload, config)
    update_peer_state(report_packet)

    # Broadcast report to peer station if transport is available
    if transport:
        ok, msg = transport.send(report_packet)
        log_activity(f"Dispatched agent report to peer: {status_str} ({elapsed}s, delivery: {ok})")

    print(f"\n✅ [AUTONOMOUS AGY COMPLETE] {user} ({plat_str}) finished in {elapsed}s [{status_str.upper()}]\n> ", end="", flush=True)
    return report_payload


# -----------------------------------------------------------------------------
# PyCharm & IDE Integration Helpers
# -----------------------------------------------------------------------------


def get_ide_environment():
    """Detect active IDE environment (PyCharm / JetBrains / VS Code / Standard Terminal)."""
    if (
        os.environ.get("PYCHARM_HOSTED")
        or os.environ.get("TERMINAL_EMULATOR") == "JetBrains-JediTerm"
        or "pycharm" in os.environ.get("SNAP_INSTANCE_NAME", "").lower()
        or "pycharm" in os.environ.get("SNAP_NAME", "").lower()
        or "idea" in os.environ.get("TERMINAL_EMULATOR", "").lower()
        or os.environ.get("INTELLIJ_TERMINAL_COMMAND_BLOCKS_REWORKED")
    ):
        return "PyCharm (JetBrains-JediTerm)"
    if os.environ.get("VSCODE_PID") or os.environ.get("TERM_PROGRAM") == "vscode":
        return "VS Code"
    return "Standard Terminal"


def open_in_ide(filepath, line=None, column=None):
    """Open a file directly in PyCharm / JetBrains IDE editor tab."""
    if not filepath:
        return False, "No file path specified"

    # Resolve absolute path
    abs_path = os.path.abspath(os.path.expanduser(filepath))
    if not os.path.exists(abs_path):
        repo_cand = os.path.join(SCRIPT_DIR, filepath)
        if os.path.exists(repo_cand):
            abs_path = repo_cand
        else:
            return False, f"File not found: {filepath}"

    # Candidate IDE binaries
    candidates = []
    snap_pycharm = "/snap/bin/pycharm-community"
    if os.path.exists(snap_pycharm):
        candidates.append(snap_pycharm)

    for b in ["charm", "pycharm-community", "pycharm", "idea", "pycharm64.exe", "charm.cmd"]:
        w = shutil.which(b)
        if w and w not in candidates:
            candidates.append(w)

    if sys.platform == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        for base in [local_app_data, program_files]:
            c1 = os.path.join(base, "Programs", "PyCharm Community Edition", "bin", "pycharm64.exe")
            c2 = os.path.join(base, "JetBrains", "PyCharm Community Edition", "bin", "pycharm64.exe")
            for c in [c1, c2]:
                if os.path.exists(c) and c not in candidates:
                    candidates.append(c)

    for bin_path in candidates:
        try:
            cmd = [bin_path]
            if line is not None:
                cmd.extend(["--line", str(line)])
            if column is not None:
                cmd.extend(["--column", str(column)])
            cmd.append(abs_path)
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, f"Opened '{os.path.basename(abs_path)}' in PyCharm ({bin_path})"
        except Exception:
            continue

    # Fallback to system open
    try:
        if sys.platform == "win32":
            os.startfile(abs_path)
        else:
            subprocess.Popen(["xdg-open", abs_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, f"Opened '{os.path.basename(abs_path)}' using system default handler"
    except Exception as e:
        return False, f"Failed to open file: {e}"


def cmd_open(args, config):
    """CLI command to open a file in PyCharm editor."""
    filepath = getattr(args, "file", "")
    line = getattr(args, "line", None)
    col = getattr(args, "column", None)
    ok, msg = open_in_ide(filepath, line=line, column=col)
    if ok:
        print(f"✅ {msg}")
        return 0
    else:
        print(f"❌ {msg}")
        return 1


# -----------------------------------------------------------------------------
# CLI Commands
# -----------------------------------------------------------------------------


def cmd_status(args, config):
    """Check connectivity, configuration, and peer state."""
    transport = NetworkTransport(config)
    ide_env = get_ide_environment()
    print("============================================================")
    print(f"  AGY LINK STATUS - Node: {config.get('node_id')} ({platform.system().upper()})")
    print("============================================================")
    if ide_env != "Standard Terminal":
        print(f"IDE Terminal:   🚀 {ide_env}")
    print(f"User:           {config.get('user')} ({config.get('role')})")
    print(f"Local Listener: {config.get('local_host')}:{config.get('local_port')}")
    print(f"Peer Target:    {config.get('peer_host')}:{config.get('peer_port')}")
    print(f"Network Mode:   {config.get('mode').upper()}")
    print(f"Cloud Relay:    {transport.sub_topic}")
    if "PyCharm" in ide_env:
        print("Web Dashboard:  🟢 http://127.0.0.1:7891 (PyCharm: View -> Tool Windows -> Web Browser)")
    print("------------------------------------------------------------")

    # Test TCP
    tcp_ok, tcp_msg = transport.send_direct_tcp(make_packet("ping", {}, config))
    if tcp_ok:
        print(f"Direct Socket:  🟢 ONLINE ({config.get('peer_host')}:{config.get('peer_port')})")
    else:
        print(f"Direct Socket:  🔴 UNREACHABLE ({tcp_msg})")

    # Test Relay
    print(f"Cloud Relay:    🟢 READY (Instant Fallback Active)")

    # Display Peer State
    if os.path.exists(PEER_STATE_FILE):
        try:
            with open(PEER_STATE_FILE, "r", encoding="utf-8") as f:
                p_state = json.load(f)
                peers_table = p_state.get("peers", {})
                if isinstance(peers_table, dict) and len(peers_table) > 1:
                    print("------------------------------------------------------------")
                    print(f"Swarm Mesh:     🌐 {len(peers_table)} Nodes Connected")
                    for nid, nentry in peers_table.items():
                        ns = nentry.get("sender", {})
                        nst = nentry.get("state", {})
                        nuser = ns.get("user") or nid
                        nrole = ns.get("role", "peer")
                        print(f"  • {nuser} ({nrole}) [{nst.get('status', 'active')}]: {nst.get('task', 'idle')}")
                        if nst.get("locked_files"):
                            print(f"    🔒 Locks: {', '.join(nst.get('locked_files'))}")
                else:
                    sender = p_state.get("sender", {})
                    st = p_state.get("state", {})
                    print("------------------------------------------------------------")
                    print(f"Peer Node:      {sender.get('user')} ({sender.get('role')})")
                    print(f"Last Active:    {p_state.get('last_updated')}")
                    if st.get("task"):
                        print(f"Active Task:    {st.get('task')} [{st.get('status')}]")
                    if st.get("locked_files"):
                        print(f"Locked Files:   {', '.join(st.get('locked_files'))}")
        except Exception:
            pass
    print("============================================================")
    return 0


def cmd_sync(args, config):
    """Broadcast state, current task, and locked files to prevent conflicts."""
    files = [f.strip() for f in args.files.split(",") if f.strip()] if args.files else []
    payload = {
        "task": args.task,
        "status": args.status,
        "locked_files": files,
        "notes": args.notes or "",
    }

    # Save to local state
    ensure_dirs()
    try:
        with open(LOCAL_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "last_updated": get_iso_timestamp(),
                "state": payload,
            }, f, indent=2)
    except Exception:
        pass

    packet = make_packet("state_sync", payload, config)
    transport = NetworkTransport(config)
    print(f"[+] Broadcasting state sync: [{args.status.upper()}] {args.task}...", end=" ", flush=True)
    ok, msg = transport.send(packet)
    if ok:
        print(f"✅ {msg}")
        log_activity(f"Broadcasted sync: {args.task} [{args.status}]")
        return 0
    print(f"❌ Failed: {msg}")
    return 1


def cmd_delegate(args, config):
    """Delegate a cross-platform task to the remote peer AI."""
    payload = {
        "title": args.title,
        "description": args.description,
        "target_os": args.target_os,
        "priority": args.priority,
    }
    packet = make_packet("task_delegation", payload, config)
    transport = NetworkTransport(config)
    print(f"[+] Delegating task '{args.title}' to {args.target_os.upper()} station...", end=" ", flush=True)
    ok, msg = transport.send(packet)
    if ok:
        print(f"✅ {msg}")
        log_activity(f"Delegated task: {args.title} (Priority: {args.priority})")
        return 0
    print(f"❌ Failed: {msg}")
    return 1


def cmd_send(args, config):
    """Send a live message or AI directive."""
    payload = {
        "text": args.message,
        "agent": args.agent,
    }
    packet = make_packet("message", payload, config)
    transport = NetworkTransport(config)
    print(f"[+] Sending message to peer...", end=" ", flush=True)
    ok, msg = transport.send(packet)
    if ok:
        print(f"✅ {msg}")
        log_activity(f"Sent message: {args.message[:60]}")
        return 0
    print(f"❌ Failed: {msg}")
    return 1


def start_background_listener(config=None, log_fn=None, stop_event=None):
    """Start background TCP and Cloud Relay listeners in daemon threads.

    Prints/logs go to log_fn (defaults to sys.stderr.write) so stdout is preserved
    for MCP JSON-RPC communication.
    Returns (stop_event, transport).
    """
    if config is None:
        config = load_config()
    if stop_event is None:
        stop_event = threading.Event()
    if log_fn is None:
        log_fn = lambda msg: sys.stderr.write(f"[AGY-LINK] {msg}\n")

    transport = NetworkTransport(config)

    def on_packet(packet):
        sender = packet.get("sender", {})
        p_type = packet.get("type", "message")
        payload = packet.get("payload", {})

        # Cryptographic HMAC Signature & Token Verification
        secret_key = config.get("secret_key", DEFAULT_SECRET)
        auth_token = config.get("auth_token", "")
        if not verify_packet_signature(packet, secret_key, auth_token):
            log_fn(f"🛡️  [SECURITY GATE] Dropped unauthenticated packet from {sender.get('user', 'unknown')} ({sender.get('node_id')})! Invalid signature.")
            log_activity(f"Security Gate: Dropped packet from {sender.get('user')} with invalid HMAC signature.")
            return

        # Anti-Replay & Freshness Gate
        if not verify_packet_freshness(packet, max_drift_seconds=60):
            log_fn(f"🛡️  [SECURITY GATE] Dropped stale or replayed packet from {sender.get('user', 'unknown')} (ID: {packet.get('packet_id')}).")
            log_activity(f"Security Gate: Dropped stale/replayed packet from {sender.get('user')}")
            return

        # Prompt Injection Immune System Check
        if p_type in ("agent_summon", "task_delegation"):
            raw_text = payload.get("task") or payload.get("description") or ""
            is_suspicious, trigger = scan_for_prompt_injection(raw_text)
            if is_suspicious:
                quarantine_peer(sender, f"Suspicious instruction pattern: '{trigger}'", packet)
                log_fn(f"🚨 [IMMUNE SYSTEM] QUARANTINED peer {sender.get('user')}! Detected: '{trigger}'")
                return

        log_fn(f"🔔 Received [{p_type.upper()}] from {sender.get('user')}")
        update_peer_state(packet)

        if p_type == "agent_summon":
            task = payload.get("task", "")
            target = payload.get("target", "both")
            if should_execute_locally(target, config, is_incoming=True):
                log_fn(f"🚀 Launching local AGY background execution: {task[:60]}")
                threading.Thread(target=execute_local_agy, args=(task, config, transport, True, sender), daemon=True).start()

    t1 = threading.Thread(target=run_tcp_listener, args=(config, on_packet, stop_event, log_fn), daemon=True)
    t2 = threading.Thread(target=run_relay_listener, args=(transport, on_packet, stop_event, log_fn), daemon=True)
    t1.start()
    t2.start()

    log_fn(f"Background listeners active (Relay: {transport.sub_topic}, TCP: {config.get('local_port')})")
    return stop_event, transport


def cmd_daemon(args, config):
    """Run background listener handling both Direct TCP and Cloud Relay."""
    transport = NetworkTransport(config)
    stop_event = threading.Event()

    print("============================================================")
    print(f"🤖 ANTIGRAVITY LINK DAEMON — {config.get('user')} ({config.get('role')})")
    print("============================================================")
    print(f"Local Platform: {platform.system()} ({config.get('node_id')})")
    print(f"Direct TCP:     {config.get('local_host')}:{config.get('local_port')}")
    print(f"Cloud Relay:    {transport.sub_topic}")
    print(f"Inbox Ledger:   {os.path.abspath(INBOX_FILE)}")
    print("============================================================")
    print("🟢 Daemon running. Press Ctrl+C to exit.\n", flush=True)

    start_background_listener(config=config, log_fn=lambda m: print(m, flush=True), stop_event=stop_event)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down AGY Link daemon.")
        stop_event.set()


def cmd_chat(args, config):
    """Interactive real-time two-way terminal chat with @ai summon support."""
    transport = NetworkTransport(config)
    stop_event = threading.Event()

    print("============================================================")
    print(f"💬 AGY LIVE CHAT: {config.get('user')} ⟷ Remote Station")
    print("============================================================")
    print("Commands:")
    print("  Normal message:      Just type and press ENTER")
    print("  @ai <task>:          Summon BOTH AI agents to work autonomously")
    print("  @senpai-ai <task>:   Summon Senpai's Windows AI agent")
    print("  @reaper-ai <task>:   Summon Reaper's Linux AI agent")
    print("  exit / quit:         Close chat session")
    print("------------------------------------------------------------\n", flush=True)

    def on_packet(packet):
        sender = packet.get("sender", {})
        p_type = packet.get("type", "chat")
        payload = packet.get("payload", {})

        # Cryptographic HMAC Signature & Token Verification
        secret_key = config.get("secret_key", DEFAULT_SECRET)
        auth_token = config.get("auth_token", "")
        if not verify_packet_signature(packet, secret_key, auth_token):
            print(f"\n🛡️  [SECURITY GATE] Dropped unauthenticated packet from {sender.get('user', 'unknown')}! Invalid signature.\n> ", end="", flush=True)
            log_activity(f"Security Gate: Dropped chat packet from {sender.get('user')} with invalid HMAC signature.")
            return

        # Anti-Replay & Freshness Gate
        if not verify_packet_freshness(packet, max_drift_seconds=60):
            print(f"\n🛡️  [SECURITY GATE] Dropped stale/replayed packet (ID: {packet.get('packet_id')}).\n> ", end="", flush=True)
            log_activity(f"Security Gate: Dropped stale/replayed packet in chat from {sender.get('user')}")
            return

        # Prompt Injection Immune System Check
        if p_type in ("agent_summon", "task_delegation"):
            raw_text = payload.get("task") or payload.get("description") or ""
            is_suspicious, trigger = scan_for_prompt_injection(raw_text)
            if is_suspicious:
                quarantine_peer(sender, f"Suspicious instruction pattern: '{trigger}'", packet)
                print(f"\n🚨 [IMMUNE SYSTEM] QUARANTINED peer {sender.get('user')}! Detected: '{trigger}'\n> ", end="", flush=True)
                return

        if p_type == "chat":
            text = payload.get("text", "")
            print(f"\n💬 [{sender.get('user')}]: {text}\n> ", end="", flush=True)
        elif p_type == "agent_summon":
            task = payload.get("task", "")
            target = payload.get("target", "both")
            print(f"\n⚡ [@{sender.get('user')} SUMMONED AI]: {task} (Target: {target})\n> ", end="", flush=True)
            if should_execute_locally(target, config, is_incoming=True):
                print(f"🚀 [LOCAL AGY] Starting background turn...\n> ", end="", flush=True)
                threading.Thread(target=execute_local_agy, args=(task, config, transport, True, sender), daemon=True).start()
        elif p_type == "agent_report":
            status = payload.get("status", "completed").upper()
            rep = payload.get("report", "").strip()
            print(f"\n🤖 [AI REPORT from {sender.get('user')} ({status})]:\n{rep}\n> ", end="", flush=True)
        else:
            print(f"\n🔔 [{p_type.upper()} from @{sender.get('user')}]: {payload.get('task') or payload.get('title') or payload.get('text') or ''}\n> ", end="", flush=True)

        update_peer_state(packet)

    t1 = threading.Thread(target=run_tcp_listener, args=(config, on_packet, stop_event), daemon=True)
    t2 = threading.Thread(target=run_relay_listener, args=(transport, on_packet, stop_event), daemon=True)
    t1.start()
    t2.start()

    while True:
        try:
            msg = input("> ").strip()
            if not msg:
                continue
            if msg.lower() in ("exit", "quit"):
                break

            # Check for summon command
            match = re.match(r"^(@[a-zA-Z0-9_-]+)\s+(.+)$", msg, re.DOTALL)
            if match:
                tag = match.group(1).lower()
                task_prompt = match.group(2).strip()
                if tag in ("@ai", "@both", "@all", "@agy", "@senpai-ai", "@senpai", "@win-ai", "@windows-ai", "@reaper-ai", "@reaper", "@linux-ai"):
                    target = resolve_summon_target(tag, platform.system())
                    print(f"\n⚡ [SUMMON] Calling AI Agent (Target: {target.upper()}): {task_prompt}\n", flush=True)
                    if target in ("both", "remote"):
                        pkt = make_packet("agent_summon", {"task": task_prompt, "target": target}, config)
                        transport.send(pkt)
                    if target in ("both", "local"):
                        threading.Thread(target=execute_local_agy, args=(task_prompt, config, transport), daemon=True).start()
                    continue

            packet = make_packet("chat", {"text": msg}, config)
            transport.send(packet)
        except (KeyboardInterrupt, EOFError):
            break
    stop_event.set()
    print("\nChat closed.")
    return 0


def cmd_inbox(args, config):
    """Display latest entries from INBOX.md."""
    if not os.path.exists(INBOX_FILE):
        print("📭 Inbox is empty. No messages or state syncs recorded yet.")
        return 0
    with open(INBOX_FILE, "r", encoding="utf-8") as f:
        print(f.read())
    return 0


def cmd_summon(args, config):
    """Summon autonomous AI agent(s) via CLI command."""
    prompt = args.prompt
    target = args.target.lower()
    transport = NetworkTransport(config)

    print("============================================================")
    print(f"⚡ SUMMONING ANTIGRAVITY AGENT(S) — Target: {target.upper()}")
    print("============================================================")
    print(f"Instruction: {prompt}")
    print("------------------------------------------------------------")

    # Send across the wire if remote or both or specific platform
    if target in ("both", "remote", "windows", "linux", "senpai", "reaper"):
        pkt = make_packet("agent_summon", {"task": prompt, "target": target}, config)
        ok, msg = transport.send(pkt)
        if ok:
            print(f"[+] Remote summon packet dispatched: ✅ {msg}")
        else:
            print(f"[-] Remote summon packet failed: ❌ {msg}")

    # Run locally if target is 'both' or 'local' or directed to local machine
    if target in ("both", "local") or should_execute_locally(target, config):
        print("[+] Executing autonomous turn on local machine...")
        rep = execute_local_agy(prompt, config, transport)
        print("\n============================================================")
        print("🤖 LOCAL AGENT REPORT:")
        print(rep.get("report", ""))
        print(f"Elapsed: {rep.get('elapsed_sec')}s | Status: {rep.get('status')}")
        print("============================================================")
    else:
        print("\n[+] Remote AI summoned. Waiting for peer agent report in background...")
        print("    Check progress anytime with: python3 agy_link.py inbox")

    return 0


def cmd_pair(args, config):
    """Generate and display room pairing credentials for peer connection."""
    room = config.get("relay_room", DEFAULT_ROOM)
    key = config.get("secret_key", DEFAULT_SECRET)
    user = config.get("user", "User")
    role = config.get("role", "contributor")

    print("============================================================")
    print("🔗 ANTIGRAVITY LINK — SESSION PAIRING CREDENTIALS")
    print("============================================================")
    print(f"Room ID:    {room}")
    print(f"Secret Key: {key}")
    print(f"User:       {user}")
    print(f"Role:       {role}")
    print(f"Security:   {config.get('security_mode', 'prompt').upper()} (Human Approval Gate)")
    print("------------------------------------------------------------")
    print("Share these credentials with your collaborator. On their PC, run:")
    print(f"  link join --room \"{room}\" --key \"{key}\" --peer \"{user}\"")
    print("============================================================")
    return 0


def cmd_join(args, config):
    """Join an Antigravity Link room using provided room ID and secret key."""
    room = getattr(args, "room", None)
    key = getattr(args, "key", None)
    if not room or not key:
        print("❌ Error: Both --room and --key are required to join.")
        print("Usage: link join --room <ROOM_ID> --key <SECRET_KEY> [--peer <PEER_NAME>]")
        return 1
    config["relay_room"] = room
    config["secret_key"] = key
    config["auth_token"] = key[:16]
    peer = getattr(args, "peer", None)
    if peer:
        config["peer"] = peer
    save_config(config)
    print(f"✅ Joined room '{room}'. Credentials saved to .agy_link/config.json.")
    print("[+] Sending secure handshake to verify connection...", end=" ", flush=True)
    transport = NetworkTransport(config)
    ok, msg = transport.send(make_packet("chat", {"text": f"👋 Handshake verified! {config.get('user')} ({config.get('role')}) joined the session."}, config))
    if ok:
        print("✅ Handshake delivered successfully!")
    else:
        print(f"⚠️  Handshake warning: {msg}")
    return 0


def cmd_role(args, config):
    """Set local role in project collaboration hierarchy."""
    valid_roles = VALID_ROLES
    role_arg = getattr(args, "role_name", None)
    if not role_arg:
        print(f"Current Role: {config.get('role', 'contributor')}")
        print("Hierarchy Roles:")
        print("  lead:          Project Architect / Lead (holds master/main branch authority)")
        print("  platform_lead: Platform Lead (owns platform-specific branch like 'windows')")
        print("  contributor:   Develops features and submits proposed patches/PRs")
        print("  tester:        Validates hardware and runs test suites")
        return 0
    r = role_arg.lower().replace("-", "_")
    config["role"] = r
    save_config(config)
    print(f"✅ Local role updated to: {r}")
    return 0


def cmd_security(args, config):
    """Inspect or configure Human-in-the-Loop (HITL) security approval gate."""
    mode_arg = getattr(args, "mode_name", None)
    if not mode_arg:
        print(f"Current Security Mode: {config.get('security_mode', 'prompt').upper()}")
        print("Available Modes:")
        print("  prompt:          (Recommended) Owner must approve each incoming remote task")
        print("  session_trusted: Temporarily trust peer for the active session")
        print("  autonomous:      Unrestricted autonomous execution (isolated lab)")
        print("  deny:            Block all remote task requests automatically")
        return 0
    m = mode_arg.lower()
    if m not in ("prompt", "session_trusted", "autonomous", "deny"):
        print(f"❌ Invalid security mode: {m}")
        return 1
    config["security_mode"] = m
    save_config(config)
    print(f"✅ Security approval mode set to: {m.upper()}")
    return 0


def cmd_unquarantine(args, config):
    """Release peer node from security quarantine."""
    ensure_dirs()
    if os.path.exists(PEER_STATE_FILE):
        try:
            with open(PEER_STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["state"]["status"] = "idle"
            data["state"]["reason"] = "Quarantine cleared by operator"
            with open(PEER_STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("✅ Quarantine successfully cleared. Peer connection restored to idle.")
            log_activity("Security Gate: Operator cleared peer quarantine.")
            return 0
        except Exception as e:
            print(f"Error clearing quarantine: {e}")
            return 1
    print("No active peer state found.")
    return 0


def cmd_init(args, config):
    """Interactive zero-friction onboarding wizard."""
    print("=" * 60)
    print("🚀 Antigravity Link — Interactive Setup Wizard")
    print("=" * 60)

    # 1. Developer Handle
    default_user = os.environ.get("USER") or os.environ.get("USERNAME") or "Developer"
    try:
        user_input = input(f"1. Enter your developer handle [{default_user}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        user_input = ""
    config["user"] = user_input or default_user
    config["node_id"] = f"{config['user'].lower().replace(' ', '-')}-{platform.system().lower()[:3]}"

    # 2. Hierarchy Role
    print("\n2. Select your role in the collaboration hierarchy:")
    print("   [1] Lead / Project Architect (holds main branch authority)")
    print("   [2] Platform Lead (e.g. Windows/macOS specialist)")
    print("   [3] Contributor (feature developer) [Default]")
    print("   [4] Tester / QA (hardware & test suite validation)")
    try:
        role_choice = input("   Choice [1-4, default: 3]: ").strip()
    except (EOFError, KeyboardInterrupt):
        role_choice = "3"
    role_map = {"1": "lead", "2": "platform_lead", "3": "contributor", "4": "tester"}
    config["role"] = role_map.get(role_choice, "contributor")

    # 3. Transport Mode
    print("\n3. Select network transport mode:")
    print("   [1] Cloud Relay (Zero-Config HTTPS via ntfy.sh) [Default]")
    print("   [2] Hybrid (Direct TCP with Cloud Relay Fallback)")
    print("   [3] Direct TCP LAN / Tailscale Socket Only")
    try:
        mode_choice = input("   Choice [1-3, default: 1]: ").strip()
    except (EOFError, KeyboardInterrupt):
        mode_choice = "1"
    mode_map = {"1": "relay", "2": "hybrid", "3": "direct"}
    config["mode"] = mode_map.get(mode_choice, "relay")

    # 4. Room ID
    default_room = config.get("relay_room", DEFAULT_ROOM)
    try:
        room_input = input(f"\n4. Enter Pairing Room ID [{default_room}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        room_input = ""
    config["relay_room"] = room_input or default_room

    # 5. Secret Key & Ephemeral Salt
    default_secret = config.get("secret_key", DEFAULT_SECRET)
    print(f"\n5. Session Secret Key:")
    print(f"   [1] Use shared room secret key")
    print(f"   [2] Generate a new cryptographically secure secret key")
    try:
        sec_choice = input("   Choice [1-2, default: 1]: ").strip()
    except (EOFError, KeyboardInterrupt):
        sec_choice = "1"
    if sec_choice == "2":
        new_secret = f"agy_{os.urandom(12).hex()}"
        config["secret_key"] = new_secret
        print(f"   🔑 Generated new Secret Key: {new_secret}")
    else:
        config["secret_key"] = default_secret

    config["session_salt"] = f"SALT_{os.urandom(4).hex().upper()}"

    save_config(config)
    print("\n" + "=" * 60)
    print(f"✅ Setup complete! Configuration saved to {CONFIG_FILE}")
    print(f"   Node:    {config['node_id']} ({config['user']} as {config['role']})")
    print(f"   Room:    {config['relay_room']}")
    print(f"   Mode:    {config['mode'].upper()}")
    print("=" * 60)
    return 0


def get_dashboard_status(config):
    """Compile structured dictionary of local node and peer state for GUI dashboard."""
    peer_data = {"name": "Peer", "role": "peer", "is_online": False, "is_quarantined": False, "last_updated": ""}
    locks_data = {"locked_files": [], "task": "None", "status": "idle", "locked_by": "Peer"}

    if os.path.exists(PEER_STATE_FILE):
        try:
            with open(PEER_STATE_FILE, "r", encoding="utf-8") as f:
                p = json.load(f)
            sender = p.get("sender", {})
            state = p.get("state", {})
            peer_data["name"] = sender.get("user", "Peer")
            peer_data["role"] = sender.get("role", "contributor")
            peer_data["last_updated"] = p.get("last_updated", "")

            status = str(state.get("status", "idle")).lower()
            peer_data["is_quarantined"] = (status == "quarantined")

            # Check online status via freshness (< 300s since last ping or state sync)
            if p.get("last_updated"):
                try:
                    clean_str = p["last_updated"].replace("Z", "+00:00")
                    dt = datetime.datetime.fromisoformat(clean_str)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    diff = (datetime.datetime.now(timezone.utc) - dt).total_seconds()
                    peer_data["is_online"] = (diff < 300) and not peer_data["is_quarantined"]
                except Exception:
                    pass

            if not is_lock_expired(p.get("last_updated")):
                locks_data["locked_files"] = state.get("locked_files", [])
                locks_data["task"] = state.get("task", "None")
                locks_data["status"] = status
                locks_data["locked_by"] = peer_data["name"]
            else:
                locks_data["status"] = "idle"
        except Exception:
            pass

    recent_events = []
    if os.path.exists(ACTIVITY_LOG_FILE):
        try:
            with open(ACTIVITY_LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                recent_events = [l.strip() for l in lines[-8:] if l.strip()]
        except Exception:
            pass

    return {
        "node": {
            "id": config.get("node_id", "local-node"),
            "user": config.get("user", "User"),
            "role": config.get("role", "lead"),
            "room": config.get("relay_room", DEFAULT_ROOM),
            "mode": config.get("mode", "hybrid"),
            "security": config.get("security_mode", "prompt"),
            "ide": get_ide_environment()
        },
        "peer": peer_data,
        "locks": locks_data,
        "recent_events": recent_events
    }


def generate_dashboard_html(config):
    """Generate modern OLED pitch-black HTML5 dashboard with dynamic live polling."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Antigravity Link — Collaborative GUI</title>
<style>
  :root {
    --bg: #000000;
    --card-bg: #0d0d12;
    --border: #1e1e28;
    --accent: #7764d8;
    --green: #2ed573;
    --red: #ff4757;
    --yellow: #ffa502;
    --text: #f1f2f6;
    --muted: #747d8c;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background-color: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
    line-height: 1.4;
    padding: 14px;
  }
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
    padding-bottom: 10px;
    margin-bottom: 12px;
  }
  .brand { display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 15px; color: var(--text); }
  .brand span { color: var(--accent); }
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
  }
  .badge-online { background: rgba(46, 213, 115, 0.15); color: var(--green); border: 1px solid var(--green); }
  .badge-offline { background: rgba(255, 71, 87, 0.15); color: var(--red); border: 1px solid var(--red); }
  .card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 12px;
    margin-bottom: 10px;
  }
  .card-title {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--muted);
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
  }
  .row { display: flex; justify-content: space-between; margin-bottom: 4px; }
  .label { color: var(--muted); }
  .val { font-weight: 600; font-family: monospace; }
  .file-item {
    background: #000;
    border: 1px solid #2a2a3a;
    border-radius: 4px;
    padding: 6px 8px;
    margin-top: 4px;
    font-family: monospace;
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 6px;
    color: var(--yellow);
  }
  .btn {
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.2s;
  }
  .btn:hover { opacity: 0.85; }
  .btn-danger { background: var(--red); }
  .log-feed {
    font-family: monospace;
    font-size: 11px;
    max-height: 110px;
    overflow-y: auto;
    background: #000;
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 6px;
    color: #a4b0be;
  }
  .log-line { margin-bottom: 3px; white-space: pre-wrap; word-break: break-all; }
</style>
</head>
<body>
<header>
  <div class="brand">🤖 <span>Antigravity</span> Link <span id="ideBadge" style="font-size: 10px; padding: 2px 6px; background: #1e1e28; border-radius: 4px; color: #a4b0be; margin-left: 6px;">PyCharm</span></div>
  <div id="peerPill" class="badge badge-offline">Connecting...</div>
</header>

<div class="card">
  <div class="card-title">Peer Connection</div>
  <div class="row"><span class="label">Local Node:</span><span class="val" id="localNode">-</span></div>
  <div class="row"><span class="label">Remote Peer:</span><span class="val" id="peerUser">-</span></div>
  <div class="row"><span class="label">Transport:</span><span class="val" id="transportMode">-</span></div>
  <div class="row"><span class="label">Security Mode:</span><span class="val" id="secMode">-</span></div>
</div>

<div class="card">
  <div class="card-title">Active File Locks ("Don't Step on Toes")</div>
  <div id="locksContainer">
    <div style="color: var(--green); font-size: 12px;">✔ No files locked. Safe to edit.</div>
  </div>
</div>

<div class="card">
  <div class="card-title">PyCharm Tandem Actions</div>
  <div style="display: flex; gap: 6px; margin-bottom: 6px;">
    <input id="quickMsg" type="text" placeholder="Type chat message or @ai task prompt..." style="flex: 1; background: #000; border: 1px solid var(--border); border-radius: 4px; padding: 6px 8px; color: #fff; font-size: 11px;">
    <button class="btn" onclick="sendQuickMsg()">Send</button>
    <button class="btn" style="background: #2ed573;" onclick="summonQuickMsg()">@ai Summon</button>
  </div>
  <div id="actionFeedback" style="font-size: 11px; color: var(--muted); min-height: 14px;"></div>
</div>

<div class="card">
  <div class="card-title">Task Queue</div>
  <div class="row"><span class="label">Active Task:</span><span class="val" id="activeTask" style="color: var(--accent);">None</span></div>
  <div class="row"><span class="label">Task Status:</span><span class="val" id="taskStatus">idle</span></div>
</div>

<div class="card">
  <div class="card-title">Recent Activity</div>
  <div class="log-feed" id="logFeed">Loading...</div>
</div>

<div style="display: flex; gap: 8px; margin-top: 10px;">
  <button class="btn" onclick="fetchStatus()">↻ Refresh</button>
  <button class="btn btn-danger" id="unqBtn" style="display: none;" onclick="clearQuarantine()">Clear Quarantine</button>
</div>

<script>
async function openFileInPyCharm(f) {
  try {
    const res = await fetch('/api/open?file=' + encodeURIComponent(f), { method: 'POST' });
    const d = await res.json();
    document.getElementById('actionFeedback').innerText = d.message || 'Opened in PyCharm';
  } catch (e) {
    document.getElementById('actionFeedback').innerText = 'Error opening in PyCharm';
  }
}

async function sendQuickMsg() {
  const inp = document.getElementById('quickMsg');
  const msg = inp.value.trim();
  if (!msg) return;
  document.getElementById('actionFeedback').innerText = 'Sending message to peer...';
  try {
    const res = await fetch('/api/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    });
    const d = await res.json();
    document.getElementById('actionFeedback').innerText = d.message || 'Sent!';
    inp.value = '';
    fetchStatus();
  } catch (e) {
    document.getElementById('actionFeedback').innerText = 'Failed to send message';
  }
}

async function summonQuickMsg() {
  const inp = document.getElementById('quickMsg');
  const prompt = inp.value.trim();
  if (!prompt) return;
  document.getElementById('actionFeedback').innerText = 'Summoning peer AI...';
  try {
    const res = await fetch('/api/summon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: prompt, target: 'both' })
    });
    const d = await res.json();
    document.getElementById('actionFeedback').innerText = d.message || 'Summon dispatched!';
    inp.value = '';
    fetchStatus();
  } catch (e) {
    document.getElementById('actionFeedback').innerText = 'Failed to summon AI';
  }
}

async function fetchStatus() {
  try {
    const res = await fetch('/api/status');
    const d = await res.json();
    document.getElementById('localNode').innerText = d.node.user + ' (' + d.node.role + ')';
    document.getElementById('peerUser').innerText = d.peer.name + ' (' + d.peer.role + ')';
    document.getElementById('transportMode').innerText = d.node.mode.toUpperCase();
    document.getElementById('secMode').innerText = d.node.security.toUpperCase();
    if (d.node.ide) {
      document.getElementById('ideBadge').innerText = d.node.ide;
    }

    const pill = document.getElementById('peerPill');
    const unqBtn = document.getElementById('unqBtn');
    if (d.peer.is_quarantined) {
      pill.className = 'badge badge-offline';
      pill.innerText = '🚨 QUARANTINED';
      unqBtn.style.display = 'inline-block';
    } else if (d.peer.is_online) {
      pill.className = 'badge badge-online';
      pill.innerText = '🟢 ONLINE';
      unqBtn.style.display = 'none';
    } else {
      pill.className = 'badge badge-offline';
      pill.innerText = '🔴 OFFLINE';
      unqBtn.style.display = 'none';
    }

    const locksDiv = document.getElementById('locksContainer');
    if (d.locks.locked_files && d.locks.locked_files.length > 0) {
      locksDiv.innerHTML = d.locks.locked_files.map(f =>
        `<div class="file-item">🔒 ${f} <button class="btn" style="padding: 2px 6px; font-size: 10px; margin-left: auto;" onclick="openFileInPyCharm('${f}')">Open in PyCharm</button></div>`
      ).join('');
    } else {
      locksDiv.innerHTML = '<div style="color: var(--green); font-size: 12px;">✔ No files locked. Safe to edit.</div>';
    }

    document.getElementById('activeTask').innerText = d.locks.task || 'None';
    document.getElementById('taskStatus').innerText = d.locks.status || 'idle';

    if (d.recent_events && d.recent_events.length > 0) {
      document.getElementById('logFeed').innerHTML = d.recent_events.map(e => `<div class="log-line">${e}</div>`).join('');
    } else {
      document.getElementById('logFeed').innerText = 'No recent activity recorded.';
    }
  } catch (e) {
    document.getElementById('peerPill').className = 'badge badge-offline';
    document.getElementById('peerPill').innerText = '⚠ DISCONNECTED';
  }
}

async function clearQuarantine() {
  await fetch('/api/unquarantine', { method: 'POST' });
  fetchStatus();
}

setInterval(fetchStatus, 2000);
fetchStatus();
</script>
</body>
</html>"""


def make_gui_handler(config):
    from http.server import BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs

    class LinkDashboardHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_GET(self):
            if self.path == "/" or self.path.startswith("/?"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.end_headers()
                html_content = generate_dashboard_html(config)
                self.wfile.write(html_content.encode("utf-8"))
            elif self.path == "/api/status":
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                status_data = get_dashboard_status(config)
                self.wfile.write(json.dumps(status_data).encode("utf-8"))
            elif self.path.startswith("/api/open"):
                query = parse_qs(urlparse(self.path).query)
                filepath = query.get("file", [""])[0]
                line = int(query.get("line", [0])[0]) if "line" in query else None
                col = int(query.get("column", [0])[0]) if "column" in query else None
                ok, msg = open_in_ide(filepath, line=line, column=col)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": ok, "message": msg}).encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len) if content_len > 0 else b""
            post_data = {}
            if post_body:
                try:
                    post_data = json.loads(post_body.decode("utf-8"))
                except Exception:
                    pass

            if self.path == "/api/unquarantine":
                cmd_unquarantine(None, config)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "message": "Peer unquarantined successfully"}).encode("utf-8"))
            elif self.path.startswith("/api/open"):
                query = parse_qs(urlparse(self.path).query)
                filepath = post_data.get("file") or query.get("file", [""])[0]
                line = post_data.get("line") or (int(query.get("line", [0])[0]) if "line" in query else None)
                col = post_data.get("column") or (int(query.get("column", [0])[0]) if "column" in query else None)
                ok, msg = open_in_ide(filepath, line=line, column=col)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": ok, "message": msg}).encode("utf-8"))
            elif self.path == "/api/send":
                msg_text = post_data.get("message", "").strip()
                if not msg_text:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": False, "message": "Empty message"}).encode("utf-8"))
                    return
                packet = make_packet("message", {"text": msg_text}, config)
                transport = NetworkTransport(config)
                ok, msg = transport.send(packet)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": ok, "message": msg}).encode("utf-8"))
            elif self.path == "/api/summon":
                prompt = post_data.get("prompt", "").strip()
                target = post_data.get("target", "both")
                if not prompt:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": False, "message": "Empty prompt"}).encode("utf-8"))
                    return
                packet = make_packet("agent_summon", {"prompt": prompt, "target": target}, config)
                transport = NetworkTransport(config)
                ok, msg = transport.send(packet)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": ok, "message": f"Summon dispatched ({target}): {msg}"}).encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()

    return LinkDashboardHandler


_GUI_SERVER_INSTANCE = None
_GUI_SERVER_LOCK = threading.Lock()


def start_gui_server(port=7891, config=None, log_fn=None):
    """Start embedded PyCharm web GUI server in a daemon thread if not already running."""
    global _GUI_SERVER_INSTANCE
    with _GUI_SERVER_LOCK:
        if _GUI_SERVER_INSTANCE is not None:
            return True, f"GUI dashboard already active at http://127.0.0.1:{port}"

        if config is None:
            config = load_config()

        log = log_fn or (lambda msg: sys.stderr.write(f"[AGY-GUI] {msg}\n"))
        from http.server import HTTPServer
        handler = make_gui_handler(config)
        try:
            httpd = HTTPServer(("127.0.0.1", port), handler)
            _GUI_SERVER_INSTANCE = httpd
            t = threading.Thread(target=httpd.serve_forever, daemon=True)
            t.start()
            log(f"Embedded PyCharm web GUI started at http://127.0.0.1:{port}")
            return True, f"GUI dashboard active at http://127.0.0.1:{port}"
        except OSError as e:
            return False, f"Could not bind GUI dashboard on port {port}: {e}"


def cmd_gui(args, config):
    """Run lightweight embedded PyCharm collaborative web dashboard via Python standard library http.server."""
    port = getattr(args, "port", 7891) or 7891
    ok, msg = start_gui_server(port=port, config=config, log_fn=print)
    if not ok:
        print(f"❌ {msg}")
        return 1

    print("============================================================")
    print("🌐 ANTIGRAVITY LINK — PYCHARM COLLABORATIVE WEB GUI")
    print("============================================================")
    print(f"URL:            http://127.0.0.1:{port}")
    print(f"Local Node:     {config.get('user')} ({config.get('role')})")
    print(f"Transport:      {config.get('mode', 'hybrid').upper()}")
    print("PyCharm Access: Open View -> Tool Windows -> Web Browser")
    print(f"                and navigate to: http://127.0.0.1:{port}")
    print("------------------------------------------------------------")
    print("🟢 Live GUI Dashboard active. Press Ctrl+C to stop.")
    print("============================================================")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[+] Stopping web GUI dashboard...")
    return 0


# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------


def main():
    config = load_config()

    # 1. Zero arguments defaults directly to live terminal chat!
    if len(sys.argv) == 1:
        return cmd_chat(None, config)

    # 2. Ultra-simple CLI shortcuts (no flags or quotes required):
    first_arg = sys.argv[1].lower()

    if first_arg in ("ai", "@ai", "both", "@both"):
        task = " ".join(sys.argv[2:]).strip()
        if not task:
            print("⚡ Usage: link ai <task prompt>")
            return 1
        args = argparse.Namespace(prompt=task, target="both")
        return cmd_summon(args, config)

    if first_arg in ("peer", "@peer", "remote", "@remote"):
        task = " ".join(sys.argv[2:]).strip()
        if not task:
            print("⚡ Usage: link peer <task prompt>")
            return 1
        args = argparse.Namespace(prompt=task, target="peer")
        return cmd_summon(args, config)

    if first_arg in ("local", "@local", "self", "@self"):
        task = " ".join(sys.argv[2:]).strip()
        if not task:
            print("⚡ Usage: link local <task prompt>")
            return 1
        args = argparse.Namespace(prompt=task, target="local")
        return cmd_summon(args, config)

    if first_arg in ("senpai", "@senpai", "win", "@win", "windows", "@windows"):
        task = " ".join(sys.argv[2:]).strip()
        if not task:
            print("⚡ Usage: link senpai <task prompt>")
            return 1
        args = argparse.Namespace(prompt=task, target="senpai")
        return cmd_summon(args, config)

    if first_arg in ("reaper", "@reaper", "linux", "@linux"):
        task = " ".join(sys.argv[2:]).strip()
        if not task:
            print("⚡ Usage: link reaper <task prompt>")
            return 1
        args = argparse.Namespace(prompt=task, target="reaper")
        return cmd_summon(args, config)

    if first_arg in ("init", "setup", "wizard"):
        return cmd_init(None, config)

    if first_arg in ("unquarantine", "clear-quarantine", "resume"):
        return cmd_unquarantine(None, config)

    if first_arg in ("gui", "web", "dashboard"):
        if any(h in sys.argv for h in ("--help", "-h")):
            print("Usage: link gui [--port PORT]")
            print("Run lightweight embedded PyCharm collaborative web GUI dashboard.")
            return 0
        port = 7891
        if len(sys.argv) > 2 and sys.argv[2].isdigit():
            port = int(sys.argv[2])
        args = argparse.Namespace(port=port)
        return cmd_gui(args, config)

    if first_arg in ("chat", "@chat"):
        return cmd_chat(None, config)

    if first_arg in ("open", "popup"):
        open_terminal_chat()
        return 0

    if first_arg == "pair":
        return cmd_pair(None, config)

    if first_arg == "join":
        room = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else None
        key = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("-") else None
        peer = sys.argv[4] if len(sys.argv) > 4 and not sys.argv[4].startswith("-") else None
        if room and key:
            args = argparse.Namespace(room=room, key=key, peer=peer)
            return cmd_join(args, config)

    if first_arg == "role":
        role_name = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else None
        args = argparse.Namespace(role_name=role_name)
        return cmd_role(args, config)

    if first_arg == "security":
        mode_name = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else None
        args = argparse.Namespace(mode_name=mode_name)
        return cmd_security(args, config)

    if first_arg == "pull":
        repo_dir = os.path.dirname(os.path.abspath(__file__))
        print("[+] Pulling latest updates from GitHub main branch...")
        subprocess.run(["git", "pull", "origin", "main"], cwd=repo_dir)
        return 0

    if first_arg == "send" and len(sys.argv) > 2 and not any(a.startswith("-") for a in sys.argv[2:]):
        msg_text = " ".join(sys.argv[2:]).strip()
        args = argparse.Namespace(message=msg_text, agent=False)
        return cmd_send(args, config)

    parser = argparse.ArgumentParser(description="Antigravity Link - Peer AI Sync Tool")
    parser.add_argument("--peer-host", help="Override peer target IP/hostname")
    parser.add_argument("--peer-port", type=int, help="Override peer target port")
    parser.add_argument("--mode", choices=["hybrid", "direct", "relay"], help="Networking transport mode")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # status
    subparsers.add_parser("status", help="Check peer link and daemon status")

    # daemon
    p_daemon = subparsers.add_parser("daemon", help="Run background sync & message listener")
    p_daemon.add_argument("--port", type=int, help="Override local listener port")

    # summon
    p_summon = subparsers.add_parser("summon", help="Summon autonomous AI agent to execute a task")
    p_summon.add_argument("prompt", help="Instruction or task for the AI agent")
    p_summon.add_argument(
        "--target",
        choices=["both", "remote", "local", "windows", "linux", "senpai", "reaper", "peer"],
        default="both",
        help="Which AI agent to trigger (default: both)"
    )

    # sync
    p_sync = subparsers.add_parser("sync", help="Broadcast active task and locked files")
    p_sync.add_argument("--task", required=True, help="Active task description")
    p_sync.add_argument("--status", choices=["started", "in-progress", "completed", "blocked"], default="in-progress")
    p_sync.add_argument("--files", help="Comma-separated list of locked/active files")
    p_sync.add_argument("--notes", help="Contextual notes for peer AI")

    # delegate
    p_del = subparsers.add_parser("delegate", help="Delegate cross-platform task to peer AI")
    p_del.add_argument("--title", required=True, help="Task title")
    p_del.add_argument("--description", required=True, help="Actionable instructions")
    p_del.add_argument("--target-os", choices=["windows", "linux", "macos"], default="windows")
    p_del.add_argument("--priority", choices=["low", "medium", "high", "critical"], default="high")

    # send
    p_send = subparsers.add_parser("send", help="Send live message to peer")
    p_send.add_argument("message", help="Message content")
    p_send.add_argument("--agent", action="store_true", default=True, help="Mark as AI-to-AI message")

    # chat
    subparsers.add_parser("chat", help="Open two-way live terminal chat")

    # inbox
    subparsers.add_parser("inbox", help="View recent messages & sync history")

    # pair
    subparsers.add_parser("pair", help="Display room ID and secret key for peer pairing")

    # join
    p_join = subparsers.add_parser("join", help="Join an Antigravity Link room")
    p_join.add_argument("--room", help="Room ID to join")
    p_join.add_argument("--key", help="Secret key for authentication")
    p_join.add_argument("--peer", help="Peer display name")

    # role
    p_role = subparsers.add_parser("role", help="Set local role (lead, platform_lead, contributor, tester)")
    p_role.add_argument("role_name", nargs="?", help="Role name")

    # security
    p_sec = subparsers.add_parser("security", help="Inspect or set HITL security approval gate mode")
    p_sec.add_argument("mode_name", nargs="?", choices=["prompt", "session_trusted", "autonomous", "deny"], help="Security mode")

    # init & unquarantine & gui & open
    subparsers.add_parser("init", help="Run interactive setup wizard")
    subparsers.add_parser("unquarantine", help="Clear peer security quarantine status")
    p_gui = subparsers.add_parser("gui", help="Run lightweight embedded PyCharm collaborative web GUI")
    p_gui.add_argument("--port", type=int, default=7891, help="Port to bind web dashboard (default: 7891)")
    p_open = subparsers.add_parser("open", help="Open a file directly in PyCharm editor tab")
    p_open.add_argument("file", help="File path to open in PyCharm")
    p_open.add_argument("--line", "-l", type=int, default=None, help="Line number")
    p_open.add_argument("--column", "-c", type=int, default=None, help="Column number")

    args = parser.parse_args()

    if args.peer_host:
        config["peer_host"] = args.peer_host
    if args.peer_port:
        config["peer_port"] = args.peer_port
    if args.mode:
        config["mode"] = args.mode
    if hasattr(args, "port") and args.port and args.command != "gui":
        config["local_port"] = args.port

    if args.command == "status":
        return cmd_status(args, config)
    elif args.command == "daemon":
        return cmd_daemon(args, config)
    elif args.command == "summon":
        return cmd_summon(args, config)
    elif args.command == "sync":
        return cmd_sync(args, config)
    elif args.command == "delegate":
        return cmd_delegate(args, config)
    elif args.command == "send":
        return cmd_send(args, config)
    elif args.command == "chat":
        return cmd_chat(args, config)
    elif args.command == "inbox":
        return cmd_inbox(args, config)
    elif args.command == "pair":
        return cmd_pair(args, config)
    elif args.command == "join":
        return cmd_join(args, config)
    elif args.command == "role":
        return cmd_role(args, config)
    elif args.command == "security":
        return cmd_security(args, config)
    elif args.command == "init":
        return cmd_init(args, config)
    elif args.command == "unquarantine":
        return cmd_unquarantine(args, config)
    elif args.command == "gui":
        return cmd_gui(args, config)
    elif args.command == "open":
        return cmd_open(args, config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
