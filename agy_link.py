#!/usr/bin/env python3
"""
Antigravity Link (agy_link.py)
==============================
A tiny, zero-dependency peer-to-peer communication bridge connecting two
Antigravity (AGY) AI assistants running on different computers over the internet.

Features:
  - Zero Setup / Zero Port-Forwarding: Connects over an encrypted private room.
  - Cross-Platform: 100% Python standard library. Runs on Windows, Linux, and macOS.
  - AI Sync: Incoming messages are saved to INBOX.md and LATEST.json for instant AI reading.
  - Direct IP support: Optional raw TCP socket mode (--direct --ip <ip>).
  - Terminal Chat: Optional live two-way chat mode for humans & AIs.

Usage:
  # Background listener (leave running in a terminal or background):
  python agy_link.py listen

  # Send a message / task / code snippet to the other AI:
  python agy_link.py send "Hey! What are you working on right now?"

  # View what the other AI sent:
  python agy_link.py inbox

  # Live two-way chat mode:
  python agy_link.py chat
"""

import argparse
import datetime
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

# Default shared secret room (match this on both computers)
DEFAULT_ROOM = "agy_link_mrreaper_senpai_8829"
RELAY_HOST = "https://ntfy.sh"

INBOX_FILE = "INBOX.md"
LATEST_FILE = "LATEST.json"
CONFIG_FILE = "config.json"


def load_config():
    """Load or create local configuration."""
    cfg = {"user": "User", "peer": "Peer", "room": DEFAULT_ROOM}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg.update(json.load(f))
        except Exception:
            pass
    return cfg


def save_config(cfg):
    """Save local configuration."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


def notify_desktop(title, message):
    """Trigger a native desktop notification on Linux or Windows."""
    system = platform.system()
    try:
        if system == "Linux" and shutil.which("notify-send"):
            subprocess.run(["notify-send", "-a", "Antigravity Link", title, message[:100]], check=False)
        elif system == "Windows":
            ps = (
                f'[reflection.assembly]::loadwithpartialname("System.Windows.Forms");'
                f'$n = new-object system.windows.forms.notifyicon;'
                f'$n.icon = [system.drawing.systemicons]::Information;'
                f'$n.visible = $true;'
                f'$n.showballoontip(10, "{title}", "{message[:100]}", [system.windows.forms.tooltipicon]::Info);'
            )
            subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=False, timeout=3)
    except Exception:
        pass


class AgyLink:
    def __init__(self, user="Mr-Reaper", peer="Senpai", room=DEFAULT_ROOM, mode="relay", ip="127.0.0.1", port=9988):
        self.user = user
        self.peer = peer
        self.room = room
        self.mode = mode
        self.ip = ip
        self.port = port
        self.running = True

        # Topics: unique channels for send/receive based on user names
        # Channel A -> B and Channel B -> A
        pair = sorted([self.user.lower(), self.peer.lower()])
        self.channel_1 = f"{self.room}_{pair[0]}_to_{pair[1]}"
        self.channel_2 = f"{self.room}_{pair[1]}_to_{pair[0]}"

        if self.user.lower() == pair[0]:
            self.pub_topic = self.channel_1
            self.sub_topic = self.channel_2
        else:
            self.pub_topic = self.channel_2
            self.sub_topic = self.channel_1

    # -------------------------------------------------------------------------
    # Relay Network (Cloud Pub/Sub - Zero Config)
    # -------------------------------------------------------------------------

    def send_relay(self, payload):
        """Send message via HTTPS relay."""
        url = f"{RELAY_HOST}/{self.pub_topic}"
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Title": f"AGY Message from {self.user}",
                "Tags": "robot,zap",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status in (200, 201)
        except Exception as e:
            print(f"[Error] Failed to send: {e}", file=sys.stderr)
            return False

    def listen_relay(self, callback):
        """Listen for incoming messages in real-time with catch-up."""
        seen_ids = set()

        # Catch-up on recent messages
        try:
            poll_url = f"{RELAY_HOST}/{self.sub_topic}/json?poll=1"
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
                        if event.get("event") == "message":
                            raw = event.get("message", "")
                            payload = json.loads(raw) if raw.startswith("{") else {"sender": self.peer, "content": raw}
                            callback(payload)
                    except Exception:
                        pass
        except Exception:
            pass

        # Real-time stream
        stream_url = f"{RELAY_HOST}/{self.sub_topic}/json"
        while self.running:
            try:
                req = urllib.request.Request(stream_url, headers={"User-Agent": "AgyLink/1.0"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    for line in resp:
                        if not self.running:
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
                                payload = json.loads(raw) if raw.startswith("{") else {"sender": self.peer, "content": raw}
                                callback(payload)
                        except Exception:
                            pass
            except Exception:
                time.sleep(2)

    # -------------------------------------------------------------------------
    # Direct IP Network (Optional Raw Socket)
    # -------------------------------------------------------------------------

    def send_direct(self, payload):
        """Send via direct TCP socket."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((self.ip, self.port))
            data = (json.dumps(payload) + "\n").encode("utf-8")
            s.sendall(data)
            s.close()
            return True
        except Exception as e:
            print(f"[Direct Error] {e}", file=sys.stderr)
            return False

    def listen_direct(self, callback):
        """Listen on raw TCP socket."""
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((self.ip, self.port))
        srv.listen(1)
        print(f"[Direct IP] Listening on {self.ip}:{self.port}...")
        while self.running:
            try:
                srv.settimeout(1.0)
                try:
                    conn, addr = srv.accept()
                except socket.timeout:
                    continue
                buffer = ""
                while self.running:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    buffer += chunk.decode("utf-8", errors="replace")
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        if line.strip():
                            try:
                                callback(json.loads(line.strip()))
                            except Exception:
                                pass
                conn.close()
            except Exception:
                time.sleep(1)

    # -------------------------------------------------------------------------
    # Routing
    # -------------------------------------------------------------------------

    def send(self, payload):
        if self.mode == "direct":
            return self.send_direct(payload)
        return self.send_relay(payload)

    def listen(self, callback):
        if self.mode == "direct":
            return self.listen_direct(callback)
        return self.listen_relay(callback)


