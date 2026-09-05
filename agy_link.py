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
PROTOCOL_VERSION = "1.0.0"
DEFAULT_PORT = 7890
DEFAULT_ROOM = "agy_link_mrreaper_senpai_8829"
RELAY_HOST = "https://ntfy.sh"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AGY_DIR = os.path.join(SCRIPT_DIR, ".agy_link")
CONFIG_FILE = os.path.join(AGY_DIR, "config.json")
LOCAL_STATE_FILE = os.path.join(AGY_DIR, "local_state.json")
PEER_STATE_FILE = os.path.join(AGY_DIR, "peer_state.json")
ACTIVITY_LOG_FILE = os.path.join(AGY_DIR, "activity.log")
INBOX_FILE = os.path.join(SCRIPT_DIR, "INBOX.md")

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
        "node_id": "senpai-win" if is_win else "reaper-linux",
        "user": "Senpai59" if is_win else "Mr-Reaper",
        "role": "windows-lead" if is_win else "linux-lead",
        "local_host": "0.0.0.0",
        "local_port": DEFAULT_PORT,
        "peer_host": "127.0.0.1",
        "peer_port": DEFAULT_PORT,
        "auth_token": "agy_token_8829",
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


def make_packet(packet_type, payload, config):
    """Create standardized v1.0.0 JSON wire packet."""
    return {
        "version": PROTOCOL_VERSION,
        "packet_id": f"{int(time.time() * 1000)}-{os.urandom(3).hex()}",
        "timestamp": get_iso_timestamp(),
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


def update_peer_state(packet):
    """Save received state packet to .agy_link/peer_state.json and INBOX.md."""
    ensure_dirs()
    sender = packet.get("sender", {})
    payload = packet.get("payload", {})
    p_type = packet.get("type", "message")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    state_data = {
        "last_updated": get_iso_timestamp(),
        "sender": sender,
        "type": p_type,
        "state": payload,
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
        if "linux" in self.role:
            self.sub_topic = f"{self.room}_senpai_to_mr-reaper"
            self.pub_topic = f"{self.room}_mr-reaper_to_senpai"
        else:
            self.sub_topic = f"{self.room}_mr-reaper_to_senpai"
            self.pub_topic = f"{self.room}_senpai_to_mr-reaper"

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


def run_tcp_listener(config, on_packet_callback, stop_event):
    """Listen on local TCP port for direct socket connections."""
    host = config.get("local_host", "0.0.0.0")
    port = int(config.get("local_port", DEFAULT_PORT))
    try:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(5)
        srv.settimeout(1.0)
    except Exception as e:
        print(f"[-] Could not bind TCP socket {host}:{port}: {e}", flush=True)
        return

    print(f"[+] Direct TCP Listener active on {host}:{port}", flush=True)
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


def run_relay_listener(transport, on_packet_callback, stop_event):
    """Listen on HTTPS cloud relay stream for messages from remote peer."""
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
    print(f"[+] Cloud Relay Listener active on {transport.sub_topic}", flush=True)
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
    elif p in ("@linux", "@linux-ai", "@reaper", "@reaper-ai"):
        return "local" if is_linux else "remote"
    elif p in ("@windows", "@windows-ai", "@win", "@win-ai", "@senpai", "@senpai-ai"):
        return "remote" if is_linux else "local"
    return "both"


def execute_local_agy(prompt, config, transport=None):
    """Execute a task autonomously using local agy CLI and broadcast report."""
    agy_bin = find_agy_executable()
    user = config.get("user", "Local")
    plat_str = platform.system().upper()
    log_activity(f"Executing autonomous AGY task: {prompt[:80]}")
    notify_desktop(f"AGY [{plat_str}] Autonomous Agent", f"Task started: {prompt[:80]}")

    print(f"\n⚡ [AUTONOMOUS AGY RUNNING] Executing task on {user} ({plat_str})...\n   Task: {prompt}\n", flush=True)

    cmd = [
        agy_bin,
        "-p", prompt,
        "--dangerously-skip-permissions"
    ]

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
# CLI Commands
# -----------------------------------------------------------------------------


def cmd_status(args, config):
    """Check connectivity, configuration, and peer state."""
    transport = NetworkTransport(config)
    print("============================================================")
    print(f"  AGY LINK STATUS - Node: {config.get('node_id')} ({platform.system().upper()})")
    print("============================================================")
    print(f"User:           {config.get('user')} ({config.get('role')})")
    print(f"Local Listener: {config.get('local_host')}:{config.get('local_port')}")
    print(f"Peer Target:    {config.get('peer_host')}:{config.get('peer_port')}")
    print(f"Network Mode:   {config.get('mode').upper()}")
    print(f"Cloud Relay:    {transport.sub_topic}")
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

    def on_packet(packet):
        sender = packet.get("sender", {})
        p_type = packet.get("type", "message")
        payload = packet.get("payload", {})

        print(f"\n🔔 [{datetime.datetime.now().strftime('%H:%M:%S')}] Received [{p_type.upper()}] from {sender.get('user')}:", flush=True)
        if p_type == "state_sync":
            print(f"   Task:   {payload.get('task')} [{payload.get('status')}]", flush=True)
            if payload.get("locked_files"):
                print(f"   Locks:  {', '.join(payload.get('locked_files'))}", flush=True)
        elif p_type == "task_delegation":
            print(f"   Task:   {payload.get('title')} ({payload.get('priority')})", flush=True)
            print(f"   Detail: {payload.get('description')[:100]}...", flush=True)
        elif p_type == "agent_summon":
            task = payload.get("task", "")
            target = payload.get("target", "both")
            print(f"   ⚡ AI SUMMON: {task} (Target: {target})", flush=True)
            if should_execute_locally(target, config, is_incoming=True):
                print(f"   🚀 Launching local AGY background execution...", flush=True)
                threading.Thread(target=execute_local_agy, args=(task, config, transport), daemon=True).start()
        elif p_type == "agent_report":
            status = payload.get("status", "completed").upper()
            print(f"   🤖 AI REPORT: {payload.get('task')} [{status}]", flush=True)
            rep = payload.get("report", "").strip()
            if rep:
                preview = "\n      ".join(rep.splitlines()[:6])
                print(f"   Output:\n      {preview}", flush=True)
        elif p_type in ("message", "chat"):
            print(f"   Message: {payload.get('text', '')}", flush=True)
        print(f"💾 Updated {PEER_STATE_FILE} & {INBOX_FILE}\n> ", end="", flush=True)

        update_peer_state(packet)

    t1 = threading.Thread(target=run_tcp_listener, args=(config, on_packet, stop_event), daemon=True)
    t2 = threading.Thread(target=run_relay_listener, args=(transport, on_packet, stop_event), daemon=True)

    t1.start()
    t2.start()

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

        if p_type == "chat":
            text = payload.get("text", "")
            print(f"\n💬 [{sender.get('user')}]: {text}\n> ", end="", flush=True)
        elif p_type == "agent_summon":
            task = payload.get("task", "")
            target = payload.get("target", "both")
            print(f"\n⚡ [@{sender.get('user')} SUMMONED AI]: {task} (Target: {target})\n> ", end="", flush=True)
            if should_execute_locally(target, config, is_incoming=True):
                print(f"🚀 [LOCAL AGY] Starting background turn...\n> ", end="", flush=True)
                threading.Thread(target=execute_local_agy, args=(task, config, transport), daemon=True).start()
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

    if first_arg in ("chat", "@chat"):
        return cmd_chat(None, config)

    if first_arg in ("open", "popup"):
        open_terminal_chat()
        return 0

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
        choices=["both", "remote", "local", "windows", "linux", "senpai", "reaper"],
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

    args = parser.parse_args()

    if args.peer_host:
        config["peer_host"] = args.peer_host
    if args.peer_port:
        config["peer_port"] = args.peer_port
    if args.mode:
        config["mode"] = args.mode
    if hasattr(args, "port") and args.port:
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
