# Read-only tri-node connectivity check, not full continuous monitoring.
[CmdletBinding()]
param([string]$CameraIp='192.168.1.55',[string]$AcerIp='192.168.1.88')
$ErrorActionPreference = 'Continue'
Write-Host '=== Acer Station ==='
try {
  Invoke-RestMethod -Uri 'http://127.0.0.1:11437/api/status' -TimeoutSec 5 |
    Select-Object proxy,proxy_error,voice,voice_error | Format-List
} catch { Write-Warning $_.Exception.Message }
Write-Host '=== Camera ==='
& ssh -o ConnectTimeout=5 ('root@'+$CameraIp) 'uname -a; cat /proc/loadavg; free; df -h /opt/wificam; /etc/init.d/S95lenya-agent status'
Write-Host '=== Ollama through Acer ==='
try {
  Invoke-RestMethod -Uri ('http://'+$AcerIp+':11435/api/version') -TimeoutSec 8 | Format-List
} catch { Write-Warning $_.Exception.Message }
Write-Host 'CORE GPU/VRAM monitoring is PLANNED, not currently provided by this script.'
