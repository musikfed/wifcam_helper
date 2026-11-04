"""Offline tests for real-frame counting and explicit private Ollama forwarding."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from wifcam_helper import bench, vision


class Vec:
    def __init__(self, values):
        self.values = values
    def cpu(self):
        return self
    def tolist(self):
        return self.values


class Boxes:
    cls = Vec([0, 0, 1])
    conf = Vec([0.98, 0.88, 0.77])
    xyxy = Vec([[0, 0, 100, 90], [110, 0, 200, 80], [20, 100, 80, 200]])


class Result:
    names = {0: "cup", 1: "book"}
    boxes = Boxes()


class VisionTests(unittest.TestCase):
    def test_count_objects_per_frame_not_summing_frames(self):
        counts, boxes = vision.counts_from_result(Result())
        self.assertEqual(counts, {"book": 1, "cup": 2})
        self.assertEqual(len(boxes), 3)
        self.assertEqual(boxes[0]["xyxy"], [0, 0, 100, 90])

    def test_consent_and_private_destination_fail_closed(self):
        with self.assertRaises(bench.BenchError):
            vision.observe("rtsp://192.168.1.55:554/ch0", model_path="/tmp/x.pt")
        for url in ("https://example.com:11434", "http://8.8.8.8:11434",
                    "http://user:pass@127.0.0.1:11434",
                    "http://127.0.0.1:11434/evil",
                    "http://169.254.169.254:11434",
                    "http://127.0.0.1:11434?q=1"):
            with self.subTest(url=url), self.assertRaises(bench.BenchError):
                vision.private_ollama_endpoint(url)
        self.assertEqual(vision.private_ollama_endpoint("http://192.168.0.100:11434"),
                         "http://192.168.0.100:11434")
        self.assertEqual(vision.private_ollama_endpoint("http://127.0.0.1:11434"),
                         "http://127.0.0.1:11434")

    def test_remote_payload_single_image_unloads_model(self):
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *_):
                return False
            def read(self, limit):
                return b'{"message":{"content":"Two cups and a book."}}'
        class Opener:
            request = None
            def open(self, request, timeout):
                self.request = request
                self.timeout = timeout
                return Response()
        sender = Opener()
        with patch.object(vision, "build_opener", return_value=sender):
            text = vision.ask_ollama(b"\xff\xd8JPEG", endpoint="http://127.0.0.1:11434",
                                     model="qwen2.5vl:7b", question="Count items", consent=True)
        self.assertEqual(text, "Two cups and a book.")
        self.assertEqual(sender.request.full_url, "http://127.0.0.1:11434/api/chat")
        body = json.loads(sender.request.data)
        self.assertEqual(body["keep_alive"], 0)
        self.assertFalse(body["stream"])
        self.assertEqual(len(body["messages"][1]["images"]), 1)
        self.assertLess(sender.timeout, 90)
        with self.assertRaises(bench.BenchError):
            vision.ask_ollama(b"\xff\xd8", endpoint="http://127.0.0.1:11434",
                              model="qwen2.5vl:7b", question="test", consent=False)

    def test_real_decode_path_mocked_not_pretend_scores(self):
        class FakeImage:
            def __enter__(self):
                return self
            def __exit__(self, *_):
                return False
            def convert(self, color):
                return object()
        class FakeModel:
            instances = 0
            def __init__(self, model):
                self.model = model
                FakeModel.instances += 1
            def predict(self, **kwargs):
                self.kwargs = kwargs
                return [Result()]
        with tempfile.TemporaryDirectory() as temp:
            weights = Path(temp) / "trusted.onnx"
            weights.write_bytes(b"mock; not actually executed")
            import sys
            from types import SimpleNamespace
            modules = {
                "PIL": SimpleNamespace(Image=SimpleNamespace(open=lambda f: FakeImage())),
                "ultralytics": SimpleNamespace(YOLO=FakeModel),
            }
            with patch.dict(sys.modules, modules), patch.object(vision, "_run",
                         return_value=(b"\xff\xd8JPEG", b"", 0.2)) as capture:
                result = vision.observe("rtsp://secret:password@192.168.1.55:554/ch0",
                                        model_path=str(weights), consent=True, samples=2)
            self.assertEqual(capture.call_count, 2)
            self.assertEqual(FakeModel.instances, 1)
            self.assertEqual(result["current_visible"], {"book": 1, "cup": 2})
            self.assertEqual(result["peak_visible"], {"book": 1, "cup": 2})
            self.assertFalse(result["remote_image_sent"])
            self.assertFalse(result["image_persisted"])
            self.assertNotIn("secret", json.dumps(result))
            self.assertIn("not unique", result["count_kind"])

    def test_remote_calls_only_once_and_only_with_consent(self):
        class FakeImage:
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def convert(self, *_): return object()
        class FakeModel:
            def __init__(self, *_): pass
            def predict(self, **_): return [Result()]
        with tempfile.TemporaryDirectory() as temp:
            weights = Path(temp) / "trusted.onnx"
            weights.write_bytes(b"mock")
            import sys
            from types import SimpleNamespace
            modules = {"PIL": SimpleNamespace(Image=SimpleNamespace(open=lambda f: FakeImage())),
                       "ultralytics": SimpleNamespace(YOLO=FakeModel)}
            with patch.dict(sys.modules, modules), patch.object(vision, "_run",
                     return_value=(b"\xff\xd8JPEG", b"", 0.2)), patch.object(
                     vision, "ask_ollama", return_value="Есть две чашки") as remote:
                info = vision.observe("rtsp://192.168.1.55/ch0", model_path=str(weights),
                                      consent=True, samples=2,
                                      ollama_endpoint="http://127.0.0.1:11434",
                                      ollama_model="qwen2.5vl:7b",
                                      ollama_consent=True)
            self.assertEqual(remote.call_count, 1)
            self.assertTrue(info["remote_image_sent"])
            self.assertEqual(info["ollama"]["keep_alive"], 0)
            self.assertEqual(info["ollama"]["frame"], 2)

    def test_cli_wiring_for_observe(self):
        with patch("wifcam_helper.vision.observe", return_value={"test": "observe"}) as observe:
            res = bench.run_test("observe", url="rtsp://127.0.0.1/ch0",
                                 model="/test.onnx", vision_consent=True, samples=1)
        self.assertEqual(res["test"], "observe")
        self.assertEqual(observe.call_args.kwargs["samples"], 1)


if __name__ == "__main__":
    unittest.main()
