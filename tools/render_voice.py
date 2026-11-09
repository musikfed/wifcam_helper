#!/usr/bin/env python3
"""Generate the robot head's short spoken boot phrase (development/CI only).

Only the trusted GitHub Actions job runs the synthesizer; YadroKreator stages
the already generated WAV without executing external Helper repository code.
"""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import wave

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "firmware/audio"
MANIFEST = AUDIO / "boot-voice.json"
OUTPUT = AUDIO / "boot-voice.wav"


def render() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data["schema"] != "peginelab.helper-voice.v1" or data["voice"] != "ru":
        raise ValueError("Invalid Helper voice manifest")
    if (data["sample_rate"], data["channels"], data["sample_width_bytes"]) != (16000, 1, 2):
        raise ValueError("Unsupported camera playback PCM format")
    text = data["spoken_text"]
    if not isinstance(text, str) or len(text) > 256:
        raise ValueError("Invalid short boot phrase")
    tts = shutil.which("espeak-ng") or shutil.which("espeak")
    ffmpeg = shutil.which("ffmpeg")
    if not tts or not ffmpeg:
        raise RuntimeError("Rendering needs espeak-ng/espeak and ffmpeg (only on the CI runner)")
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "speech.wav"
        output = Path(tmp) / "voice.wav"
        subprocess.run([tts,"-v","ru","-s",str(data["rate"]),"-p",str(data["pitch"]),
                        "-a",str(data["amplitude"]),"-w",str(source),text],check=True)
        subprocess.run([ffmpeg,"-nostdin","-hide_banner","-loglevel","error","-y",
                        "-i",str(source),"-af",
                        "highpass=f=140,lowpass=f=3200,compand=attacks=0:decays=0.15:points=-80/-80|-25/-15|0/-6",
                        "-ar","16000","-ac","1","-c:a","pcm_s16le",str(output)],check=True)
        with wave.open(str(output),"rb") as pcm:
            if (pcm.getnchannels(),pcm.getframerate(),pcm.getsampwidth()) != (1,16000,2):
                raise RuntimeError("Unexpected camera PCM format")
            if not (16000 <= pcm.getnframes() <= 15 * 16000):
                raise RuntimeError("Voice phrase must last 1 to 15 seconds")
        OUTPUT.write_bytes(output.read_bytes())
    print(f"Generated spoken Helper startup: {OUTPUT} ({OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    render()
