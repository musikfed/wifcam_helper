#!/usr/bin/env bash
# No docker, GPU, kernel or factory service actions.
set -euo pipefail
[[ "$(id -u)" != "0" ]] || { echo 'Run as normal Ubuntu user, not root' >&2; exit 2; }
UNIT=peginelab-wifcam-helper.service
ACTION=status
if (( $# > 0 )); then ACTION="$1"; fi
case "$ACTION" in
  start) systemctl --user start "$UNIT" ;;
  stop) systemctl --user stop "$UNIT" ;;
  restart) systemctl --user restart "$UNIT" ;;
  status) systemctl --user --no-pager status "$UNIT" || true ;;
  *) echo 'Usage: bash scripts/helper-service.sh [status|start|stop|restart]' >&2; exit 2 ;;
esac
