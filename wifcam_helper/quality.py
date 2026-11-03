"""Rank ONLY manually measured glass-to-glass latency against real image scores.

No guessed camera capabilities; no automatic Raptor/ISP/kernel modifications.
Capture a scene with a second phone at 120/240fps, comparing its direct
view of an LED/clock to the displayed camera picture.
"""
from __future__ import annotations

import csv
from pathlib import Path
import statistics
from urllib.parse import urlsplit
from .bench import BenchError


REQUIRED = {"profile", "scene", "transport", "glass_to_glass_ms",
            "image_quality_1_to_5", "dropout_pct"}


def analyze_csv(path: Path, *, min_quality: float = 3.0, max_dropout: float = 3.0) -> dict:
    if not 1 <= min_quality <= 5 or not 0 <= max_dropout <= 100:
        raise BenchError("Invalid quality thresholds")
    if not path.is_file() or path.stat().st_size > 256_000:
        raise BenchError("Measurement CSV missing or too large")
    groups: dict[str, list[dict]] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not REQUIRED.issubset(set(reader.fieldnames or [])):
            raise BenchError("CSV fields missing")
        for row in reader:
            profile = row["profile"].strip()
            scene = row["scene"].strip().lower()
            transport = row["transport"].strip().lower()
            if not profile or len(profile) > 80 or scene not in ("day", "night", "motion") or transport not in ("tcp", "udp"):
                raise BenchError("Invalid profile / day, night, motion scene / TCP or UDP")
            try:
                ms = float(row["glass_to_glass_ms"])
                quality = float(row["image_quality_1_to_5"])
                loss = float(row["dropout_pct"])
            except (ValueError, TypeError) as exc:
                raise BenchError("Every row must contain real numeric measurements") from exc
            if not (0 < ms < 30000 and 1 <= quality <= 5 and 0 <= loss <= 100):
                raise BenchError("Measurement out of range")
            groups.setdefault(profile + "/" + transport, []).append({
                "scene": scene, "latency_ms": ms, "quality": quality, "loss_pct": loss,
            })
    ranked = []
    for key, rows in groups.items():
        # A single well-lit scene cannot justify the optimal image profile.
        scenes = {r["scene"] for r in rows}
        enough = scenes == {"day", "night", "motion"}
        latency = round(statistics.median(r["latency_ms"] for r in rows), 2)
        quality = round(statistics.mean(r["quality"] for r in rows), 2)
        loss = round(max(r["loss_pct"] for r in rows), 2)
        approved = bool(enough and quality >= min_quality and loss <= max_dropout)
        ranked.append({"profile_transport": key, "scenes": sorted(scenes),
                       "median_glass_to_glass_ms": latency,
                       "mean_manual_quality_1_to_5": quality,
                       "max_dropouts_pct": loss,
                       "satisfies_constraints": approved})
    sorted_rank = sorted((r for r in ranked if r["satisfies_constraints"]),
                         key=lambda r: (r["median_glass_to_glass_ms"], -r["mean_manual_quality_1_to_5"]))
    return {
        "schema": "peginelab.wifcam-helper.image-quality.v1",
        "source": "operator-measured physical glass-to-glass + manual scene scoring",
        "ranked": sorted(ranked, key=lambda x: x["profile_transport"]),
        "recommended_if_hardware_verified": sorted_rank[0]["profile_transport"] if sorted_rank else None,
        "next": "Manually review candidate, verify sound/PTZ/SSH and commit firmware changes in WIFICAM only",
        "camera_configuration_modified": False,
    }
