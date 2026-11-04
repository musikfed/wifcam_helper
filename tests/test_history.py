"""Helper-only SQLite report history; migration does not erase old reports."""
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

from wifcam_helper import bench,history


class HelperHistoryTests(unittest.TestCase):
    def test_legacy_import_and_new_results_do_not_touch_factory(self):
        with tempfile.TemporaryDirectory() as tmp:
            state=Path(tmp)/"helper"
            state.mkdir()
            old={"schema":"peginelab.wifcam-helper.report.v1",
                 "created_utc":"2026-01-01T00:00:00Z",
                 "result":{"test":"inventory","values":{"audio":"available"}}}
            (state/"last-report.json").write_text(json.dumps(old),encoding="utf8")
            factory=Path(tmp)/"factory.sqlite3"
            factory.write_bytes(b"do-not-touch")
            with patch.object(bench,"STATE",state):
                self.assertEqual(history.recent(state,20)[0],old)
                new=bench.store({"test":"probe","audio_track":False})
                self.assertEqual(bench.read_last(),new)
                records=history.recent(state,20)
            self.assertEqual(len(records),2)
            self.assertEqual(records[0]["result"]["test"],"probe")
            self.assertEqual(records[1]["result"]["test"],"inventory")
            self.assertEqual(factory.read_bytes(),b"do-not-touch")
            self.assertEqual((state/"history.sqlite3").stat().st_mode & 0o777,0o600)
            self.assertEqual(state.stat().st_mode & 0o777,0o700)

    def test_reject_symlinked_state_without_touching_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            actual=base/"unrelated-data"
            actual.mkdir(mode=0o750)
            sentinel=actual/"sentinel.txt"
            sentinel.write_text("keep")
            link=base/"helper"
            link.symlink_to(actual, target_is_directory=True)
            before=actual.stat().st_mode & 0o777
            with self.assertRaises(ValueError):
                history.summary(link)
            self.assertEqual(actual.stat().st_mode & 0o777,before)
            self.assertEqual(sentinel.read_text(),"keep")
            self.assertFalse((actual/"history.sqlite3").exists())

    def test_idempotent_import_and_read_only_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            state=Path(tmp)/"helper"
            self.assertEqual(history.summary(state)["total"],0)
            doc={"schema":"peginelab.wifcam-helper.report.v1",
                 "created_utc":"before","result":{"test":"microphone"}}
            (state/"last-report.json").write_text(json.dumps(doc))
            self.assertEqual(history.summary(state)["total"],1)
            self.assertEqual(history.summary(state)["total"],1)
            self.assertEqual(history.summary(state)["last_test"],"microphone")
            with self.assertRaises(ValueError):history.recent(state,0)


if __name__=="__main__":
    unittest.main()