def save_message_to_inbox(payload):
    """Append incoming message to INBOX.md and overwrite LATEST.json."""
    sender = payload.get("sender", "Peer AI")
    content = payload.get("content", "").strip()
    timestamp = payload.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    msg_type = payload.get("type", "message").upper()
    topic = payload.get("topic", "")

    # Save to LATEST.json
    try:
        with open(LATEST_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    # Append to INBOX.md
    if not os.path.exists(INBOX_FILE):
        header = (
            "# 🤖 Antigravity Peer Inbox\n"
            "Incoming messages, instructions, and collaboration updates from your peer AI.\n\n"
        )
        with open(INBOX_FILE, "w", encoding="utf-8") as f:
            f.write(header)

    entry = f"\n---\n\n### 📨 [{msg_type}] From `{sender}` — `{timestamp}`\n"
    if topic:
        entry += f"**Topic / Task:** {topic}  \n"
    entry += f"\n{content}\n"

    with open(INBOX_FILE, "a", encoding="utf-8") as f:
        f.write(entry)

    notify_desktop(f"Antigravity from {sender}", content[:80])


def on_message_received(payload):
    """Callback triggered on incoming message."""
    sender = payload.get("sender", "Peer AI")
    content = payload.get("content", "").strip()
    timestamp = payload.get("timestamp", datetime.datetime.now().strftime("%H:%M:%S"))
    topic = payload.get("topic", "")

    print(f"\n🔔 [{timestamp}] Message from @{sender}:", flush=True)
    if topic:
        print(f"📌 Topic: {topic}", flush=True)
    print(f"{content}\n", flush=True)
    print(f"💾 Recorded in {INBOX_FILE} & {LATEST_FILE}", flush=True)
    print("> ", end="", flush=True)

    save_message_to_inbox(payload)


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------


def cmd_listen(link, _):
    """Start listening daemon."""
    print("=" * 60)
    print("🤖 ANTIGRAVITY LINK — LIVE AGENT MESH")
    print("=" * 60)
    print(f"Local User : {link.user}")
    print(f"Peer User  : {link.peer}")
    print(f"Room ID    : {link.room}")
    print(f"Network    : {'Cloud Relay (Zero-Config)' if link.mode == 'relay' else f'Direct ({link.ip}:{link.port})'}")
    print(f"Inbox File : {os.path.abspath(INBOX_FILE)}")
    print("=" * 60)
    print("🟢 Connected. Waiting for messages from peer AI... (Press Ctrl+C to exit)\n")

    try:
        link.listen(on_message_received)
    except KeyboardInterrupt:
        print("\n🛑 Link stopped.")


def cmd_send(link, args):
    """Send a message to peer."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "sender": link.user,
        "recipient": link.peer,
        "type": args.type,
        "topic": args.topic or "",
        "content": args.message,
        "timestamp": now_str,
    }
    print(f"🚀 Sending message to {link.peer}...", end=" ", flush=True)
    if link.send(payload):
        print("✅ Delivered!")
        return 0
    print("❌ Delivery failed.")
    return 1


def cmd_chat(link, _):
    """Interactive terminal chat."""
    print("=" * 60)
    print(f"💬 ANTIGRAVITY LIVE CHAT: @{link.user} ⟷ @{link.peer}")
    print("=" * 60)
    print("Type your message and press ENTER. Type 'exit' to quit.\n")

    t = threading.Thread(target=link.listen, args=(on_message_received,), daemon=True)
    t.start()

    while True:
        try:
            msg = input("> ").strip()
            if not msg:
                continue
            if msg.lower() in ("exit", "quit"):
                break
            payload = {
                "sender": link.user,
                "recipient": link.peer,
                "type": "chat",
                "content": msg,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            link.send(payload)
        except (KeyboardInterrupt, EOFError):
            break
    link.running = False
    print("\nChat closed.")
    return 0


def cmd_inbox(_, __):
    """Print the contents of INBOX.md."""
    if not os.path.exists(INBOX_FILE):
        print("📭 Inbox is empty. No messages received yet.")
        return 0
    with open(INBOX_FILE, "r", encoding="utf-8") as f:
        print(f.read())
    return 0


# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------


def main():
    cfg = load_config()

    parser = argparse.ArgumentParser(description="Antigravity Link: Peer AI Sync Tool")
    parser.add_argument("--user", default=cfg.get("user", "Mr-Reaper"), help="Your display name / role")
    parser.add_argument("--peer", default=cfg.get("peer", "Senpai"), help="Remote peer's display name / role")
    parser.add_argument("--room", default=cfg.get("room", DEFAULT_ROOM), help="Shared private room secret")
    parser.add_argument("--direct", action="store_true", help="Use direct TCP socket instead of cloud relay")
    parser.add_argument("--ip", default="0.0.0.0", help="IP address for direct TCP socket")
    parser.add_argument("--port", type=int, default=9988, help="Port for direct TCP socket")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # listen
    subparsers.add_parser("listen", help="Run live background listener daemon")

    # send
    p_send = subparsers.add_parser("send", help="Send a message to peer AI")
    p_send.add_argument("message", help="Message text / instructions / code snippet")
    p_send.add_argument("--topic", help="Optional task or topic title")
    p_send.add_argument("--type", default="message", help="Message category (message, task, code, question)")

    # chat
    subparsers.add_parser("chat", help="Open two-way live terminal chat")

    # inbox
    subparsers.add_parser("inbox", help="View recent incoming messages")

    args = parser.parse_args()

    # Save configuration preferences
    cfg["user"] = args.user
    cfg["peer"] = args.peer
    cfg["room"] = args.room
    save_config(cfg)

    link = AgyLink(
        user=args.user,
        peer=args.peer,
        room=args.room,
        mode="direct" if args.direct else "relay",
        ip=args.ip,
        port=args.port,
    )

    if args.command == "listen":
        return cmd_listen(link, args)
    elif args.command == "send":
        return cmd_send(link, args)
    elif args.command == "chat":
        return cmd_chat(link, args)
    elif args.command == "inbox":
        return cmd_inbox(link, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
