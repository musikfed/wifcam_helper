"""Local-only T23N test primitives. No firmware flash, config change or open mic by default."""
from __future__ import annotations

import argparse
import datetime as dt
import ipaddress
import json
import math
import shlex
import os
from pathlib import Path
import re
import shutil
import statistics
import struct
import subprocess
import sys
import time
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
STATE = Path(os.environ.get("WIFCAM_HELPER_STATE", str(Path.home() / ".local/state/wifcam-helper"))).expanduser()
HOST_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]{0,252}$")
USER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]{0,31}$")
ALLOWED_TRANSPORTS = ("tcp", "udp")


class BenchError(RuntimeError):
    pass


def host_ok(host: str) -> str:
    if not HOST_RE.fullmatch(host) or ".." in host or host.endswith("."):
        raise BenchError("Invalid SSH hostname; expected an IP or ordinary DNS name")
    return host


def user_ok(user: str) -> str:
    if not USER_RE.fullmatch(user):
        raise BenchError("Invalid SSH username")
    return user


def stream_url(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme.lower() != "rtsp" or not parts.hostname:
        raise BenchError("Use an explicit rtsp:// URL for your own camera")
    # Allow only the host, port and stream path. Do not accept queries/fragments
    # that may contain tokens and might accidentally be included in results.
    if parts.query or parts.fragment:
        raise BenchError("RTSP URLs with query strings or fragments are not supported")
    if parts.hostname.startswith("-"):
        raise BenchError("Invalid RTSP host")
    return url


def redacted_url(url: str) -> str:
    p = urlsplit(url)
    return urlunsplit((p.scheme, p.hostname + (":" + str(p.port) if p.port else ""), p.path, "", ""))


def _run(args: list[str], *, timeout: float = 20, input_bytes: bytes | None = None,
         stdout_limit: int = 2_000_000) -> tuple[bytes, bytes, float]:
    if not shutil.which(args[0]):
        raise BenchError("Missing program: " + args[0])
    started = time.monotonic()
    try:
        done = subprocess.run(args, input=input_bytes, capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise BenchError(f"Timed out after {timeout:g}s: {args[0]}") from exc
    if len(done.stdout) > stdout_limit or len(done.stderr) > 150_000:
        raise BenchError("Tool output exceeded safe diagnostic limit")
    if done.returncode:
        # Never return FFmpeg/SSH stderr: it may echo a password-bearing URL.
        raise BenchError(f"{args[0]} exited with status {done.returncode}; verify stream/permissions")
    return done.stdout, done.stderr, round(time.monotonic() - started, 3)


def ssh_argv(host: str, user: str = "root", key: str | None = None) -> list[str]:
    args = ["ssh", "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
            "-o", "ConnectTimeout=5", "-o", "LogLevel=ERROR"]
    if key:
        p = Path(key).expanduser()
        if not p.is_file():
            raise BenchError("SSH key not found; use a pre-provisioned identity")
        args += ["-i", str(p)]
    return args + [user_ok(user) + "@" + host_ok(host)]


INVENTORY_COMMAND = """
printf 'kernel='; uname -r
printf 'board='; cat /proc/cpuinfo 2>/dev/null | grep -m1 -E 'system type|cpu model' | cut -c1-120 || true
printf 'memory='; grep -m1 MemAvailable /proc/meminfo 2>/dev/null || true
for cmd in rac play microphone speaker raptorctl ffmpeg; do
  if command -v "$cmd" >/dev/null 2>&1; then echo "tool.$cmd=present"; else echo "tool.$cmd=absent"; fi
done
for svc in rvd rsd rad rhd rac motors-daemon dropbear; do
  if pidof "$svc" >/dev/null 2>&1; then echo "process.$svc=running"; else echo "process.$svc=stopped"; fi
done
printf 'speaker='; speaker status 2>/dev/null || echo unavailable
printf 'microphone='; microphone status 2>/dev/null || echo unavailable
for pair in 'audio enabled' 'audio ao_enabled' 'rtsp backchannel' 'stream0 fps' 'stream0 bitrate' 'sensor low_latency' 'jpeg fps'; do
  set -- $pair
  printf 'raptor.%s.%s=' "$1" "$2"
  raptorctl config get "$1" "$2" 2>/dev/null | head -c 100 || true
  echo
done
""".strip()


def inventory(*, host: str, user: str = "root", key: str | None = None) -> dict:
    out, _, wall = _run(ssh_argv(host, user, key) + ["sh -c " + shlex.quote(INVENTORY_COMMAND)], timeout=14)
    items = {}
    for line in out.decode("utf-8", "replace").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            if re.fullmatch(r"[a-zA-Z0-9_.-]+", k):
                items[k] = v.strip()[:140]
    return {"test": "inventory", "host": host_ok(host), "elapsed_s": wall, "values": items,
            "physical_mic_verified": False, "physical_speaker_verified": False}


def probe(url: str, transport: str = "tcp") -> dict:
    stream_url(url)
    if transport not in ALLOWED_TRANSPORTS:
        raise BenchError("Transport must be tcp or udp")
    out, _, wall = _run(["ffprobe", "-v", "error", "-rtsp_transport", transport,
                         "-show_entries", "stream=index,codec_type,codec_name,width,height,avg_frame_rate,bit_rate,sample_rate,channels",
                         "-of", "json", url], timeout=18)
    try:
        streams = json.loads(out).get("streams", [])
    except (ValueError, AttributeError) as exc:
        raise BenchError("ffprobe returned invalid stream metadata") from exc
    if not isinstance(streams, list) or not streams:
        raise BenchError("No RTSP streams advertised")
    keep = ("index", "codec_type", "codec_name", "width", "height", "avg_frame_rate",
            "bit_rate", "sample_rate", "channels")
    clean = [{k: x[k] for k in keep if k in x} for x in streams if isinstance(x, dict)]
    return {"test": "probe", "url": redacted_url(url), "transport": transport,
            "setup_s": wall, "streams": clean, "audio_track": any(s.get("codec_type") == "audio" for s in clean)}


def video_sample(url: str, transport: str = "tcp", seconds: int = 4) -> dict:
    stream_url(url)
    if transport not in ALLOWED_TRANSPORTS or seconds not in (3, 4, 5):
        raise BenchError("Video test requires tcp/udp and 3, 4, or 5 seconds")
    # Decode-only, no playback, no saved frames or modified camera settings.
    args = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
            "-rtsp_transport", transport, "-fflags", "nobuffer", "-flags", "low_delay",
            "-probesize", "32768", "-analyzeduration", "200000",
            "-i", url, "-map", "0:v:0", "-an", "-t", str(seconds),
            "-f", "null", "-", "-progress", "pipe:1"]
    out, _, wall = _run(args, timeout=seconds + 20)
    frames = [int(v) for v in re.findall(rb"(?:^|\n)frame=(\d+)", out)]
    count = max(frames, default=0)
    return {"test": "video", "url": redacted_url(url), "transport": transport,
            "seconds_requested": seconds, "wall_s": wall, "decoded_frames": count,
            "effective_fps_including_setup": round(count / wall, 2) if wall else 0,
            "note": "Decode throughput incl. setup; NOT glass-to-glass latency"}


def microphone(url: str, *, seconds: int = 2, consent: bool = False) -> dict:
    if not consent:
        raise BenchError("Microphone analysis requires explicit --mic-consent")
    stream_url(url)
    if seconds not in (1, 2, 3):
        raise BenchError("Mic test duration must be 1-3 seconds")
    out, _, wall = _run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
                         "-rtsp_transport", "tcp", "-i", url, "-map", "0:a:0", "-vn",
                         "-t", str(seconds), "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
                         "-f", "s16le", "pipe:1"], timeout=seconds + 15, stdout_limit=200_000)
    if not out or len(out) % 2:
        raise BenchError("No valid microphone PCM16 samples")
    samples = struct.unpack("<" + "h" * (len(out) // 2), out)
    rms = math.sqrt(sum(v * v for v in samples) / len(samples)) / 32768
    dbfs = round(20 * math.log10(max(rms, 1e-9)), 2)
    return {"test": "microphone", "url": redacted_url(url), "duration_s": wall,
            "pcm_samples": len(samples), "rms_dbfs": dbfs,
            "audio_persisted": False, "physical_mic_verified": False,
            "note": "An audio track and RMS do not establish a correctly wired microphone"}


def speaker(*, host: str, user: str = "root", key: str | None = None,
            consent: bool = False) -> dict:
    if not consent:
        raise BenchError("Speaker test requires explicit --speaker-consent")
    rate, duration, amplitude = 16000, 0.20, 0.025
    pcm = b"".join(struct.pack("<h", int(32767 * amplitude * math.sin(2 * math.pi * 440 * i / rate)))
                   for i in range(int(rate * duration)))
    # Tiny quiet test tone only; no remote configuration edits.
    _, _, wall = _run(ssh_argv(host, user, key) + ["play -s -r 16000 -"],
                       timeout=12, input_bytes=pcm)
    return {"test": "speaker", "host": host_ok(host), "command_success": True,
            "elapsed_s": wall, "physical_speaker_verified": False,
            "note": "Ask a person near camera to confirm the quiet 0.2s tone was audible"}


def state_file() -> Path:
    STATE.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        os.chmod(STATE, 0o700)
    except OSError:
        pass
    return STATE / "last-report.json"


def store(report: dict) -> dict:
    doc = {"schema": "peginelab.wifcam-helper.report.v1",
           "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
           "result": report}
    p = state_file()
    # Persist in Helper-only SQLite before updating the legacy last-report cache.
    # Neither factory jobs nor camera firmware databases are touched.
    from .history import append
    append(STATE, doc)
    tmp = p.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.chmod(tmp, 0o600)
    tmp.replace(p)
    return doc


def read_last() -> dict | None:
    p = state_file()
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def conservative_preset() -> dict:
    """Build-only allowlist. No measurement can imply that physical audio works."""
    return {
        "schema": "peginelab.wifcam-helper.build-preset.v1",
        "camera": "galayou_g2_t23n_sc2336_atbm6012bx",
        "branch": "mymarrchWFcam",
        "build_env": {"WIFICAM_WEBRTC": "0"},
        "requires_hardware_verification": True,
        "notes": "Safe lean Raptor profile; RAD/RAC mic and speaker mandatory; factory PUBLISH=0",
    }


def export_preset(path: Path) -> dict:
    doc = conservative_preset()
    path = path.expanduser().resolve()
    if path.suffix != ".json":
        raise BenchError("Preset destination must be .json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return doc


def run_test(kind: str, *, host: str = "", user: str = "root", key: str = "",
             url: str = "", alt_url: str = "", transport: str = "tcp", mic_consent: bool = False,
             speaker_consent: bool = False, vision_consent: bool = False,
             model: str = "", device: str = "cpu") -> dict:
    if kind == "inventory":
        return inventory(host=host, user=user, key=key or None)
    if kind == "probe":
        return probe(url, transport)
    if kind == "video":
        return video_sample(url, transport)
    if kind == "compare":
        from .matrix import compare
        return compare([u for u in (url, alt_url) if u])
    if kind == "microphone":
        return microphone(url, consent=mic_consent)
    if kind == "speaker":
        return speaker(host=host, user=user, key=key or None, consent=speaker_consent)
    if kind == "classification":
        from .classifier import classify
        return classify(url, model_path=model, device=device, consent=vision_consent)
    raise BenchError("Unsupported test")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wifcam-helper", description="Non-destructive T23N bench")
    parser.add_argument("command", choices=["inventory", "probe", "video", "compare", "microphone", "speaker", "classification",
                                             "report", "export-preset", "quality-evaluate", "web"])
    parser.add_argument("--host", default="")
    parser.add_argument("--user", default="root")
    parser.add_argument("--ssh-key", default="")
    parser.add_argument("--rtsp-url", default="")
    parser.add_argument("--alt-rtsp-url", default="")
    parser.add_argument("--transport", choices=ALLOWED_TRANSPORTS, default="tcp")
    parser.add_argument("--mic-consent", action="store_true")
    parser.add_argument("--speaker-consent", action="store_true")
    parser.add_argument("--vision-consent", action="store_true")
    parser.add_argument("--model", default="")
    parser.add_argument("--device", choices=("cpu", "cuda:0"), default="cpu")
    parser.add_argument("--output", default="")
    parser.add_argument("--csv", default="")
    args = parser.parse_args(argv)
    try:
        if args.command == "web":
            from .web import serve
            serve()
            return 0
        if args.command == "report":
            result = read_last()
        elif args.command == "export-preset":
            dst = Path(args.output) if args.output else STATE / "build-preset.json"
            result = export_preset(dst)
        elif args.command == "quality-evaluate":
            if not args.csv:
                raise BenchError("Provide --csv with real day/night/motion glass-to-glass measurements")
            from .quality import analyze_csv
            result = store(analyze_csv(Path(args.csv)))
        else:
            result = store(run_test(
                args.command, host=args.host, user=args.user, key=args.ssh_key,
                url=args.rtsp_url, alt_url=args.alt_rtsp_url, transport=args.transport,
                mic_consent=args.mic_consent, speaker_consent=args.speaker_consent,
                vision_consent=args.vision_consent, model=args.model, device=args.device,
            ))
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (BenchError, OSError, ValueError, json.JSONDecodeError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 2
