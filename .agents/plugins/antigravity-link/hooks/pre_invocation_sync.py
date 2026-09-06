#!/usr/bin/env python3
"""
Antigravity Link - PreInvocation Hook
Injects peer lock notifications into turn context before the model generates code.
"""
import sys
import json
import os

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

    workspace_paths = payload.get("workspacePaths", [])
    state_file = find_peer_state(workspace_paths)

    inject_steps = []

    if state_file and os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            state = data.get("state", {})
            status = str(state.get("status", "")).lower()
            locked_files = state.get("locked_files", [])
            task = state.get("task", "Active task")
            sender = data.get("sender", {})
            user = sender.get("user", "Peer")
            role = sender.get("role", "Peer AI")

            if status == "in-progress" and (locked_files or task):
                files_str = ", ".join(locked_files) if locked_files else "none specified"
                msg = (
                    f"⚠️ [Antigravity Link] Peer Lock Active: {user} ({role}) is currently working on: "
                    f"\"{task}\". Locked files: [{files_str}]. "
                    f"Coordinate before modifying shared files to prevent merge conflicts."
                )
                inject_steps.append({"ephemeralMessage": msg})
        except Exception:
            pass

    output = {"injectSteps": inject_steps}
    print(json.dumps(output))

if __name__ == "__main__":
    main()
