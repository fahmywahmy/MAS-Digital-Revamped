# Install MAS Digital as reboot-durable Windows services via NSSM.
#
# Why NSSM: the durable runtime only delivers "survives a restart" if the worker
# process itself comes back after a crash or host reboot. NSSM supervises it
# (auto-restart on failure, auto-start on boot) and captures logs — the Windows
# equivalent of systemd on a cloud box. This replaces the dev .bat launchers as
# the durable path.
#
# PREREQUISITES (run as Administrator):
#   1. NSSM on PATH.  Install via:  choco install nssm   (or scoop install nssm)
#   2. .venv created + deps installed; `npm install` done for the webapp.
#
# STATUS: operator-run. Not yet installed/verified on a host by the build — the
# worker binary it points at (`-m tools.runtime.worker`) IS proven (restart-survival
# proof). Run this on the target host, then `Get-Service MAS-*` to confirm.
#
# Usage:   powershell -ExecutionPolicy Bypass -File deploy\windows\install-services.ps1
[CmdletBinding()]
param(
  [string]$RepoRoot = (Resolve-Path "$PSScriptRoot\..\.."),
  [switch]$IncludeWebapp  # enable once the P2 console build exists
)

$ErrorActionPreference = "Stop"
if (-not (Get-Command nssm -ErrorAction SilentlyContinue)) {
  throw "nssm not found on PATH. Install it (choco install nssm) and re-run as Administrator."
}

$python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw ".venv python not found at $python" }
$logDir = Join-Path $RepoRoot "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Install-Service($name, $exe, $args, $appDir) {
  Write-Host "Installing service $name ..."
  & nssm install $name $exe $args
  & nssm set $name AppDirectory $appDir
  & nssm set $name AppStdout (Join-Path $logDir "$name.out.log")
  & nssm set $name AppStderr (Join-Path $logDir "$name.err.log")
  & nssm set $name AppExit Default Restart          # restart on crash
  & nssm set $name AppRestartDelay 5000             # 5s backoff
  & nssm set $name Start SERVICE_AUTO_START         # start on boot
  & nssm set $name AppRotateFiles 1                 # rotate logs
}

# ── Worker (the durable-runtime component) ──────────────────────────────────────
Install-Service "MAS-Worker" $python "-m tools.runtime.worker" $RepoRoot

# ── Webapp (enable after the P2 console is built: needs `npm run build` first) ──
if ($IncludeWebapp) {
  $npm = (Get-Command npm).Source
  Install-Service "MAS-Webapp" $npm "run start" $RepoRoot
}

Write-Host ""
Write-Host "Done. Start now with:  Start-Service MAS-Worker"
Write-Host "Verify with:           Get-Service MAS-*"
Write-Host "Logs:                  $logDir"
