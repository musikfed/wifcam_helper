#!/usr/bin/env bash
set -euo pipefail
echo "WifCam Helper host preflight — no camera configuration changed"
for cmd in python3 git ssh ffprobe ffmpeg; do
  if command -v "$cmd" >/dev/null 2>&1; then printf 'OK %s: %s\n' "$cmd" "$(command -v "$cmd")"; else printf 'MISSING %s\n' "$cmd"; fi
done
python3 -c 'import sys; print("Python:", sys.version.split()[0]); assert sys.version_info >= (3,12)'
if command -v uv >/dev/null 2>&1; then uv --version; fi
if command -v nvidia-smi >/dev/null 2>&1; then
  echo "Optional external GPU (never used by T23N encoder):"
  nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true
else echo "No GPU status utility; CPU-only camera checks work"; fi
