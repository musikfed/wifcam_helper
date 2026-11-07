"""Hardware-free checks for the actual camera-side SD firmware overlay."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OVERLAY=ROOT/"firmware"/"overlay"
EXPECTED={
    "etc/wifcam-helper-release",
    "etc/init.d/S92wifcam-helper",
    "usr/bin/wifcam-helper-probe",
    "usr/bin/wifcam-helper-mode",
    "usr/share/wificam-web/cgi-bin/helper-capabilities",
}

class FirmwareOverlayTests(unittest.TestCase):
    def test_files_are_camera_side_not_python_stand_in(self):
        actual={p.relative_to(OVERLAY).as_posix() for p in OVERLAY.rglob("*") if p.is_file()}
        self.assertEqual(actual,EXPECTED)
        self.assertIn("PEGINELAB_HELPER_FIRMWARE_V1",
                      (OVERLAY/"etc/wifcam-helper-release").read_text())
        self.assertIn("inference", (OVERLAY/"usr/bin/wifcam-helper-probe").read_text())
        self.assertIn("application/json",
                      (OVERLAY/"usr/share/wificam-web/cgi-bin/helper-capabilities").read_text())
        self.assertFalse(any(OVERLAY.rglob("*.py")))
        self.assertIn("robot_head", (OVERLAY/"usr/bin/wifcam-helper-mode").read_text())
        self.assertIn("csrf_invalid", (OVERLAY/"usr/share/wificam-web/cgi-bin/helper-capabilities").read_text())

    def test_posix_shell_syntax(self):
        for name in EXPECTED:
            if name.endswith(("wifcam-helper-probe","wifcam-helper-mode","helper-capabilities","S92wifcam-helper")):
                subprocess.run(["sh","-n",str(OVERLAY/name)],check=True)

    def test_contract_requests_real_build_adapter(self):
        contract=json.loads((ROOT/"peginelab.project.json").read_text())
        self.assertEqual(contract["project"]["mode"],"build")
        self.assertEqual(contract["project"]["repository"],"musikfed/wifcam_helper")
        self.assertEqual(contract["pipeline"]["adapter"],"t23n_helper_sd")
        self.assertEqual(contract["platform"]["architecture"],"mipsel")
        self.assertTrue(contract["outputs"])

if __name__=="__main__":
    unittest.main()
