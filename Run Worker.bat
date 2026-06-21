@echo off
REM ── Run the durable-queue worker in the FOREGROUND (dev mode) ──────────────
REM The dev counterpart to the NSSM service (deploy/windows/). Drains the
REM pipeline queue; self-heals orphaned jobs on startup. Ctrl+C stops it cleanly.
REM For a reboot-durable install, use deploy/windows/install-services.ps1 instead.

cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [Run Worker] .venv not found. Create it first:
  echo     python -m venv .venv ^&^& .venv\Scripts\pip install -r requirements.txt
  exit /b 1
)
echo [Run Worker] starting durable-queue worker (Ctrl+C to stop)...
".venv\Scripts\python.exe" -m tools.runtime.worker
