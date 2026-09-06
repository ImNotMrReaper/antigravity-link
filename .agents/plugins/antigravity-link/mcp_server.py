#!/usr/bin/env python3
"""
Antigravity Link MCP Server
Exposes Antigravity Link peer collaboration tools over Model Context Protocol (stdio).
"""

import json
import os
import sys
import shutil
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def find_agy_link():
    # 1. repo_path.txt if written during global plugin install
    repo_txt = os.path.join(SCRIPT_DIR, "repo_path.txt")
    if os.path.exists(repo_txt):
        try:
            with open(repo_txt, "r", encoding="utf-8") as f:
                p = f.read().strip()
                candidate = os.path.join(p, "agy_link.py")
                if os.path.exists(candidate):
                    return candidate
        except Exception:
            pass

    # 2. Local in same directory
    local_candidate = os.path.join(SCRIPT_DIR, "agy_link.py")
    if os.path.exists(local_candidate):
        return local_candidate

    # 3. Workspace root (3 levels up: .agents/plugins/antigravity-link -> repo root)
    up_3 = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR))), "agy_link.py")
    if os.path.exists(up_3):
        return up_3

    # 4. Find via 'link' command in PATH
    link_bin = shutil.which("link") or shutil.which("link.cmd")
    if link_bin:
        # On Linux ~/.local/bin/link might be a script, or on Windows link.cmd in repo
        candidate = os.path.join(os.path.dirname(os.path.abspath(link_bin)), "agy_link.py")
        if os.path.exists(candidate):
            return candidate

    # 5. Common repo locations
    user_home = os.path.expanduser("~")
    for base in ["PycharmProjects/antigravity-link", "antigravity-link", "Desktop/antigravity-link"]:
        c = os.path.join(user_home, base, "agy_link.py")
        if os.path.exists(c):
            return c

    return "agy_link.py"


# Ensure agy_link can be imported directly
_agy_path = find_agy_link()
if os.path.exists(_agy_path):
    _agy_dir = os.path.dirname(os.path.abspath(_agy_path))
    if _agy_dir not in sys.path:
        sys.path.insert(0, _agy_dir)

try:
    import agy_link
except Exception:
    agy_link = None


def run_agy_link(args):
    agy_link_py = find_agy_link()
    work_dir = os.path.dirname(os.path.abspath(agy_link_py)) if os.path.exists(agy_link_py) else None
    cmd = [sys.executable, agy_link_py] + args
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120, cwd=work_dir)
        return res.stdout.strip()
    except Exception as e:
        return f"Error running agy_link: {e}"



TOOLS = [
    {
        "name": "link_status",
        "description": "Check connection status and active locks of the peer AI station (Windows/Linux).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "link_summon",
        "description": "Summon the peer AI agent or both AI agents to autonomously execute a task and report back.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Actionable task or question for the AI agent(s)"
                },
                "target": {
                    "type": "string",
                    "enum": ["both", "remote", "local", "senpai", "reaper"],
                    "description": "Which station AI to summon (default: both)"
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "link_send",
        "description": "Send a chat message or note to the peer node.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Message text to send"
                }
            },
            "required": ["message"]
        }
    },
    {
        "name": "link_sync",
        "description": "Broadcast active task progress and lock files to prevent peer AI conflicts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Description of current task"
                },
                "status": {
                    "type": "string",
                    "enum": ["started", "in-progress", "completed", "blocked"],
                    "description": "Status of the task"
                },
                "files": {
                    "type": "string",
                    "description": "Comma-separated list of active/locked files"
                }
            },
            "required": ["task"]
        }
    },
    {
        "name": "link_inbox",
        "description": "Read recent peer messages and task handoffs from INBOX.md.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "link_open",
        "description": "Open a file directly in PyCharm IDE editor tab at an optional line and column.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "Path to file to open in PyCharm"
                },
                "line": {
                    "type": "integer",
                    "description": "Optional line number to navigate to"
                },
                "column": {
                    "type": "integer",
                    "description": "Optional column number to navigate to"
                }
            },
            "required": ["file"]
        }
    },
    {
        "name": "link_gui",
        "description": "Get the URL and access instructions for the PyCharm embedded collaborative web GUI dashboard.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "port": {
                    "type": "integer",
                    "description": "Port number for GUI dashboard (default: 7891)"
                }
            },
            "required": []
        }
    }
]


def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "antigravity-link",
                    "version": "1.0.0"
                }
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "link_status":
            output = run_agy_link(["status"])
        elif tool_name == "link_summon":
            prompt = args.get("prompt", "")
            target = args.get("target", "both")
            output = run_agy_link(["summon", prompt, "--target", target])
        elif tool_name == "link_send":
            msg = args.get("message", "")
            output = run_agy_link(["send", msg])
        elif tool_name == "link_sync":
            task = args.get("task", "")
            status = args.get("status", "in-progress")
            files = args.get("files", "")
            cmd_args = ["sync", "--task", task, "--status", status]
            if files:
                cmd_args.extend(["--files", files])
            output = run_agy_link(cmd_args)
        elif tool_name == "link_inbox":
            output = run_agy_link(["inbox"])
        elif tool_name == "link_open":
            file_arg = args.get("file", "")
            line_arg = args.get("line")
            col_arg = args.get("column")
            if agy_link is not None and hasattr(agy_link, "open_in_ide"):
                ok, msg = agy_link.open_in_ide(file_arg, line=line_arg, column=col_arg)
                output = f"[{'OK' if ok else 'FAILED'}] {msg}"
            else:
                cli_args = ["open", file_arg]
                if line_arg is not None:
                    cli_args.extend(["--line", str(line_arg)])
                if col_arg is not None:
                    cli_args.extend(["--column", str(col_arg)])
                output = run_agy_link(cli_args)
        elif tool_name == "link_gui":
            port = args.get("port", 7891)
            status_line = ""
            if agy_link is not None and hasattr(agy_link, "start_gui_server"):
                try:
                    ok, msg = agy_link.start_gui_server(port=port, log_fn=lambda m: sys.stderr.write(f"[MCP-GUI] {m}\n"))
                    status_line = f"Status: {msg}\n\n"
                except Exception as e:
                    status_line = f"Notice: {e}\n\n"
            output = (
                f"🌐 Antigravity Link — PyCharm Collaborative Web Dashboard\n"
                f"URL: http://127.0.0.1:{port}\n\n"
                f"{status_line}"
                f"PyCharm Access:\n"
                f"1. Open View -> Tool Windows -> Web Browser\n"
                f"2. Navigate to: http://127.0.0.1:{port}\n"
                f"3. Live peer telemetry, active locks, and one-click 'Open in PyCharm' buttons are active."
            )
        else:
            output = f"Unknown tool: {tool_name}"

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": output
                    }
                ]
            }
        }
    elif method == "notifications/initialized":
        return None
    elif req_id is not None:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }
    return None


def main():
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # Start embedded background transport listener automatically
    if agy_link is not None and hasattr(agy_link, "start_background_listener"):
        try:
            agy_link.start_background_listener(
                log_fn=lambda m: sys.stderr.write(f"[MCP-LINK] {m}\n")
            )
            sys.stderr.write("[MCP-LINK] Embedded background transport listener active.\n")
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"[MCP-LINK] Warning: Could not start background listener: {e}\n")
            sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            if resp:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception:
            pass


if __name__ == "__main__":
    main()
