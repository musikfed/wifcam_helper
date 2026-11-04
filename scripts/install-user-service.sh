#!/usr/bin/env bash
# Install a separate unprivileged user service; no firmware/build jobs.
set -euo pipefail
[[ "$(id -u)" != "0" ]] || { echo 'Run as normal Ubuntu user, not root' >&2; exit 2; }
ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
[[ -f "$ROOT/wifcam_helper/web.py" ]] || { echo "Helper repo missing" >&2; exit 2; }
[[ "$ROOT" != *' '* ]] || { echo "Path must not contain spaces" >&2; exit 2; }
[[ -x /usr/bin/python3 ]] || { echo "/usr/bin/python3 missing" >&2; exit 2; }
UNIT=peginelab-wifcam-helper.service
DIR="$HOME/.config/systemd/user"
mkdir -p "$DIR"
if [[ -f "$DIR/$UNIT" ]] && ! grep -Fqx "WorkingDirectory=$ROOT" "$DIR/$UNIT"; then
  echo "Existing Helper service belongs to a different checkout; inspect before replacing." >&2
  exit 3
fi
cat > "$DIR/$UNIT" <<EOF
[Unit]
Description=PegineLab WifCam Helper independent camera diagnostics
After=network.target

[Service]
Type=simple
WorkingDirectory=$ROOT
ExecStart=/usr/bin/python3 -m wifcam_helper web
Environment=PYTHONUNBUFFERED=1
UMask=0077
NoNewPrivileges=true
Restart=on-failure
RestartSec=3

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
echo "Installed $UNIT; loopback 127.0.0.1:8765, never public."
echo "Start explicitly with: bash scripts/helper-service.sh start"
if (( $# > 0 )) && [[ "$1" == "--start" ]]; then
  systemctl --user enable --now "$UNIT"
elif (( $# > 0 )); then
  echo "Usage: bash scripts/install-user-service.sh [--start]" >&2
  exit 2
fi
