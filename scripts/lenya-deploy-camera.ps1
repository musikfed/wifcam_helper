# Apply existing verified camera overlay to a running T23N over SSH + scp -O.
# Dry-run by default. Never reflash, reboot or reconfigure Raptor/network.
[CmdletBinding()]
param(
  [string]$PackageRoot = 'F:\peginelab',
  [string]$CameraIp = '192.168.1.55',
  [switch]$Apply
)
$ErrorActionPreference = 'Stop'
$parsed = $null
if (-not [Net.IPAddress]::TryParse($CameraIp,[ref]$parsed) -or
    $parsed.AddressFamily -ne [Net.Sockets.AddressFamily]::InterNetwork) {
  throw 'Expected IPv4 camera address'
}
$src = Join-Path $PackageRoot 'Lenya_Station_v2\camera'
if (-not (Test-Path (Join-Path $src 'INSTALL_CAMERA.sh'))) { throw "No camera sources: $src" }
$hostName = 'root@' + $CameraIp
Write-Host "Camera: $hostName"
& ssh -o ConnectTimeout=6 $hostName 'uname -m; test -s /opt/wificam/httpd.conf; test -s /usr/share/wificam-web/index.html'
if ($LASTEXITCODE -ne 0) { throw 'Camera preflight failed. Nothing changed.' }
if (-not $Apply) { Write-Host 'DRY RUN. Add -Apply to deploy.'; exit 0 }
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupCommand = 'mkdir -p /opt/wificam/backups /opt/wificam/Lenya_Station_v2; if [ -d /opt/wificam/Lenya_Station_v2/camera ]; then cp -R /opt/wificam/Lenya_Station_v2/camera /opt/wificam/backups/lenya-camera-source-' + $stamp + '; fi'
& ssh $hostName $backupCommand
if ($LASTEXITCODE -ne 0) { throw 'Remote backup failed' }
# Legacy SCP is required because the camera has no SFTP server.
& scp -O -r $src ($hostName + ':/opt/wificam/Lenya_Station_v2/')
if ($LASTEXITCODE -ne 0) { throw 'SCP failed; installer not started' }
& ssh $hostName 'sh /opt/wificam/Lenya_Station_v2/camera/INSTALL_CAMERA.sh'
if ($LASTEXITCODE -ne 0) { throw 'Camera installer failed; inspect on-SD backups' }
Write-Host 'Overlay installed. Existing voice enable flag and endpoint config preserved.'
