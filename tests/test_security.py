#!/usr/bin/env python3
"""
Unit tests for Antigravity Link Security Gate, Roles, and Permission Boundaries.
"""
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Ensure repository root is on PYTHONPATH
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from agy_link import request_user_permission, VALID_ROLES


class TestSecurityGateAndRoles(unittest.TestCase):
    def setUp(self):
        self.sender_info = {
            "user": "Senpai59",
            "role": "platform_lead",
            "platform": "windows"
        }

    def test_security_mode_autonomous_auto_approves(self):
        config = {"security_mode": "autonomous"}
        result = request_user_permission("Run tests on machine", self.sender_info, config)
        self.assertTrue(result, "Autonomous mode must auto-approve tasks without prompting")

    def test_security_mode_deny_auto_rejects(self):
        config = {"security_mode": "deny"}
        result = request_user_permission("Delete all files", self.sender_info, config)
        self.assertFalse(result, "Deny mode must immediately reject incoming remote tasks")

    @patch("subprocess.run")
    @patch("shutil.which", return_value="/usr/bin/zenity")
    @patch.dict(os.environ, {"DISPLAY": ":0"})
    @patch("sys.platform", "linux")
    def test_security_gate_linux_zenity_approved(self, mock_which, mock_subproc):
        mock_res = MagicMock()
        mock_res.returncode = 0  # 0 indicates Yes / Approved
        mock_subproc.return_value = mock_res

        config = {"security_mode": "prompt"}
        result = request_user_permission("Run harmless lint", self.sender_info, config)
        self.assertTrue(result, "User approval (exit code 0) should grant permission")

    @patch("subprocess.run")
    @patch("shutil.which", return_value="/usr/bin/zenity")
    @patch.dict(os.environ, {"DISPLAY": ":0"})
    @patch("sys.platform", "linux")
    def test_security_gate_linux_zenity_denied(self, mock_which, mock_subproc):
        mock_res = MagicMock()
        mock_res.returncode = 1  # 1 indicates No / Denied / Closed
        mock_subproc.return_value = mock_res

        config = {"security_mode": "prompt"}
        result = request_user_permission("Run arbitrary command", self.sender_info, config)
        self.assertFalse(result, "User denial (exit code 1) must block execution")

    @patch("subprocess.run")
    @patch("sys.platform", "win32")
    def test_security_gate_windows_powershell_approved(self, mock_subproc):
        mock_res = MagicMock()
        mock_res.returncode = 0  # 0 indicates Yes
        mock_subproc.return_value = mock_res

        config = {"security_mode": "prompt"}
        result = request_user_permission("Run test on windows", self.sender_info, config)
        self.assertTrue(result, "Windows prompt approval (exit code 0) should grant permission")

    @patch("subprocess.run")
    @patch("sys.platform", "win32")
    def test_security_gate_windows_powershell_denied(self, mock_subproc):
        mock_res = MagicMock()
        mock_res.returncode = 1  # 1 indicates No
        mock_subproc.return_value = mock_res

        config = {"security_mode": "prompt"}
        result = request_user_permission("Run test on windows", self.sender_info, config)
        self.assertFalse(result, "Windows prompt denial (exit code 1) must block execution")

    @patch("builtins.input", return_value="y")
    @patch("sys.stdin.isatty", return_value=True)
    @patch("shutil.which", return_value=None)
    @patch.dict(os.environ, {"DISPLAY": "", "WAYLAND_DISPLAY": ""})
    @patch("sys.platform", "linux")
    def test_security_gate_terminal_fallback_approved(self, mock_which, mock_isatty, mock_input):
        config = {"security_mode": "prompt"}
        result = request_user_permission("Run terminal command", self.sender_info, config)
        self.assertTrue(result, "Terminal interactive 'y' should approve task")

    @patch("sys.stdin.isatty", return_value=False)
    @patch("shutil.which", return_value=None)
    @patch.dict(os.environ, {"DISPLAY": "", "WAYLAND_DISPLAY": ""})
    @patch("sys.platform", "linux")
    def test_security_gate_headless_defaults_to_deny(self, mock_which, mock_isatty):
        config = {"security_mode": "prompt"}
        result = request_user_permission("Run headless command", self.sender_info, config)
        self.assertFalse(result, "Headless non-interactive environment must default to safe denial")

    def test_role_hierarchy_completeness(self):
        valid_roles = ["lead", "platform_lead", "contributor", "tester"]
        for role in valid_roles:
            self.assertIn(role, VALID_ROLES, f"Expected role '{role}' missing from VALID_ROLES registry")


if __name__ == "__main__":
    unittest.main()
