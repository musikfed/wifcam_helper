"""Opt-in single-frame classification on CORE, never on the Ingenic T23N.

Requires user-supplied, trusted local model weights and optional ultralytics.
No model download, picture archive or persistent camera process.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import time

from .bench import BenchError, _run, redacted_url, stream_url


def classify(url: str, *, model_path: str, device: str = "cpu", consent: bool = False) -> dict:
    if not consent:
        raise BenchError("Visual classification requires explicit --vision-consent")
    stream_url(url)
    if device not in ("cpu", "cuda:0"):
        raise BenchError("Only cpu or cuda:0 is supported")
    if not model_path:
        raise BenchError("Provide a local, operator-trusted YOLO model path")
    weights = Path(model_path).expanduser().resolve()
    if not weights.is_file() or weights.suffix.lower() not in (".pt", ".onnx"):
        raise BenchError("Trusted local YOLO .pt/.onnx weights not found; auto-download is disabled")
    try:
        from PIL import Image
        from ultralytics import YOLO
    except ImportError as exc:
        raise BenchError("Optional classifier not installed on CORE; install ultralytics explicitly") from exc
    out, _, decode = _run(
        ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
         "-rtsp_transport", "tcp", "-fflags", "nobuffer",
         "-i", url, "-map", "0:v:0", "-frames:v", "1",
         "-f", "image2pipe", "-vcodec", "mjpeg", "pipe:1"],
        timeout=20, stdout_limit=5_000_000,
    )
    if not out.startswith(b"\xff\xd8"):
        raise BenchError("Camera did not return a valid JPEG")
    started = time.monotonic()
    image = Image.open(BytesIO(out)).convert("RGB")
    model = YOLO(str(weights))
    results = model.predict(source=image, device=device, imgsz=416,
                            conf=0.35, verbose=False, save=False)
    inference = time.monotonic() - started
    detected = []
    if results:
        result = results[0]
        names = result.names
        if result.boxes is not None:
            for box in result.boxes[:30]:
                index = int(box.cls.item())
                name = names.get(index, str(index)) if isinstance(names, dict) else names[index]
                detected.append({"class": str(name)[:70], "confidence": round(float(box.conf.item()), 3)})
    return {"test": "classification", "url": redacted_url(url),
            "device": device, "trusted_model_file": weights.name,
            "startup_and_decode_s": decode, "model_load_and_inference_s": round(inference, 3),
            "detections": detected, "image_persisted": False,
            "physical_image_quality_assessed": False,
            "note": "Single-frame optional YOLO on CORE, not real-time camera vision or latency"}
