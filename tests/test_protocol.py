#!/usr/bin/env python3
"""
Unit tests for Antigravity Link Protocol & HMAC-SHA256 Wire Signing.
"""
import unittest
import json
import os
import sys

# Ensure repository root is on PYTHONPATH
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from agy_link import compute_packet_signature, verify_packet_signature, make_packet, PROTOCOL_VERSION


class TestProtocolAndHMAC(unittest.TestCase):
    def setUp(self):
        self.secret_key = "test_super_secret_link_key_2026"
        self.config = {
            "node_id": "test-node-1",
            "user": "Alice",
            "role": "lead",
            "auth_token": "token_123",
            "secret_key": self.secret_key
        }

    def test_make_packet_structure(self):
        payload = {"message": "Hello from unit test"}
        pkt = make_packet("message", payload, self.config)

        self.assertEqual(pkt["version"], PROTOCOL_VERSION)
        self.assertEqual(pkt["type"], "message")
        self.assertEqual(pkt["sender"]["user"], "Alice")
        self.assertEqual(pkt["sender"]["role"], "lead")
        self.assertEqual(pkt["payload"], payload)
        self.assertTrue("signature" in pkt)
        self.assertTrue(len(pkt["signature"]) == 64)  # SHA-256 hex digest length

    def test_hmac_signature_verification_success(self):
        payload = {"task": "Sync test", "status": "in-progress"}
        pkt = make_packet("state_sync", payload, self.config)

        is_valid = verify_packet_signature(pkt, self.secret_key)
        self.assertTrue(is_valid, "Valid signature failed verification")

    def test_hmac_signature_fails_on_wrong_key(self):
        payload = {"task": "Secret task"}
        pkt = make_packet("state_sync", payload, self.config)

        is_valid = verify_packet_signature(pkt, "wrong_secret_key")
        self.assertFalse(is_valid, "Signature should fail with incorrect secret key")

    def test_hmac_signature_detects_payload_tampering(self):
        payload = {"command": "safe_command"}
        pkt = make_packet("agent_summon", payload, self.config)

        # Tamper with payload after signing
        pkt["payload"]["command"] = "malicious_command"
        is_valid = verify_packet_signature(pkt, self.secret_key)
        self.assertFalse(is_valid, "Tampered payload was not detected by signature check")

    def test_hmac_signature_detects_sender_spoofing(self):
        payload = {"msg": "legitimate message"}
        pkt = make_packet("message", payload, self.config)

        # Attacker tries to impersonate the lead AI
        pkt["sender"]["role"] = "lead"
        pkt["sender"]["user"] = "FakeLeader"
        is_valid = verify_packet_signature(pkt, self.secret_key)
        self.assertFalse(is_valid, "Sender spoofing was not detected by signature check")

    def test_signature_deterministic(self):
        pkt = {
            "version": "1.1.0",
            "type": "message",
            "timestamp": "2026-09-05T00:00:00Z",
            "sender": {"user": "Bob", "node_id": "bob-1"},
            "payload": {"text": "Deterministic test"}
        }
        sig1 = compute_packet_signature(pkt, self.secret_key)
        sig2 = compute_packet_signature(pkt, self.secret_key)
        self.assertEqual(sig1, sig2, "Signatures should be strictly deterministic")


if __name__ == "__main__":
    unittest.main()
