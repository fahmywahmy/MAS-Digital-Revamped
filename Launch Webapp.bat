@echo off
setlocal enabledelayedexpansion
title MAS Digital Revamped - Webapp Launcher

REM ---------------------------------------------------------------------------
REM  Launch Webapp.bat  (MAS Digital Revamped)
REM
REM  Double-click to start the Next.js dev server and open the app in your
REM  browser. If the server is already running, it just opens the browser.
REM
REM    1. If port 3000 is already listening -> open http://localhost:3000.
REM    2. Otherwise -> start `npm run dev` in a labeled cmd window, then open
REM       the splash page (.launcher\splash.html) which polls localhost:3000
REM       and redirects automatically once Next.js finishes its first compile.
REM ---------------------------------------------------------------------------

set "REPO=%~dp0"
set "WEBAPP=%REPO%webapp"
set "SPLASH=%REPO%.launcher\splash.html"
set "PORT=3000"

REM -- Sanity: is the webapp present in this repo yet? -------------------------
if not exist "%WEBAPP%\package.json" (
  echo [Launcher] webapp not found at %WEBAPP%
  echo [Launcher] The Next.js webapp has not been ported into this repo yet.
  echo [Launcher] See PORTING_PLAN.md ^(section D, step 5^), then re-run this.
  echo [Launcher] ^(Run this file from the repo root.^)
  pause
  exit /b 1
)

REM -- First run: install dependencies once ------------------------------------
if not exist "%WEBAPP%\node_modules" (
  echo [Launcher] node_modules not found - running npm install once...
  pushd "%WEBAPP%"
  call npm install
  if errorlevel 1 (
    echo [Launcher] npm install failed. See the output above.
    popd
    pause
    exit /b 1
  )
  popd
)

REM -- Already running? Just open the browser. ---------------------------------
netstat -ano | findstr ":%PORT% " | findstr LISTENING >nul 2>&1
if !errorlevel! equ 0 (
  echo [Launcher] Server already running on port %PORT%. Opening browser...
  start "" "http://localhost:%PORT%"
  timeout /t 2 /nobreak >nul
  exit /b 0
)

REM -- Start the dev server in a separate, clearly labeled window. -------------
echo [Launcher] Starting Next.js dev server in a new window...
echo [Launcher] (Close that window when you're done - that stops the server.)
start "MAS Webapp Server (do not close)" cmd /k "cd /d ""%WEBAPP%"" && npm run dev"

REM -- Open the splash so the user sees progress. -----------------------------
if exist "%SPLASH%" (
  start "" "%SPLASH%"
) else (
  echo [Launcher] Splash missing - opening localhost directly in 15s.
  timeout /t 15 /nobreak >nul
  start "" "http://localhost:%PORT%"
)

exit /b 0
