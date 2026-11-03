#!/usr/bin/env bash
# Audit the approved source/build hand-off; NEVER compile, push or flash here.
set -euo pipefail
THIS="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="$(cd "$THIS/../.." && pwd)"
PROJECTS="$ROOT/projects"
if [[ "$PROJECTS" != "$(dirname "$THIS")" ]]; then
  echo "Projects are not sibling directories under PEGINELAB_HOME/projects" >&2
  exit 2
fi
FACTORY="$PROJECTS/YadroKreator"
FIRMWARE="$PROJECTS/wificam_T23N"
test -f "$FACTORY/helper_profiles.py" || { echo "YadroKreator is missing helper_profiles.py; update it from GitHub main" >&2; exit 2; }
test -f "$FIRMWARE/scripts/build_thingino_wificam_image.sh" || { echo "Missing sibling WIFICAM build script" >&2; exit 2; }
test -f "$THIS/profiles/t23n_lean.json"
export PEGINELAB_HOME="$ROOT"
# Validate exact allowlist using the actual factory code without triggering a job.
PYTHONPATH="$FACTORY" python3 - "$THIS/profiles/t23n_lean.json" <<'PY'
import json, sys
from pathlib import Path
from helper_profiles import checked_profile
file = Path(sys.argv[1])
validated = checked_profile(json.loads(file.read_text(encoding="utf-8")), branch="mymarrchWFcam")
print("Factory import contract: OK")
print("Camera profile:", validated["camera"])
print("Allowed build options:", validated["build_env"])
print("Next step: choose mymarrchWFcam and tick WifCam Helper in YadroKreator Builds.")
print("No builds, kernel edits, SD writes or camera commands performed.")
PY
