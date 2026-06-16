@echo off
setlocal enabledelayedexpansion
title MAS Digital Revamped - Stop Webapp

REM ---------------------------------------------------------------------------
REM  Stop Webapp.bat  (MAS Digital Revamped)
REM
REM  Finds whatever process is listening on port 3000 and kills it. Use this
REM  if you closed the splash but the server window is still hanging around,
REM  or if `npm run dev` is wedged.
REM ---------------------------------------------------------------------------

set "PORT=3000"

set "PID="
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORT% " ^| findstr LISTENING') do (
  set "PID=%%a"
)

if "!PID!"=="" (
  echo [Stop] Nothing is listening on port %PORT%. Nothing to do.
  timeout /t 2 /nobreak >nul
  exit /b 0
)

echo [Stop] Killing PID !PID! (port %PORT%)...
taskkill /PID !PID! /T /F
if errorlevel 1 (
  echo [Stop] taskkill failed. Close the server cmd window manually.
  pause
  exit /b 1
)

echo [Stop] Server stopped.
timeout /t 2 /nobreak >nul
exit /b 0
