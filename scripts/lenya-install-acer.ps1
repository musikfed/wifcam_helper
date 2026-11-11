# Install reviewed Lenya Station sources from local peginelab.zip extraction.
# Dry-run by default; never overwrite station-config.json, venv, voices or credentials.
[CmdletBinding()]
param(
  [string]$PackageRoot = 'F:\peginelab',
  [string]$Target = 'F:\peginelab\Lenya_Station_v2\acer',
  [switch]$Apply
)
$ErrorActionPreference = 'Stop'
$source = Join-Path $PackageRoot 'Lenya_Station_v2\acer'
$patch = Join-Path $PackageRoot 'Lenya_Wake_Fix_v22\lenya_voice_server.py'
$names = @('bridge_server.py','lenya_station.py','lenya_voice_server.py',
           'Setup-Station.ps1','Setup-Voice.ps1','Run-Station.ps1',
           'Configure-Station-Firewall.ps1','station-config.json.example','warmup_whisper.py')
foreach ($name in $names) {
  if (-not (Test-Path (Join-Path $source $name))) { throw "Missing source: $name" }
}
if (-not (Test-Path $patch)) { throw 'Missing tested v2.2 wake fix' }
Write-Host "Source: $source"
Write-Host "Target: $Target"
if (-not $Apply) { Write-Host 'DRY RUN. Use -Apply to install.'; exit 0 }
if (Get-NetTCPConnection -LocalPort 11437 -State Listen -ErrorAction SilentlyContinue) {
  throw 'Stop Run-Station.ps1 (Ctrl+C) before updating'
}
New-Item -ItemType Directory -Force -Path $Target | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backup = Join-Path (Split-Path $Target -Parent) ("backup-before-github-$stamp")
New-Item -ItemType Directory -Force -Path $backup | Out-Null
foreach ($name in $names) {
  $from = if ($name -eq 'lenya_voice_server.py') { $patch } else { Join-Path $source $name }
  $to = Join-Path $Target $name
  if ([IO.Path]::GetFullPath($from) -eq [IO.Path]::GetFullPath($to)) { continue }
  if (Test-Path $to) { Copy-Item -LiteralPath $to -Destination (Join-Path $backup $name) -Force }
  Copy-Item -LiteralPath $from -Destination $to -Force
}
$srcTests = Join-Path $PackageRoot 'Lenya_Station_v2\tests'
if (Test-Path $srcTests) {
  $dstTests = Join-Path (Split-Path $Target -Parent) 'tests'
  New-Item -ItemType Directory -Force -Path $dstTests | Out-Null
  foreach ($name in @('test_camera.py','test_station.py','test-fixture.html')) {
    if (Test-Path (Join-Path $srcTests $name)) {
      Copy-Item (Join-Path $srcTests $name) (Join-Path $dstTests $name) -Force
    }
  }
}
Write-Host "Installed source files. Backup: $backup"
Write-Host 'Local config, models, VPN and other Python projects were not changed.'
Write-Host "Next: cd '$Target'; .\Setup-Station.ps1; .\Run-Station.ps1"
