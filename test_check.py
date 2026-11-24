"""Tests for check.sh against local fake pages (python3 test_check.py)."""
import http.server
import os
import subprocess
import threading
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class Page(http.server.BaseHTTPRequestHandler):
    answers: list = []

    def do_GET(self):
        code = self.answers.pop(0) if self.answers else 200
        self.send_response(code)
        self.end_headers()

    def log_message(self, *a):
        pass


def run(url, **env):
    return subprocess.run(["bash", str(HERE / "check.sh"), url], capture_output=True, text=True,
                          env={**os.environ, "WAIT": "0", **env}, stdin=subprocess.DEVNULL, timeout=60)


class CheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = http.server.HTTPServer(("127.0.0.1", 0), Page)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.srv.server_port}/health/ready"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def test_up(self):
        Page.answers = [200]
        r = run(self.url)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("UP", r.stdout)

    def test_one_blip_is_not_down(self):
        Page.answers = [503, 200]
        r = run(self.url)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("try 2", r.stdout)

    def test_database_down_twice_is_down(self):
        Page.answers = [503, 503]
        r = run(self.url)
        self.assertEqual(r.returncode, 1)
        self.assertIn("DOWN", r.stdout)
        self.assertIn("HTTP 503", r.stdout)

    def test_no_answer_is_down(self):
        r = run("http://127.0.0.1:9/health/ready", TRIES="2")
        self.assertEqual(r.returncode, 1)
        self.assertIn("HTTP 000", r.stdout)

    def test_workflow_basics(self):
        wf = (HERE / ".github" / "workflows" / "site-check.yml").read_text(encoding="utf-8")
        self.assertIn("cron: '7,37 * * * *'", wf)
        self.assertIn("runs-on: ubuntu-latest", wf)            # GitHub's runner: needs neither server nor Mac
        self.assertIn("https://erp.lixo.co.in/health/ready", wf)
        self.assertNotIn("secrets.", wf)                       # no secrets in this public repo


if __name__ == "__main__":
    unittest.main()
