#!/usr/bin/env python3
"""
Antigravity Link - PreToolUse Conflict Guard Hook
Blocks or prompts user when an agent attempts to edit a file currently locked by peer AI.
"""
import sys
import json
import os
from datetime import datetime, timezone

def is_lock_expired(last_updated_str, ttl_seconds=7200):
    if not last_updated_str:
        return False
    try:
        clean_str = last_updated_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - dt).total_seconds() > ttl_seconds
    except Exception:
        return False

def find_peer_state(workspace_paths=None):
    # 1. Workspace paths (highest priority - represents the active project)
    if workspace_paths:
        for wp in workspace_paths:
            cand = os.path.join(wp, ".agy_link", "peer_state.json")
            if os.path.exists(cand):
                return cand

    # 2. Current working directory
    cwd_cand = os.path.join(os.getcwd(), ".agy_link", "peer_state.json")
    if os.path.exists(cwd_cand):
        return cwd_cand

    # 3. repo_path.txt configured during installation
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_dir = os.path.dirname(script_dir)
    repo_txt = os.path.join(plugin_dir, "repo_path.txt")
    if os.path.exists(repo_txt):
        try:
            with open(repo_txt, "r", encoding="utf-8") as f:
                p = f.read().strip()
                cand = os.path.join(p, ".agy_link", "peer_state.json")
                if os.path.exists(cand):
                    return cand
        except Exception:
            pass

    # 4. Common locations
    home = os.path.expanduser("~")
    for base in ["PycharmProjects/antigravity-link", "antigravity-link", "Desktop/antigravity-link"]:
        cand = os.path.join(home, base, ".agy_link", "peer_state.json")
        if os.path.exists(cand):
            return cand

    return None

def main():
    try:
        raw_input = sys.stdin.read()
        payload = json.loads(raw_input) if raw_input.strip() else {}
    except Exception:
        payload = {}

    tool_call = payload.get("toolCall", {})
    args = tool_call.get("args", {})
    
    # Extract file path from tool args
    target_file = (
        args.get("TargetFile") or 
        args.get("FilePath") or 
        args.get("file") or 
        args.get("path") or 
        ""
    )

    if not target_file:
        print(json.dumps({"decision": "allow"}))
        return

    target_base = os.path.basename(target_file).lower()
    target_norm = os.path.normpath(target_file).lower().replace("\\", "/")

    workspace_paths = payload.get("workspacePaths", [])
    state_file = find_peer_state(workspace_paths)

    if state_file and os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            state = data.get("state", {})
            status = str(state.get("status", "")).lower()
            locked_files = state.get("locked_files", [])
            task = state.get("task", "Active task")
            sender = data.get("sender", {})
            user = sender.get("user", "Peer AI")

            if status == "in-progress" and locked_files and not is_lock_expired(data.get("last_updated")):
                for lf in locked_files:
                    lf_clean = lf.strip().lower().replace("\\", "/")
                    lf_base = os.path.basename(lf_clean)
                    if lf_clean == target_norm or lf_base == target_base or target_norm.endswith(lf_clean):
                        reason = (
                            f"Antigravity Link Conflict Prevention: '{os.path.basename(target_file)}' is currently "
                            f"locked by {user} working on '{task}'. Coordinate with peer before overwriting."
                        )
                        print(json.dumps({"decision": "ask", "reason": reason}))
                        return
        except Exception:
            pass

    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
