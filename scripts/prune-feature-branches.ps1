# Clean only reviewed obsolete remote branches, never main. Dry-run by default.
# Credentials are managed by Git, never stored in this script.
[CmdletBinding()]
param([string]$Repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
      [switch]$Apply)
$ErrorActionPreference = 'Stop'
$branches = @(
  'feature/acer-cpu-vision-ollama-20261104',
  'feature/helper-dual-mode-sd-20261107',
  'feature/helper-t23n-firmware-lane-20261104',
  'feature/helper-ui-audio-build-20261109',
  'feature/service-and-isolated-history-20261104',
  'feature/voice-boot-no-chiptune-20261109',
  'plcodestore/vitrine-proposal'
)
$remote = (& git -C $Repo remote get-url origin)
if ($LASTEXITCODE -ne 0 -or $remote -notmatch 'musikfed/wifcam_helper(\.git)?$') {
  throw "Wrong Git repository or origin: $remote"
}
& git -C $Repo fetch origin --prune
if ($LASTEXITCODE -ne 0) { throw 'Git fetch failed' }
$found = @()
foreach ($branch in $branches) {
  & git -C $Repo show-ref --verify --quiet ('refs/remotes/origin/' + $branch)
  if ($LASTEXITCODE -ne 0) { continue }
  $found += $branch
  $unique = @(& git -C $Repo log --format='%h %s' --max-count=2 ('origin/main..origin/' + $branch))
  Write-Host "Candidate: $branch"
  if ($unique.Count -gt 0) {
    Write-Warning "Unique commits exist on this branch:"
    $unique | ForEach-Object { Write-Host $_ }
  }
}
if (-not $found.Count) { Write-Host 'No obsolete branches found.'; exit 0 }
if (-not $Apply) {
  Write-Host 'DRY RUN. No branches deleted. Review differences before -Apply.'
  exit 0
}
$answer = Read-Host ("Type DELETE {0} to delete these remote branches (main stays)" -f $found.Count)
if ($answer -cne ('DELETE ' + $found.Count)) { throw 'Not confirmed; nothing deleted' }
foreach ($branch in $found) {
  & git -C $Repo push origin --delete $branch
  if ($LASTEXITCODE -ne 0) { Write-Warning "Failed to delete $branch" }
}
Write-Host 'Review remaining branches on GitHub. main and its history were untouched.'
