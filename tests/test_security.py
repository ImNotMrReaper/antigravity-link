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
    def test_security_gate_user_approved(self, mock_subproc):
        mock_res = MagicMock()
        mock_res.returncode = 0  # 0 indicates Yes / Approved
        mock_subproc.return_value = mock_res

        config = {"security_mode": "prompt"}
        result = request_user_permission("Run harmless lint", self.sender_info, config)
        self.assertTrue(result, "User approval (exit code 0) should grant permission")

    @patch("subprocess.run")
    def test_security_gate_user_denied(self, mock_subproc):
        mock_res = MagicMock()
        mock_res.returncode = 1  # 1 indicates No / Denied / Closed
        mock_subproc.return_value = mock_res

        config = {"security_mode": "prompt"}
        result = request_user_permission("Run arbitrary command", self.sender_info, config)
        self.assertFalse(result, "User denial (exit code 1) must block execution")

    def test_role_hierarchy_completeness(self):
        valid_roles = ["lead", "platform_lead", "contributor", "tester"]
        for role in valid_roles:
            self.assertIn(role, VALID_ROLES, f"Expected role '{role}' missing from VALID_ROLES registry")


if __name__ == "__main__":
    unittest.main()
