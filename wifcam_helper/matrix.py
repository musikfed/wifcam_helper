"""Conservative multi-run comparison; never alters camera registers or flash.

Compare only *already available* RTSP streams. Scores describe decode
throughput and connection overhead, not optical quality or camera latency.
"""
from __future__ import annotations
from .bench import BenchError, probe, video_sample, stream_url, redacted_url


def compare(urls: list[str], *, seconds: int = 4) -> dict:
    if not 1 <= len(urls) <= 2:
        raise BenchError("Compare one or two known camera RTSP URLs")
    if len(set(urls)) != len(urls):
        raise BenchError("Duplicate RTSP stream URL")
    for url in urls:
        stream_url(url)
    outcomes = []
    for url in urls:
        for transport in ("tcp", "udp"):
            row = {"stream": redacted_url(url), "transport": transport}
            try:
                info = probe(url, transport)
                frame = video_sample(url, transport, seconds)
                row.update({"ok": True, "streams": info["streams"],
                            "audio_track": info["audio_track"],
                            "setup_s": info["setup_s"],
                            "effective_fps_including_setup": frame["effective_fps_including_setup"],
                            "decoded_frames": frame["decoded_frames"]})
            except BenchError:
                # Never expose FFmpeg stderr or URLs with embedded credentials.
                row.update({"ok": False, "error": "Stream unavailable or decode failed"})
            outcomes.append(row)
    available = [x for x in outcomes if x.get("ok") and x.get("decoded_frames", 0) >= 3]
    # A throughput pick is not an image quality or physical latency verdict.
    best = sorted(available, key=lambda x: (-x["effective_fps_including_setup"], x["setup_s"]))[0] if available else None
    return {"test": "compare", "camera_settings_changed": False,
            "results": outcomes, "decode_throughput_candidate": {
                "stream": best["stream"], "transport": best["transport"]} if best else None,
            "physical_latency_measured": False, "picture_quality_assessed": False,
            "next": "Review H.264 resolution/bitrate, low-light image, motion blur and independently measure glass-to-glass delay",
            "note": "Candidate optimizes host decode throughput only; never auto-flash or rewrite kernel"}
