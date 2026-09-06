#!/usr/bin/env python3
"""
Unit tests for Antigravity Link PyCharm Embedded Collaborative Web GUI.
"""
import unittest
import json
import urllib.request
import threading
import time
import socket
from http.server import HTTPServer
from agy_link import get_dashboard_status, generate_dashboard_html, cmd_unquarantine, get_ide_environment, open_in_ide, PEER_STATE_FILE, ensure_dirs
from unittest.mock import patch


class TestWebGUI(unittest.TestCase):
    def setUp(self):
        self.config = {
            "node_id": "test-node",
            "user": "TestUser",
            "role": "lead",
            "relay_room": "test_room",
            "mode": "hybrid",
            "security_mode": "prompt"
        }

    def test_get_dashboard_status_structure(self):
        status = get_dashboard_status(self.config)
        self.assertIn("node", status)
        self.assertIn("peer", status)
        self.assertIn("locks", status)
        self.assertIn("recent_events", status)
        self.assertEqual(status["node"]["user"], "TestUser")
        self.assertEqual(status["node"]["role"], "lead")
        self.assertIn("ide", status["node"])

    def test_get_ide_environment(self):
        with patch.dict("os.environ", {"TERMINAL_EMULATOR": "JetBrains-JediTerm"}):
            self.assertIn("PyCharm", get_ide_environment())
        with patch.dict("os.environ", {"SNAP_INSTANCE_NAME": "pycharm-community"}, clear=True):
            self.assertIn("PyCharm", get_ide_environment())
        with patch.dict("os.environ", {"TERM_PROGRAM": "vscode"}, clear=True):
            self.assertEqual("VS Code", get_ide_environment())
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual("Standard Terminal", get_ide_environment())

    def test_open_in_ide_validation(self):
        ok, msg = open_in_ide("")
        self.assertFalse(ok)
        self.assertIn("No file", msg)

        ok, msg = open_in_ide("nonexistent_file_xyz123.abc")
        self.assertFalse(ok)
        self.assertIn("File not found", msg)

    def test_generate_dashboard_html_contains_critical_elements(self):
        html_doc = generate_dashboard_html(self.config)
        self.assertIn("<!DOCTYPE html>", html_doc)
        self.assertIn("peerPill", html_doc)
        self.assertIn("locksContainer", html_doc)
        self.assertIn("activeTask", html_doc)
        self.assertIn("/api/status", html_doc)
        self.assertIn("fetchStatus", html_doc)
        self.assertIn("openFileInPyCharm", html_doc)
        self.assertIn("PyCharm Tandem Actions", html_doc)


    def test_gui_http_server_endpoints(self):
        # Find a free ephemeral port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 0))
        free_port = s.getsockname()[1]
        s.close()

        # Import handler and start test server
        from http.server import BaseHTTPRequestHandler

        config = self.config

        class TestHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

            def do_GET(self):
                if self.path == "/" or self.path.startswith("/?"):
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(generate_dashboard_html(config).encode("utf-8"))
                elif self.path == "/api/status":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps(get_dashboard_status(config)).encode("utf-8"))
                else:
                    self.send_response(404)
                    self.end_headers()

            def do_POST(self):
                if self.path == "/api/unquarantine":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
                else:
                    self.send_response(404)
                    self.end_headers()

        httpd = HTTPServer(("127.0.0.1", free_port), TestHandler)
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        time.sleep(0.1)

        try:
            # 1. Test GET / (HTML Dashboard)
            req = urllib.request.Request(f"http://127.0.0.1:{free_port}/")
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                body = resp.read().decode("utf-8")
                self.assertIn("Antigravity Link", body)

            # 2. Test GET /api/status (JSON API)
            req_api = urllib.request.Request(f"http://127.0.0.1:{free_port}/api/status")
            with urllib.request.urlopen(req_api, timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(data["node"]["user"], "TestUser")

            # 3. Test POST /api/unquarantine
            req_post = urllib.request.Request(f"http://127.0.0.1:{free_port}/api/unquarantine", data=b"", method="POST")
            with urllib.request.urlopen(req_post, timeout=2.0) as resp:
                self.assertEqual(resp.status, 200)
                res_json = json.loads(resp.read().decode("utf-8"))
                self.assertTrue(res_json.get("ok"))
        finally:
            httpd.shutdown()
            httpd.server_close()

    def test_start_gui_server_lifecycle(self):
        from agy_link import start_gui_server, _GUI_SERVER_INSTANCE
        import agy_link

        # Pick an ephemeral port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()

        ok, msg = start_gui_server(port=port, config=self.config, log_fn=lambda m: None)
        self.assertTrue(ok)
        self.assertIn(str(port), msg)

        # Calling again reports already active
        ok2, msg2 = start_gui_server(port=port, config=self.config, log_fn=lambda m: None)
        self.assertTrue(ok2)
        self.assertIn("already active", msg2)

        # Verify server actually answers HTTP request
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/status")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data["node"]["user"], "TestUser")


if __name__ == "__main__":
    unittest.main()
