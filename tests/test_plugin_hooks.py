#!/usr/bin/env python3
"""
Unit tests for Antigravity Link Lifecycle Hooks (PreInvocation & PreToolUse).
"""
import unittest
import json
import os
import sys
import tempfile
import subprocess
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS_DIR = os.path.join(REPO_ROOT, ".agents", "plugins", "antigravity-link", "hooks")
PRE_INVOCATION_SCRIPT = os.path.join(HOOKS_DIR, "pre_invocation_sync.py")
PRE_TOOL_SCRIPT = os.path.join(HOOKS_DIR, "pre_tool_guard.py")


class TestPluginLifecycleHooks(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace_dir = self.temp_dir.name
        self.agy_dir = os.path.join(self.workspace_dir, ".agy_link")
        os.makedirs(self.agy_dir, exist_ok=True)
        self.state_file = os.path.join(self.agy_dir, "peer_state.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_pre_invocation_injects_warning_when_files_locked(self):
        peer_state = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "sender": {"user": "Senpai59", "role": "platform_lead"},
            "type": "state_sync",
            "state": {
                "task": "Refactor Windows Audio Engine",
                "status": "in-progress",
                "locked_files": ["audio_winmm.py", "mixer.cpp"]
            }
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(peer_state, f)

        payload = {"workspacePaths": [self.workspace_dir]}
        res = subprocess.run(
            [sys.executable, PRE_INVOCATION_SCRIPT],
            input=json.dumps(payload),
            text=True,
            capture_output=True
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertIn("injectSteps", data)
        self.assertEqual(len(data["injectSteps"]), 1)
        warning_msg = data["injectSteps"][0]["ephemeralMessage"]
        self.assertIn("Senpai59", warning_msg)
        self.assertIn("audio_winmm.py", warning_msg)
        self.assertIn("Refactor Windows Audio Engine", warning_msg)

    def test_pre_invocation_empty_when_peer_completed(self):
        peer_state = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "sender": {"user": "Senpai59", "role": "platform_lead"},
            "type": "state_sync",
            "state": {
                "task": "Finished PR",
                "status": "completed",
                "locked_files": []
            }
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(peer_state, f)

        payload = {"workspacePaths": [self.workspace_dir]}
        res = subprocess.run(
            [sys.executable, PRE_INVOCATION_SCRIPT],
            input=json.dumps(payload),
            text=True,
            capture_output=True
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertEqual(data.get("injectSteps"), [])

    def test_pre_tool_guard_blocks_locked_file(self):
        peer_state = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "sender": {"user": "Senpai59", "role": "platform_lead"},
            "type": "state_sync",
            "state": {
                "task": "Working on JoyCon Windows driver",
                "status": "in-progress",
                "locked_files": ["joycon_mouse.py"]
            }
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(peer_state, f)

        # Attempt to edit joycon_mouse.py
        payload = {
            "workspacePaths": [self.workspace_dir],
            "toolCall": {
                "name": "replace_file_content",
                "args": {
                    "TargetFile": "/home/user/projects/joycon_mouse.py"
                }
            }
        }
        res = subprocess.run(
            [sys.executable, PRE_TOOL_SCRIPT],
            input=json.dumps(payload),
            text=True,
            capture_output=True
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertEqual(data.get("decision"), "ask")
        self.assertIn("locked by Senpai59", data.get("reason", ""))

    def test_pre_tool_guard_allows_unlocked_file(self):
        peer_state = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "sender": {"user": "Senpai59", "role": "platform_lead"},
            "type": "state_sync",
            "state": {
                "task": "Working on JoyCon Windows driver",
                "status": "in-progress",
                "locked_files": ["joycon_mouse.py"]
            }
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(peer_state, f)

        # Attempt to edit unrelated file
        payload = {
            "workspacePaths": [self.workspace_dir],
            "toolCall": {
                "name": "replace_file_content",
                "args": {
                    "TargetFile": "/home/user/projects/unrelated_readme.md"
                }
            }
        }
        res = subprocess.run(
            [sys.executable, PRE_TOOL_SCRIPT],
            input=json.dumps(payload),
            text=True,
            capture_output=True
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertEqual(data.get("decision"), "allow")

    def test_pre_tool_guard_handles_windows_path_separators(self):
        peer_state = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "sender": {"user": "Senpai59", "role": "platform_lead"},
            "type": "state_sync",
            "state": {
                "task": "Working on Windows batch files",
                "status": "in-progress",
                "locked_files": ["scripts\\build.bat"]
            }
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(peer_state, f)

        # Attempt to edit with unix forward slashes
        payload = {
            "workspacePaths": [self.workspace_dir],
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": "C:/repo/scripts/build.bat"
                }
            }
        }
        res = subprocess.run(
            [sys.executable, PRE_TOOL_SCRIPT],
            input=json.dumps(payload),
            text=True,
            capture_output=True
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertEqual(data.get("decision"), "ask")

    def test_pre_invocation_ignores_stale_expired_lock(self):
        peer_state = {
            "last_updated": "2020-01-01T00:00:00Z",
            "sender": {"user": "Senpai59", "role": "platform_lead"},
            "type": "state_sync",
            "state": {
                "task": "Old forgotten task",
                "status": "in-progress",
                "locked_files": ["ancient_file.py"]
            }
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(peer_state, f)

        payload = {"workspacePaths": [self.workspace_dir]}
        res = subprocess.run(
            [sys.executable, PRE_INVOCATION_SCRIPT],
            input=json.dumps(payload),
            text=True,
            capture_output=True
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertEqual(data.get("injectSteps"), [])

    def test_pre_tool_guard_allows_stale_expired_lock(self):
        peer_state = {
            "last_updated": "2020-01-01T00:00:00Z",
            "sender": {"user": "Senpai59", "role": "platform_lead"},
            "type": "state_sync",
            "state": {
                "task": "Old forgotten task",
                "status": "in-progress",
                "locked_files": ["ancient_file.py"]
            }
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(peer_state, f)

        payload = {
            "workspacePaths": [self.workspace_dir],
            "toolCall": {
                "name": "replace_file_content",
                "args": {
                    "TargetFile": "/path/to/ancient_file.py"
                }
            }
        }
        res = subprocess.run(
            [sys.executable, PRE_TOOL_SCRIPT],
            input=json.dumps(payload),
            text=True,
            capture_output=True
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertEqual(data.get("decision"), "allow")

    def test_pre_invocation_handles_quarantine(self):
        peer_state = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "sender": {"user": "MaliciousPeer", "role": "attacker"},
            "type": "state_sync",
            "state": {
                "status": "quarantined",
                "reason": "Prompt injection detected"
            }
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(peer_state, f)

        payload = {"workspacePaths": [self.workspace_dir]}
        res = subprocess.run(
            [sys.executable, PRE_INVOCATION_SCRIPT],
            input=json.dumps(payload),
            text=True,
            capture_output=True
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertIn("injectSteps", data)
        self.assertEqual(len(data["injectSteps"]), 1)
        warning_msg = data["injectSteps"][0]["ephemeralMessage"]
        self.assertIn("QUARANTINED", warning_msg)
        self.assertIn("link unquarantine", warning_msg)

    def test_pre_tool_guard_blocks_when_quarantined(self):
        peer_state = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "sender": {"user": "MaliciousPeer", "role": "attacker"},
            "type": "state_sync",
            "state": {
                "status": "quarantined",
                "reason": "Suspicious payload"
            }
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(peer_state, f)

        payload = {
            "workspacePaths": [self.workspace_dir],
            "toolCall": {
                "name": "replace_file_content",
                "args": {
                    "TargetFile": "/path/to/any_file.py"
                }
            }
        }
        res = subprocess.run(
            [sys.executable, PRE_TOOL_SCRIPT],
            input=json.dumps(payload),
            text=True,
            capture_output=True
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertEqual(data.get("decision"), "deny")
        self.assertIn("QUARANTINED", data.get("reason", ""))
        self.assertIn("link unquarantine", data.get("reason", ""))


if __name__ == "__main__":
    unittest.main()
