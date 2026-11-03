"""Hardware-free security and localization tests. Never contact an actual camera."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from wifcam_helper import bench

ROOT = Path(__file__).resolve().parents[1]


class WifCamBenchTests(unittest.TestCase):
    def test_seven_complete_locale_dictionaries(self):
        loc = json.loads((ROOT / "locales/strings.json").read_text(encoding="utf-8"))
        self.assertEqual(set(loc), {"ru", "en", "be", "sah", "de", "fr", "zh-CN"})
        keys = set(loc["ru"])
        self.assertGreaterEqual(len(keys), 45)
        for lang, strings in loc.items():
            with self.subTest(lang=lang):
                self.assertEqual(set(strings), keys)
                self.assertTrue(all(isinstance(v, str) and v.strip() for v in strings.values()))
                self.assertTrue((ROOT / "wiki" / ("Guide-" + lang.upper() + ".md")).is_file())

    def test_remote_host_rejects_ssh_option_injection(self):
        for host in ("-oProxyCommand=evil", "foo bar", "../etc/passwd", "a@b", ""):
            with self.subTest(host=host), self.assertRaises(bench.BenchError):
                bench.ssh_argv(host)
        self.assertIn("StrictHostKeyChecking=yes", bench.ssh_argv("192.168.1.55"))
        self.assertIn("root@192.168.1.55", bench.ssh_argv("192.168.1.55"))

    def test_no_mic_capture_without_consent(self):
        with self.assertRaisesRegex(bench.BenchError, "consent"):
            bench.microphone("rtsp://127.0.0.1/ch0", consent=False)

    def test_no_speaker_sound_without_consent(self):
        with self.assertRaisesRegex(bench.BenchError, "consent"):
            bench.speaker(host="127.0.0.1", consent=False)

    def test_speaker_is_quiet_and_has_no_physical_pass_claim(self):
        with patch.object(bench, "_run", return_value=(b"", b"", 0.22)) as called:
            info = bench.speaker(host="127.0.0.1", consent=True)
        self.assertFalse(info["physical_speaker_verified"])
        argv = called.call_args.args[0]
        self.assertEqual(argv[-1], "play -s -r 16000 -")
        self.assertEqual(len(called.call_args.kwargs["input_bytes"]), 6400)

    def test_probe_redacts_rtsp_credentials(self):
        fake = b'{"streams":[{"index":0,"codec_type":"video","codec_name":"h264","width":1920,"height":1080},{"index":1,"codec_type":"audio","codec_name":"pcm_mulaw"}]}'
        with patch.object(bench, "_run", return_value=(fake, b"", 0.33)):
            result = bench.probe("rtsp://secret:pw@127.0.0.1:554/ch0")
        self.assertNotIn("secret", json.dumps(result))
        self.assertNotIn("pw@", json.dumps(result))
        self.assertTrue(result["audio_track"])
        self.assertEqual(result["streams"][0]["codec_name"], "h264")

    def test_report_stored_outside_repo_with_private_mode(self):
        with tempfile.TemporaryDirectory() as home:
            with patch.object(bench, "STATE", Path(home)):
                doc = bench.store({"test": "inventory", "physical_speaker_verified": False})
                self.assertEqual(bench.read_last(), doc)
                self.assertEqual((Path(home) / "last-report.json").stat().st_mode & 0o777, 0o600)

    def test_preset_schema_is_bounded_and_no_shell(self):
        preset = bench.conservative_preset()
        self.assertEqual(preset["camera"], "galayou_g2_t23n_sc2336_atbm6012bx")
        self.assertEqual(preset["branch"], "mymarrchWFcam")
        self.assertEqual(preset["build_env"], {"WIFICAM_WEBRTC": "0"})
        self.assertTrue(preset["requires_hardware_verification"])

    def test_inventory_ssh_quotes_multiline_script(self):
        with patch.object(bench, "_run", return_value=(b"speaker=false\nmicrophone=true\n", b"", 0.4)) as run:
            data = bench.inventory(host="192.168.1.55")
        self.assertTrue(run.call_args.args[0][-1].startswith("sh -c '"))
        self.assertEqual(data["values"]["microphone"], "true")
        self.assertFalse(data["physical_mic_verified"])

    def test_video_never_claims_glass_to_glass(self):
        with patch.object(bench, "_run", return_value=(b"frame=1\nframe=10\nprogress=end\n", b"", 4.5)):
            result = bench.video_sample("rtsp://192.168.1.55:554/ch0")
        self.assertEqual(result["decoded_frames"], 10)
        self.assertIn("NOT glass-to-glass", result["note"])
        self.assertNotIn("glass_to_glass_ms", result)

    def test_no_firmware_actions_in_bench(self):
        data = (ROOT / "wifcam_helper/bench.py").read_text(encoding="utf-8")
        for forbidden in ("dd if=", "mkfs.", "systemctl restart", "speaker on", "microphone on", "raptorctl config set"):
            self.assertNotIn(forbidden, data)
        self.assertIn('"127.0.0.1", PORT', (ROOT / "wifcam_helper/web.py").read_text())

    def test_wiki_publish_guard_is_manual(self):
        script = (ROOT / "scripts/publish-wiki.sh").read_text()
        self.assertIn('WIFCAM_PUBLISH_WIKI', script)
        self.assertIn('git clone --depth 1', script)


if __name__ == "__main__":
    unittest.main()
