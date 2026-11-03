#!/usr/bin/env bash
set -euo pipefail
# Wiki is an independent Git repo. User must create initial wiki page on GitHub.
if [[ "$WIFCAM_PUBLISH_WIKI" != "YES" ]]; then
  echo "Explicit WIFCAM_PUBLISH_WIKI=YES required after reviewing wiki/*.md" >&2
  exit 2
fi
BASE="$(cd "$(dirname "$0")/.." && pwd)"
WIKI_REPO="https://github.com/musikfed/wifcam_helper.wiki.git"
command -v git >/dev/null
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git clone --depth 1 "$WIKI_REPO" "$TMP/repo"
cp "$BASE"/wiki/*.md "$TMP/repo/"
git -C "$TMP/repo" add -- '*.md'
if git -C "$TMP/repo" diff --cached --quiet; then echo "No wiki changes"; exit 0; fi
git -C "$TMP/repo" commit -m "docs(wiki): seven-language WifCam Helper hardware bench"
git -C "$TMP/repo" push
echo "Wiki published: https://github.com/musikfed/wifcam_helper/wiki"
