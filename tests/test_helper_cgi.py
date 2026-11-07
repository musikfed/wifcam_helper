"""Hardware-free CGI regressions: auth, POST CSRF, role allowlist and JSON."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CGI = ROOT / "firmware/overlay/usr/share/wificam-web/cgi-bin/helper-capabilities"


class HelperCgiContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.token = root / "csrf"
        self.token.write_text("known42\n")
        self.calls = root / "mode-calls"
        self.mode = root / "mode"
        self.mode.write_text(
            '#!/bin/sh\n'
            'printf "%s\\n" "$*" >> "$HELPER_TEST_CALLS"\n'
            'echo voice_assistant\n'
        )
        self.probe = root / "probe"
        self.probe.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' '{\"ok\":true,\"schema\":\"peginelab.camera-head.v1\","
            "\"mode\":\"voice_assistant\"}'\n"
        )
        self.mode.chmod(0o755)
        self.probe.chmod(0o755)
        script = CGI.read_text()
        script = script.replace("/usr/bin/wifcam-helper-probe", str(self.probe))
        script = script.replace("/usr/bin/wifcam-helper-mode", str(self.mode))
        script = script.replace("/var/run/wificam-csrf", str(self.token))
        self.cgi = root / "helper-capabilities"
        self.cgi.write_text(script)

    def request(self, method="GET", body="", *, auth=True):
        env = os.environ.copy()
        env.update({"REQUEST_METHOD": method,
                    "CONTENT_LENGTH": str(len(body.encode())),
                    "HELPER_TEST_CALLS": str(self.calls)})
        env.pop("REMOTE_USER", None)
        if auth:
            env["REMOTE_USER"] = "admin"
        proc = subprocess.run(["sh", str(self.cgi)], input=body, text=True,
                              capture_output=True, env=env, check=True)
        self.assertIn("Content-Type: application/json", proc.stdout)
        self.assertIn("Cache-Control: no-store", proc.stdout)
        return json.loads(proc.stdout.split("\n\n", 1)[1])

    def test_read_only_status_requires_auth(self):
        self.assertEqual(self.request(auth=False)["error"], "authentication_required")
        self.assertEqual(self.request()["schema"], "peginelab.camera-head.v1")
        self.assertFalse(self.calls.exists())

    def test_valid_post_and_strict_mode_whitelist(self):
        result = self.request("POST", "mode=robot_head&csrf=known42")
        self.assertEqual(result["mode"], "voice_assistant")  # stub probe
        self.assertIn("set robot_head", self.calls.read_text())
        before = self.calls.read_text()
        self.assertEqual(self.request("POST", "mode=../../bin/sh&csrf=known42")["error"],
                         "invalid_mode")
        self.assertEqual(self.request("POST", "mode=robot_head&csrf=bad")["error"],
                         "csrf_invalid")
        self.assertEqual(self.request("POST", "mode=robot_head&csrf=known42", auth=False)["error"],
                         "authentication_required")
        self.assertEqual(before, self.calls.read_text())

    def test_verb_and_csrf_missing_fail_closed(self):
        self.assertEqual(self.request("POST", "mode=voice_assistant")["error"], "csrf_required")
        self.assertEqual(self.request("DELETE")["error"], "method_not_allowed")
        self.assertFalse(self.calls.exists())


if __name__ == "__main__":
    unittest.main()
