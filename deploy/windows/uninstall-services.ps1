# Remove the MAS Digital Windows services. Run as Administrator.
# Usage:  powershell -ExecutionPolicy Bypass -File deploy\windows\uninstall-services.ps1
$ErrorActionPreference = "SilentlyContinue"
foreach ($name in @("MAS-Worker", "MAS-Webapp")) {
  if (Get-Service $name -ErrorAction SilentlyContinue) {
    Write-Host "Removing $name ..."
    & nssm stop $name
    & nssm remove $name confirm
  }
}
Write-Host "Done."
